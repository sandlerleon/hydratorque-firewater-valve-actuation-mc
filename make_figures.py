# -*- coding: utf-8 -*-
"""Draws the figures of the paper from results/results.json (and, for the distribution plots, from the same seeded draws).
    python make_figures.py [results_dir] [figures_dir]"""
import json
import math
import os
import sys
from dataclasses import replace

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import HydraTorque_MC as H

RES = sys.argv[1] if len(sys.argv) > 1 else "results"
OUT = sys.argv[2] if len(sys.argv) > 2 else "figures"
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(RES, "results.json")))
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100})
BL, OR, GR, RD, PU, GY = "#1f5f99", "#d9822b", "#4f8f3a", "#b03a2e", "#7a5aa6", "#777777"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=200)
    plt.close(fig)


def pct(x):
    return 100.0 * np.asarray(x)


# ---- Fig 1 architecture
def fig_arch():
    fig, ax = plt.subplots(figsize=(7.6, 3.3)); ax.set_xlim(0, 100); ax.set_ylim(0, 44); ax.axis("off")
    def box(x, y, w, h, t, c="#e8eef5", fs=8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=c, ec="#33475b", lw=1.0))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)
    def arr(x1, y1, x2, y2, t=None, c="#33475b", dy=2.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, lw=1.1, color=c))
        if t:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, t, ha="center", fontsize=7, color=c)
    box(1, 24, 13, 12, "Firewater\nsource\n(ring, truck,\nhydrant)", "#dbe9f6")
    box(18, 24, 9, 12, "Fire\nhose", "#dbe9f6")
    box(31, 15, 29, 27, "", "#f6f1e3")
    ax.text(45.5, 39.0, "Smart Power Coupling", ha="center", fontsize=8, fontweight="bold")
    box(33, 28.5, 12, 7, "strainer +\nflow limiter", "#fff", 7); box(47.5, 28.5, 10.5, 7, "slow-open\nshut-off", "#fff", 7)
    box(33, 17.5, 12, 7, "inlet relief\n(torque limit)", "#fbe3df", 7); box(47.5, 17.5, 10.5, 7, "accumulator\n(optional)", "#e3f1e0", 7)
    box(65, 24, 14, 12, "Water-hydraulic\nmotor, D cc/rev", "#e3f1e0", 7.5)
    box(83, 24, 15, 12, "Planetary gearbox\nratio R", "#e3f1e0", 7.5)
    box(76, 4, 22, 9, "Valve interface and\nreaction arm -> stem", "#f1e6f5", 7.5)
    box(30, 4, 44, 9, "Discharge hose to drain or sump", "#dbe9f6", 8)
    arr(14.6, 30, 17.6, 30); arr(27.6, 30, 30.6, 30); arr(60.6, 30, 64.6, 30, "water", dy=2.2); arr(79.6, 30, 82.6, 30)
    arr(72, 23.4, 72, 13.6, "exhaust", dy=-0.5); arr(90.5, 23.4, 90.5, 13.6, "torque", dy=-0.5)
    ax.text(50, 0.4, "a stall shows as a pressure rise; the relief valve bounds the motor pressure drop and hence the torque", ha="center", fontsize=7, style="italic")
    save(fig, "Fig1_architecture.png")


# ---- Fig 2 verification
def fig_verify():
    P = R["pressure"]; fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    a = ax[0]
    a.plot(P["psi"], pct(P["analytic"]), "k--", label="closed form")
    a.plot(P["psi"], pct(P["mc"]), "o", ms=4, color=BL, label="Monte Carlo, same assumptions")
    a.plot(P["psi"], pct(P["full"]), "-s", ms=3, color=OR, label="full model 2")
    a.set_xlabel("static supply pressure at the tool (psi)"); a.set_ylabel("probability (%)"); a.set_title("(a) breakaway probability against supply pressure", fontsize=9)
    a.legend(frameon=False, fontsize=7)
    b = ax[1]; L = R["ladder"]; x = np.arange(len(L)); w = 0.27
    b.bar(x - w, pct([r["success"] for r in L]), w, color=BL, label="success")
    b.bar(x, pct([r["success_safe"] for r in L]), w, color=GR, label="success without over-torque")
    b.bar(x + w, pct([r["overtorque"] for r in L]), w, color=RD, label="over-torque")
    b.set_xticks(x); b.set_xticklabels(["v1"] + [r["step"].replace("+ ", "").replace("_", "\n") for r in L[1:]], fontsize=6.5)
    b.set_ylabel("probability (%)"); b.set_ylim(0, 105); b.set_title("(b) switching the mechanisms on, one at a time", fontsize=9); b.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper center")
    save(fig, "Fig2_verification.png")


S_BASE = None
def base_run():
    global S_BASE
    if S_BASE is None:
        S_BASE = H.simulate("mix", H.Tool2(), 200_000, R["meta"]["seed"])
    return S_BASE


# ---- Fig 3 capability vs demand
def fig_capability():
    r = base_run(); fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2)); bins = np.logspace(1.5, 4.4, 70)
    a = ax[0]
    a.hist(r["T_break"], bins, alpha=.5, density=True, color=BL, label="valve breakaway demand")
    a.hist(r["T_cap"], bins, alpha=.5, density=True, color=OR, label="tool capability (relief-limited)")
    a.hist(r["T_allow"], bins, histtype="step", density=True, color=GR, lw=1.5, label="allowable stem torque")
    a.set_xscale("log"); a.set_xlabel("torque (N.m)"); a.set_ylabel("density"); a.legend(frameon=False, fontsize=7); a.set_title("(a) capability against demand", fontsize=9)
    b = ax[1]
    ratio = r["T_peak"] / r["T_allow"]
    b.hist(ratio, np.logspace(-1, 0.8, 70), color=PU, alpha=.8)
    b.axvline(1, color="k", ls=":"); b.set_xscale("log"); b.set_xlabel("peak stall torque / allowable stem torque"); b.set_ylabel("count"); b.set_title("(b) end-of-travel stall, baseline tool", fontsize=9)
    b.text(1.05, b.get_ylim()[1] * 0.8, "%.1f%% above 1" % (100 * (ratio > 1).mean()), fontsize=8)
    save(fig, "Fig3_capability.png")


# ---- Fig 4 relief
def fig_relief():
    Rl = R["relief"]; fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.3))
    a = ax[0]
    for basis, c, lab in (("median", BL, "chart = multiple of class median breakaway"), ("allowable", GR, "chart = fraction of nominal allowable stem torque")):
        rows = Rl[basis]
        a.plot([100 * r["overtorque"] for r in rows], [100 * r["safe"] for r in rows], "-o", ms=3.5, color=c, label=lab)
        for r in rows[::2]:
            a.annotate("%g" % r["mult"], (100 * r["overtorque"], 100 * r["safe"]), textcoords="offset points", xytext=(3, -9), fontsize=6.5, color=c)
    n0 = Rl["no_relief"]; a.plot(100 * n0["overtorque"], 100 * n0["safe"], "^", color=RD, label="no relief valve")
    a.axvline(1, color="k", ls=":"); a.text(1.3, 3, "1% (illustrative)", fontsize=7)
    a.set_xlabel("over-torque probability (%)"); a.set_ylabel("success without over-torque (%)"); a.set_title("(a) torque-limiter setting", fontsize=9); a.legend(frameon=False, fontsize=6.5, loc="lower right")
    b = ax[1]; acc = R["accumulator"]; ks = list(acc); x = np.arange(len(ks)); w = 0.27
    b.bar(x - w, [100 * acc[k]["safe"] for k in ks], w, color=GR, label="success without over-torque")
    b.bar(x, [100 * acc[k]["overtorque"] for k in ks], w, color=RD, label="over-torque")
    b.bar(x + w, [100 * acc[k]["damage"] for k in ks], w, color=PU, label="stem damage")
    b.set_xticks(x); b.set_xticklabels(["%g" % float(k) for k in ks]); b.set_xlabel("fraction of the stall surge absorbed by an accumulator"); b.set_ylabel("probability (%)")
    b.set_title("(b) hose-side accumulator", fontsize=9); b.legend(frameon=False, fontsize=7)
    save(fig, "Fig4_relief_accumulator.png")


# ---- Fig 5 design space
def fig_grid():
    G = R["grid"]; fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.3))
    for a, key, title, cm in ((ax[0], "safe", "(a) success without over-torque (%)", "viridis"), (ax[1], "overtorque", "(b) over-torque probability (%)", "magma_r")):
        M = 100 * np.array(G[key]); im = a.imshow(M, origin="lower", cmap=cm, aspect="auto")
        a.set_xticks(range(len(G["R"]))); a.set_xticklabels(G["R"]); a.set_yticks(range(len(G["D"]))); a.set_yticklabels(G["D"])
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                a.text(j, i, "%.0f" % M[i, j], ha="center", va="center", fontsize=7.5, color="w" if (M[i, j] < M.mean()) == (key == "safe") else "k")
        a.set_xlabel("gear ratio"); a.set_ylabel("motor displacement (cc/rev)"); a.set_title(title, fontsize=9); fig.colorbar(im, ax=a, shrink=.8)
    save(fig, "Fig6_design_space.png")


# ---- Fig 6 Pareto
def fig_pareto():
    O = R["optimization"]; fig, ax = plt.subplots(1, 2, figsize=(8.2, 3.5))
    cols = {"allowable|0": BL, "median|0": GY, "allowable|0.75": GR, "median|0.75": OR}
    labs = {"allowable|0": "allowable basis, no accumulator", "median|0": "median basis, no accumulator", "allowable|0.75": "allowable basis, accumulator 0.75", "median|0.75": "median basis, accumulator 0.75"}
    for k, v in O.items():
        if k.endswith("creep"):
            continue
        d = v["designs"]; c = cols[k]
        ax[0].scatter([100 * x["overtorque"] for x in d], [100 * x["safe"] for x in d], s=4, color=c, alpha=.25)
        xs = np.array([100 * x["overtorque"] for x in d]); ys = np.array([100 * x["safe"] for x in d]); o = np.argsort(xs)
        env = np.maximum.accumulate(ys[o])
        ax[0].step(xs[o], env, where="post", color=c, lw=1.6, label=labs[k])
    for k, v in O.items():
        if not k.endswith("creep"):
            continue
        d = v["designs"]; c = cols[k[:-6]]
        xs = np.array([100 * x["overtorque"] for x in d]); ys = np.array([100 * x["safe"] for x in d]); o = np.argsort(xs)
        ax[0].step(xs[o], np.maximum.accumulate(ys[o]), where="post", color=c, lw=1.6, ls="--", label=labs[k[:-6]] + ", creep")
    bl = R["baseline"]; ax[0].plot(100 * bl["overtorque"]["p"], 100 * bl["success_safe"]["p"], "k*", ms=11, label="baseline tool")
    ax[0].axvline(1, color="k", ls=":"); ax[0].set_xlim(0, 25); ax[0].set_ylim(30, 75)
    ax[0].set_xlabel("over-torque probability (%)"); ax[0].set_ylabel("success without over-torque (%)"); ax[0].set_title("(a) designs and best safe-stroke probability reached", fontsize=9); ax[0].legend(frameon=False, fontsize=5.6, loc="lower right", ncol=1)
    # (b) water per stroke along the frontier of the allowable/0.75 family
    v = O["allowable|0.75"]; d = v["designs"]
    sc = ax[1].scatter([100 * x["overtorque"] for x in d], [x["volume"] for x in d], c=[100 * x["safe"] for x in d], s=6, cmap="viridis")
    ax[1].set_xlim(0, 25); ax[1].set_ylim(0, 3500); ax[1].set_xlabel("over-torque probability (%)"); ax[1].set_ylabel("median water per stroke (L)")
    ax[1].set_title("(b) water per stroke (accumulator 0.75, allowable basis)", fontsize=9); fig.colorbar(sc, ax=ax[1], label="success without over-torque (%)")
    save(fig, "Fig8_pareto.png")


# ---- Fig 7 robustness
def fig_robust():
    Rb = R["robust"]; sc = list(next(iter(Rb.values()))["scenarios"])
    want = ["baseline (chart 2x median, no accumulator)", "baseline + accumulator 0.75", "optimized allowable|0", "optimized allowable|0.75"]
    want += [n for n in Rb if n.startswith("robust allowable|0.75")][:1]
    want += [n for n in Rb if n == "optimized allowable|0.75|creep"]
    pick = [n for n in want if n in Rb]
    fig, ax = plt.subplots(2, 1, figsize=(8.4, 5.6), sharex=True); x = np.arange(len(sc)); w = 0.8 / max(len(pick), 1)
    cols = [GY, PU, BL, GR, OR, RD]
    for i, n in enumerate(pick):
        xs = x + (i - (len(pick) - 1) / 2) * w
        ax[0].bar(xs, [100 * Rb[n]["scenarios"][s_]["safe"] for s_ in sc], w, color=cols[i % 6], label=n)
        ax[1].bar(xs, [100 * Rb[n]["scenarios"][s_]["overtorque"] for s_ in sc], w, color=cols[i % 6])
    ax[0].set_ylabel("success without\nover-torque (%)"); ax[1].set_ylabel("over-torque\nprobability (%)"); ax[1].axhline(1, color="k", ls=":")
    ax[1].set_xticks(x); ax[1].set_xticklabels(sc, rotation=25, ha="right", fontsize=7.5); ax[0].set_ylim(0, 88); ax[0].legend(frameon=False, fontsize=6.3, ncol=2)
    save(fig, "Fig9_robustness.png")


# ---- Fig 8 flow limiter and reserve
def fig_flow():
    Q = R["qlimit"]; Rv = R["reserve"]; fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.1))
    a = ax[0]
    a.plot([r["q"] for r in Q], [100 * r["safe"] for r in Q], "-o", ms=3.5, color=BL, label="success without over-torque")
    a.plot([r["q"] for r in Q], [100 * r["time_ok"] for r in Q], "-s", ms=3.5, color=GR, label="stroke within 15 min")
    a.set_xlabel("flow-limiter setting (gpm)"); a.set_ylabel("probability (%)"); a.set_title("(a) speed against flow limit", fontsize=9); a.legend(frameon=False, fontsize=7)
    b = ax[1]
    b.plot([r["q"] for r in Q], [r["volume_median_L"] for r in Q], "-o", ms=3.5, color=OR)
    b.set_xlabel("flow-limiter setting (gpm)"); b.set_ylabel("median water per successful stroke (L)"); b.set_title("(b) water consumed", fontsize=9)
    c = ax[2]
    c.semilogx([r["mult"] for r in Rv], [100 * r["reserve_viol"] for r in Rv], "-o", ms=3.5, color=RD, label="reserve violated (60 gpm, no rule)")
    c.semilogx([r["mult"] for r in Rv], [100 * r["safe"] for r in Rv], "-s", ms=3.5, color=BL, label="success w/o over-torque, no rule")
    c.semilogx([r["mult"] for r in Rv], [100 * r["safe_adaptive"] for r in Rv], "-^", ms=3.5, color=GR, label="success w/o over-torque, adaptive rule")
    c.set_xlabel("spare flow (multiple of prior)"); c.set_ylabel("probability (%)"); c.set_title("(c) firefighting reserve", fontsize=9); c.legend(frameon=False, fontsize=6.3)
    save(fig, "Fig7_flow_reserve.png")


# ---- Fig 9 sensitivity
def fig_sens():
    s = R["sensitivity"]; fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.9))
    nice = {"Ps": "supply pressure", "elev": "elevation", "T_break": "breakaway torque (rel. to class)", "seize": "seizure", "eta_g": "gearbox efficiency", "eta_m": "motor efficiency",
            "relief_f": "relief set-point error", "hose_len": "hose length", "hose_C": "hose coefficient", "foul": "strainer fouling", "f_run": "running-torque fraction",
            "T_allow": "allowable stem torque (rel. to nominal)", "Qa": "source flow capacity", "drop": "efficiency loss at stall", "class_median": "valve class (median torque)",
            "wave_speed": "wave speed", "stop_time": "stopping time", "surge_unrelieved": "unrelieved surge fraction", "relief_override": "relief override"}
    for a, key, title in ((ax[0], "prcc_margin", "(a) torque margin ln(T_cap/T_break)"), (ax[1], "prcc_peak_ratio", "(b) peak ratio ln(T_peak/T_allow)")):
        d = s[key]; ks = sorted(d, key=lambda k: abs(d[k]))[-12:]; a.barh([nice.get(k, k) for k in ks], [d[k] for k in ks], color=[BL if d[k] > 0 else OR for k in ks])
        a.set_xlabel("partial rank correlation"); a.set_title(title, fontsize=9); a.tick_params(axis="y", labelsize=7)
    save(fig, "Fig11_sensitivity.png")


# ---- Fig 10 time and water
def fig_time():
    r = base_run(); ok = r["success"]; fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    for name, c in (("gate_12in", BL), ("gate_24in", GR), ("butterfly_36in", OR), ("plug_16in", PU), ("legacy_seized", RD), ("ypf_1500", GY)):
        rr = H.simulate(name, H.Tool2(), 60_000, R["meta"]["seed"]); t = np.sort(rr["t_min"][rr["success"]])
        ax[0].plot(t, np.arange(1, len(t) + 1) / 60_000 * 100, color=c, label=name)
    ax[0].axvline(15, color="k", ls=":"); ax[0].set_xlim(0, 25); ax[0].set_xlabel("operating time to stroke (min)"); ax[0].set_ylabel("cumulative success (%)"); ax[0].legend(frameon=False, fontsize=6.5)
    ax[0].set_title("(a) stroking time", fontsize=9)
    ax[1].hist(r["volume_L"][ok], 60, color=BL, alpha=.8); ax[1].set_xlabel("water used in one stroke (L)"); ax[1].set_ylabel("count"); ax[1].set_title("(b) water per successful stroke, baseline", fontsize=9)
    save(fig, "Fig12_time_water.png")


# ---- Fig 11 benchmarks
def fig_bench():
    B = R["benchmarks"]; names = list(B); fig, ax = plt.subplots(figsize=(7.6, 3.1)); x = np.arange(len(names)); w = 0.38
    ax.bar(x - w / 2, [100 * B[n]["success"] for n in names], w, color=BL, label="success")
    ax.bar(x + w / 2, [100 * B[n]["safe"] for n in names], w, color=GR, label="success without over-torque")
    ax.set_xticks(x); ax.set_xticklabels([n.replace(", ", ",\n").replace(" (", "\n(") for n in names], fontsize=6.5); ax.set_ylabel("probability (%)"); ax.legend(frameon=False, fontsize=7)
    save(fig, "Fig13_benchmarks.png")


def fig_surge_het():
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.3)); a = ax[0]
    for (name, rows), c in zip(R["surge_study"].items(), (RD, GR, BL)):
        a.plot([r["mult"] for r in rows], [100 * r["overtorque"] for r in rows], "-o", ms=3.5, color=c, label=name)
    a.axhline(1, color="k", ls=":"); a.set_xlabel("surge multiplier (1 = prior)"); a.set_ylabel("over-torque probability (%)"); a.set_title("(a) sensitivity to the surge assumptions", fontsize=9); a.legend(frameon=False, fontsize=6.5)
    b = ax[1]; Hh = R["hetero"]; names = list(next(iter(Hh.values()))["per_class"]); x = np.arange(len(names)); w = 0.38
    for i, (k, c, lab) in enumerate((("median|0.75", OR, "chart from class median breakaway"), ("allowable|0.75", GR, "chart from nominal allowable stem torque"))):
        if Hh.get(k, {}).get("per_class"):
            b.bar(x + (i - 0.5) * w, [100 * Hh[k]["per_class"][n_]["overtorque"] for n_ in names], w, color=c, label=lab)
    b.axhline(1, color="k", ls=":"); b.set_xticks(x); b.set_xticklabels(names, rotation=20, ha="right", fontsize=7); b.set_ylabel("over-torque probability (%)")
    b.set_title("(b) stem strength differs between classes", fontsize=9); b.legend(frameon=False, fontsize=6.5)
    save(fig, "Fig10_surge_hetero.png")


def fig_creep():
    C = R["creep"]; fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.2))
    def pick(acc, cs, ce, ns=1, ne=2):
        return [r for r in C if r["acc"] == acc and r["cs"] == cs and r["ce"] == ce and r["ns"] == ns and r["ne"] == ne][0]
    ends = [0, 40, 20, 10]
    a = ax[0]
    for acc, c, lab in ((0.0, RD, "no accumulator"), (0.75, GR, "accumulator 0.75")):
        a.plot(range(len(ends)), [100 * pick(acc, 0, e)["overtorque"] for e in ends], "-o", ms=4, color=c, label=lab)
    a.set_xticks(range(len(ends))); a.set_xticklabels(["none", "40", "20", "10"]); a.set_xlabel("flow during the last 2 turns (gpm)"); a.set_ylabel("over-torque probability (%)")
    a.set_title("(a) creep at the end of travel", fontsize=9); a.legend(frameon=False, fontsize=7)
    b = ax[1]
    for acc, c, lab in ((0.0, RD, "no accumulator"), (0.75, GR, "accumulator 0.75")):
        b.plot(range(len(ends)), [100 * pick(acc, 0, e)["safe"] for e in ends], "-o", ms=4, color=c, label=lab)
        b.plot(range(len(ends)), [100 * pick(acc, 0, e)["success"] for e in ends], "--s", ms=3, color=c, alpha=.6)
    b.set_xticks(range(len(ends))); b.set_xticklabels(["none", "40", "20", "10"]); b.set_xlabel("flow during the last 2 turns (gpm)"); b.set_ylabel("probability (%)")
    b.set_title("(b) safe stroke (solid) and success (dashed)", fontsize=9)
    c_ = ax[2]
    variants = [(0, 0, 1, 2, "none"), (0, 20, 1, 2, "end 20"), (10, 10, 1, 2, "10/10, 1+2 turns"), (10, 10, 2, 4, "10/10, 2+4 turns"), (10, 10, 4, 8, "10/10, 4+8 turns")]
    x = np.arange(len(variants)); w = 0.38
    c_.bar(x - w / 2, [pick(0.0, v[0], v[1], v[2], v[3])["t_med"] for v in variants], w, color=BL, label="median stroking time (min)")
    c_.bar(x + w / 2, [100 * pick(0.0, v[0], v[1], v[2], v[3])["time_ok"] / 10 for v in variants], w, color=OR, label="in time (% / 10)")
    c_.set_xticks(x); c_.set_xticklabels([v[4] for v in variants], rotation=20, ha="right", fontsize=7); c_.set_title("(c) time cost of the slow phases", fontsize=9); c_.legend(frameon=False, fontsize=6.5)
    save(fig, "Fig5_creep.png")


def fig_convergence():
    c = R["convergence"]; fig, ax = plt.subplots(figsize=(5.4, 3.0)); ax.semilogx(c["n"], pct(c["running"]), color=BL); ax.axhline(100 * c["running"][-1], color="k", ls=":")
    ax.set_xlabel("samples"); ax.set_ylabel("running estimate (%)"); ax.set_title("success without over-torque", fontsize=9); save(fig, "FigS1_convergence.png")


def fig_kit():
    K = R["kit"]; fig, ax = plt.subplots(figsize=(7.4, 3.2)); names = list(K); x = np.arange(len(names)); cf = [(r["D"], r["R"]) for r in K[names[0]]]; w = 0.15
    for i, (D, Rr) in enumerate(cf):
        ax.bar(x + (i - 2) * w, [100 * K[n][i]["safe"] for n in names], w, label="%d cc, %d:1" % (D, Rr))
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=7); ax.set_ylabel("success without over-torque (%)"); ax.legend(frameon=False, fontsize=7, ncol=3)
    save(fig, "FigS2_kit.png")


if __name__ == "__main__":
    for f in (fig_arch, fig_verify, fig_capability, fig_relief, fig_grid, fig_pareto, fig_robust, fig_flow, fig_sens, fig_time, fig_bench, fig_surge_het, fig_creep, fig_convergence, fig_kit):
        f(); print(f.__name__, "ok")
