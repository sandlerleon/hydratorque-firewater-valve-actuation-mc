#!/usr/bin/env python3
"""
HydraTorque_MC.py - Monte Carlo validation of a fire-hose-powered portable valve operator.

One self-contained file (numpy + scipy-free + matplotlib), MyUncle-style:
  * valve-class presets sharing one engine
  * closed-form results that cross-check the simulation
  * one-call figure suite + Markdown results skeleton + SQLite run log

Question answered:
    Given uncertain firewater supply (source, pressure, hose, elevation, fouling),
    uncertain valve torque demand (breakaway, seizure, running torque), and a
    pressure-set torque limiter, how often does a water-hydraulic tool
    (displacement D, gear ratio R) open/close the valve in time without
    exceeding the valve's allowable stem torque?

Physics (per sample):
    k_T      = D/(2*pi) * eta_m * R * eta_g            [N.m per Pa across motor]
    T_stall  = k_T * min(P_static, P_relief)           breakaway capability
    dP_run   = T_run / k_T                             running pressure drop
    Q_run    = sqrt((P_static - dP_run - foul)/(C*L/1e6 + k_spc)) , capped by flow limiter
    n_out    = Q_run * eta_v / (D*R)                   output speed
    time     = turns / n_out
    (hose friction, IFSTA form: FL = C*(Q/100)^2*(L/100) psi, Q in gpm, L in ft)

Every distribution below is an ASSUMED PRIOR to be calibrated in Phase 1
(valve torque survey, supply-pressure survey, bench rig). Nothing here is measured data.

Usage:
    python HydraTorque_MC.py --demo                 # self-test (analytics vs MC, energy balance)
    python HydraTorque_MC.py --reproduce            # full figure suite + results.md + results.json
    python HydraTorque_MC.py --preset gate_24in --n 500000
    python HydraTorque_MC.py --grid-size
"""
import argparse, json, math, os, sqlite3, time
from dataclasses import dataclass, replace
import numpy as np

PSI = 6894.757            # Pa per psi
GPM_LPM = 3.78541         # L/min per gpm
GPM_M3S = 6.30902e-5      # m3/s per gpm

# ----------------------------------------------------------------------------- presets
@dataclass(frozen=True)
class Tool:
    D_cc: float = 200.0            # motor displacement, cc/rev
    ratio: float = 250.0           # planetary reduction
    eta_m: tuple = (0.85, 0.03)    # motor mechanical efficiency (mean, sd)
    eta_v: tuple = (0.92, 0.02)    # motor volumetric efficiency
    eta_g: tuple = (0.70, 0.05)    # gearbox + valve-interface efficiency
    q_limit_gpm: float = 60.0      # SPC flow limiter
    spc_k: float = 0.0044          # SPC loss coefficient, psi/gpm^2 (about 3 psi at 26 gpm)
    relief_enabled: bool = True
    relief_mult: float = 2.0       # relief torque chart setting = mult * class median breakaway
    relief_tol: float = 0.05       # relative sd of relief set-point

@dataclass(frozen=True)
class ValveClass:
    name: str
    median_Nm: float               # median breakaway torque
    sigma: float                   # lognormal sigma of breakaway torque
    turns: tuple                   # (lo, hi) handwheel turns to stroke
    p_seize: float                 # probability of seized/stiff condition
    allow_mult: float = 3.0        # nominal allowable stem torque = allow_mult * median
    allow_sigma: float = 0.25      # lognormal sigma of allowable stem torque

PRESETS = {
    "gate_12in":     ValveClass("gate_12in",      400, 0.45, (14, 22), 0.05),
    "gate_24in":     ValveClass("gate_24in",     1200, 0.50, (30, 50), 0.08),
    "butterfly_36in":ValveClass("butterfly_36in",1500, 0.45, (35, 70), 0.06),
    "plug_16in":     ValveClass("plug_16in",      800, 0.50, (8, 16),  0.07),
    "legacy_seized": ValveClass("legacy_seized", 2000, 0.60, (25, 60), 0.25),
}
MIX_WEIGHTS = {"gate_12in": .30, "gate_24in": .25, "butterfly_36in": .15, "plug_16in": .10, "legacy_seized": .20}
SOURCES = [("firewater_ring", .50, 140., 20.), ("fire_truck", .30, 120., 25.), ("municipal_hydrant", .20, 60., 15.)]
HOSES = [(1.75, 15.5, .30), (2.5, 2.0, .50), (3.0, 0.8, .20)]   # (inch, IFSTA C, weight)
T_MAX_MIN = 15.0               # assumed closing-time requirement (operating time, excl. setup)
INTERFERENCE_FRAC = 0.25       # tool draw > 25% of source flow = firefighting interference

def class_arrays(preset):
    names = list(MIX_WEIGHTS) if preset == "mix" else [preset]
    w = np.array([MIX_WEIGHTS[k] for k in names]) if preset == "mix" else np.array([1.0])
    cls = [PRESETS[k] for k in names]
    return names, w / w.sum(), cls

# ----------------------------------------------------------------------------- engine
def simulate(preset="mix", tool=Tool(), n=200_000, seed=1, Ps_override=None, nominal=False):
    """Vectorised Monte Carlo. nominal=True removes all input randomness except valve
    breakaway demand (used for the closed-form cross-check)."""
    rng = np.random.default_rng(seed)
    names, w, cls = class_arrays(preset)
    ci = rng.choice(len(cls), size=n, p=w)
    med = np.array([c.median_Nm for c in cls])[ci]
    sig = np.array([c.sigma for c in cls])[ci]
    tlo = np.array([c.turns[0] for c in cls])[ci]; thi = np.array([c.turns[1] for c in cls])[ci]
    pse = np.array([c.p_seize for c in cls])[ci]
    am = np.array([c.allow_mult for c in cls])[ci]; asg = np.array([c.allow_sigma for c in cls])[ci]

    T_break = med * np.exp(sig * rng.standard_normal(n))
    seize = rng.random(n) < pse
    seize_mult = rng.uniform(1.5, 3.0, n)
    f_run = rng.uniform(0.3, 0.6, n)
    turns = rng.uniform(tlo, thi)
    T_allow = am * med * np.exp(asg * rng.standard_normal(n))

    src = rng.choice(len(SOURCES), size=n, p=[s[1] for s in SOURCES])
    Ps = np.clip(rng.normal(np.array([s[2] for s in SOURCES])[src], np.array([s[3] for s in SOURCES])[src]), 20, 250)
    elev_psi = 0.433 * rng.normal(0, 15, n)
    hi = rng.choice(len(HOSES), size=n, p=[h[2] for h in HOSES])
    C = np.array([h[1] for h in HOSES])[hi]
    L = rng.uniform(50, 400, n)
    eta_m = np.clip(rng.normal(*tool.eta_m, n), .6, .95)
    eta_v = np.clip(rng.normal(*tool.eta_v, n), .7, .99)
    eta_g = np.clip(rng.normal(*tool.eta_g, n), .5, .85)
    rel_f = rng.normal(1, tool.relief_tol, n)
    foul = rng.lognormal(math.log(2.0), 0.8, n) + np.where(rng.random(n) < 0.03, rng.uniform(20, 60, n), 0)
    Qsrc = rng.lognormal(math.log(300), 0.5, n)

    if nominal:   # degenerate everything except breakaway demand
        seize[:] = False; f_run[:] = 0.45; elev_psi[:] = 0; C[:] = 2.0; L[:] = 200
        eta_m[:] = tool.eta_m[0]; eta_v[:] = tool.eta_v[0]; eta_g[:] = tool.eta_g[0]
        rel_f[:] = 1.0; foul[:] = 0.0
    if Ps_override is not None:
        Ps = np.full(n, float(Ps_override))
    T_break = np.where(seize, T_break * seize_mult, T_break)

    D = tool.D_cc * 1e-6; R = tool.ratio
    kT = D / (2 * math.pi) * eta_m * R * eta_g                    # N.m per Pa
    kT_nom = D / (2 * math.pi) * tool.eta_m[0] * R * tool.eta_g[0]
    dP_static = (Ps - elev_psi) * PSI
    if tool.relief_enabled:
        P_rel = (tool.relief_mult * med) / kT_nom * rel_f          # chart-set relief pressure (Pa)
        dP_stall = np.minimum(dP_static, P_rel)
    else:
        P_rel = np.full(n, np.inf); dP_stall = dP_static
    T_stall = kT * dP_stall
    break_ok = T_stall >= T_break
    press_limited = dP_static < T_break / kT                       # supply too weak
    relief_limited = (~break_ok) & (~press_limited)

    T_run = f_run * T_break
    dP_req_psi = T_run / kT / PSI
    head = (Ps - elev_psi) - dP_req_psi - foul
    coeff = C * L / 1e6 + tool.spc_k
    Q_fric = np.sqrt(np.clip(head, 0, None) / coeff)
    Q_run = np.minimum(Q_fric, tool.q_limit_gpm)
    run_ok = (head > 0) & (T_run * 1.0 <= T_stall)
    n_out = Q_run * GPM_LPM * 1000 * eta_v / tool.D_cc / R         # rpm
    with np.errstate(divide="ignore", invalid="ignore"):
        t_min = np.where(n_out > 0, turns / n_out, np.inf)
    time_ok = t_min <= T_MAX_MIN
    success = break_ok & run_ok & time_ok

    # energy balance: mechanical out <= hydraulic in at the motor
    P_in = dP_req_psi * PSI * Q_run * GPM_M3S
    P_out = T_run * n_out * 2 * math.pi / 60
    with np.errstate(divide="ignore", invalid="ignore"):
        eb = np.where(P_in > 0, P_out / P_in, 0)
    return dict(
        n=n, success=success, break_ok=break_ok, run_ok=run_ok, time_ok=time_ok,
        pressure_limited=press_limited & ~break_ok, relief_limited=relief_limited,
        overtorque=T_stall > T_allow, interference=(Q_run / Qsrc) > INTERFERENCE_FRAC,
        T_break=T_break, T_stall=T_stall, T_allow=T_allow, t_min=t_min, Q_run=Q_run, n_out=n_out,
        energy_ratio=eb, margin=np.log(np.maximum(T_stall, 1e-9) / T_break),
        inputs=dict(Ps=Ps, elev=elev_psi, T_break=T_break, seize=seize.astype(float), eta_g=eta_g,
                    eta_m=eta_m, relief_f=rel_f, hose_len=L, hose_C=C, foul=foul, f_run=f_run),
    )

# ----------------------------------------------------------------------------- analytics
def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def analytic_breakaway_mix(T_cap, preset="mix"):
    """Closed form: P(T_break <= T_cap) for lognormal demand, mixture of valve classes, no seizure."""
    names, w, cls = class_arrays(preset)
    return float(sum(wi * Phi((math.log(T_cap) - math.log(c.median_Nm)) / c.sigma) for wi, c in zip(w, cls)))

def nominal_capacity_Nm(tool, Ps_psi):
    kT = tool.D_cc * 1e-6 / (2 * math.pi) * tool.eta_m[0] * tool.ratio * tool.eta_g[0]
    return kT * Ps_psi * PSI

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)

def summarize(r):
    n = r["n"]; s = {}
    for k in ("success", "break_ok", "run_ok", "time_ok", "pressure_limited", "relief_limited", "overtorque", "interference"):
        v = int(r[k].sum()); lo, hi = wilson(v, n)
        s[k] = dict(p=v / n, lo=lo, hi=hi)
    ok = r["success"]
    s["t_min_median"] = float(np.median(r["t_min"][ok])) if ok.any() else None
    s["t_min_p90"] = float(np.percentile(r["t_min"][ok], 90)) if ok.any() else None
    s["T_stall_median_Nm"] = float(np.median(r["T_stall"]))
    s["T_stall_p05_Nm"] = float(np.percentile(r["T_stall"], 5))
    s["Q_run_median_gpm"] = float(np.median(r["Q_run"]))
    s["n_out_median_rpm"] = float(np.median(r["n_out"][ok])) if ok.any() else None
    s["energy_ratio_max"] = float(r["energy_ratio"].max())
    return s

def rank(x): return np.argsort(np.argsort(x)).astype(float)
def spearman(x, y):
    a, b = rank(x), rank(y); a -= a.mean(); b -= b.mean()
    return float((a * b).sum() / math.sqrt((a * a).sum() * (b * b).sum()))

# ----------------------------------------------------------------------------- studies
def study_presets(tool, n, seed):
    out = {}
    for name in list(PRESETS) + ["mix"]:
        out[name] = summarize(simulate(name, tool, n, seed))
    return out

def study_pressure(tool, n, seed, pressures=range(40, 205, 10)):
    mc, an = [], []
    for P in pressures:
        r = simulate("mix", replace(tool, relief_enabled=False), n, seed, Ps_override=P, nominal=True)
        mc.append(float(r["break_ok"].mean()))
        an.append(analytic_breakaway_mix(nominal_capacity_Nm(tool, P)))
    return list(pressures), mc, an

def study_grid(tool, n, seed, Ds=(100, 150, 200, 300, 400), Rs=(100, 150, 250, 350, 500)):
    G = np.zeros((len(Ds), len(Rs))); OT = np.zeros_like(G)
    for i, D in enumerate(Ds):
        for j, Rr in enumerate(Rs):
            r = simulate("mix", replace(tool, D_cc=D, ratio=Rr), n, seed)
            G[i, j] = r["success"].mean(); OT[i, j] = r["overtorque"].mean()
    return Ds, Rs, G, OT

def study_relief(tool, n, seed, mults=(0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0)):
    rows = []
    for m in mults:
        r = simulate("mix", replace(tool, relief_mult=m), n, seed)
        rows.append((m, float(r["success"].mean()), float(r["overtorque"].mean())))
    r0 = simulate("mix", replace(tool, relief_enabled=False), n, seed)
    return rows, (float(r0["success"].mean()), float(r0["overtorque"].mean()))

def study_qlimit(tool, n, seed, limits=(15, 20, 30, 40, 60, 80, 100)):
    rows = []
    for q in limits:
        r = simulate("mix", replace(tool, q_limit_gpm=q), n, seed)
        rows.append((q, float(r["success"].mean()), float(r["interference"].mean()), float(r["time_ok"].mean())))
    return rows

def study_kit(tool, n, seed, cfgs=((100, 500), (150, 350), (200, 250), (300, 150), (400, 100))):
    """Per valve class: success for each (D_cc, ratio) on the D*R ~ 50,000 ridge; operator picks the best."""
    out = {}
    for name in PRESETS:
        out[name] = [(D, Rr, float(simulate(name, replace(tool, D_cc=D, ratio=Rr), n, seed)["success"].mean())) for D, Rr in cfgs]
    return out

def study_sensitivity(tool, n, seed):
    r = simulate("mix", tool, n, seed)
    return {k: spearman(v, r["margin"]) for k, v in r["inputs"].items()}

def selftest(tool, n=100_000, seed=7):
    pr, mc, an = study_pressure(tool, n, seed)
    dev = max(abs(a - b) for a, b in zip(mc, an))
    r = simulate("mix", tool, n, seed)
    assert dev < 0.01, f"MC vs closed form deviation {dev:.4f}"
    assert r["energy_ratio"].max() < 1.0, "energy balance violated"
    assert abs(nominal_capacity_Nm(tool, 100) - 3265) / 3265 < 0.03, "baseline torque mismatch"
    return dev, float(r["energy_ratio"].max())

# ----------------------------------------------------------------------------- figures + report
def reproduce_paper(outdir="hydratorque_mc_out", n=200_000, n_sweep=60_000, seed=2026, tool=Tool()):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    dev, emax = selftest(tool)
    pres = study_presets(tool, n, seed)
    pr, mc, an = study_pressure(tool, n_sweep, seed)
    Ds, Rs, G, OT = study_grid(tool, n_sweep, seed)
    relief_rows, no_relief = study_relief(tool, n_sweep, seed)
    sens = study_sensitivity(tool, n_sweep, seed)
    qrows = study_qlimit(tool, n_sweep, seed)
    kit = study_kit(tool, n_sweep, seed)
    base = simulate("mix", tool, n, seed)
    bsum = pres["mix"]
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    figs = {}

    f, ax = plt.subplots(figsize=(6.4, 3.4))
    bins = np.logspace(1.5, 4.2, 70)
    ax.hist(base["T_break"], bins, alpha=.55, label="Valve breakaway demand", density=True)
    ax.hist(base["T_stall"], bins, alpha=.55, label="Tool stall capability", density=True)
    ax.set_xscale("log"); ax.set_xlabel("Torque (N.m)"); ax.set_ylabel("Density"); ax.legend(frameon=False)
    ax.set_title("Capability vs demand (valve-class mix)"); f.tight_layout()
    figs["fig1_capability_vs_demand.png"] = f

    f, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(pr, an, "k--", label="Closed form (clean valves)")
    ax.plot(pr, mc, "o", ms=4, label="Monte Carlo (same assumptions)")
    full = [simulate("mix", tool, n_sweep, seed, Ps_override=P)["success"].mean() for P in pr]
    ax.plot(pr, full, "-s", ms=3, label="Full model (relief, seizure, time limit)")
    ax.set_xlabel("Static supply pressure at tool (psi)"); ax.set_ylabel("Probability of success")
    ax.set_title("Success vs supply pressure; analytics cross-check simulation"); ax.legend(frameon=False, fontsize=8); f.tight_layout()
    figs["fig2_pressure_crosscheck.png"] = f

    f, ax = plt.subplots(figsize=(5.2, 3.9))
    im = ax.imshow(G * 100, origin="lower", cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(Rs))); ax.set_xticklabels(Rs); ax.set_yticks(range(len(Ds))); ax.set_yticklabels(Ds)
    for i in range(len(Ds)):
        for j in range(len(Rs)):
            ax.text(j, i, f"{G[i, j] * 100:.0f}", ha="center", va="center", color="w" if G[i, j] < .6 else "k", fontsize=8)
    ax.set_xlabel("Gear ratio"); ax.set_ylabel("Motor displacement (cc/rev)"); ax.set_title("Overall success probability (%)")
    f.colorbar(im, ax=ax, shrink=.8); f.tight_layout()
    figs["fig3_design_space.png"] = f

    f, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot([r[2] * 100 for r in relief_rows], [r[1] * 100 for r in relief_rows], "-o", ms=4)
    for m, s, o in relief_rows:
        ax.annotate(f"{m:g}x", (o * 100, s * 100), textcoords="offset points", xytext=(4, -9), fontsize=7)
    ax.plot(no_relief[1] * 100, no_relief[0] * 100, "r^", label="No relief")
    ax.set_xlabel("Over-torque (damage-risk) probability (%)"); ax.set_ylabel("Success probability (%)")
    ax.set_title("Relief-setting trade-off"); ax.legend(frameon=False); f.tight_layout()
    figs["fig4_relief_tradeoff.png"] = f

    f, ax = plt.subplots(figsize=(6.0, 3.5))
    for name in list(PRESETS) + ["mix"]:
        r = simulate(name, tool, 60_000, seed); t = np.sort(r["t_min"][r["success"]])
        if len(t): ax.plot(t, np.arange(1, len(t) + 1) / 60_000, label=name, lw=2 if name == "mix" else 1)
    ax.axvline(T_MAX_MIN, color="k", ls=":"); ax.set_xlim(0, 25)
    ax.set_xlabel("Operating time to stroke (min)"); ax.set_ylabel("Cumulative probability of success within time")
    ax.legend(frameon=False, fontsize=7); ax.set_title("Closing-time distribution"); f.tight_layout()
    figs["fig5_time_cdf.png"] = f

    f, ax = plt.subplots(figsize=(5.6, 3.4))
    ks = sorted(sens, key=lambda k: abs(sens[k]))
    ax.barh(ks, [sens[k] for k in ks]); ax.set_xlabel("Spearman correlation with log torque margin")
    ax.set_title("Sensitivity of capability margin to inputs"); f.tight_layout()
    figs["fig6_sensitivity.png"] = f

    f, ax = plt.subplots(figsize=(5.6, 3.2))
    cs = np.cumsum(base["success"]) / np.arange(1, n + 1); idx = np.unique(np.logspace(2, math.log10(n), 120).astype(int)) - 1
    ax.semilogx(idx + 1, cs[idx]); ax.axhline(cs[-1], color="k", ls=":")
    ax.set_xlabel("Samples"); ax.set_ylabel("Running success estimate"); ax.set_title("Monte Carlo convergence"); f.tight_layout()
    figs["fig7_convergence.png"] = f
    f, ax = plt.subplots(figsize=(5.6, 3.5))
    ax.plot([r[0] for r in qrows], [r[1] * 100 for r in qrows], "-o", ms=4, label="Success")
    ax.plot([r[0] for r in qrows], [r[2] * 100 for r in qrows], "-s", ms=4, label="Firefighting interference")
    ax.set_xlabel("Flow-limiter setting (gpm)"); ax.set_ylabel("Probability (%)")
    ax.set_title("Flow limiter: speed vs interference"); ax.legend(frameon=False); f.tight_layout()
    figs["fig8_flow_limiter.png"] = f
    for name, fg in figs.items():
        fg.savefig(os.path.join(outdir, name), dpi=170); plt.close(fg)

    results = dict(
        meta=dict(n=n, n_sweep=n_sweep, seed=seed, tool=tool.__dict__, t_max_min=T_MAX_MIN, runtime_s=round(time.time() - t0, 1)),
        selftest=dict(max_dev_vs_closed_form=dev, max_energy_ratio=emax),
        presets=pres, pressure=dict(psi=pr, mc=mc, analytic=an),
        grid=dict(D=list(Ds), R=list(Rs), success=G.tolist(), overtorque=OT.tolist()),
        relief=dict(rows=relief_rows, no_relief=no_relief), qlimit=qrows, kit=kit, sensitivity=sens)
    with open(os.path.join(outdir, "results.json"), "w") as fh: json.dump(results, fh, indent=1, default=float)

    db = sqlite3.connect(os.path.join(outdir, "mc_log.sqlite"))
    db.execute("CREATE TABLE IF NOT EXISTS runs(ts TEXT, preset TEXT, n INT, seed INT, tool TEXT, summary TEXT)")
    for k, v in pres.items():
        db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?)", (time.strftime("%F %T"), k, n, seed, json.dumps(tool.__dict__), json.dumps(v, default=float)))
    db.commit(); db.close()

    p = lambda d: f"{d['p'] * 100:.1f}% [{d['lo'] * 100:.1f}, {d['hi'] * 100:.1f}]"
    md = [f"# HydraTorque Monte Carlo results (n={n:,}, seed={seed})", "",
          f"Closed-form vs MC max deviation: {dev:.4f}; max mechanical/hydraulic power ratio: {emax:.3f} (<1).", "",
          "| Preset | Success | Breakaway | Over-torque | Interference | Median time (min) |", "|---|---|---|---|---|---|"]
    for k, v in pres.items():
        md.append(f"| {k} | {p(v['success'])} | {p(v['break_ok'])} | {p(v['overtorque'])} | {p(v['interference'])} | {v['t_min_median'] and round(v['t_min_median'], 1)} |")
    open(os.path.join(outdir, "results.md"), "w").write("\n".join(md))
    return results

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true"); ap.add_argument("--reproduce", action="store_true")
    ap.add_argument("--grid-size", action="store_true"); ap.add_argument("--preset", default=None)
    ap.add_argument("--n", type=int, default=200_000); ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--outdir", default="hydratorque_mc_out")
    a = ap.parse_args()
    if a.grid_size: print(5 * 5); return
    if a.demo:
        dev, e = selftest(Tool()); print(f"OK: MC vs closed form max dev {dev:.4f}; energy ratio max {e:.3f}")
        print(json.dumps(summarize(simulate("mix", Tool(), 100_000, 1)), indent=1, default=float)); return
    if a.preset:
        print(json.dumps(summarize(simulate(a.preset, Tool(), a.n, a.seed)), indent=1, default=float)); return
    reproduce_paper(a.outdir, n=a.n, seed=a.seed); print("done ->", a.outdir)

if __name__ == "__main__":
    main()
