# -*- coding: utf-8 -*-
"""Automated checks of HydraTorque_MC.py (run: python -m pytest -q tests). They test the numerical consistency of the model with its own
assumptions (closed forms, limiting cases, conservation, reproducibility, equivalence with version 1); they do not validate the physical assumptions."""
import importlib.util
import math
import os
import sys
from dataclasses import replace

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
import HydraTorque_MC as H   # noqa: E402

spec = importlib.util.spec_from_file_location("v1", os.path.join(ROOT, "legacy_v1", "HydraTorque_MC_v1.py"))
V1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V1)


@pytest.mark.parametrize("preset", ["mix", "gate_24in", "legacy_seized", "plug_16in"])
def test_legacy_switches_reproduce_version1_exactly(preset):
    a = V1.simulate(preset, V1.Tool(), 30_000, 3)
    b = H.simulate(preset, H.Tool2(), 30_000, 3, H.Model2.legacy())
    for k in ("success", "break_ok", "run_ok", "time_ok", "overtorque", "interference"):
        assert np.array_equal(a[k], b[k]), k


def test_closed_form_breakaway_probability():
    pr, mc, an = H.study_pressure(H.Tool2(), 100_000, 7)
    assert max(abs(x - y) for x, y in zip(mc, an)) < 0.01


def test_closed_form_exceedance_probability_with_relief():
    """Relief-limited, deterministic stall torque = mult x class median: P(T_allow < T_cap) is a mixture of lognormal cdfs."""
    for mult in (1.5, 2.0, 3.0):
        t = replace(H.Tool2(), relief_tol=0.0, relief_mult=mult)
        r = H.simulate("mix", t, 200_000, 5, H.Model2.legacy(), Ps_override=250, nominal=True)
        assert abs(r["overtorque"].mean() - H.analytic_exceedance(mult)) < 0.004


def test_energy_balance_and_tap_power():
    r = H.simulate("mix", H.Tool2(), 100_000, 2)
    assert r["energy_ratio"].max() < 1.0
    assert np.all(r["P_tap"] + 1e-9 >= r["P_in"])


def test_baseline_torque_and_units():
    assert abs(H.nominal_capacity_Nm(H.Tool2(), 100) - 3265) / 3265 < 0.01
    assert abs(H.PSI * 100 / 1e5 - 6.894757) < 1e-6
    assert abs(60 * H.GPM_LPM - 227.1246) < 1e-3


def test_hose_friction_coefficient_matches_fire_service_form():
    C, L, Q = 2.0, 100.0, 250.0
    assert abs(C * L / 1e6 * Q * Q - C * (Q / 100) ** 2 * (L / 100)) < 1e-12


def test_joukowsky_surge_value():
    S = H.sample_inputs("gate_12in", 50, 3)
    S["hose_in"][:] = 2.5; S["a_wave"][:] = 250.0; S["t_close"][:] = 0.01; S["L"][:] = 400.0
    r = H.evaluate(H.Tool2(q_limit_gpm=60.0), S)
    ok = r["Q_run"] > 59.9
    v = 60 * H.GPM_M3S / (math.pi / 4 * (2.5 * H.INCH) ** 2)
    expect = H.RHO * 250.0 * v / H.PSI
    assert ok.any() and np.allclose(r["surge_psi"][ok], expect, rtol=1e-9)


def test_surge_is_reduced_for_slow_closure():
    S = H.sample_inputs("gate_12in", 50, 3)
    S["hose_in"][:] = 2.5; S["a_wave"][:] = 250.0; S["L"][:] = 50.0
    S["t_close"][:] = 0.01; fast = H.evaluate(H.Tool2(), S)["surge_psi"]
    S["t_close"][:] = 0.5; slow = H.evaluate(H.Tool2(), S)["surge_psi"]
    assert np.all(slow <= fast + 1e-12) and np.any(slow < fast)


def test_success_is_monotone_in_supply_pressure():
    vals = [H.simulate("mix", H.Tool2(), 40_000, 4, Ps_override=P)["success"].mean() for P in (40, 80, 120, 160, 200)]
    assert all(b >= a - 0.002 for a, b in zip(vals, vals[1:]))


def test_common_random_numbers_and_reproducibility():
    S = H.sample_inputs("mix", 20_000, 9)
    snap = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in S.items()}
    a = H.evaluate(H.Tool2(), S); b = H.evaluate(replace(H.Tool2(), D_cc=300, ratio=150), S); c = H.evaluate(H.Tool2(), S)
    assert np.array_equal(a["success"], c["success"]) and not np.array_equal(a["success"], b["success"])
    assert all(np.array_equal(snap[k], S[k]) for k in snap if isinstance(snap[k], np.ndarray))
    S2 = H.sample_inputs("mix", 20_000, 9)
    assert np.array_equal(S["z_break"], S2["z_break"]) and np.array_equal(S["a_wave"], S2["a_wave"])


def test_adaptive_reserve_rule_removes_reserve_violations():
    S = H.sample_inputs("mix", 50_000, 6, shift=dict(qspare_mult=0.1))
    plain = H.evaluate(H.Tool2(), S); adapt = H.evaluate(replace(H.Tool2(), reserve_rule="adaptive"), S)
    assert plain["reserve_viol"].mean() > 0.01 and adapt["reserve_viol"].sum() == 0
    assert not adapt["reserve_viol"][~adapt["shared"]].any()


def test_accumulator_never_increases_damage():
    S = H.sample_inputs("mix", 50_000, 8)
    d = [H.evaluate(replace(H.Tool2(), accumulator=a), S)["damage"].mean() for a in (0.0, 0.25, 0.5, 0.75)]
    assert all(b <= a + 1e-12 for a, b in zip(d, d[1:]))


def test_relief_off_cannot_lower_breakaway_and_raises_exceedance():
    S = H.sample_inputs("mix", 50_000, 8)
    on = H.evaluate(H.Tool2(), S); off = H.evaluate(replace(H.Tool2(), relief_enabled=False), S)
    assert off["break_ok"].mean() >= on["break_ok"].mean() and off["overtorque"].mean() > on["overtorque"].mean()


def test_lossless_benchmark_is_an_upper_bound_on_breakaway():
    S = H.sample_inputs("mix", 50_000, 8)
    ideal = H.evaluate(H.ideal_tool(H.Tool2()), S, H.Model2.legacy())
    base = H.evaluate(H.Tool2(), S)
    assert ideal["break_ok"].mean() >= base["break_ok"].mean()


def test_stress_shifts_move_outcomes_in_the_expected_direction():
    base = H.simulate("mix", H.Tool2(), 50_000, 2)["success"].mean()
    for sh in (dict(torque_mult=1.5), dict(ps_shift=-30.0), dict(seize_mult=2.0), dict(eff_shift=-0.1)):
        assert H.simulate("mix", H.Tool2(), 50_000, 2, shift=sh)["success"].mean() < base


def test_pareto_mask():
    F = np.array([[1, 5], [2, 4], [3, 3], [2, 6], [3, 4]], float)
    assert list(H.pareto_mask(F)) == [True, True, True, False, False]


def test_water_volume_is_flow_times_time():
    r = H.simulate("mix", H.Tool2(), 20_000, 3)
    ok = r["success"]
    assert np.allclose(r["volume_L"][ok], r["Q_run"][ok] * H.GPM_LPM * r["t_min"][ok])
