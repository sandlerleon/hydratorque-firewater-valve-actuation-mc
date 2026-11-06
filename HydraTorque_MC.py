#!/usr/bin/env python3
"""
HydraTorque_MC.py (version 2.0) -- probabilistic design and safety-constrained optimization of a firewater-powered portable valve operator.

One self-contained file (numpy + matplotlib; scipy is not needed).

Question answered
    A portable water-hydraulic tool (motor displacement D, gear ratio R, torque-limiting relief valve, flow limiter) is driven by pressurized firewater
    through a fire hose. For uncertain supply (source, pressure, flow capacity, hose, elevation, fouling), uncertain valve demand (breakaway,
    seizure, running torque, stem strength) and uncertain tool behaviour (efficiencies, leakage, relief overshoot, surge on stall), how often does it
    (i) stroke the valve in time, (ii) without exceeding the allowable stem torque, and (iii) without taking water that firefighting needs?
    Which designs give the best compromise, and does the answer survive wrong input distributions?

Model 2 (this file) extends the concept-stage model of version 1 (kept unchanged in legacy_v1/) by switchable mechanisms:
    flow_supply  source pressure falls with the flow drawn:  P_src(Q) = Ps - (Ps - 20 psi) (Q/Qa)^1.85           (hydrant-flow-test form)
    foul_flow    strainer/fitting loss scales with the square of the flow (version 1: constant)
    back         exhaust-hose back-pressure on the motor
    start_eff    breakaway/stall torque efficiency lower than the running one
    leak         motor leakage flow proportional to the pressure drop (version 1: a constant volumetric factor)
    surge        pressure spike on stall (Joukowsky, limited by hose compliance, closing time and relief response) added to the relief override
With every mechanism switched off (Model2.legacy()) the engine reproduces version 1 exactly (tests/test_hydratorque.py).

Every distribution is an ASSUMED PRIOR for a concept-stage study. Nothing here is measured data.

Usage
    python HydraTorque_MC.py --demo                          verification suite (about 1 minute)
    python HydraTorque_MC.py --reproduce --outdir results    every result and figure of the paper (about 20 minutes)
    python HydraTorque_MC.py --legacy --outdir legacy_out    the version 1 study (200,000 trials, seed 2026)
"""
import argparse
import json
import math
import os
import sqlite3
import time
from dataclasses import dataclass, replace

import numpy as np

VERSION = "2.3.0"
PSI = 6894.757            # Pa per psi
GPM_LPM = 3.78541         # L/min per gpm
GPM_M3S = 6.30902e-5      # m3/s per gpm
RHO = 1000.0              # water density, kg/m3
INCH = 0.0254
FT = 0.3048
T_MAX_MIN = 15.0          # assumed stroking-time requirement (operating time, excluding set-up)
INTERFERENCE_FRAC = 0.25  # version-1 interference metric: tool draw above 25% of a lognormal "source flow"
P_RESID = 20.0            # residual pressure at the flow-test capacity, psi (convention of hydrant flow tests)
N_FLOW = 1.85             # flow-test exponent
Q_FOUL_REF = 60.0         # gpm at which the strainer/fouling loss equals its sampled value
Q_MAX = 1500.0            # upper bracket of the circuit solution, gpm
RPM_CAP = 3000.0          # assumed limit on the motor speed at the flow limit, rpm (no published speed limit of water-hydraulic motors of this class was found; 1,500 rpm is also reported)


def motor_rpm(d):
    """motor speed at the flow limit of a design row (leakage neglected), rpm"""
    return d["q"] * GPM_LPM * 1000.0 / d["D"]

# ----------------------------------------------------------------------------- definitions
@dataclass(frozen=True)
class ValveClass:
    name: str
    median_Nm: float               # median breakaway torque
    sigma: float                   # lognormal sigma of breakaway torque
    turns: tuple                   # (lo, hi) handwheel turns to stroke
    p_seize: float                 # probability of a seized/stiff condition
    allow_mult: float = 3.0        # nominal allowable stem torque = allow_mult * median
    allow_sigma: float = 0.25      # lognormal sigma of the true allowable stem torque about its nominal value


PRESETS = {
    "gate_12in":      ValveClass("gate_12in",      400, 0.45, (14, 22), 0.05),
    "gate_24in":      ValveClass("gate_24in",     1200, 0.50, (30, 50), 0.08),
    "butterfly_36in": ValveClass("butterfly_36in", 1500, 0.45, (35, 70), 0.06),
    "plug_16in":      ValveClass("plug_16in",      800, 0.50, (8, 16),  0.07),
    "legacy_seized":  ValveClass("legacy_seized", 2000, 0.60, (25, 60), 0.25),
    "ypf_1500":       ValveClass("ypf_1500",      1500, 0.35, (20, 40), 0.10),   # the 1,500 N.m example of the Wazoku challenge (2 to 16 inch valves)
}
MIX_WEIGHTS = {"gate_12in": .30, "gate_24in": .25, "butterfly_36in": .15, "plug_16in": .10, "legacy_seized": .20}
SOURCES = [("firewater_ring", .50, 140., 20.), ("fire_truck", .30, 120., 25.), ("municipal_hydrant", .20, 60., 15.)]
SHARED = np.array([True, False, True])                              # a fire truck is a dedicated source; ring and hydrant are shared
QA_MED = np.array([2000., 500., 1000.]); QA_SIG = np.array([0.5, 0.4, 0.5])     # flow at the 20 psi residual, gpm (assumed)
QSPARE_MED = np.array([400., 1e9, 200.]); QSPARE_SIG = np.array([0.6, 0.0, 0.5])  # flow the shared source can give without cutting firefighting reserve, gpm (assumed)
HOSES = [(1.75, 15.5, .30), (2.5, 2.0, .50), (3.0, 0.8, .20)]       # (inch, IFSTA coefficient, weight)
# stem strength relative to the median breakaway torque when it differs between classes (a stem is sized by its own structural limit, not by the operating torque)
HET_ALLOW = {"gate_12in": 4.0, "gate_24in": 3.0, "butterfly_36in": 2.2, "plug_16in": 3.5, "legacy_seized": 2.0, "ypf_1500": 3.0}


@dataclass(frozen=True)
class Tool2:
    D_cc: float = 200.0            # motor displacement, cc/rev
    ratio: float = 250.0           # planetary reduction
    eta_m: tuple = (0.85, 0.03)    # motor mechanical efficiency while running (mean, sd)
    drop: tuple = (0.05, 0.20)     # reduction of the efficiency at breakaway and stall, uniform (lo, hi)
    eta_v: tuple = (0.92, 0.02)    # volumetric efficiency at 100 psi and 100 rpm motor speed
    eta_g: tuple = (0.70, 0.05)    # gearbox and interface efficiency
    q_limit_gpm: float = 60.0      # flow limiter of the Smart Power Coupling
    spc_k: float = 0.0044          # coupling loss coefficient, psi/gpm^2
    relief_enabled: bool = True
    relief_basis: str = "median"   # "median": set = mult x class median breakaway; "allowable": set = mult x nominal allowable stem torque
    relief_mult: float = 2.0
    relief_tol: float = 0.05       # relative sd of the relief set-point
    reserve_rule: str = "none"     # "adaptive": on a shared source the flow limit is lowered to the spare flow of the source
    accumulator: float = 0.0       # fraction of the stall surge absorbed by a hose-side accumulator
    creep_start_gpm: float = 0.0   # flow during the first turns of the stroke (0 = no creep): slow torque build-up against a stuck valve
    creep_end_gpm: float = 0.0     # flow during the last turns before the end of travel (0 = no creep): slow approach to the stop
    creep_turns_start: float = 1.0 # handwheel turns at the start flow
    creep_turns_end: float = 2.0   # handwheel turns at the end flow


@dataclass(frozen=True)
class Model2:
    flow_supply: bool = True
    foul_flow: bool = True
    back: bool = True
    start_eff: bool = True
    leak: bool = True
    surge: bool = True
    creep: bool = True

    @staticmethod
    def legacy():
        return Model2(False, False, False, False, False, False, False)

    def names(self):
        return [k for k in ("flow_supply", "foul_flow", "back", "start_eff", "leak", "surge") if getattr(self, k)]


def ideal_tool(t):
    """Lossless benchmark: same displacement and ratio, unit efficiencies (the model switches are set by ideal_model)."""
    return replace(t, eta_m=(1.0, 0.0), eta_v=(1.0, 0.0), eta_g=(1.0, 0.0), drop=(0.0, 0.0), spc_k=0.0, relief_tol=0.0)


def class_arrays(preset):
    names = list(MIX_WEIGHTS) if preset == "mix" else [preset]
    w = np.array([MIX_WEIGHTS[k] for k in names]) if preset == "mix" else np.array([1.0])
    return names, w / w.sum(), [PRESETS[k] for k in names]


# ----------------------------------------------------------------------------- sampling (common random numbers)
def sample_inputs(preset="mix", n=200_000, seed=1, nominal=False, shift=None, Ps_override=None, heterogeneous=False):
    """Draw every random input once; designs are then evaluated on the same draws (common random numbers).
    The first block of draws follows version 1 in order, so Model2.legacy() reproduces it exactly; the added mechanisms draw from a second stream.
    shift: dict of assumption shifts applied to the draws (torque_mult, sigma_add, ps_shift, seize_mult, eff_shift, foul_mult, allow_mult, qspare_mult, surge_mult)."""
    sh = dict(torque_mult=1.0, sigma_add=0.0, ps_shift=0.0, seize_mult=1.0, eff_shift=0.0, foul_mult=1.0, allow_mult=1.0, qspare_mult=1.0, surge_mult=1.0)
    sh.update(shift or {})
    rng = np.random.default_rng(seed)
    names, w, cls = class_arrays(preset)
    ci = rng.choice(len(cls), size=n, p=w)
    S = dict(n=n, preset=preset, ci=ci, shift=sh, nominal=nominal)
    S["med"] = np.array([c.median_Nm for c in cls])[ci]
    S["sig"] = np.array([c.sigma for c in cls])[ci]
    tlo = np.array([c.turns[0] for c in cls])[ci]; thi = np.array([c.turns[1] for c in cls])[ci]
    S["pse"] = np.array([c.p_seize for c in cls])[ci]
    S["am"] = np.array([HET_ALLOW[nm] if heterogeneous else c.allow_mult for nm, c in zip(names, cls)])[ci]; S["asg"] = np.array([c.allow_sigma for c in cls])[ci]
    S["heterogeneous"] = heterogeneous
    S["z_break"] = rng.standard_normal(n)
    S["u_seize"] = rng.random(n)
    S["seize_mult"] = rng.uniform(1.5, 3.0, n)
    S["f_run"] = rng.uniform(0.3, 0.6, n)
    S["turns"] = rng.uniform(tlo, thi)
    S["z_allow"] = rng.standard_normal(n)
    S["src"] = rng.choice(len(SOURCES), size=n, p=[s[1] for s in SOURCES])
    S["z_ps"] = rng.standard_normal(n)
    S["z_elev"] = rng.standard_normal(n)
    hi = rng.choice(len(HOSES), size=n, p=[h[2] for h in HOSES])
    S["hose_in"] = np.array([h[0] for h in HOSES])[hi]
    S["C"] = np.array([h[1] for h in HOSES])[hi]
    S["L"] = rng.uniform(50, 400, n)
    S["z_m"] = rng.standard_normal(n); S["z_v"] = rng.standard_normal(n); S["z_g"] = rng.standard_normal(n)
    S["z_rel"] = rng.standard_normal(n)
    S["z_foul"] = rng.standard_normal(n)
    S["u_foulsev"] = rng.random(n); S["foul_sev"] = rng.uniform(20, 60, n)
    S["z_qsrc"] = rng.standard_normal(n)
    # second stream: mechanisms added in model 2
    r2 = np.random.default_rng([seed, 7777])
    S["z_qa"] = r2.standard_normal(n); S["z_qspare"] = r2.standard_normal(n)
    S["Ld"] = r2.uniform(10, 100, n)
    S["u_drop"] = r2.random(n)
    S["a_wave"] = r2.uniform(150, 400, n)
    S["t_close"] = r2.uniform(0.05, 0.5, n)
    S["ramp"] = r2.uniform(0.05, 0.25, n)
    S["kappa"] = r2.uniform(0.0, 0.3, n)
    S["y_mult"] = r2.uniform(1.3, 2.0, n)
    if nominal:   # degenerate every input except the valve breakaway demand (closed-form cross-check)
        for k in ("z_m", "z_v", "z_g", "z_rel", "z_elev", "z_foul"):
            S[k] = np.zeros(n)
        S["u_seize"] = np.ones(n); S["f_run"] = np.full(n, 0.45); S["C"] = np.full(n, 2.0); S["L"] = np.full(n, 200.0)
        S["u_foulsev"] = np.ones(n)
    if Ps_override is not None:
        S["Ps_fixed"] = float(Ps_override)
    return S


# ----------------------------------------------------------------------------- engine
def _solve_flow(Ffun, n):
    """Largest flow (gpm) at which the decreasing function F(Q) is still non-negative (0 if F(0) <= 0); bisection."""
    lo = np.zeros(n); hi = np.full(n, Q_MAX)
    f0 = Ffun(lo)
    for _ in range(44):
        mid = 0.5 * (lo + hi)
        ok = Ffun(mid) >= 0
        lo = np.where(ok, mid, lo); hi = np.where(ok, hi, mid)
    return np.where(f0 > 0, lo, 0.0), f0


def evaluate(tool=Tool2(), S=None, model=Model2()):
    n = S["n"]; sh = S["shift"]
    D = tool.D_cc * 1e-6; R = tool.ratio
    med, sig = S["med"], S["sig"]
    T_break = med * sh["torque_mult"] * np.exp((sig + sh["sigma_add"]) * S["z_break"])
    seize = S["u_seize"] < np.minimum(S["pse"] * sh["seize_mult"], 1.0)
    T_break = np.where(seize, T_break * S["seize_mult"], T_break)
    f_run = S["f_run"]; turns = S["turns"]
    T_allow_nom = S["am"] * med * sh["allow_mult"]
    T_allow = T_allow_nom * np.exp(S["asg"] * S["z_allow"])
    src = S["src"]
    mu = np.array([s[2] for s in SOURCES])[src] + sh["ps_shift"]; sd = np.array([s[3] for s in SOURCES])[src]
    Ps = np.clip(mu + sd * S["z_ps"], 20, 250) if "Ps_fixed" not in S else np.full(n, S["Ps_fixed"])
    elev = 0.433 * 15.0 * S["z_elev"]
    eta_m = np.clip(tool.eta_m[0] + sh["eff_shift"] + tool.eta_m[1] * S["z_m"], .6, .95)
    eta_v = np.clip(tool.eta_v[0] + tool.eta_v[1] * S["z_v"], .7, .99)
    eta_g = np.clip(tool.eta_g[0] + sh["eff_shift"] + tool.eta_g[1] * S["z_g"], .5, .85)
    rel_f = 1 + tool.relief_tol * S["z_rel"]
    foul0 = (np.exp(math.log(2.0) + 0.8 * S["z_foul"]) + np.where(S["u_foulsev"] < 0.03, S["foul_sev"], 0.0)) * sh["foul_mult"]
    Qsrc = np.exp(math.log(300) + 0.5 * S["z_qsrc"])
    if S.get("nominal"):
        foul0 = np.zeros(n)

    drop = (tool.drop[0] + (tool.drop[1] - tool.drop[0]) * S["u_drop"]) if model.start_eff else np.zeros(n)
    kT_run = D / (2 * math.pi) * eta_m * R * eta_g                      # N.m per Pa across the motor, running
    kT_nom = D / (2 * math.pi) * tool.eta_m[0] * R * tool.eta_g[0]
    kT_st = D / (2 * math.pi) * np.maximum(eta_m - drop, 0.05) * R * eta_g   # breakaway and stall
    dP_static = (Ps - elev) * PSI
    if tool.relief_enabled:
        base = med if tool.relief_basis == "median" else S["am"] * med
        P_rel = (tool.relief_mult * base) / kT_nom * rel_f
        dP_cap = np.minimum(dP_static, P_rel)
    else:
        P_rel = np.full(n, np.inf); dP_cap = dP_static
    T_cap = kT_st * dP_cap
    break_ok = T_cap >= T_break
    press_limited = dP_static < T_break / kT_st
    relief_limited = (~break_ok) & (~press_limited)

    # running operating point
    T_run = f_run * T_break
    dP_req = T_run / kT_run / PSI                                         # psi
    coeff = S["C"] * S["L"] / 1e6 + tool.spc_k
    if model.back:
        coeff = coeff + 2.0 * S["Ld"] / 1e6
    if model.foul_flow:
        coeff = coeff + foul0 / Q_FOUL_REF ** 2
    Qa = QA_MED[src] * np.exp(QA_SIG[src] * S["z_qa"])
    Qspare = np.where(SHARED[src], sh["qspare_mult"] * QSPARE_MED[src] * np.exp(QSPARE_SIG[src] * S["z_qspare"]), np.inf)
    const_loss = 0.0 if model.foul_flow else foul0
    if model.flow_supply:
        def Ffun(Q):
            return Ps - (Ps - P_RESID) * (Q / Qa) ** N_FLOW - elev - dP_req - coeff * Q * Q - const_loss
        Q_c, f0 = _solve_flow(Ffun, n)
        head_ok = f0 > 0
    else:
        head = (Ps - elev) - dP_req - foul0
        Q_c = np.sqrt(np.clip(head, 0, None) / coeff); head_ok = head > 0
    Q_lim = np.minimum(tool.q_limit_gpm, Qspare) if tool.reserve_rule == "adaptive" else np.full(n, tool.q_limit_gpm)
    Q_run = np.minimum(Q_c, Q_lim)
    run_ok = head_ok & (T_run <= T_cap)
    leak_ref_cc = (1.0 / eta_v - 1.0) * tool.D_cc * 100.0                  # cc/min at 100 psi and 100 rpm motor speed

    def speed(Qg):
        """output speed (rpm) at a flow of Qg gpm, running pressure drop dP_req"""
        if model.leak:
            return np.maximum(Qg * GPM_LPM * 1000.0 - leak_ref_cc * dP_req / 100.0, 0.0) / tool.D_cc / R
        return Qg * GPM_LPM * 1000 * eta_v / tool.D_cc / R

    n_out = speed(Q_run)
    creep_on = model.creep and (tool.creep_start_gpm > 0 or tool.creep_end_gpm > 0)
    Ns = Ne = np.zeros(n)
    Q_s = Q_e = Q_run
    with np.errstate(divide="ignore", invalid="ignore"):
        if creep_on:
            if tool.creep_start_gpm > 0:
                Ns = np.minimum(tool.creep_turns_start, 0.25 * turns); Q_s = np.minimum(Q_run, tool.creep_start_gpm)
            if tool.creep_end_gpm > 0:
                Ne = np.minimum(tool.creep_turns_end, 0.25 * turns); Q_e = np.minimum(Q_run, tool.creep_end_gpm)
            n_s, n_e = speed(Q_s), speed(Q_e)
            ok_speed = (n_out > 0) & (n_s > 0) & (n_e > 0)
            t_min = np.where(ok_speed, (turns - Ns - Ne) / n_out + Ns / n_s + Ne / n_e, np.inf)
        else:
            t_min = np.where(n_out > 0, turns / n_out, np.inf)
    time_ok = t_min <= T_MAX_MIN
    success = break_ok & run_ok & time_ok

    # stall: end of travel or obstruction (relief override, surge)
    if model.surge:
        Q_stall = np.where(break_ok & run_ok, Q_e, Q_s)                    # flow just before the stall: end-of-travel creep for a stroke that proceeds, start creep for a valve that does not break free
        v = Q_stall * GPM_M3S / (math.pi / 4 * (S["hose_in"] * INCH) ** 2)  # m/s in the supply hose just before the stall
        L_m = S["L"] * FT
        red = np.minimum(1.0, (2 * L_m / S["a_wave"]) / S["t_close"])
        dJ = RHO * S["a_wave"] * v * red / PSI * (1.0 - tool.accumulator) * sh["surge_mult"]  # psi
        ramp, kappa = S["ramp"], S["kappa"]
    else:
        dJ = np.zeros(n); ramp = np.zeros(n); kappa = np.zeros(n)
    P_static_psi = Ps - elev
    if tool.relief_enabled:
        P_set_psi = P_rel / PSI
        Ppk = np.minimum(P_static_psi + dJ, P_set_psi * (1 + ramp) + kappa * dJ)    # relief override and un-relieved part of the surge
    else:
        Ppk = P_static_psi + dJ
    T_peak = kT_st * Ppk * PSI
    overtorque = T_peak > T_allow
    damage = T_peak > T_allow * S["y_mult"]
    peak_ratio = T_peak / T_allow

    P_in = dP_req * PSI * Q_run * GPM_M3S
    P_out = T_run * n_out * 2 * math.pi / 60
    with np.errstate(divide="ignore", invalid="ignore"):
        eb = np.where(P_in > 0, P_out / P_in, 0)
    P_tap = ((Ps - (Ps - P_RESID) * (Q_run / Qa) ** N_FLOW if model.flow_supply else Ps) - elev) * PSI * Q_run * GPM_M3S    # hydraulic power at the tap, elevation head included
    shared = SHARED[src]
    reserve_viol = shared & (Q_run > Qspare)
    if creep_on:
        with np.errstate(divide="ignore", invalid="ignore"):
            vol = np.where(np.isfinite(t_min), GPM_LPM * (Q_run * (turns - Ns - Ne) / n_out + np.where(Ns > 0, Q_s * Ns / n_s, 0.0) + np.where(Ne > 0, Q_e * Ne / n_e, 0.0)), np.nan)
    else:
        vol = np.where(np.isfinite(t_min), Q_run * GPM_LPM * np.where(np.isfinite(t_min), t_min, 0.0), np.nan)       # litres used in one stroke
    return dict(
        n=n, success=success, break_ok=break_ok, run_ok=run_ok, time_ok=time_ok, pressure_limited=press_limited & ~break_ok, relief_limited=relief_limited,
        overtorque=overtorque, damage=damage, success_safe=success & ~overtorque, success_nodamage=success & ~damage,
        success_reserve=success & ~overtorque & ~reserve_viol,
        interference=(Q_run / Qsrc) > INTERFERENCE_FRAC, reserve_viol=reserve_viol, shared=shared,
        T_break=T_break, T_cap=T_cap, T_peak=T_peak, T_allow=T_allow, peak_ratio=peak_ratio, T_run=T_run, t_min=t_min, Q_run=Q_run, Q_c=Q_c, n_out=n_out, dP_req=dP_req, surge_psi=dJ,
        volume_L=vol, energy_ratio=eb, P_in=P_in, P_out=P_out, P_tap=P_tap, margin=np.log(np.maximum(T_cap, 1e-9) / T_break),
        inputs=dict(Ps=Ps, elev=elev, T_break=T_break / med, seize=seize.astype(float), eta_g=eta_g, eta_m=eta_m, relief_f=rel_f, hose_len=S["L"], hose_C=S["C"],
                    foul=foul0, f_run=f_run, T_allow=T_allow / T_allow_nom, Qa=Qa, drop=drop, class_median=med, wave_speed=S["a_wave"], stop_time=S["t_close"],
                    surge_unrelieved=S["kappa"], relief_override=S["ramp"]))


def simulate(preset="mix", tool=Tool2(), n=200_000, seed=1, model=Model2(), shift=None, Ps_override=None, nominal=False):
    return evaluate(tool, sample_inputs(preset, n, seed, nominal=nominal, shift=shift, Ps_override=Ps_override), model)


# ----------------------------------------------------------------------------- analytics and statistics
def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def analytic_breakaway_mix(T_cap, preset="mix", shift_mult=1.0):
    """Closed form: P(T_break <= T_cap) for lognormal demand, a mixture of valve classes, without seizure."""
    names, w, cls = class_arrays(preset)
    return float(sum(wi * Phi((math.log(T_cap) - math.log(c.median_Nm * shift_mult)) / c.sigma) for wi, c in zip(w, cls)))


def nominal_capacity_Nm(tool, Ps_psi):
    kT = tool.D_cc * 1e-6 / (2 * math.pi) * tool.eta_m[0] * tool.ratio * tool.eta_g[0]
    return kT * Ps_psi * PSI


def analytic_exceedance(cap_over_median, preset="mix"):
    """Closed form: P(T_allow < T_cap) with a deterministic stall torque T_cap = cap_over_median x class median (relief-limited, no tolerance)."""
    names, w, cls = class_arrays(preset)
    return float(sum(wi * Phi((math.log(cap_over_median) - math.log(c.allow_mult)) / c.allow_sigma) for wi, c in zip(w, cls)))


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


KEYS = ("success", "success_safe", "success_reserve", "break_ok", "run_ok", "time_ok", "pressure_limited", "relief_limited", "overtorque", "damage",
        "interference", "reserve_viol")


def summarize(r):
    n = r["n"]; s = {}
    for k in KEYS:
        v = int(r[k].sum()); lo, hi = wilson(v, n)
        s[k] = dict(p=v / n, lo=lo, hi=hi)
    ok = r["success"]
    s["t_min_median"] = float(np.median(r["t_min"][ok])) if ok.any() else None
    s["t_min_p90"] = float(np.percentile(r["t_min"][ok], 90)) if ok.any() else None
    s["T_cap_median_Nm"] = float(np.median(r["T_cap"]))
    s["Q_run_median_gpm"] = float(np.median(r["Q_run"]))
    s["Q_run_p95_gpm"] = float(np.percentile(r["Q_run"], 95))
    s["volume_median_L"] = float(np.nanmedian(r["volume_L"][ok])) if ok.any() else None
    s["volume_p90_L"] = float(np.nanpercentile(r["volume_L"][ok], 90)) if ok.any() else None
    s["n_out_median_rpm"] = float(np.median(r["n_out"][ok])) if ok.any() else None
    s["surge_median_psi"] = float(np.median(r["surge_psi"]))
    s["energy_ratio_max"] = float(r["energy_ratio"].max())
    return s


def block_se(x, blocks=10):
    n = len(x) // blocks * blocks
    m = x[:n].reshape(blocks, -1).mean(axis=1)
    return float(m.std(ddof=1) / math.sqrt(blocks))


def rank(x):
    """average ranks (ties share the mean rank)"""
    x = np.asarray(x, float)
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    csum = np.cumsum(cnt)
    avg = csum - (cnt - 1) / 2.0
    return avg[inv]


def spearman(x, y):
    a, b = rank(x), rank(y); a -= a.mean(); b -= b.mean()
    return float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))


def prcc(X, y):
    """Partial rank correlation of each column of X with y."""
    Z = np.column_stack([rank(X[:, j]) for j in range(X.shape[1])]); yr = rank(y)
    out = []
    for j in range(Z.shape[1]):
        others = np.delete(Z, j, axis=1); A = np.column_stack([others, np.ones(len(yr))])
        rx = Z[:, j] - A @ np.linalg.lstsq(A, Z[:, j], rcond=None)[0]; ry = yr - A @ np.linalg.lstsq(A, yr, rcond=None)[0]
        out.append(float((rx * ry).sum() / math.sqrt((rx * rx).sum() * (ry * ry).sum())))
    return out


# ----------------------------------------------------------------------------- benchmarks (capability-limited conventional tools)
@dataclass(frozen=True)
class Conventional:
    name: str
    T_cap_Nm: float          # rated torque
    P_kW: float              # mechanical output power
    availability: float      # probability that the energy source is usable when the demand arises (assumed)
    n_max_rpm: float = 30.0


def conventional(preset, tool_bm, S, seed=11):
    """Success of a conventional portable operator on the same valve draws: breakaway <= rated torque, running torque sustained,
    speed limited by power and rated speed, energy source available."""
    r = evaluate(Tool2(), S, Model2())
    T_break, T_run, turns, T_allow = r["T_break"], r["T_run"], S["turns"], r["T_allow"]
    rng = np.random.default_rng([seed, 4242]); avail = rng.random(S["n"]) < tool_bm.availability
    n_out = np.minimum(tool_bm.P_kW * 1000 / np.maximum(T_run, 1) * 60 / (2 * math.pi), tool_bm.n_max_rpm)
    t_min = turns / n_out
    ok = (T_break <= tool_bm.T_cap_Nm) & (T_run <= tool_bm.T_cap_Nm) & (t_min <= T_MAX_MIN) & avail
    ot = tool_bm.T_cap_Nm > T_allow
    return dict(success=ok, success_safe=ok & ~ot, overtorque=ot, t_min=t_min)


# ----------------------------------------------------------------------------- studies
def study_presets(tool, n, seed, model=Model2()):
    return {name: summarize(simulate(name, tool, n, seed, model)) for name in list(PRESETS) + ["mix"]}


def study_ladder(tool, n, seed):
    """Switch the model-2 mechanisms on one at a time, in order, starting from the version-1 physics."""
    rows = []
    order = ["flow_supply", "foul_flow", "back", "start_eff", "leak", "surge"]
    S = sample_inputs("mix", n, seed)
    flags = {k: False for k in order}
    rows.append(dict(step="version 1 physics", **_ladder_row(evaluate(tool, S, Model2(**flags)))))
    for k in order:
        flags[k] = True
        rows.append(dict(step="+ " + k, **_ladder_row(evaluate(tool, S, Model2(**flags)))))
    return rows


def _ladder_row(r):
    return {k: float(r[k].mean()) for k in ("success", "success_safe", "overtorque", "damage", "break_ok", "time_ok", "interference")} | \
           {"median_Q_gpm": float(np.median(r["Q_run"]))}


def study_pressure(tool, n, seed, pressures=range(40, 205, 10)):
    """Cross-check of the simulation against the closed form: relief off, nominal inputs except valve demand, constant supply pressure."""
    mc, an = [], []
    for P in pressures:
        r = simulate("mix", replace(tool, relief_enabled=False), n, seed, Model2.legacy(), Ps_override=P, nominal=True)
        mc.append(float(r["break_ok"].mean()))
        t0 = replace(tool)
        an.append(analytic_breakaway_mix(nominal_capacity_Nm(t0, P)))
    return list(pressures), mc, an


def study_grid(tool, S, Ds=(100, 150, 200, 300, 400), Rs=(100, 150, 250, 350, 500)):
    G = np.zeros((len(Ds), len(Rs))); GS = np.zeros_like(G); OT = np.zeros_like(G)
    for i, D in enumerate(Ds):
        for j, Rr in enumerate(Rs):
            r = evaluate(replace(tool, D_cc=D, ratio=Rr), S)
            G[i, j] = r["success"].mean(); GS[i, j] = r["success_safe"].mean(); OT[i, j] = r["overtorque"].mean()
    return Ds, Rs, G, GS, OT


def study_relief(tool, S, mults_med=(0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0), mults_all=(0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0)):
    rows = {"median": [], "allowable": []}
    for basis, ms in (("median", mults_med), ("allowable", mults_all)):
        for m in ms:
            r = evaluate(replace(tool, relief_basis=basis, relief_mult=m), S)
            rows[basis].append(dict(mult=m, success=float(r["success"].mean()), safe=float(r["success_safe"].mean()), overtorque=float(r["overtorque"].mean()),
                                    damage=float(r["damage"].mean())))
    r0 = evaluate(replace(tool, relief_enabled=False), S)
    rows["no_relief"] = dict(success=float(r0["success"].mean()), safe=float(r0["success_safe"].mean()), overtorque=float(r0["overtorque"].mean()),
                             damage=float(r0["damage"].mean()))
    return rows


def study_qlimit(tool, S, limits=(15, 20, 30, 40, 60, 80, 100, 150)):
    rows = []
    for q in limits:
        t = replace(tool, q_limit_gpm=q)
        r = evaluate(t, S); ra = evaluate(replace(t, reserve_rule="adaptive"), S)
        rows.append(dict(q=q, success=float(r["success"].mean()), safe=float(r["success_safe"].mean()), interference_v1=float(r["interference"].mean()),
                         reserve_viol=float(r["reserve_viol"].mean()), time_ok=float(r["time_ok"].mean()),
                         success_adaptive=float(ra["success"].mean()), safe_adaptive=float(ra["success_safe"].mean()), reserve_viol_adaptive=float(ra["reserve_viol"].mean()),
                         volume_median_L=float(np.nanmedian(r["volume_L"][r["success"]])) if r["success"].any() else None))
    return rows


def study_kit(tool, n, seed, cfgs=((100, 500), (150, 350), (200, 250), (300, 150), (400, 100))):
    out = {}
    for name in PRESETS:
        S = sample_inputs(name, n, seed)
        rows = []
        for D, Rr in cfgs:
            r = evaluate(replace(tool, D_cc=D, ratio=Rr), S)
            rows.append(dict(D=D, R=Rr, safe=float(r["success_safe"].mean()), success=float(r["success"].mean())))
        out[name] = rows
    return out


def study_sensitivity(tool, S):
    """Partial rank correlation of every input with two continuous responses: the torque margin ln(T_cap/T_break) (success) and ln(T_peak/T_allow) (over-torque)."""
    r = evaluate(tool, S)
    ins = r["inputs"]; keys = list(ins)
    X = np.column_stack([ins[k] for k in keys])[:30000]
    return dict(prcc_margin={k: v for k, v in zip(keys, prcc(X, r["margin"][:30000]))},
                prcc_peak_ratio={k: v for k, v in zip(keys, prcc(X, np.log(r["peak_ratio"][:30000])))},
                spearman_margin={k: spearman(ins[k], r["margin"]) for k in keys})


def study_surge(tool, S_fn, mults=(0.0, 0.5, 1.0, 1.5, 2.0, 3.0)):
    """Over-torque probability against the surge multiplier (0 = no surge) for a given tool; S_fn(shift) returns the draws."""
    rows = []
    for m in mults:
        r = evaluate(tool, S_fn(dict(surge_mult=m)))
        rows.append(dict(mult=m, overtorque=float(r["overtorque"].mean()), damage=float(r["damage"].mean()), safe=float(r["success_safe"].mean())))
    return rows


# ----------------------------------------------------------------------------- optimization
def lhs(n, dims, rng):
    X = np.empty((n, dims))
    for j in range(dims):
        X[:, j] = (rng.permutation(n) + rng.random(n)) / n
    return X


def design_from_unit(u, basis, creep=False):
    D = float(math.exp(math.log(60) + u[0] * (math.log(500) - math.log(60))))
    R = float(math.exp(math.log(60) + u[1] * (math.log(600) - math.log(60))))
    if basis == "allowable":
        mult = 0.2 + u[2] * (1.0 - 0.2)
    else:
        mult = 0.6 + u[2] * (4.0 - 0.6)
    q = 15 + u[3] * (100 - 15)
    d = dict(D=D, R=R, mult=float(mult), q=float(q))
    if creep:
        d["cs"] = float(5 + u[4] * (60 - 5))        # creep flow at the start and at the end of travel, gpm (a value above the flow limit means no creep)
        d["ce"] = float(5 + u[5] * (60 - 5))
    return d


def tool_from(d, basis, acc=0.0, base=Tool2()):
    t = replace(base, D_cc=d["D"], ratio=d["R"], relief_basis=basis, relief_mult=d["mult"], q_limit_gpm=d["q"], reserve_rule="adaptive", accumulator=acc)
    if "cs" in d:
        t = replace(t, creep_start_gpm=d["cs"] if d["cs"] < d["q"] else 0.0, creep_end_gpm=d["ce"] if d["ce"] < d["q"] else 0.0)
    return t


def objectives(r):
    ok = r["success_safe"]
    vol = float(np.nanmedian(r["volume_L"][ok])) if ok.any() else 1e9
    return dict(safe=float(ok.mean()), success=float(r["success"].mean()), overtorque=float(r["overtorque"].mean()), damage=float(r["damage"].mean()),
                reserve=float(r["reserve_viol"].mean()), volume=vol, t_med=float(np.median(r["t_min"][r["success"]])) if r["success"].any() else None)


def pareto_mask(F):
    """Non-dominated rows of F (all objectives to be minimised)."""
    n = len(F); keep = np.ones(n, bool)
    for i in range(n):
        if not keep[i]:
            continue
        dom = np.all(F <= F[i], axis=1) & np.any(F < F[i], axis=1)
        if dom.any():
            keep[i] = False
    return keep


FAMILIES = (("allowable", 0.0, False), ("median", 0.0, False), ("allowable", 0.75, False), ("median", 0.75, False),
            ("allowable", 0.0, True), ("allowable", 0.75, True), ("median", 0.0, True), ("median", 0.75, True))


def study_optimize(S_opt, n_designs=1500, seed=5, ot_limit=0.01, families=FAMILIES, rpm_cap=RPM_CAP):
    """Latin-hypercube search of (D, R, relief multiple, flow limit) for each family (relief basis, accumulator fraction); Pareto set in
    (success without over-torque, over-torque probability, water per stroke); best design under P(over-torque) <= ot_limit and a motor speed at the flow limit of at most rpm_cap
    (best_feasible), and the best design without the speed limit (best_any)."""
    rng = np.random.default_rng(seed)
    out = {}
    for fam in families:
        basis, acc = fam[0], fam[1]
        creep = len(fam) > 2 and fam[2]
        U = lhs(n_designs, 6 if creep else 4, rng)
        rows = []
        for u in U:
            d = design_from_unit(u, basis, creep)
            rows.append(dict(d, **objectives(evaluate(tool_from(d, basis, acc), S_opt))))
        F = np.array([[-r["safe"], r["overtorque"], r["volume"]] for r in rows])
        pm = pareto_mask(F)
        feas_any = [r for r in rows if r["overtorque"] <= ot_limit]
        feas = [r for r in feas_any if motor_rpm(r) <= rpm_cap]
        best = max(feas, key=lambda r: r["safe"]) if feas else None
        best_any = max(feas_any, key=lambda r: r["safe"]) if feas_any else None
        out["%s|%g%s" % (basis, acc, "|creep" if creep else "")] = dict(basis=basis, acc=acc, creep=creep, designs=rows, pareto=[i for i in range(len(rows)) if pm[i]], best_feasible=best,
                                                                         best_any=best_any, n_feasible=len(feas_any), n_feasible_speed=len(feas), rpm_cap=rpm_cap)
    return out


SHIFTS = {"nominal priors": {}, "valve torque x1.5": dict(torque_mult=1.5), "valve scatter +0.15": dict(sigma_add=0.15), "supply -30 psi": dict(ps_shift=-30.0),
          "seizure x2": dict(seize_mult=2.0), "efficiencies -0.10": dict(eff_shift=-0.10), "fouling x3": dict(foul_mult=3.0), "stem strength x0.7": dict(allow_mult=0.7),
          "surge x2": dict(surge_mult=2.0),
          "combined stress": dict(torque_mult=1.3, sigma_add=0.1, ps_shift=-20.0, seize_mult=1.5, eff_shift=-0.05, foul_mult=2.0, allow_mult=0.85, surge_mult=1.5)}


def study_robust_select(family, n, seed, top=150, limits=(0.02, 0.03, 0.05, 0.10)):
    """Among the feasible designs of one family (nominal over-torque <= 2%), evaluate the worst case over the assumption shifts and, for each limit
    on the worst-case over-torque probability, choose the design that maximises the worst-case probability of a safe stroke."""
    basis, acc = family["basis"], family["acc"]
    feas = [r for r in family["designs"] if r["overtorque"] <= 0.02 and motor_rpm(r) <= RPM_CAP]
    feas = sorted(feas, key=lambda r: -r["safe"])
    cand = feas[:top // 2] + feas[top // 2:][::max(1, len(feas[top // 2:]) // (top // 2))][:top // 2]
    Ss = {k: sample_inputs("mix", n, seed, shift=sh) for k, sh in SHIFTS.items()}
    rows = []
    for d in cand:
        t = tool_from(d, basis, acc)
        obj = {k: objectives(evaluate(t, S)) for k, S in Ss.items()}
        rows.append(dict(d, wc_safe=min(o["safe"] for o in obj.values()), wc_ot=max(o["overtorque"] for o in obj.values())))
    picks = {}
    for lim in limits:
        ok = [r for r in rows if r["wc_ot"] <= lim]
        picks["%g" % lim] = max(ok, key=lambda r: r["wc_safe"]) if ok else None
    return dict(candidates=rows, picks=picks)


def study_hetero(n, seed, designs=1000):
    """Chart basis when the stem strength differs between valve classes: designs optimised on draws with HET_ALLOW, per-class over-torque of the best designs."""
    S = sample_inputs("mix", n, seed, heterogeneous=True)
    fam = study_optimize(S, designs, seed + 1, families=(("allowable", 0.75, False), ("median", 0.75, False), ("allowable", 0.75, True), ("median", 0.75, True)))
    out = {}
    for k, v in fam.items():
        bf = v["best_feasible"]
        row = dict(n_feasible=v["n_feasible"], best=bf, per_class=None)
        if bf:
            t = tool_from(bf, v["basis"], v["acc"]); pc_ = {}
            for name in list(MIX_WEIGHTS):
                r = evaluate(t, sample_inputs(name, 40_000, seed + 2, heterogeneous=True))
                pc_[name] = dict(overtorque=float(r["overtorque"].mean()), safe=float(r["success_safe"].mean()))
            row["per_class"] = pc_
        out[k] = row
    return out


def study_class_specific(n, seed, designs=500, acc=0.75, ot_limit=0.01):
    """Best design per valve class (allowable-stem-torque relief basis) under the same over-torque limit."""
    rng = np.random.default_rng(seed)
    out = {}
    for name in list(MIX_WEIGHTS):
        S = sample_inputs(name, n, seed + 1)
        rows = []
        for u in lhs(designs, 4, rng):
            d = design_from_unit(u, "allowable")
            rows.append(dict(d, **objectives(evaluate(tool_from(d, "allowable", acc), S))))
        feas = [r for r in rows if r["overtorque"] <= ot_limit and motor_rpm(r) <= RPM_CAP]
        out[name] = max(feas, key=lambda r: r["safe"]) if feas else None
    return out


def study_creep(tool, S):
    """Slow flow at the start and at the end of travel, baseline tool: effect on over-torque, damage, safe stroke, stroke time and water."""
    rows = []
    cases = [(0, 0, 1, 2), (0, 40, 1, 2), (0, 20, 1, 2), (0, 10, 1, 2), (20, 0, 1, 2), (10, 0, 1, 2), (20, 20, 1, 2), (10, 10, 1, 2), (10, 10, 0.5, 1), (10, 10, 2, 4), (10, 10, 4, 8)]
    for acc in (0.0, 0.75):
        for cs, ce, ns, ne in cases:
            t = replace(tool, accumulator=acc, creep_start_gpm=float(cs), creep_end_gpm=float(ce), creep_turns_start=ns, creep_turns_end=ne)
            r = evaluate(t, S); ok = r["success"]
            rows.append(dict(acc=acc, cs=cs, ce=ce, ns=ns, ne=ne, success=float(ok.mean()), safe=float(r["success_safe"].mean()), overtorque=float(r["overtorque"].mean()),
                             damage=float(r["damage"].mean()), time_ok=float(r["time_ok"].mean()), t_med=float(np.median(r["t_min"][ok])) if ok.any() else None,
                             volume=float(np.nanmedian(r["volume_L"][ok])) if ok.any() else None))
    return rows


def study_reserve(tool, n, seed, mults=(0.1, 0.25, 0.5, 1.0, 2.0)):
    rows = []
    for m in mults:
        S = sample_inputs("mix", n, seed, shift=dict(qspare_mult=m))
        r = evaluate(tool, S); ra = evaluate(replace(tool, reserve_rule="adaptive"), S)
        rows.append(dict(mult=m, reserve_viol=float(r["reserve_viol"].mean()), safe=float(r["success_safe"].mean()), safe_adaptive=float(ra["success_safe"].mean()),
                         time_ok_adaptive=float(ra["time_ok"].mean())))
    return rows


# ----------------------------------------------------------------------------- verification
def selftest(tool=Tool2(), n=100_000, seed=7):
    out = {}
    pr, mc, an = study_pressure(tool, n, seed)
    out["closed_form_max_dev"] = max(abs(a - b) for a, b in zip(mc, an))
    r = simulate("mix", tool, n, seed)
    out["energy_ratio_max"] = float(r["energy_ratio"].max())
    out["tap_power_ge_motor_power"] = bool(np.all(r["P_tap"] + 1e-9 >= r["P_in"]))
    out["baseline_torque_Nm"] = nominal_capacity_Nm(tool, 100)
    assert out["closed_form_max_dev"] < 0.01, out
    assert out["energy_ratio_max"] < 1.0 and out["tap_power_ge_motor_power"]
    assert abs(out["baseline_torque_Nm"] - 3265) / 3265 < 0.03
    return out


def reproduce_paper(outdir="results", n=200_000, n_sweep=60_000, n_opt=15_000, designs=1500, seed=2026, tool=Tool2()):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    res = dict(meta=dict(version=VERSION, rpm_cap=RPM_CAP, n=n, n_sweep=n_sweep, n_opt=n_opt, designs=designs, seed=seed, tool=tool.__dict__, t_max_min=T_MAX_MIN))
    res["selftest"] = selftest(tool)
    print("selftest ok", round(time.time() - t0))
    S = sample_inputs("mix", n, seed)
    Ssw = sample_inputs("mix", n_sweep, seed + 1)
    base = evaluate(tool, S)
    res["presets"] = study_presets(tool, n, seed)
    res["presets_v1"] = study_presets(tool, n, seed, Model2.legacy())
    res["baseline"] = summarize(base)
    res["baseline_se"] = {k: block_se(base[k].astype(float)) for k in ("success", "success_safe", "overtorque", "damage")}
    res["ladder"] = study_ladder(tool, n_sweep, seed)
    pr, mc, an = study_pressure(tool, n_sweep, seed)
    res["pressure"] = dict(psi=pr, mc=mc, analytic=an)
    full = [float(evaluate(tool, sample_inputs("mix", n_sweep, seed, Ps_override=P))["success"].mean()) for P in pr]
    res["pressure"]["full"] = full
    Ds, Rs, G, GS, OT = study_grid(tool, Ssw)
    res["grid"] = dict(D=list(Ds), R=list(Rs), success=G.tolist(), safe=GS.tolist(), overtorque=OT.tolist())
    res["relief"] = study_relief(tool, Ssw)
    res["qlimit"] = study_qlimit(tool, Ssw)
    res["kit"] = study_kit(tool, n_sweep, seed)
    res["sensitivity"] = study_sensitivity(tool, Ssw)
    print("sweeps ok", round(time.time() - t0))
    # transients
    acc = {}
    for a in (0.0, 0.25, 0.5, 0.75):
        r = evaluate(replace(tool, accumulator=a), Ssw)
        acc[str(a)] = dict(overtorque=float(r["overtorque"].mean()), damage=float(r["damage"].mean()), safe=float(r["success_safe"].mean()))
    res["accumulator"] = acc
    res["surge"] = dict(median_psi=float(np.median(base["surge_psi"])), p95_psi=float(np.percentile(base["surge_psi"], 95)), share_of_static=float(np.median(base["surge_psi"] / base["inputs"]["Ps"])))
    # optimization
    So = sample_inputs("mix", n_opt, seed + 2)
    opt = study_optimize(So, designs, seed + 3)
    res["optimization"] = {k: dict(basis=v["basis"], acc=v["acc"], creep=v["creep"], n_feasible=v["n_feasible"], n_feasible_speed=v["n_feasible_speed"], pareto=v["pareto"], best_feasible=v["best_feasible"],
                                   best_any=v["best_any"], designs=v["designs"])
                           for k, v in opt.items()}
    print("optimization ok", round(time.time() - t0))
    res["class_specific"] = study_class_specific(n_opt, seed + 5)
    res["reserve"] = study_reserve(tool, n_sweep, seed)
    res["creep"] = study_creep(tool, Ssw)
    rob = {k: study_robust_select(v, n_opt // 2, seed + 6) for k, v in opt.items() if k.startswith("allowable")}
    res["robust_select"] = {k: dict(picks=v["picks"], n_candidates=len(v["candidates"]), candidates=v["candidates"]) for k, v in rob.items()}
    res["hetero"] = study_hetero(n_opt, seed + 7)
    print("hetero ok", round(time.time() - t0))
    surge_rows = {}
    for dname, t in (("baseline", tool), ("baseline + accumulator 0.75", replace(tool, accumulator=0.75))):
        surge_rows[dname] = study_surge(t, lambda sh: sample_inputs("mix", n_sweep, seed + 8, shift=sh))
    bfa = opt["allowable|0.75"]["best_feasible"]
    if bfa:
        surge_rows["optimized allowable|0.75"] = study_surge(tool_from(bfa, "allowable", 0.75), lambda sh: sample_inputs("mix", n_sweep, seed + 8, shift=sh))
    res["surge_study"] = surge_rows
    print("robust selection ok", round(time.time() - t0))
    # out-of-sample re-evaluation and robustness
    Soos = sample_inputs("mix", n, seed + 4)
    designs_eval = {"baseline (chart 2x median, no accumulator)": tool}
    for k, v in opt.items():
        bf = v["best_feasible"]
        if bf:
            designs_eval["optimized %s" % k] = tool_from(bf, v["basis"], v["acc"])
    for k, v in rob.items():
        for lim, pk in v["picks"].items():
            if pk and lim in ("0.03", "0.1"):
                designs_eval["robust %s (worst-case limit %s)" % (k, lim)] = tool_from(pk, opt[k]["basis"], opt[k]["acc"])
    designs_eval["baseline + accumulator 0.75"] = replace(tool, accumulator=0.75)
    for k, v in opt.items():
        ba = v["best_any"]
        if ba and v["best_feasible"] and ba is not v["best_feasible"] and motor_rpm(ba) > RPM_CAP:
            designs_eval["unrestricted %s" % k] = tool_from(ba, v["basis"], v["acc"])
    robust = {}
    for dname, t in designs_eval.items():
        rr = {}
        for sname, sh in SHIFTS.items():
            r = evaluate(t, sample_inputs("mix", n_sweep * 2, seed + 4, shift=sh))
            rr[sname] = objectives(r) | dict(interference_v1=float(r["interference"].mean()))
        robust[dname] = dict(tool=dict(D=t.D_cc, R=t.ratio, mult=t.relief_mult, q=t.q_limit_gpm, basis=t.relief_basis, rule=t.reserve_rule, acc=t.accumulator),
                             scenarios=rr, out_of_sample=objectives(evaluate(t, Soos)))
    res["robust"] = robust
    # benchmarks
    ideal = evaluate(ideal_tool(tool), Ssw, Model2(False, False, False, False, False, False))
    res["benchmarks"] = dict(ideal_waterhydraulic=dict(success=float(ideal["success"].mean()), safe=float(ideal["success_safe"].mean())),
                             hydratorque=dict(success=float(evaluate(tool, Ssw)["success"].mean()), safe=float(evaluate(tool, Ssw)["success_safe"].mean())))
    for bm in (Conventional("battery-electric operator, 1,000 N.m, 1.5 kW", 1000, 1.5, 0.90), Conventional("pneumatic operator, 1,500 N.m, 3 kW (plant air)", 1500, 3.0, 0.50),
               Conventional("engine-driven oil-hydraulic pack, 3,000 N.m, 5 kW", 3000, 5.0, 0.95, 10.0)):
        c = conventional("mix", bm, Ssw)
        res["benchmarks"][bm.name] = dict(success=float(c["success"].mean()), safe=float(c["success_safe"].mean()), overtorque=float(c["overtorque"].mean()))
    # challenge example valve
    res["ypf"] = {k: summarize(evaluate(t, sample_inputs("ypf_1500", n_sweep, seed))) for k, t in designs_eval.items()}
    # convergence
    cs = np.cumsum(base["success_safe"]) / np.arange(1, n + 1)
    idx = np.unique(np.logspace(2, math.log10(n), 60).astype(int)) - 1
    res["convergence"] = dict(n=[int(i + 1) for i in idx], running=[float(cs[i]) for i in idx])
    res["meta"]["runtime_s"] = round(time.time() - t0, 1)
    with open(os.path.join(outdir, "results.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    db = sqlite3.connect(os.path.join(outdir, "mc_log.sqlite"))
    db.execute("CREATE TABLE IF NOT EXISTS runs(ts TEXT, preset TEXT, n INT, seed INT, tool TEXT, summary TEXT)")
    for k, v in res["presets"].items():
        db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?)", (time.strftime("%F %T"), k, n, seed, json.dumps(tool.__dict__), json.dumps(v, default=float)))
    db.commit(); db.close()
    return res, dict(S=S, base=base, opt=opt)


# ----------------------------------------------------------------------------- transient check of the surge model (method of characteristics)
def moc_peak(L, a, d_in, Q0_gpm, p_run_psi, p_up_psi, tc, p_set_psi=None, eps=0.15, t_r=0.05, N=40):
    """One-dimensional water-hammer simulation of the supply hose by the method of characteristics (frictionless; constant-pressure source behind a linear
    resistance, the flow limiter; motor end stopped linearly in time tc; relief valve at the motor end that opens linearly over t_r once p >= p_set and passes
    the running flow at p_set (1 + eps)). Returns the peak pressure at the motor end, psi. It checks the surge relations of the screening model against
    classical results and against the transient behaviour of the model's own assumptions; it is not an experimental validation."""
    A = math.pi / 4 * (d_in * INCH) ** 2
    Z = RHO * a / A
    Q0 = Q0_gpm * GPM_M3S
    p0 = p_run_psi * PSI; pup = p_up_psi * PSI
    Rs = max((pup - p0) / Q0, 0.0)
    dt = L / (a * N)
    nsteps = int(6 * L / a / dt) + int(tc / dt) + 5
    p = np.full(N + 1, p0); q = np.full(N + 1, Q0)
    s_open = 0.0
    use_relief = p_set_psi is not None
    if use_relief:
        pset = p_set_psi * PSI
        Kr = Q0 / math.sqrt(pset * (1 + eps))
    peak = p0
    for k in range(1, nsteps + 1):
        t = k * dt
        pn = p.copy(); qn = q.copy()
        pn[1:N] = 0.5 * ((p[0:N - 1] + p[2:N + 1]) + Z * (q[0:N - 1] - q[2:N + 1]))
        qn[1:N] = 0.5 * ((q[0:N - 1] + q[2:N + 1]) + (p[0:N - 1] - p[2:N + 1]) / Z)
        q0 = (pup - p[1] + Z * q[1]) / (Z + Rs)
        qn[0] = q0; pn[0] = pup - Rs * q0
        qm = Q0 * max(0.0, 1.0 - t / tc)
        B = p[N - 1] + Z * q[N - 1]
        if use_relief and p[N] >= pset:
            s_open = min(1.0, s_open + dt / t_r)
        if use_relief and s_open > 0:
            c = Z * Kr * s_open
            y = (-c + math.sqrt(c * c - 4 * (Z * qm - B))) / 2
            pN = y * y
        else:
            pN = B - Z * qm
        pn[N] = pN; qn[N] = qm + (Kr * s_open * math.sqrt(max(pN, 0)) if use_relief else 0.0)
        p, q = pn, qn
        peak = max(peak, p[N])
    return peak / PSI


def joukowsky_rise_psi(L, a, d_in, Q0_gpm, tc):
    """surge of the screening model: rho a v min(1, 2L/(a tc)), psi"""
    v = Q0_gpm * GPM_M3S / (math.pi / 4 * (d_in * INCH) ** 2)
    return RHO * a * v * min(1.0, 2 * L / (a * tc)) / PSI


def study_moc(n_cases=300, seed=3):
    """(i) the solver against the classical Joukowsky and Michaud results; (ii) the peak pressure of the screening model (static supply plus surge, limited by the relief
    override and the unrelieved fraction kappa) against the transient simulation for random hoses, flows, relief settings and valve response times; (iii) the unrelieved
    fraction kappa implied by the simulation against the prior of the model (uniform 0 to 0.3) and its dependence on the relief response time."""
    out = {}
    d_in, Q0 = 2.5, 60.0
    cls = []
    for a_ in (150, 250, 400):
        cls.append(dict(kind="instantaneous", a=a_, tc=1e-4, L=60.0, classical=joukowsky_rise_psi(60.0, a_, d_in, Q0, 1e-4), moc=moc_peak(60.0, a_, d_in, Q0, 50.0, 50.0, 1e-4) - 50.0))
    for tc in (0.8, 1.2, 2.0, 4.0):
        v = Q0 * GPM_M3S / (math.pi / 4 * (d_in * INCH) ** 2)
        cls.append(dict(kind="slow (Michaud)", a=300.0, tc=tc, L=60.0, classical=2 * RHO * 60.0 * v / tc / PSI, moc=moc_peak(60.0, 300.0, d_in, Q0, 50.0, 50.0, tc) - 50.0))
    for tc in (0.05, 0.2):
        cls.append(dict(kind="short (reduction factor)", a=300.0, tc=tc, L=60.0, classical=joukowsky_rise_psi(60.0, 300.0, d_in, Q0, tc), moc=moc_peak(60.0, 300.0, d_in, Q0, 50.0, 50.0, tc) - 50.0))
    out["classical"] = cls
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_cases):
        L = rng.uniform(15, 120); a_ = rng.uniform(150, 400); tc = rng.uniform(0.05, 0.5); tr = rng.uniform(0.01, 0.1); eps = rng.uniform(0.05, 0.25)
        din = float(rng.choice([1.75, 2.5, 3.0])); q0 = rng.uniform(15, 100); p_run = rng.uniform(10, 80); p_set = p_run * rng.uniform(1.2, 4.0); p_up = p_set * rng.uniform(1.1, 3.0)
        dJ = joukowsky_rise_psi(L, a_, din, q0, tc)
        pk = moc_peak(L, a_, din, q0, p_run, p_up, tc, p_set, eps, tr)
        kap = rng.uniform(0, 0.3)
        model = min(p_up + dJ, p_set * (1 + eps) + kap * dJ)
        rows.append(dict(moc=pk, model=model, kappa_eff=(pk - p_set * (1 + eps)) / dJ, dJ=dJ, override=p_set * (1 + eps), t_r=tr))
    K = np.array([r["kappa_eff"] for r in rows])
    out["compare"] = dict(n=n_cases, model_ge_moc=float(np.mean([r["model"] >= r["moc"] for r in rows])), median_ratio=float(np.median([r["model"] / r["moc"] for r in rows])),
                          kappa_q=[float(x) for x in np.percentile(K, [5, 50, 95, 99])], share_kappa_above_prior=float((K > 0.3).mean()), points=[(r["moc"], r["model"]) for r in rows[:150]])
    sweep = []
    for tr in (0.01, 0.03, 0.1, 0.3, 1.0):
        ks = []
        for i in range(120):
            L = rng.uniform(15, 120); a_ = rng.uniform(150, 400); tc = rng.uniform(0.05, 0.5); eps = rng.uniform(0.05, 0.25)
            din = float(rng.choice([1.75, 2.5, 3.0])); q0 = rng.uniform(15, 100); p_run = rng.uniform(10, 80); p_set = p_run * rng.uniform(1.2, 4.0); p_up = p_set * rng.uniform(1.1, 3.0)
            dJ = joukowsky_rise_psi(L, a_, din, q0, tc)
            ks.append((moc_peak(L, a_, din, q0, p_run, p_up, tc, p_set, eps, tr) - p_set * (1 + eps)) / dJ)
        ks = np.array(ks)
        sweep.append(dict(t_r=tr, median=float(np.median(ks)), p95=float(np.percentile(ks, 95)), share_above_prior=float((ks > 0.3).mean())))
    out["relief_response"] = sweep
    return out


# ----------------------------------------------------------------------------- stem strength, confidence limits and preliminary mechanical loads
def _tool_of(row, basis, acc):
    return tool_from(row, basis, acc)


def study_stem(res, n=60_000, seed=21):
    """Over-torque probability against the true stem strength (relative to the data sheet) for four tools, and the relief derating that keeps P(over-torque) <= 1% when the
    stem may be weaker by a given factor, with the safe-stroke probability that remains."""
    opt = res["optimization"]
    tools = {"baseline": Tool2(), "baseline + accumulator 0.75": replace(Tool2(), accumulator=0.75)}
    for k in ("allowable|0.75", "allowable|0.75|creep"):
        bf = opt[k]["best_feasible"]
        tools["optimized " + k] = tool_from(bf, "allowable", 0.75)
    factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5]
    curves = {}
    for name, t in tools.items():
        row = []
        for f in factors:
            r = evaluate(t, sample_inputs("mix", n, seed, shift=dict(allow_mult=f)))
            row.append(dict(f=f, overtorque=float(r["overtorque"].mean()), safe=float(r["success_safe"].mean())))
        curves[name] = row
    base_t = tools["optimized allowable|0.75|creep"]
    der = []
    for f in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
        S = sample_inputs("mix", n, seed, shift=dict(allow_mult=f))
        lo, hi = 0.05, 1.5
        for _ in range(14):
            mid = 0.5 * (lo + hi)
            ot = evaluate(replace(base_t, relief_mult=base_t.relief_mult * mid), S)["overtorque"].mean()
            lo, hi = (mid, hi) if ot <= 0.01 else (lo, mid)
        r = evaluate(replace(base_t, relief_mult=base_t.relief_mult * lo), S)
        der.append(dict(f=f, scale=lo, mult=base_t.relief_mult * lo, safe=float(r["success_safe"].mean()), overtorque=float(r["overtorque"].mean())))
    return dict(curves=curves, derating=der, tool=dict(D=base_t.D_cc, R=base_t.ratio, mult=base_t.relief_mult, q=base_t.q_limit_gpm))


def study_ci(res, n_opt=None):
    """Wilson 95% limits of the over-torque probability of every chosen design on the independent draws, and the best design chosen so that the
    upper limit of the in-sample estimate is at most 1% (a strict compliance rule)."""
    n_opt = n_opt or res["meta"]["n_opt"]; n_oos = res["meta"]["n"]
    out = dict(designs={}, strict={})
    for name, v in res["robust"].items():
        p_ = v["out_of_sample"]["overtorque"]; k = int(round(p_ * n_oos)); lo, hi = wilson(k, n_oos)
        out["designs"][name] = dict(p=p_, lo=lo, hi=hi, n=n_oos)
    for fam, v in res["optimization"].items():
        feas = [r for r in v["designs"] if wilson(int(round(r["overtorque"] * n_opt)), n_opt)[1] <= 0.01 and motor_rpm(r) <= RPM_CAP]
        if not feas:
            out["strict"][fam] = None
            continue
        best = max(feas, key=lambda r: r["safe"])
        t = tool_from(best, v["basis"], v["acc"])
        r = evaluate(t, sample_inputs("mix", n_oos, res["meta"]["seed"] + 4))
        k = int(r["overtorque"].sum()); lo, hi = wilson(k, n_oos)
        out["strict"][fam] = dict(design=best, n_feasible=len(feas), safe=float(r["success_safe"].mean()), overtorque=float(r["overtorque"].mean()), lo=lo, hi=hi,
                                  in_sample_safe=best["safe"], in_sample_ot=best["overtorque"])
    return out


def study_mech(res, n=100_000, seed=33, arm_m=0.6, sf=2.0, sigma_y_mpa=355.0):
    """Preliminary mechanical loads of the baseline tool and two optimized tools: peak stall torque, gearbox rating, reaction force and arm section modulus,
    motor speed and power, hose velocity and the gas volume of an accumulator that absorbs the surge energy. Screening estimates for the draws of the model,
    not a design."""
    opt = res["optimization"]
    tools = {"baseline": Tool2()}
    for k in ("allowable|0", "allowable|0.75|creep"):
        tools["optimized " + k] = tool_from(opt[k]["best_feasible"], "allowable", 0.75 if "0.75" in k else 0.0)
    ba = opt["allowable|0.75|creep"].get("best_any")
    if ba and motor_rpm(ba) > RPM_CAP:
        tools["unrestricted allowable|0.75|creep"] = tool_from(ba, "allowable", 0.75)
    out = {}
    S = sample_inputs("mix", n, seed)
    for name, t in tools.items():
        r = evaluate(t, S)
        Tp = r["T_peak"]
        Tq = lambda q_: float(np.percentile(Tp, q_))
        v = r["Q_run"] * GPM_M3S / (math.pi / 4 * (S["hose_in"] * INCH) ** 2)
        chi = t.accumulator if t.accumulator > 0 else 0.75
        E = 0.5 * RHO * (math.pi / 4 * (S["hose_in"] * INCH) ** 2) * (S["L"] * FT) * v ** 2          # kinetic energy of the water column in the hose, J
        p2 = np.maximum(r["inputs"]["Ps"] * 0 + (t.relief_mult * (S["am"] * S["med"] if t.relief_basis == "allowable" else S["med"]) / (t.D_cc * 1e-6 / (2 * math.pi) * t.eta_m[0] * t.ratio * t.eta_g[0])) * 1.15, 1.0)
        p1 = np.maximum(0.9 * r["dP_req"] * PSI, 0.2e5)
        ok = p2 > 1.05 * p1
        Vg = np.where(ok, chi * E / (p1 * np.log(np.where(ok, p2 / p1, 2.0))), np.nan) * 1e3             # litres of gas at precharge (isothermal)
        n_motor = r["Q_run"] * GPM_LPM * 1000.0 / t.D_cc                                              # motor rpm at the running flow
        P_motor = r["dP_req"] * PSI * r["Q_run"] * GPM_M3S / 1e3                                      # hydraulic power at the motor, kW
        out[name] = dict(has_accumulator=bool(t.accumulator > 0), tool=dict(D=t.D_cc, R=t.ratio, mult=t.relief_mult, q=t.q_limit_gpm, acc=t.accumulator, cs=t.creep_start_gpm, ce=t.creep_end_gpm),
                         T_peak_p50=Tq(50), T_peak_p99=Tq(99), T_peak_p999=Tq(99.9), gearbox_rating_Nm=1.5 * Tq(99.9),
                         reaction_kN_p99=Tq(99) / arm_m / 1e3, arm_Z_cm3_p99=Tq(99) * sf / (sigma_y_mpa * 1e6) * 1e6, arm_m=arm_m, sf=sf, sigma_y_mpa=sigma_y_mpa,
                         motor_rpm_p50=float(np.median(n_motor)), motor_rpm_p95=float(np.percentile(n_motor, 95)), motor_kW_p50=float(np.median(P_motor)), motor_kW_p95=float(np.percentile(P_motor, 95)),
                         hose_v_p50=float(np.median(v)), hose_v_p95=float(np.percentile(v, 95)), hose_E_p95=float(np.percentile(E, 95)),
                         accumulator_gas_L_p50=float(np.nanmedian(Vg)), accumulator_gas_L_p95=float(np.nanpercentile(Vg, 95)), accumulator_gas_L_p99=float(np.nanpercentile(Vg, 99)))
    return out


def run_extras(outdir="results"):
    """Adds the transient check, the stem-strength study, the confidence limits and the mechanical loads to results.json without repeating the main study."""
    path = os.path.join(outdir, "results.json")
    res = json.load(open(path))
    t0 = time.time()
    res["moc"] = study_moc(); print("moc ok", round(time.time() - t0))
    res["stem"] = study_stem(res); print("stem ok", round(time.time() - t0))
    res["ci"] = study_ci(res); print("ci ok", round(time.time() - t0))
    res["mech"] = study_mech(res); print("mech ok", round(time.time() - t0))
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true"); ap.add_argument("--reproduce", action="store_true"); ap.add_argument("--legacy", action="store_true")
    ap.add_argument("--extras", action="store_true", help="transient check, stem-strength study, confidence limits and mechanical loads (adds to results.json)")
    ap.add_argument("--n", type=int, default=200_000); ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()
    if a.demo:
        print(json.dumps(selftest(), indent=1, default=float))
        print(json.dumps(summarize(simulate("mix", Tool2(), 100_000, 1)), indent=1, default=float)); return
    if a.legacy:
        import importlib.util
        here = os.path.dirname(os.path.abspath(__file__))
        spec = importlib.util.spec_from_file_location("v1", os.path.join(here, "legacy_v1", "HydraTorque_MC_v1.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.reproduce_paper(a.outdir, n=a.n, seed=a.seed); print("done ->", a.outdir); return
    if a.reproduce:
        reproduce_paper(a.outdir, n=a.n, seed=a.seed); run_extras(a.outdir); print("done ->", a.outdir); return
    if a.extras:
        run_extras(a.outdir); print("done ->", a.outdir); return
    ap.print_help()


if __name__ == "__main__":
    main()
