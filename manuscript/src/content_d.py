# -*- coding: utf-8 -*-
"""Manuscript, part D: Discussion, limitations and validation, conclusions, declarations and references (Sections 7-9)."""
from common import *

OOS = R["robust"]
BEST = {k: v["best_feasible"] for k, v in OPT.items()}
o0 = OOS["optimized allowable|0"]["out_of_sample"]
o75 = OOS["optimized allowable|0.75"]["out_of_sample"]
dr = [BEST[k]["D"] * BEST[k]["R"] for k in BEST]

add(("h1", "7. Discussion"))
add(("h2", "7.1 What the study says about the design of the tool"))
add(("p", "Three results are specific enough to guide a bench programme, each conditional on the assumed priors. First, the safety of the tool is decided at the end of the stroke, not during it: the hose and the circuit do not limit it (a lossless tool gains about one percentage point of success); "
          "what limits the safe-stroke probability is the torque that the tool delivers at stall, set by a relief valve whose pressure is low for small valves and which cannot relieve a surge in time. The relief chart and the surge, not the motor, are the design problem. "
          "Second, a chart computed from the stem strength, with a hose-side accumulator, brings the over-torque probability to 1%% at a cost of %s to %s percentage points of safe strokes relative to the baseline; a slow approach to the end of travel recovers %s to %s points of it, and the rest is paid in valves "
          "that the tool then cannot break free, which need a higher-pressure source or another tool. Third, the water budget is a design variable: a stroke uses of the order of a thousand litres, and whether that is acceptable depends on a spare flow that the operator has to know."
          % (n(100 * (BASE["success_safe"]["p"] - o75["safe"]), 0), n(100 * (BASE["success_safe"]["p"] - o0["safe"]), 0), n(100 * (OOS["optimized allowable|0.75|creep"]["out_of_sample"]["safe"] - o75["safe"]), 0),
             n(100 * (OOS["optimized allowable|0|creep"]["out_of_sample"]["safe"] - o0["safe"]), 0))))
add(("p", "The results suggest the following design hypotheses, to be tested on the bench before they are rules: a relief chart set at about half of the nominal allowable stem torque of the valve; a "
          "hose-side accumulator or an equivalent surge absorber; a variable flow limiter that creeps for the first turn and the last two turns of the stroke; a flow limit between %s and %s gpm for strokes of 30 to 70 turns, with the adaptive reduction on shared sources; a product of displacement "
          "and gear ratio of about %s to %s; and a dedicated source for the large valves and for any site that has not measured its spare firewater flow. The numbers will move with the priors, and "
          "the robustness analysis shows in which direction: a weaker stem or a larger surge calls for a lower chart."
          % (n(min(BEST[k]["q"] for k in BEST)), n(max(BEST[k]["q"] for k in BEST)), n(round(min(dr) / 500) * 500), n(round(max(dr) / 500) * 500))))
add(("h2", "7.2 Relation to existing devices and what is claimed"))
add(("p", "Existing portable valve operators run on electricity, batteries, gasoline or compressed air; hydrant operating apparatus carries a hose coupler and a drive socket for the hydrant stem [@Jackman1985], a hydrant-attached remote-controlled valve opens a flow channel with a "
          "pilot-operated piston [@Kolacz2014], and an oscillatory actuator controls a valve on a fire truck [@Leete1992]. Water-hydraulic motors [@Yang2015;@Majdic2019] and water hammer [@Ghidaoui2005] are established. The contribution claimed here is neither of these but the joint "
          "probabilistic treatment of a firewater-powered tool: the safe stroke as a combined event, the surge-aware relief chart, the water and firefighting-reserve constraints, and the test of the optimum against wrong priors. The comparison with conventional operators (Section @S:bench@) "
          "rests on assumed ratings, no claim of superiority is made, and a full prior-art and freedom-to-operate review would be needed before any claim of novelty."))
add(("h2", "7.3 Deployment constraints"))
add(("p", "Four constraints follow from the setting and are not captured by the numbers above. The tool must not compromise the firefighting reserve; the model turns this into an operating rule that is only as good as the knowledge of the spare flow. The reaction torque must be carried by an "
          "anchor, whose failure is a hazard to the operator that the model does not include (Section @S:mech@). Water-filled equipment freezes, so use in cold regions, such as the Austral Zone of Patagonia named in the industrial challenge [@YPF2026], needs drain-down procedures or an "
          "anti-freeze flush, and a mechanical tool of this kind would have to be assessed as non-electrical equipment for explosive atmospheres [@ISO80079] and under the risk-assessment principles for machinery [@ISO12100] before use in a classified area; the valve is subject to its own "
          "pressure-class rules [@ASMEB1634]. Finally, the technology readiness of the concept is that of a computational study: the industrial challenge asks for a solution that is commercially available or at a readiness level of 5 to 9 with proven field reliability [@YPF2026], "
          "which this concept does not meet."))

add(("h2", "@S:mech@ Preliminary mechanical feasibility"))
MECH = R["mech"]; mb = MECH["baseline"]; m0 = MECH["optimized allowable|0"]; m75 = MECH["optimized allowable|0.75|creep"]
add(("p", "The operating envelope of Section @S:opt@ is only useful if the loads it implies are mechanically attainable in a portable tool. Table @T:mech@ gives screening estimates for the draws of the model: the stall torque that the tool delivers, the output "
          "torque rating that a planetary gearbox would need (1.5 times the 99.9th percentile of the peak stall torque), the reaction force and the section modulus of a steel reaction arm (yield %s MPa, safety factor %s, arm length %s m), the motor speed and hydraulic power, "
          "the velocity in the hose and the gas volume of an isothermal accumulator that would absorb %s of the kinetic energy of the water column. They are not a design: the arm is a cantilever of one load case, the gearbox rating ignores shock loads and duty, the "
          "accumulator volume ignores the compliance of the hose and the precharge of a real unit, and the dimensions and mass of the assembly cannot be estimated without component data. They define the data to ask of the manufacturers."
          % (n(mb["sigma_y_mpa"]), n(mb["sf"], 1), n(mb["arm_m"], 1), "75%")))
rows = []
for lab, key, fmt in (("Peak stall torque, median (N.m)", "T_peak_p50", 0), ("Peak stall torque, 99th percentile (N.m)", "T_peak_p99", 0), ("Gearbox output rating, 1.5 x 99.9th percentile (N.m)", "gearbox_rating_Nm", 0),
                      ("Reaction force at the arm tip, 99th percentile (kN)", "reaction_kN_p99", 1), ("Arm section modulus, 99th percentile (cm3)", "arm_Z_cm3_p99", 0),
                      ("Motor speed at the flow limit (rpm)", "motor_rpm_p50", 0), ("Hydraulic power at the motor, 95th percentile (kW)", "motor_kW_p95", 1),
                      ("Velocity in the hose, 95th percentile (m/s)", "hose_v_p95", 1), ("Accumulator gas volume, median (L)", "accumulator_gas_L_p50", 1), ("Accumulator gas volume, 95th percentile (L)", "accumulator_gas_L_p95", 1),
                      ("Accumulator gas volume, 99th percentile (L)", "accumulator_gas_L_p99", 1)):
    rows.append([lab] + [n(m[key], fmt) for m in (mb, m0, m75)])
add(("table", "Table @T:mech@. Preliminary mechanical loads for the baseline tool (D = %s cc, R = %s), the best design without an accumulator or creep (D = %s cc, R = %s) and the best design with an accumulator and creep (D = %s cc, R = %s); "
              "%s draws, valve-class mix." % (n(mb["tool"]["D"]), n(mb["tool"]["R"]), n(m0["tool"]["D"]), n(m0["tool"]["R"]), n(m75["tool"]["D"]), n(m75["tool"]["R"]), n(100000)),
     ["Quantity", "Baseline", "Best, no accumulator", "Best, accumulator and creep"], rows, [3.3, 0.9, 1.3, 1.5], 15))
spd = lambda row: row["q"] * 3785.41 / row["D"]
capped = {}
for cap in (1500, 3000):
    capped[cap] = {k: max([r for r in OPT[k]["designs"] if r["overtorque"] <= 0.01 and spd(r) <= cap], key=lambda r: r["safe"], default=None) for k in ("allowable|0.75", "allowable|0.75|creep")}
add(("p", "Four observations follow. The stall torque is of the order of 1.5 to 5 kN.m, so the gearbox must be rated for %s to %s N.m at the output and the reaction arm must carry %s to %s kN at %s m, which is a modest steel section (a section modulus of %s to %s cm3 at the 99th percentile); "
          "the optimized designs lower these loads by %s to %s because their relief setting is lower. The accumulator is of moderate size: a gas volume of %s L at the median and %s L at the 95th percentile for the best design with creep, and %s L for the baseline, "
          "volumes that a portable assembly can plausibly carry, to be confirmed with manufacturers. The search placed no limit on the motor speed, and the best designs with creep drive a %s cc motor at about %s rpm at the flow limit, which may exceed what a water-hydraulic motor can sustain; "
          "restricting the motor speed at the flow limit to 3,000 rpm lowers the best probability of a safe stroke found in the search (in-sample) from %s to %s for the family with an accumulator and creep, and restricting it to 1,500 rpm to %s. "
          "Finally, the velocity of the water in the hose reaches %s m/s at the 95th percentile at the largest flow limits, which would favor the larger hose sizes."
          % (n(min(m["gearbox_rating_Nm"] for m in (m0, m75))), n(mb["gearbox_rating_Nm"]), n(min(m["reaction_kN_p99"] for m in (m0, m75)), 1), n(mb["reaction_kN_p99"], 1), n(mb["arm_m"], 1),
             n(min(m["arm_Z_cm3_p99"] for m in (m0, m75))), n(mb["arm_Z_cm3_p99"]), pc(1 - m75["T_peak_p99"] / mb["T_peak_p99"], 0), pc(1 - m0["T_peak_p99"] / mb["T_peak_p99"], 0),
             n(m75["accumulator_gas_L_p50"], 1), n(m75["accumulator_gas_L_p95"], 1), n(mb["accumulator_gas_L_p95"], 1), n(m75["tool"]["D"]), n(m75["motor_rpm_p50"], -2 if False else 0),
             pc(BEST["allowable|0.75|creep"]["safe"], 1), pc(capped[3000]["allowable|0.75|creep"]["safe"], 1) if capped[3000]["allowable|0.75|creep"] else "none",
             pc(capped[1500]["allowable|0.75|creep"]["safe"], 1) if capped[1500]["allowable|0.75|creep"] else "none", n(m75["hose_v_p95"], 1))))
add(("h1", "8. Limitations and future validation"))
add(("p", "The principal limitation is that every input distribution is an assumed prior: no published distribution of breakaway torques of the valves of interest was found, and the surge parameters, the efficiency at stall and the spare flows of firewater sources are assumptions. A larger number "
          "of simulations does not compensate for uncertain priors; Sections @S:shifts@ and @S:robust@ are the only protection. The model is lumped: the relief valve acts as an override with sampled overshoot, the hose compliance is a sampled wave speed, and the stem is a single strength with a sampled yield "
          "margin. The inputs are independent although valve size, age, stem strength and breakaway torque are correlated. The surge model is a screening approximation, checked against classical results and a transient simulation of its own assumptions (Section @S:moc@) but not against a measured stall "
          "transient; the mechanical loads of Section @S:mech@ are screening estimates, and the search placed no limit on motor speed. The model is verified numerically, not validated physically [@Oberkampf2002]; its numbers should not be quoted as field reliability."))
add(("p", "A validation programme that would replace the assumed priors has six steps. (i) A survey of breakaway, running and allowable stem torques of the valves to be served (2 to 16 inches) calibrates the valve classes and the stem strengths. (ii) A bench rig with a torque transducer measures "
          "motor torque and leakage against pressure drop and speed, including the loss at start-up. (iii) An instrumented stall test with fast pressure transducers measures the surge, the wave speed and the response of the relief valve, with and without an accumulator and creep. "
          "(iv) Hydrant and firewater flow tests [@NFPA291] give the spare flows of shared sources. (v) A field pilot with a hazard identification tests the operating procedure. (vi) A hazardous-area assessment closes the certification path."))

add(("h1", "9. Conclusions"))
add(("num", "A simulation of a firewater-powered portable valve operator, with an explicit hydraulic circuit and the surge on stall, shows that a stroke without exceeding the allowable stem torque "
            "occurs in %s of the draws for the baseline tool, against the 80%% success reported by the first-order model; the over-torque probability is %s, not 5%%, and the stem-damage probability is %s. "
            "These are simulation outputs under assumed priors." % (pc(BASE["success_safe"]["p"], 0), pc(BASE["overtorque"]["p"], 0), pc(BASE["damage"]["p"], 1))))
add(("num", "The surge on stall is the main source of over-torque, and it is largest in relative terms for small valves, whose relief pressure is low. A hose-side accumulator lowers the over-torque "
            "probability of the baseline tool from %s to %s, and a slow creep flow for the last two turns of the stroke lowers it from %s to %s (two turns at 20 gpm), at a cost of about %s minutes of stroking time."
            % (pc(R["accumulator"]["0.0"]["overtorque"], 0), pc(R["accumulator"]["0.75"]["overtorque"], 0), pc([r for r in R["creep"] if r["acc"] == 0 and r["cs"] == 0 and r["ce"] == 0][0]["overtorque"], 0),
               pc([r for r in R["creep"] if r["acc"] == 0 and r["cs"] == 0 and r["ce"] == 20 and r["ns"] == 1][0]["overtorque"], 0),
               n([r for r in R["creep"] if r["acc"] == 0 and r["cs"] == 0 and r["ce"] == 20 and r["ns"] == 1][0]["t_med"] - [r for r in R["creep"] if r["acc"] == 0 and r["cs"] == 0 and r["ce"] == 0][0]["t_med"], 1))))
add(("num", "Under a 1%% limit on the over-torque probability, which is an illustrative constraint, a design exists in every family searched, and it holds out of sample; the cost is %s to %s percentage points of "
            "the safe-stroke probability. A single configuration is almost as good as valve-class-specific ones; the relief chart is what has to be specific."
            % (n(100 * (BASE["success_safe"]["p"] - o75["safe"]), 0), n(100 * (BASE["success_safe"]["p"] - o0["safe"]), 0))))
add(("num", "A stroke uses about %s L of water at the 60 gpm limit; the 50 to 100 L/min of the first-order study is the flow for 1 to 2 rpm, too slow for a 15-minute stroke. The firefighting reserve "
            "is protected only if the spare flow of a shared source is known, and a dedicated source is the safe default for large valves." % n(round(BASE["volume_median_L"], -2))))

add(("num", "The surge relations of the model reproduce the classical Joukowsky and Michaud results and are conservative in %s of random transient cases, but only for a relief valve that responds within about 0.1 s; they are verified, not validated, and an instrumented stall test is "
            "the experiment that the model needs." % pc(R["moc"]["compare"]["model_ge_moc"], 0)))
add(("num", "The optimized configuration cannot be considered operationally safe without verified stem-strength information: a stem 10%% weaker than the data sheet raises the over-torque probability to %s, and 30%% weaker to %s; the over-torque probability of a design chosen at an "
            "estimated 1%% is %s to %s with upper 95%% limits up to %s, and a strict compliance rule costs %s to %s percentage points of safe strokes."
            % (pc([r for r in R["stem"]["curves"]["optimized allowable|0.75|creep"] if r["f"] == 0.9][0]["overtorque"], 1), pc([r for r in R["stem"]["curves"]["optimized allowable|0.75|creep"] if r["f"] == 0.7][0]["overtorque"], 0),
               pc(min(v["p"] for k, v in R["ci"]["designs"].items() if k.startswith("optimized")), 2), pc(max(v["p"] for k, v in R["ci"]["designs"].items() if k.startswith("optimized")), 2),
               pc(max(v["hi"] for k, v in R["ci"]["designs"].items() if k.startswith("optimized")), 2),
               n(100 * min(OOS["optimized %s" % k]["out_of_sample"]["safe"] - R["ci"]["strict"][k]["safe"] for k in R["ci"]["strict"] if R["ci"]["strict"][k]), 1),
               n(100 * max(OOS["optimized %s" % k]["out_of_sample"]["safe"] - R["ci"]["strict"][k]["safe"] for k in R["ci"]["strict"] if R["ci"]["strict"][k]), 1))))
add(("num", "The chart basis matters only if stem strength differs between valve classes relative to their operating torque, in which case a chart from the allowable stem torque is required."))

add(("h1", "Declarations"))
add(("p0", "Funding. The work received no external funding. It was carried out by the author as an independent researcher, with no grant, contract or award; the industrial challenge that motivated it "
           "states no prize, and the concept was prepared at the author's own expense."))
add(("p0", "Competing interests. The author has no financial or non-financial interests that are directly or indirectly related to the work. The concept was prepared by the author as a white paper "
           "for an industrial scouting challenge [@YPF2026]; no patent has been filed and no contract or payment has resulted."))
add(("p0", "Availability of data and material. All results are generated by the code archived at https://doi.org/%s (all versions) and available at %s; the manuscript and its Supplementary "
           "Information are archived at https://doi.org/%s (all versions). No measured data were used." % (DOIS["code_concept"].replace("10.5281/", "10.5281/"), GITHUB, DOIS["paper_concept"])))
add(("p0", "Code availability. The simulation (HydraTorque_MC.py, version %s, numpy and matplotlib only), its automated tests and the figure and manuscript builders are in the repository; "
           "python HydraTorque_MC.py --reproduce regenerates every number and figure (seed %s)." % (VERSION, R["meta"]["seed"])))
add(("p0", "Author contributions. The author is the sole contributor."))
add(("p0", "Use of generative AI. During the preparation of this work the author used a generative AI tool (Claude, Anthropic) for code development (the extended hydraulic model, the optimization "
           "and the automated tests), for the analysis scripts and for drafting and editing the text. After using the tool, the author reviewed and edited the content and takes full responsibility "
           "for the content of the publication."))
add(("refs",))
