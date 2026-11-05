# -*- coding: utf-8 -*-
"""Supplementary Information."""
from common import *
M = R["meta"]

adds(("title", "Supplementary Information for: " + TITLE))
adds(("author", "Leon Sandler"))
adds(("small", "Independent Researcher, Northbrook, Illinois, USA · leon.sandler@alumni.swinburne.edu"))
adds(("blank",))
adds(("h1", "S1. Reproduction"))
adds(("p0", "Software: HydraTorque_MC.py version %s (numpy and matplotlib only), archived at https://doi.org/%s. Commands: python HydraTorque_MC.py --demo (verification suite, about one minute); "
            "python -m pytest -q tests (automated checks); python HydraTorque_MC.py --reproduce --outdir results (every result of the paper, seed %s, about 12 minutes); python make_figures.py "
            "(figures); python manuscript/src/build_manuscript.py (manuscript and this document); python HydraTorque_MC.py --legacy (the concept-stage study, unchanged, in legacy_v1/)."
            % (VERSION, DOIS["code_concept"], R["meta"]["seed"])))
adds(("h1", "S2. Model switches and defaults"))
adds(("table", "Table S1. The six mechanisms of model 2 and the concept-stage behavior they replace.",
      ["Switch", "Model 2 (on)", "Concept-stage model (off)"],
      [["flow_supply", "Source pressure falls with flow, p_s - (p_s - 20 psi)(Q/Q_a)^1.85", "Constant supply pressure"],
       ["foul_flow", "Strainer and fouling loss proportional to Q^2 (sampled value at 60 gpm)", "Constant loss in psi"],
       ["back", "Exhaust-hose back-pressure, 2.0 (Q/100)^2 (L_d/100) psi", "None"],
       ["start_eff", "Breakaway and stall efficiency lower than running efficiency by 0.05 to 0.20", "Same efficiency"],
       ["leak", "Motor leakage proportional to the pressure drop", "Constant volumetric factor"],
       ["surge", "Joukowsky surge on stall with relief override and unrelieved fraction", "Stall at the relief pressure, no surge"]],
      [1.2, 3.4, 2.0], 16))
adds(("h1", "S3. Water, flow limit and reserve"))
rows = [[n(r["q"]), pc(r["success"], 1), pc(r["safe"], 1), pc(r["time_ok"], 1), pc(r["interference_v1"], 1), pc(r["reserve_viol"], 2), pc(r["safe_adaptive"], 1), n(r["volume_median_L"])] for r in R["qlimit"]]
adds(("table", "Table S2. Flow-limit sweep for the baseline tool (%s draws): success, safe stroke, stroke within 15 minutes, interference (v1 metric), reserve violation, safe stroke with the adaptive rule and "
               "median water per successful stroke." % n(M["n_sweep"]),
      ["Limit (gpm)", "Success", "Safe stroke", "In time", "Interference v1", "Reserve violated", "Safe, adaptive", "Water (L)"], rows, [0.9, 0.8, 0.9, 0.8, 1.0, 1.0, 1.0, 0.8], 16))
rows = [[n(r["mult"], 2), pc(r["reserve_viol"], 1), pc(r["safe"], 1), pc(r["safe_adaptive"], 1), pc(r["time_ok_adaptive"], 1)] for r in R["reserve"]]
adds(("table", "Table S3. Spare flow of shared sources as a multiple of the prior (60 gpm baseline).", ["Spare-flow multiple", "Reserve violated", "Safe stroke, no rule", "Safe stroke, adaptive", "In time, adaptive"],
      rows, [1.4, 1.2, 1.4, 1.4, 1.3], 16))
adds(("h1", "S4. Surge, accumulator and chart"))
rows = []
for nm, rs in R["surge_study"].items():
    for r in rs:
        rows.append([nm, n(r["mult"], 1), pc(r["overtorque"], 1), pc(r["damage"], 2), pc(r["safe"], 1)])
adds(("table", "Table S4. Over-torque, damage and safe stroke against the surge multiplier (0 = no surge).", ["Tool", "Surge multiplier", "Over-torque", "Damage", "Safe stroke"], rows, [2.4, 1.2, 1.0, 1.0, 1.0], 15))
rows = []
for basis in ("median", "allowable"):
    for r in R["relief"][basis]:
        rows.append([basis, n(r["mult"], 2), pc(r["success"], 1), pc(r["safe"], 1), pc(r["overtorque"], 1), pc(r["damage"], 2)])
adds(("table", "Table S5. Relief-setting sweep, baseline tool (chart multiple of the class median breakaway torque, or of the nominal allowable stem torque).",
      ["Basis", "Multiple", "Success", "Safe stroke", "Over-torque", "Damage"], rows, [1.2, 1.0, 1.0, 1.0, 1.0, 1.0], 15))
adds(("h1", "S5. Optimization details"))
rows = []
for k, v in OPT.items():
    bf = v["best_feasible"]
    rows.append([k, n(v["n_feasible"]), n(len(v["pareto"])), n(bf["D"]), n(bf["R"]), n(bf["mult"], 2), n(bf["q"]), pc(bf["safe"], 1), pc(bf["overtorque"], 2), n(bf["volume"])])
adds(("table", "Table S6. Search results by family (basis|accumulator fraction): feasible designs under the 1% constraint, size of the non-dominated set, and the best feasible design (in-sample).",
      ["Family", "Feasible", "Non-dominated", "D", "R", "Relief", "Q limit", "Safe", "Over-torque", "Water (L)"], rows, [1.3, 0.7, 0.9, 0.5, 0.5, 0.6, 0.6, 0.6, 0.8, 0.7], 15))
rows = []
for c, d in R["class_specific"].items():
    rows.append([c, n(d["D"]), n(d["R"]), n(d["mult"], 2), n(d["q"]), pc(d["safe"], 1), pc(d["overtorque"], 2)] if d else [c, "none", "", "", "", "", ""])
adds(("table", "Table S7. Best design for each valve class separately (allowable-torque chart, accumulator 0.75, P(over-torque) <= 1%).", ["Class", "D", "R", "Relief", "Q limit", "Safe", "Over-torque"], rows,
      [1.6, 0.7, 0.7, 0.8, 0.8, 0.8, 1.0], 16))
rows = []
for k, v in R["robust_select"].items():
    for lim, pk in v["picks"].items():
        rows.append([k, "%g%%" % (100 * float(lim)), n(pk["D"]), n(pk["R"]), n(pk["mult"], 2), n(pk["q"]), pc(pk["wc_safe"], 1), pc(pk["wc_ot"], 1)] if pk else [k, "%g%%" % (100 * float(lim)), "none", "", "", "", "", ""])
adds(("table", "Table S8. Robust selection: for each limit on the worst-case over-torque probability over the assumption shifts, the candidate with the largest worst-case safe-stroke probability.",
      ["Family", "Worst-case limit", "D", "R", "Relief", "Q limit", "Worst-case safe", "Worst-case over-torque"], rows, [1.2, 1.0, 0.6, 0.6, 0.7, 0.7, 1.0, 1.2], 15))
adds(("h1", "S6. Valve classes with unequal stem strength"))
rows = []
for k, v in R["hetero"].items():
    if v["per_class"]:
        rows.append([k, pc(v["best"]["safe"], 1)] + [pc(v["per_class"][c]["overtorque"], 1) for c in ("gate_12in", "gate_24in", "butterfly_36in", "plug_16in", "legacy_seized")])
adds(("table", "Table S9. Best design of each chart basis (accumulator 0.75, constraint on the mix) when the allowable stem torques are 4.0, 3.0, 2.2, 3.5 and 2.0 times the class median breakaway torque; "
               "over-torque probability by class.", ["Family", "Safe stroke (mix)", "Gate 12 in", "Gate 24 in", "Butterfly 36 in", "Plug 16 in", "Legacy seized"], rows, [1.3, 1.1, 0.9, 0.9, 1.0, 0.9, 1.0], 15))
adds(("fig", "FigS1_convergence.png", "Fig. S1. Convergence of the running estimate of the probability of a safe stroke with the number of samples (baseline tool).", 5.0))
adds(("fig", "FigS2_kit.png", "Fig. S2. Probability of a safe stroke by valve class for five displacement and ratio pairs on the ridge, baseline relief chart and flow limit.", 6.2))
adds(("h1", "S7. Challenge valve and robustness of all designs"))
rows = [[k, pc(v["success"]["p"], 1), pc(v["success_safe"]["p"], 1), pc(v["overtorque"]["p"], 2), pc(v["damage"]["p"], 3)] for k, v in R["ypf"].items()]
adds(("table", "Table S10. The 1,500 N.m challenge valve class (lognormal, sigma 0.35, 10% seizure), all designs evaluated.", ["Design", "Success", "Safe stroke", "Over-torque", "Damage"], rows, [3.0, 0.9, 0.9, 0.9, 0.9], 15))
SC = list(next(iter(R["robust"].values()))["scenarios"])
rows = []
for dn, v in R["robust"].items():
    rows.append([dn, pc(v["out_of_sample"]["safe"], 1), pc(v["out_of_sample"]["overtorque"], 2), pc(min(v["scenarios"][s]["safe"] for s in SC), 0), pc(max(v["scenarios"][s]["overtorque"] for s in SC), 1)])
adds(("table", "Table S11. All designs: out-of-sample safe stroke and over-torque, and the worst case over the assumption shifts.",
      ["Design", "Safe (out of sample)", "Over-torque (o.o.s.)", "Worst-case safe", "Worst-case over-torque"], rows, [3.1, 1.0, 1.0, 1.0, 1.1], 15))
adds(("refs",))
