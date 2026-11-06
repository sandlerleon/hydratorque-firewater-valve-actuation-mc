# -*- coding: utf-8 -*-
"""Manuscript, part C: Results (Section 6)."""
from common import *

M = R["meta"]
PRE = R["presets"]; V1 = R["presets_v1"]
CLS = ["gate_12in", "gate_24in", "butterfly_36in", "plug_16in", "legacy_seized", "mix"]
NICE = {"gate_12in": "Gate 12 in", "gate_24in": "Gate 24 in", "butterfly_36in": "Butterfly 36 in", "plug_16in": "Plug 16 in", "legacy_seized": "Legacy seized", "mix": "Weighted mix",
        "ypf_1500": "Challenge valve (1,500 N.m)"}
B0 = BASE
OPTK = {k: v for k, v in OPT.items()}
BEST = {k: v["best_feasible"] for k, v in OPT.items()}


def p(d, dd=1):
    return pc(d["p"], dd)


def ast(cond, msg):
    if not cond:
        raise AssertionError("manuscript claim not supported by results: " + msg)


ast(B0["success_safe"]["p"] < B0["success"]["p"], "safe stroke is a subset of success")
ast(all(b is not None for b in BEST.values()), "a feasible design exists in every family")

add(("h1", "6. Results"))
# ---------------------------------------------------------------------------------------------- 6.1
add(("h2", "@S:base@ The baseline tool and what the added mechanisms change"))
v1mix = V1["mix"]
add(("p", "The baseline tool has a 200 cc motor, a 250:1 gearbox, a 60 gpm flow limiter and a relief valve set at twice the median breakaway torque of the valve class, and is evaluated on %s draws. "
          "Under the assumed priors it completes the stroke in %s of the draws (Wilson interval %s to %s), but it does so without exceeding the allowable stem torque in only %s (%s to %s). "
          "The stall torque exceeds the allowable value in %s of the draws and the yield margin in %s (Table @T:base@). The concept-stage model gave a success probability of %s, an over-torque probability of "
          "%s and, when the two are combined, %s. Model 2 gives %s: about five eighths of the draws, not four fifths, give a safe stroke, and the surge on stall, which the concept-stage model omitted, is the main reason the over-torque "
          "probability now exceeds 15%%."
          % (n(M["n"]), pc(B0["success"]["p"], 1), pp(B0["success"]["lo"]), pp(B0["success"]["hi"]), pc(B0["success_safe"]["p"], 1), pp(B0["success_safe"]["lo"]), pp(B0["success_safe"]["hi"]),
             pc(B0["overtorque"]["p"], 1), pc(B0["damage"]["p"], 1), pc(v1mix["success"]["p"], 1), pc(v1mix["overtorque"]["p"], 1), pc(LAD[0]["success_safe"], 1), pc(B0["success_safe"]["p"], 1))))
rows = []
for c in CLS:
    a, b = PRE[c], V1[c]
    rows.append([NICE[c], pc(b["success"]["p"], 1), pc(a["success"]["p"], 1), pc(a["success_safe"]["p"], 1), pc(a["overtorque"]["p"], 1), pc(a["damage"]["p"], 1),
                 n(a["t_min_median"], 1), n(a["volume_median_L"])])
add(("table", "Table @T:base@. Baseline tool (200 cc, 250:1, 60 gpm, relief at 2 x class median breakaway). Success of the concept-stage model (v1) and of model 2; probabilities over %s draws per class; "
              "time and water are medians of successful strokes. Safe stroke = success without exceedance of the allowable stem torque." % n(M["n"]),
     ["Valve class", "Success v1", "Success", "Safe stroke", "Over-torque", "Stem damage", "Time (min)", "Water (L)"], rows, [1.7, 0.8, 0.8, 0.8, 0.9, 0.9, 0.8, 0.8], 16))
add(("p", "The six added mechanisms do not change the result equally (Table @T:ladder@, Fig. @F:verify@b). The source characteristic, the flow-dependent fouling loss and the exhaust back-pressure change the success probability "
          "by less than %s percentage points, because the flow limiter, not the circuit, sets the flow in most draws (the median operating flow is %s gpm, the limiter setting). The lower torque "
          "efficiency at breakaway and stall lowers the success probability by %s points and the over-torque probability by %s points, since the stall torque is smaller than the concept-stage model assumed. "
          "Replacing the constant volumetric factor by a leakage that is proportional to the pressure drop raises the success probability by %s points (the motor leaks less at the low running pressures "
          "than the constant factor implied). The surge on stall changes the picture: it raises the over-torque probability from %s to %s and the damage probability from %s to %s."
          % (n(100 * max(abs(LAD[i]["success"] - LAD[0]["success"]) for i in (1, 2, 3)), 1), n(BASE["Q_run_median_gpm"]), n(100 * (LAD[3]["success"] - LAD[4]["success"]), 1),
             n(100 * (LAD[3]["overtorque"] - LAD[4]["overtorque"]), 1), n(100 * (LAD[5]["success"] - LAD[4]["success"]), 1), pc(LAD[5]["overtorque"], 1), pc(LAD[6]["overtorque"], 1),
             pc(LAD[5]["damage"], 2), pc(LAD[6]["damage"], 1))))
rows = [[r["step"].replace("version 1 physics", "v1 physics").replace("_", " "), pc(r["success"], 1), pc(r["success_safe"], 1), pc(r["overtorque"], 1), pc(r["damage"], 2), pc(r["interference"], 1)] for r in LAD]
add(("table", "Table @T:ladder@. Switching the model-2 mechanisms on one at a time, in order, on the same %s draws (baseline tool, valve-class mix)." % n(M["n_sweep"]),
     ["Step", "Success", "Safe stroke", "Over-torque", "Stem damage", "Interference (v1 metric)"], rows, [2.2, 0.9, 1.0, 1.0, 1.0, 1.4], 16))
add(("fig", "@FILE:verify@", "Fig. @F:verify@. Verification and mechanism ladder. (a) Breakaway probability against the supply pressure at the tool: closed form, Monte Carlo with the same assumptions, "
            "and the full model. (b) Success, success without over-torque and over-torque probability as the mechanisms of model 2 are switched on in order (v1: the concept-stage physics).", 6.6))
add(("p", "The concept-stage study stated that the tool draws 50 to 100 L/min (13 to 26 gpm), and its simulation used a 60 gpm (227 L/min) flow limiter. The 13 to 26 gpm is the flow that a 200 cc motor needs at an output speed of 1 to 2 rpm. Valves that need 30 to 70 handwheel "
          "turns cannot be stroked in 15 minutes at that speed: the median output speed of a successful stroke in the simulation is %s rpm. The operating flow is therefore the limiter setting, %s gpm "
          "(%s L/min), in most draws, and a successful stroke uses a median of %s L of water (90th percentile %s L; Fig. @F:time@b). A limit of 20 gpm completes the stroke within 15 minutes in only %s of the draws, "
          "and 40 gpm in %s (Fig. @F:flow@a)."
          % (n(BASE["n_out_median_rpm"], 1), n(BASE["Q_run_median_gpm"]), n(BASE["Q_run_median_gpm"] * 3.78541), n(BASE["volume_median_L"]), n(BASE["volume_p90_L"]),
             pc([r for r in R["qlimit"] if r["q"] == 20][0]["time_ok"]), pc([r for r in R["qlimit"] if r["q"] == 40][0]["time_ok"]))))

# ---------------------------------------------------------------------------------------------- 6.2
add(("h2", "@S:relief@ The torque limiter, the surge on stall and stem damage"))
nr, rel_m = R["relief"]["no_relief"], R["relief"]["median"]
r15 = [r for r in rel_m if r["mult"] == 1.5][0]; r20 = [r for r in rel_m if r["mult"] == 2.0][0]; r10 = [r for r in rel_m if r["mult"] == 1.0][0]
add(("p", "The relief valve is essential. Without it the success probability is %s, but the success without exceedance of the allowable stem torque is only %s and the probability of damage "
          "(a torque above the yield margin) is %s. With the relief valve set at twice the median breakaway torque the safe-stroke probability is %s (Fig. @F:relief@a). Lowering the setting to 1.5 times the median "
          "reduces the over-torque probability to %s while the safe-stroke probability falls to %s; at a setting equal to the median breakaway torque the safe-stroke probability is %s because the tool "
          "can no longer break half of the valves free. The success probability and the over-torque probability both rise with the setting, so the probability of a safe stroke has an interior maximum near twice the median; the setting is a safety-critical, "
          "valve-specific parameter, and whatever safety the chart buys is paid for in valves that the tool cannot move."
          % (pc(nr["success"], 1), pc(nr["safe"], 1), pc(nr["damage"], 1), pc(r20["safe"], 1), pc(r15["overtorque"], 1), pc(r15["safe"], 1), pc(r10["safe"], 1))))
sg_ = R["surge"]
add(("p", "The surge on stall is the largest single source of over-torque in the model. Its median is %s psi (%s of the static supply pressure), with a 95th percentile of %s psi. For a small valve the "
          "relief pressure is low: a 12-inch gate valve with a median breakaway torque of 400 N.m has a relief set-point of about 25 psi on the baseline tool, below the typical surge, so the pressure that the relief "
          "valve cannot relieve in time exceeds the pressure that the chart is meant to enforce; the over-torque probability of this class is %s (Table @T:base@). A hose-side accumulator that absorbs a "
          "quarter, a half or three quarters of the surge lowers the over-torque probability of the baseline tool from %s to %s, %s and %s, and the damage probability from %s to %s (Fig. @F:relief@b). The surge "
          "inputs, the wave speed in the hose, the stopping time and the unrelieved fraction, are assumed, and Fig. @F:surgehet@a shows how the over-torque probability follows the surge multiplier: "
          "when the surge is twice the prior the over-torque probability is %s for the baseline tool, %s with the accumulator, and %s for the optimized design of Section @S:opt@."
          % (n(sg_["median_psi"]), pc(sg_["share_of_static"]), n(sg_["p95_psi"]), pc(PRE["gate_12in"]["overtorque"]["p"], 0), pc(R["accumulator"]["0.0"]["overtorque"], 1),
             pc(R["accumulator"]["0.25"]["overtorque"], 1), pc(R["accumulator"]["0.5"]["overtorque"], 1), pc(R["accumulator"]["0.75"]["overtorque"], 1),
             pc(R["accumulator"]["0.0"]["damage"], 2), pc(R["accumulator"]["0.75"]["damage"], 2), pc(R["surge_study"]["baseline"][4]["overtorque"], 0),
             pc(R["surge_study"]["baseline + accumulator 0.75"][4]["overtorque"], 0), pc(R["surge_study"]["optimized allowable|0.75"][4]["overtorque"], 1))))
ssu = R["surge_study"]
ast(all(r["overtorque"] <= rr["overtorque"] + 1e-9 for rr, r in zip(ssu["baseline"], ssu["baseline + accumulator 0.75"])), "accumulator never raises over-torque")
add(("fig", "@FILE:cap@", "Fig. @F:cap@. (a) Distributions of the valve breakaway demand, the stall capability of the baseline tool (limited by the relief valve) and the allowable stem torque over the draws. "
            "(b) Ratio of the peak stall torque to the allowable stem torque; the dotted line marks the exceedance.", 6.6))
add(("fig", "@FILE:relief@", "Fig. @F:relief@. (a) Probability of a safe stroke against the probability of over-torque as the relief setting is varied (labels: multiple of the median breakaway "
            "torque, or fraction of the nominal allowable stem torque), for the two chart bases and without a relief valve. (b) Effect of a hose-side accumulator on the safe stroke, the over-torque and "
            "the stem damage.", 6.6))

# ---------------------------------------------------------------------------------------------- 6.3 creep
add(("h2", "@S:creep@ Creep at the start and at the end of travel"))
CR = R["creep"]


def cr(acc, cs, ce, ns=1, ne=2):
    return [r for r in CR if r["acc"] == acc and r["cs"] == cs and r["ce"] == ce and r["ns"] == ns and r["ne"] == ne][0]


c00, c020, c010, c1010, c2010, c100 = cr(0.0, 0, 0), cr(0.0, 0, 20), cr(0.0, 0, 10), cr(0.0, 10, 10), cr(0.0, 20, 0), cr(0.0, 10, 0)
a00, a020 = cr(0.75, 0, 0), cr(0.75, 0, 20)
add(("p", "A tool whose flow can be turned down is a natural remedy for the surge, which is proportional to the velocity of the water that the stall has to stop. Two creep phases are evaluated for the baseline tool: a slow flow for the first turns of the stroke, which builds torque gradually "
          "against a stuck valve, and a slow flow for the last turns, which brings the tool to the stop slowly. In the model the end creep lowers the flow before the stall, and the start creep lowers it for valves that stall at the start because they do not break free; both cost time, and a "
          "stroke that no longer finishes in 15 minutes is a failure. The opening transient of the supply is not modeled; the slow-opening shut-off is assumed to remove it."))
rows = []
for r in CR:
    if r["acc"] == 0.0 or (r["cs"], r["ce"], r["ns"], r["ne"]) in ((0, 0, 1, 2), (0, 20, 1, 2), (10, 10, 1, 2)):
        rows.append(["%s" % ("none" if r["acc"] == 0 else "0.75"), n(r["cs"]) if r["cs"] else "-", n(r["ce"]) if r["ce"] else "-", "%s + %s" % (n(r["ns"], 1), n(r["ne"], 1)) if (r["cs"] or r["ce"]) else "-",
                     pc(r["safe"], 1), pc(r["overtorque"], 1), pc(r["damage"], 2), pc(r["success"], 1), n(r["t_med"], 1), n(r["volume"])])
add(("table", "Table @T:creep@. Creep at the start and at the end of travel, baseline tool (200 cc, 250:1, 60 gpm, relief at 2 x median), %s draws: flows (gpm), turns at those flows, safe stroke, over-torque, damage, "
              "success, median time of successful strokes (min) and water (L). First column: accumulator fraction." % n(M["n_sweep"]),
     ["Accum.", "Start", "End", "Turns", "Safe", "Over-torque", "Damage", "Success", "Time", "Water"], rows, [0.7, 0.6, 0.6, 0.8, 0.7, 0.9, 0.8, 0.8, 0.6, 0.7], 14))
add(("p", "Creep at the end of travel works. Two turns at 20 gpm lower the over-torque probability from %s to %s and the damage probability from %s to %s, and raise the probability of a safe stroke from %s to %s, at the cost of %s minutes of median stroking time and %s points of success "
          "(strokes that no longer finish in 15 minutes). A slower approach, 10 gpm, lowers the over-torque probability to %s but the safe-stroke probability to %s (success %s). Creep at the start alone does little for the over-torque probability (%s at 20 gpm and %s at 10 gpm, against %s) because in this model "
          "it matters only for valves that do not break free; its practical benefit, a shock-free build-up of torque against a stuck valve, is not captured. The length of the slow phases matters as much as their flow (Fig. @F:creep@c): two and four turns at 10 gpm raise the median time to %s minutes and cut the "
          "success to %s. With the accumulator the gain of the end creep is smaller (over-torque from %s to %s), so the two measures are complementary with diminishing returns."
          % (pc(c00["overtorque"], 1), pc(c020["overtorque"], 1), pc(c00["damage"], 2), pc(c020["damage"], 2), pc(c00["safe"], 1), pc(c020["safe"], 1), n(c020["t_med"] - c00["t_med"], 1), n(100 * (c00["success"] - c020["success"]), 1),
             pc(c010["overtorque"], 1), pc(c010["safe"], 1), pc(c010["success"], 1), pc(c2010["overtorque"], 1), pc(c100["overtorque"], 1), pc(c00["overtorque"], 1), n(cr(0.0, 10, 10, 2, 4)["t_med"], 1), pc(cr(0.0, 10, 10, 2, 4)["success"], 1),
             pc(a00["overtorque"], 1), pc(a020["overtorque"], 1))))
add(("fig", "@FILE:creep@", "Fig. @F:creep@. Creep at the start and at the end of travel, baseline tool. (a) Over-torque probability against the flow during the last two turns, without and with an accumulator. "
            "(b) Probability of a safe stroke (solid) and of success (dashed). (c) Median stroking time and share of strokes finishing in 15 minutes (divided by 10) for slow phases of different flow and length.", 6.8))

# ---------------------------------------------------------------------------------------------- 6.4
add(("h2", "@S:grid@ The design space"))
G = R["grid"]; Ds, Rs = G["D"], G["R"]
gs = G["safe"]; best_ij = max(((i, j) for i in range(len(Ds)) for j in range(len(Rs))), key=lambda t: gs[t[0]][t[1]])
worst = min(gs[i][j] for i in range(len(Ds)) for j in range(len(Rs)))
add(("p", "With the flow limited, the torque scales with $D\\,R$ and the speed falls in the same proportion, so useful designs lie along a ridge of constant $D\\,R$ (Fig. @F:grid@a): %s%% or more of the draws give a safe stroke along the diagonal from 100 cc at 500:1 to 400 cc at 100:1, "
          "and %s%% for the largest products. The over-torque probability rises with $D\\,R$ (Fig. @F:grid@b, from %s%% to %s%% over the grid) because a larger product means a lower relief pressure, and the surge, which is a pressure, becomes a larger fraction of it."
          % (n(100 * min(gs[i][4 - i] for i in range(5))), n(100 * worst), n(100 * min(min(r) for r in G["overtorque"])), n(100 * max(max(r) for r in G["overtorque"])))))
add(("fig", "@FILE:grid@", "Fig. @F:grid@. (a) Probability of a safe stroke and (b) probability of over-torque against motor displacement and gear ratio, for the baseline relief chart "
            "(2 x median) and 60 gpm.", 6.4))

# ---------------------------------------------------------------------------------------------- 6.4
add(("h2", "@S:reserve@ Firewater reserve and the flow limit"))
Q = R["qlimit"]; RV = R["reserve"]
q60 = [r for r in Q if r["q"] == 60][0]; q150 = [r for r in Q if r["q"] == 150][0]
add(("p", "The concept-stage study found that the tool draws more than a quarter of the available source flow in 31%% of the draws. That figure depends on how the source flow is defined and is "
          "%s in the present model, where it is kept for continuity (Table @T:ladder@). The event that matters for safety is different: the tool takes more than the flow a shared source can spare "
          "without cutting its firefighting reserve. Under the assumed spare flows (median 400 gpm for a firewater ring and 200 gpm for a hydrant) this reserve violation occurs in only %s of the draws "
          "at 60 gpm and in %s at 150 gpm, but it is very sensitive to the assumption: if the spare flow is a quarter of the prior it occurs in %s, and if it is a tenth in %s (Fig. @F:flow@c). The adaptive "
          "rule, which lowers the limiter to the spare flow of a shared source, removes the violations by construction and costs success: the safe-stroke probability falls from %s to %s with a quarter "
          "of the spare flow, and to %s with a tenth, where only %s of the strokes finish in 15 minutes. A site that has not measured its spare firewater flow cannot be assured that the tool is "
          "compatible with its firefighting reserve, and the right operating rule is to use a dedicated source for large valves."
          % (pc(q60["interference_v1"], 0), pc(q60["reserve_viol"], 1), pc(q150["reserve_viol"], 1), pc(RV[1]["reserve_viol"], 0), pc(RV[0]["reserve_viol"], 0), pc(RV[1]["safe"], 1),
             pc(RV[1]["safe_adaptive"], 1), pc(RV[0]["safe_adaptive"], 1), pc(RV[0]["time_ok_adaptive"], 0))))
add(("fig", "@FILE:flow@", "Fig. @F:flow@. (a) Probability of a safe stroke and of finishing within 15 minutes against the flow limit. (b) Median water used in a successful stroke against the flow limit. "
            "(c) Probability of violating the firefighting reserve at 60 gpm, and the probability of a safe stroke without and with the adaptive rule, against the spare flow of shared sources (multiple of the prior).", 6.8))

# ---------------------------------------------------------------------------------------------- 6.5
add(("h2", "@S:opt@ Safety-constrained optimization"))
fam = {k: v for k, v in OPT.items() if not k.endswith("creep")}
CRP = {k: v for k, v in OPT.items() if k.endswith("creep")}
fnames = {"allowable|0|creep": "Chart from allowable torque, creep, no accumulator", "median|0|creep": "Chart from median breakaway, creep, no accumulator", "allowable|0.75|creep": "Chart from allowable torque, creep, accumulator 0.75", "median|0.75|creep": "Chart from median breakaway, creep, accumulator 0.75", "allowable|0": "Chart from allowable torque, no accumulator", "median|0": "Chart from median breakaway, no accumulator", "allowable|0.75": "Chart from allowable torque, accumulator 0.75",
          "median|0.75": "Chart from median breakaway, accumulator 0.75"}
rows = []
oos = R["robust"]
rows.append(["Baseline tool", "200", "250", "2.0 x median", "60", "none", pc(B0["success_safe"]["p"], 1), pc(B0["overtorque"]["p"], 1), pc(B0["damage"]["p"], 2), n(B0["volume_median_L"])])
for k in ("allowable|0", "median|0", "allowable|0.75", "median|0.75"):
    d = BEST[k]; o = oos["optimized %s" % k]["out_of_sample"]
    rows.append([fnames[k], n(d["D"]), n(d["R"]), ("%s x allowable" % n(d["mult"], 2)) if k.startswith("allowable") else ("%s x median" % n(d["mult"], 2)), n(d["q"]), "none",
                 pc(o["safe"], 1), pc(o["overtorque"], 1), pc(o["damage"], 2), n(o["volume"])])
for k in ("allowable|0|creep", "median|0|creep", "allowable|0.75|creep", "median|0.75|creep"):
    d = BEST[k]; o = oos["optimized %s" % k]["out_of_sample"]
    crs = "%s / %s" % (n(d["cs"]) if d["cs"] < d["q"] else "-", n(d["ce"]) if d["ce"] < d["q"] else "-")
    rows.append([fnames[k], n(d["D"]), n(d["R"]), ("%s x allowable" % n(d["mult"], 2)) if k.startswith("allowable") else ("%s x median" % n(d["mult"], 2)), n(d["q"]), crs,
                 pc(o["safe"], 1), pc(o["overtorque"], 1), pc(o["damage"], 2), n(o["volume"])])
ast(all(oos["optimized %s" % k]["out_of_sample"]["overtorque"] < 0.012 for k in CRP), "the constraint holds out of sample in the creep families")
ast(all(oos["optimized %s" % k]["out_of_sample"]["overtorque"] < 0.012 for k in fam), "the constraint holds out of sample in every family")
add(("table", "Table @T:designs@. Best design of each family under P(over-torque) <= 1%%, found on %s draws and re-evaluated on %s independent draws (shown). Relief multiple of the allowable stem torque or of the "
              "median breakaway torque; D in cc, flow limit and creep flows (start / end) in gpm; water is the median per successful stroke (L)." % (n(M["n_opt"]), n(M["n"])),
     ["Design", "D", "R", "Relief", "Q", "Creep", "Safe", "Over-torque", "Damage", "Water (L)"], rows, [2.3, 0.45, 0.45, 1.1, 0.45, 0.8, 0.6, 0.8, 0.7, 0.7], 14))
b0, b75 = BEST["allowable|0"], BEST["allowable|0.75"]
o0, o75 = oos["optimized allowable|0"]["out_of_sample"], oos["optimized allowable|0.75"]["out_of_sample"]
add(("p", "A design that satisfies the 1%% constraint exists in every family (%s to %s of the %s designs searched meet it), and the constraint is respected out of sample (Table @T:designs@): the "
          "over-torque probability of the chosen designs, re-evaluated on independent draws, is between %s and %s. The price is the probability of a safe stroke. Without an accumulator the best "
          "design completes a safe stroke in %s of the draws, against %s for the baseline tool, which exceeds the allowable stem torque in %s; with an accumulator that absorbs three quarters of "
          "the surge the best design reaches %s. The baseline tool with the accumulator and the original chart gives %s with %s over-torque, so at the 1%% constraint the safer configuration gives "
          "up %s to %s percentage points of the safe-stroke probability of the baseline against a reduction of the over-torque probability by a factor of about %s. The chosen designs "
          "have a relief setting at about half of the nominal allowable stem torque (%s to %s of it, which is %s to %s times the median breakaway torque), flow limits of %s to %s gpm and a product $D\\,R$ of %s to %s: "
          "lower than the baseline's 50,000. The probability of a safe stroke at this constraint is not sensitive to the exact displacement and ratio along the ridge (Fig. @F:pareto@a)."
          % (n(min(v["n_feasible"] for v in fam.values())), n(max(v["n_feasible"] for v in fam.values())), n(M["designs"]), pc(min(o["overtorque"] for o in [oos["optimized %s" % k]["out_of_sample"] for k in fam]), 1),
             pc(max(o["overtorque"] for o in [oos["optimized %s" % k]["out_of_sample"] for k in fam]), 1), pc(o0["safe"], 1), pc(B0["success_safe"]["p"], 1), pc(B0["overtorque"]["p"], 0),
             pc(o75["safe"], 1), pc(oos["baseline + accumulator 0.75"]["out_of_sample"]["safe"], 1), pc(oos["baseline + accumulator 0.75"]["out_of_sample"]["overtorque"], 1),
             n(100 * (B0["success_safe"]["p"] - o75["safe"]), 1), n(100 * (B0["success_safe"]["p"] - o0["safe"]), 1), n(B0["overtorque"]["p"] / max(o75["overtorque"], 1e-4)),
             n(min(BEST[k]["mult"] for k in fam if k.startswith("allowable")), 2), n(max(BEST[k]["mult"] for k in fam if k.startswith("allowable")), 2),
             n(min(BEST[k]["mult"] for k in fam if k.startswith("allowable")) * 3, 1), n(max(BEST[k]["mult"] for k in fam if k.startswith("allowable")) * 3, 1),
             n(min(BEST[k]["q"] for k in fam)), n(max(BEST[k]["q"] for k in fam)), n(min(BEST[k]["D"] * BEST[k]["R"] for k in fam)), n(max(BEST[k]["D"] * BEST[k]["R"] for k in fam)))))
# creep families
cr0, cr75 = BEST["allowable|0|creep"], BEST["allowable|0.75|creep"]
oc0, oc75 = oos["optimized allowable|0|creep"]["out_of_sample"], oos["optimized allowable|0.75|creep"]["out_of_sample"]
add(("p", "Allowing the creep flows at the start and at the end of travel to be chosen raises the best probability of a safe stroke under the same constraint (Table @T:designs@, out of sample) from %s to %s without an "
          "accumulator and from %s to %s with one. The gain comes from the end of travel: the chosen designs run at %s and %s gpm for the last two turns, which is %s and %s of their flow limit, so the flow that the stall has to stop, and with it the surge, "
          "is a small fraction of the running flow, and the flow limit and the relief chart can be set higher for the same over-torque probability (relief at %s and %s of the allowable stem torque, flow limits of %s and %s gpm). "
          "Without an accumulator the optimizer chooses a very slow approach (about 5 gpm) and pays for it in time (median %s minutes against %s without creep); with an accumulator a moderate one. The start creep chosen, %s and %s gpm, should not be read as an optimum: "
          "in this model it acts only on valves that do not break free, so the objective is nearly flat in it."
          % (pc(o0["safe"], 1), pc(oc0["safe"], 1), pc(o75["safe"], 1), pc(oc75["safe"], 1), n(cr0["ce"]), n(cr75["ce"]), pc(cr0["ce"] / cr0["q"], 0), pc(cr75["ce"] / cr75["q"], 0), n(cr0["mult"], 2), n(cr75["mult"], 2),
             n(cr0["q"]), n(cr75["q"]), n(oc0["t_med"], 1), n(o0["t_med"], 1), n(cr0["cs"]), n(cr75["cs"]))))
# sensitivity of the optimum to the constraint
lims = [0.005, 0.01, 0.02, 0.05]
rowsl = []
for k in ("allowable|0", "allowable|0.75", "allowable|0|creep", "allowable|0.75|creep"):
    row = [fnames[k]]
    for lim in lims:
        f = [r for r in OPT[k]["designs"] if r["overtorque"] <= lim]
        row.append(pc(max(r["safe"] for r in f), 1) if f else "none")
    rowsl.append(row)
add(("p", "The 1%% limit is illustrative, and Table @T:limits@ shows how the best safe-stroke probability found by the search moves with it: for the family with the accumulator it is %s at 0.5%%, %s at 1%%, %s at 2%% and %s at 5%%. "
          "The decision belongs to the operator and the regulator, and the figures give them the exchange rate."
          % tuple(pc(max(r["safe"] for r in fam["allowable|0.75"]["designs"] if r["overtorque"] <= lim), 1) for lim in lims)))
add(("table", "Table @T:limits@. Best probability of a safe stroke among the searched designs (in-sample) as the limit on the over-torque probability is varied.",
     ["Family", "P(over-torque) <= 0.5%", "<= 1%", "<= 2%", "<= 5%"], rowsl, [2.6, 1.3, 1.0, 1.0, 1.0], 16))
# confidence limits of the chosen designs
CI_ = R["ci"]
fam_order = ["allowable|0", "median|0", "allowable|0.75", "median|0.75", "allowable|0|creep", "median|0|creep", "allowable|0.75|creep", "median|0.75|creep"]
rows = []
for k in fam_order:
    d1 = CI_["designs"]["optimized %s" % k]; st = CI_["strict"][k]
    rows.append([fnames[k], "%s%% (%s to %s)" % (n(100 * d1["p"], 2), n(100 * d1["lo"], 2), n(100 * d1["hi"], 2)), pc(oos["optimized %s" % k]["out_of_sample"]["safe"], 1),
                 ("%s%% (%s to %s)" % (n(100 * st["overtorque"], 2), n(100 * st["lo"], 2), n(100 * st["hi"], 2))) if st else "none", pc(st["safe"], 1) if st else "none", n(st["n_feasible"]) if st else "0"])
add(("table", "Table @T:ci@. Over-torque probability with Wilson 95%% limits on %s independent draws, for the best design of each family chosen at an estimated probability of at most 1%% and for the best design chosen so that the upper limit of "
              "the in-sample estimate (%s draws) is at most 1%%; probability of a safe stroke; number of designs that qualify under the strict rule." % (n(M["n"]), n(M["n_opt"])),
     ["Family", "Chosen at estimate <= 1%", "Safe", "Strict rule", "Safe", "Qualifying"], rows, [2.5, 1.5, 0.7, 1.5, 0.7, 0.8], 14))
n_above = sum(1 for k in fam_order if CI_["designs"]["optimized %s" % k]["hi"] > 0.01)
strict_hi = max(CI_["strict"][k]["hi"] for k in fam_order if CI_["strict"][k])
cost = np_cost = [oos["optimized %s" % k]["out_of_sample"]["safe"] - CI_["strict"][k]["safe"] for k in fam_order if CI_["strict"][k]]
add(("p", "On %s independent draws the designs chosen at an estimated 1%% have over-torque probabilities of %s to %s, and the upper 95%% limit exceeds 1%% for %s of the eight (Table @T:ci@): a point estimate near 1%% does not establish compliance with a strict "
          "limit. Under the strict rule every design has an upper limit of at most %s, and the price is %s to %s percentage points of the probability of a safe stroke. A statement of compliance should be made with the strict rule, and with a number of draws chosen for the "
          "margin that is wanted; the limits are Monte Carlo limits for the assumed priors and say nothing about the error of the priors."
          % (n(M["n"]), pc(min(CI_["designs"]["optimized %s" % k]["p"] for k in fam_order), 2), pc(max(CI_["designs"]["optimized %s" % k]["p"] for k in fam_order), 2), n(n_above), pc(strict_hi, 2), n(100 * min(cost), 1), n(100 * max(cost), 1))))
add(("fig", "@FILE:pareto@", "Fig. @F:pareto@. (a) Searched designs (points) and non-dominated sets (lines) in the plane of safe-stroke probability against over-torque probability, for the eight families; "
            "dashed lines are the families with creep, the star is the baseline tool and the dotted line the 1% constraint. (b) Median water per stroke of the designs of the family with the accumulator and the allowable-torque chart.", 6.8))
# class-specific
CS = R["class_specific"]
wts = {"gate_12in": .30, "gate_24in": .25, "butterfly_36in": .15, "plug_16in": .10, "legacy_seized": .20}
kit_mix = sum(w * CS[c]["safe"] for c, w in wts.items() if CS[c])
add(("p", "A single configuration is almost as good as valve-class-specific ones: choosing the displacement, ratio, relief setting and flow limit separately for each class under the same constraint gives a weighted safe-stroke probability of %s against %s for the best single design with the "
          "accumulator (a gain of %s points, part of it the optimism of choosing the best of 500 designs per class). What cannot be shared is the relief setting, which is read from the chart of each class (Supplementary Fig. S2)."
          % (pc(kit_mix, 1), pc(o75["safe"], 1), n(100 * (kit_mix - o75["safe"]), 1))))

# ---------------------------------------------------------------------------------------------- 6.6
add(("h2", "@S:robust@ Robustness to wrong input distributions"))
SC = list(next(iter(oos.values()))["scenarios"])
names = ["baseline (chart 2x median, no accumulator)", "baseline + accumulator 0.75", "optimized allowable|0", "optimized allowable|0.75", "optimized allowable|0.75|creep"]
rows = []
for s_ in SC:
    rows.append([s_] + ["%s / %s" % (pc(oos[nm]["scenarios"][s_]["safe"], 0), pc(oos[nm]["scenarios"][s_]["overtorque"], 1)) for nm in names])
add(("table", "Table @T:robust@. Probability of a safe stroke / probability of over-torque under each assumption shift, for the baseline tool, the baseline with an accumulator, and the best designs of the "
              "allowable-torque families, with and without creep (%s draws each)." % n(2 * M["n_sweep"]),
     ["Assumption shift", "Baseline", "Baseline + accumulator", "Optimized, no accumulator", "Optimized, accumulator", "Optimized, accumulator and creep"], rows, [1.5, 1.0, 1.2, 1.3, 1.3, 1.4], 14))
wc = lambda nm: min(oos[nm]["scenarios"][s_]["safe"] for s_ in SC)
wot = lambda nm: max(oos[nm]["scenarios"][s_]["overtorque"] for s_ in SC)
add(("p", "The optimum is not robust to every wrong prior (Table @T:robust@, Fig. @F:robust@). At the assumed priors the baseline tools have the larger probability of a safe stroke, but they pay for it in over-torque; the optimized designs keep the over-torque probability near "
          "1%% under shifts of the valve torque, the supply, the seizure, the efficiencies and the fouling, because the chart limits the torque whatever the demand, and the safe-stroke probability moves "
          "as the demand moves, for example from %s to %s when the breakaway torques are multiplied by 1.5. One shift breaks the constraint decisively. If the true stem strength is 30%% lower than the data "
          "sheet says, the over-torque probability of the optimized design with the accumulator rises to %s (%s with creep as well), because the chart was computed from the nominal strength; a surge twice the "
          "prior roughly doubles it, to %s, against %s for the baseline tool. With the stems 30%% weaker the order of the designs by safe strokes reverses: the optimized designs then lead, because the baseline tools lose "
          "most of their safe strokes to over-torque. These are the two inputs of which the model knows least, and they are the first things to measure. A chart that is safe against both would have to be lower, at a "
          "cost in the safe-stroke probability: among %s candidate designs with a nominal over-torque probability of at most 2%%, the largest worst-case safe-stroke probability that keeps the worst-case over-torque "
          "probability at or below 3%%, 5%% and 10%% is %s, %s and %s for the family with the accumulator (%s, %s and %s without it)."
          % (pc(oos["optimized allowable|0.75"]["scenarios"]["nominal priors"]["safe"], 0), pc(oos["optimized allowable|0.75"]["scenarios"]["valve torque x1.5"]["safe"], 0),
             pc(oos["optimized allowable|0.75"]["scenarios"]["stem strength x0.7"]["overtorque"], 0), pc(oos["optimized allowable|0.75|creep"]["scenarios"]["stem strength x0.7"]["overtorque"], 0), pc(oos["optimized allowable|0.75"]["scenarios"]["surge x2"]["overtorque"], 1),
             pc(oos["baseline (chart 2x median, no accumulator)"]["scenarios"]["surge x2"]["overtorque"], 0), n(R["robust_select"]["allowable|0.75"]["n_candidates"]),
             *[(pc(R["robust_select"]["allowable|0.75"]["picks"][l]["wc_safe"], 0) if R["robust_select"]["allowable|0.75"]["picks"][l] else "n/a") for l in ("0.03", "0.05", "0.1")],
             *[(pc(R["robust_select"]["allowable|0"]["picks"][l]["wc_safe"], 0) if R["robust_select"]["allowable|0"]["picks"][l] else "n/a") for l in ("0.03", "0.05", "0.1")])))
add(("fig", "@FILE:robust@", "Fig. @F:robust@. Probability of a safe stroke (top) and of over-torque (bottom) under the assumption shifts for the baseline tool, the baseline with an accumulator, and the best "
            "designs found with and without an accumulator. The dotted line marks 1%.", 6.8))
STM = R["stem"]; SC_ = STM["curves"]
cv = SC_["optimized allowable|0.75|creep"]; cv0 = SC_["optimized allowable|0.75"]; cb = SC_["baseline"]
fpick = lambda rows, f: [r for r in rows if abs(r["f"] - f) < 1e-9][0]
DER = STM["derating"]
add(("p", "The strongest limitation of the nominal 1%% constraint is the stem strength, and it deserves a direct statement: the optimized configuration cannot be considered operationally safe without verified stem-strength information. "
          "The over-torque probability of the optimized design with an accumulator and creep is %s when the stems are as strong as the data sheet says, %s when they are 10%% weaker, %s when they are 20%% weaker and %s when they are 30%% weaker (Fig. @F:stem@a); the baseline tool is at %s, %s, %s and %s. "
          "The chart is computed from the nominal strength, so an error in the nominal strength passes straight to the stem. Holding 1%% over-torque when the stems may be weaker than the data sheet by a given factor requires a lower chart "
          "(Table @T:derate@): %s of the allowable stem torque instead of %s when 10%% weaker stems must be tolerated, %s at 20%% and %s at 30%%, and the probability of a safe stroke that remains falls to %s, %s and %s (Fig. @F:stem@b). "
          "Each 10%% of stem strength that is not known therefore costs about %s to %s percentage points of safe strokes. The operating rule that follows is that a relief chart is issued for a valve only with a verified stem strength for that valve, "
          "and that a valve of unknown stem strength is operated with a derated chart, or by another means."
          % (pc(fpick(cv, 1.0)["overtorque"], 1), pc(fpick(cv, 0.9)["overtorque"], 1), pc(fpick(cv, 0.8)["overtorque"], 1), pc(fpick(cv, 0.7)["overtorque"], 0),
             pc(fpick(cb, 1.0)["overtorque"], 0), pc(fpick(cb, 0.9)["overtorque"], 0), pc(fpick(cb, 0.8)["overtorque"], 0), pc(fpick(cb, 0.7)["overtorque"], 0),
             n(DER[1]["mult"], 2), n(DER[0]["mult"], 2), n(DER[2]["mult"], 2), n(DER[3]["mult"], 2), pc(DER[1]["safe"], 0), pc(DER[2]["safe"], 0), pc(DER[3]["safe"], 0),
             n(100 * min(DER[i]["safe"] - DER[i + 1]["safe"] for i in range(3)), 0), n(100 * max(DER[i]["safe"] - DER[i + 1]["safe"] for i in range(3)), 0))))
rows = [[n(r["f"], 1), n(r["mult"], 2), n(r["scale"], 2), pc(r["safe"], 1), pc(r["overtorque"], 2)] for r in DER]
add(("table", "Table @T:derate@. Relief chart (multiple of the nominal allowable stem torque) that keeps the over-torque probability at 1%% when the true stem strength is a factor f of the data-sheet value, for the optimized design with an accumulator and creep "
              "(D = %s cc, R = %s, flow limit %s gpm; nominal chart %s), with the factor by which the nominal chart is lowered and the probability of a safe stroke that remains." % (n(STM["tool"]["D"]), n(STM["tool"]["R"]), n(STM["tool"]["q"]), n(STM["tool"]["mult"], 2)),
     ["Stem strength f", "Chart", "Factor", "Safe stroke", "Over-torque"], rows, [1.4, 1.0, 1.0, 1.2, 1.2], 16))
add(("fig", "@FILE:stem@", "Fig. @F:stem@. (a) Over-torque probability against the true stem strength relative to the data-sheet value (the chart is computed from the data-sheet value), for the baseline tool, the baseline with an accumulator, and the "
            "optimized designs with an accumulator without and with creep; the dotted line is 1%. (b) Probability of a safe stroke and relief chart that keep the over-torque probability at 1% when the stem may be weaker than the data sheet by the factor shown.", 6.8))
H_ = R["hetero"]
h_all, h_med = H_["allowable|0.75"], H_["median|0.75"]
add(("p", "The chart basis matters only when stems are not equally strong relative to the operating torque. With the stem strength proportional to the median breakaway torque (Table @T:inputs@) the two bases are algebraically the same. With allowable torques of 4.0, 3.0, 2.2, 3.5 and 2.0 times "
          "the median breakaway torque for the five classes, the best design with a chart from the median breakaway torque has a safe-stroke probability of %s but an over-torque probability of %s for the worst class (%s), while the chart from the allowable torque reaches %s with a worst class at %s "
          "(Fig. @F:surgehet@b): the data sheet of the stem is part of the information that the chart needs."
          % (pc(h_med["best"]["safe"], 1) if h_med["best"] else "n/a", pc(max(v["overtorque"] for v in h_med["per_class"].values()), 1) if h_med["per_class"] else "n/a",
             NICE[max(h_med["per_class"], key=lambda c: h_med["per_class"][c]["overtorque"])].lower(), pc(h_all["best"]["safe"], 1) if h_all["best"] else "n/a",
             pc(max(v["overtorque"] for v in h_all["per_class"].values()), 1) if h_all["per_class"] else "n/a")))
add(("fig", "@FILE:surgehet@", "Fig. @F:surgehet@. (a) Over-torque probability against a multiplier of the assumed surge, for the baseline tool, the baseline with an accumulator, and the best design "
            "with an accumulator. (b) Over-torque probability of each valve class for the best designs of the two chart bases when the stem strength differs between classes.", 6.8))

# ---------------------------------------------------------------------------------------------- 6.7
add(("h2", "@S:sens@ Sensitivity"))
SE = R["sensitivity"]
top_m = sorted(SE["prcc_margin"], key=lambda k: -abs(SE["prcc_margin"][k]))[:3]
top_p = sorted(SE["prcc_peak_ratio"], key=lambda k: -abs(SE["prcc_peak_ratio"][k]))[:3]
nm_ = {"Ps": "the supply pressure", "elev": "the elevation", "T_break": "the breakaway torque of the valve", "seize": "seizure", "eta_g": "the gearbox efficiency", "eta_m": "the motor efficiency",
       "relief_f": "the relief set-point error", "hose_len": "the hose length", "hose_C": "the hose coefficient", "foul": "the strainer fouling", "f_run": "the running-torque fraction",
       "T_allow": "the allowable stem torque", "Qa": "the source flow capacity", "drop": "the efficiency loss at stall", "class_median": "the valve class", "wave_speed": "the wave speed",
       "stop_time": "the stopping time", "surge_unrelieved": "the unrelieved surge fraction", "relief_override": "the relief override"}
add(("p", "The torque margin of the tool (the logarithm of its stall capability over the breakaway demand) is controlled by %s (partial rank correlation %s; variance-based indices [@Saltelli2010] are a natural extension), %s (%s) and %s (%s); hose length, "
          "the hose coefficient, the fouling and the source capacity have correlations below 0.05 in magnitude, so the hose does not limit the torque margin at these flows. The ratio of the peak stall torque to "
          "the allowable stem torque is controlled by %s (%s), %s (%s) and %s (%s), and it also depends on the hose, through the velocity of the water that the stall has to stop (hose coefficient %s) (Fig. @F:sens@). A measurement programme should therefore start with the stem strength and the breakaway torque of "
          "real valves, and with an instrumented stall test."
          % (nm_[top_m[0]], n(SE["prcc_margin"][top_m[0]], 2), nm_[top_m[1]], n(SE["prcc_margin"][top_m[1]], 2), nm_[top_m[2]], n(SE["prcc_margin"][top_m[2]], 2),
             nm_[top_p[0]], n(SE["prcc_peak_ratio"][top_p[0]], 2), nm_[top_p[1]], n(SE["prcc_peak_ratio"][top_p[1]], 2), nm_[top_p[2]], n(SE["prcc_peak_ratio"][top_p[2]], 2), n(SE["prcc_peak_ratio"]["hose_C"], 2))))
add(("fig", "@FILE:sens@", "Fig. @F:sens@. Partial rank correlation of the inputs with (a) the torque margin ln(T_cap/T_break) and (b) the peak ratio ln(T_peak/T_allow), baseline tool, valve-class mix.", 6.6))
add(("fig", "@FILE:time@", "Fig. @F:time@. (a) Distribution of the stroking time of successful strokes by valve class, baseline tool; the dotted line is the 15-minute limit. "
            "(b) Water used in one successful stroke.", 6.6))

# ---------------------------------------------------------------------------------------------- 6.8
add(("h2", "@S:bench@ Comparison with benchmark tools"))
BM = R["benchmarks"]
bn = [k for k in BM if k not in ("ideal_waterhydraulic", "hydratorque")]
add(("p", "Two benchmarks put the tool in context under the same valve draws. A lossless water-hydraulic tool with the same displacement and ratio, no hose or coupling loss, no leakage and no start-up "
          "loss reaches a success probability of %s, against %s for the baseline: the circuit and efficiency losses cost about %s percentage points of success, and the shortfall of the baseline from "
          "an ideal tool is therefore not in the hydraulics. Three conventional portable operators (assumed rated torque, power, availability and speed) give: %s. The engine-driven pack reaches a higher success probability than the water tool because its rating is higher, not because of any advantage in safety. The conventional operators are capability-limited, with a rated torque that is either too low for the stiff valves or, for the engine-driven pack, "
          "without a torque limiter, so that the rated torque would exceed the allowable stem torque in %s of the draws. These figures rest on assumed ratings and availabilities, not on measured "
          "performance; they show where the torque ceiling of each approach lies and do not support a claim of superiority."
          % (pc(BM["ideal_waterhydraulic"]["success"], 1), pc(BM["hydratorque"]["success"], 1), n(100 * (BM["ideal_waterhydraulic"]["success"] - BM["hydratorque"]["success"]), 1),
             "; ".join("%s: success %s, safe %s" % (k, pc(BM[k]["success"], 0), pc(BM[k]["safe"], 0)) for k in bn), pc(BM[bn[2]]["overtorque"], 0))))
add(("fig", "@FILE:bench@", "Fig. @F:bench@. Success and success without over-torque of the baseline tool, a lossless water-hydraulic tool (no surge model) and three conventional portable "
            "operators described by rated torque, power and availability, on the same valve draws.", 6.6))

Y = R["ypf"]

