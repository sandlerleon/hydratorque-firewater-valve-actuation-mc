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
add(("p", "Three results are specific enough to guide a bench programme, and each is conditional on the assumed priors. First, the safety of the tool is decided at the end of the stroke, not during "
          "it. The tool is strong enough, and the hose and the circuit are not the limiting elements: a lossless tool gains about one percentage point of success. What limits the safe-stroke "
          "probability is the torque that the tool can deliver at stall, which is set by a relief valve whose pressure is low for small valves and which cannot relieve a surge in time. The relief chart "
          "and the surge, not the motor, are the design problem. Second, a chart that is computed from the stem strength, together with a hose-side accumulator, brings the over-torque probability to "
          "1%% at a cost of %s to %s percentage points of safe strokes relative to the baseline; the cost is paid in valves that the tool then cannot break free, and those valves need a higher-pressure "
          "source or another tool. Third, the water budget is a design variable. A stroke uses of the order of a thousand litres, and whether that is acceptable depends on a spare flow that the "
          "operator has to know."
          % (n(100 * (BASE["success_safe"]["p"] - o75["safe"]), 0), n(100 * (BASE["success_safe"]["p"] - o0["safe"]), 0))))
add(("p", "The results suggest the following design hypotheses, to be tested on the bench before they are rules: a relief chart set at about half of the nominal allowable stem torque of the valve; a "
          "hose-side accumulator or an equivalent surge absorber; a flow limit between %s and %s gpm for strokes of 30 to 70 turns, with the adaptive reduction on shared sources; a product of displacement "
          "and gear ratio of about %s to %s; and a dedicated source for the large valves and for any site that has not measured its spare firewater flow. The numbers will move with the priors, and "
          "the robustness analysis shows in which direction: a weaker stem or a larger surge calls for a lower chart."
          % (n(min(BEST[k]["q"] for k in BEST)), n(max(BEST[k]["q"] for k in BEST)), n(round(min(dr) / 500) * 500), n(round(max(dr) / 500) * 500))))
add(("h2", "7.2 Relation to existing devices and what is claimed"))
add(("p", "Existing portable valve operators run on electricity, batteries, gasoline or compressed air; hydrant operating apparatus carries a hose coupler and a drive socket for the hydrant stem [@Jackman1985]; "
          "a hydrant-attached remote-controlled valve opens a flow channel with a pilot-operated piston [@Kolacz2014]; and an oscillatory actuator controls a valve on a fire truck [@Leete1992]. Water-hydraulic motors "
          "are established components [@Yang2015;@Majdic2019], and the pressure surge in water lines is well understood [@Ghidaoui2005]. The contribution claimed here is neither the use of water to turn a motor "
          "nor the surge on stall, but the joint probabilistic treatment of a firewater-powered tool: the safe stroke as a combined event, the surge-aware relief chart, the water and firefighting-reserve "
          "constraints, and the test of the optimum against wrong priors. The comparison with conventional operators (Section 6.8) rests on assumed ratings and availabilities, and the study does not "
          "claim superiority over any of them. A preliminary search of the literature and of patents is not a proof of novelty, and a full prior-art and freedom-to-operate review "
          "would be needed before any claim of that kind."))
add(("h2", "7.3 Deployment constraints"))
add(("p", "Four constraints follow from the setting and are not captured by the numbers above. The tool must not be used on a firewater system in a way that could compromise the reserve it has to "
          "deliver; the study turns this into an operating rule, and the rule is only as good as the knowledge of the spare flow. The reaction torque of the tool must be carried by an anchor: at a peak "
          "stall torque of 3 kN.m and a reaction arm of 0.6 m the arm and the anchor see 5 kN, and a failure of the anchor is a hazard to the operator that the model does not include. Water-filled "
          "equipment freezes, so use in cold regions, such as the Austral Zone of Patagonia named in the industrial challenge [@YPF2026], requires drain-down procedures or an anti-freeze flush, and a mechanical "
          "tool of this kind would have to be assessed as non-electrical equipment for explosive atmospheres [@ISO80079] and under the risk-assessment principles for machinery [@ISO12100] before it is used "
          "in a classified area; the valve itself is subject to its own pressure-class rules [@ASMEB1634]. Finally, the technology readiness of the concept is that of a computational study, "
          "not of a tool: the industrial challenge asks for a solution that is commercially available or at a readiness level of 5 to 9 with proven field reliability [@YPF2026], which this concept does not meet."))

add(("h1", "8. Limitations and future validation"))
add(("p", "The principal limitation is that every input distribution is an assumed prior. No published distribution of breakaway torques of the industrial valves of interest was found; the "
          "surge parameters, the efficiency at stall and the spare flows of firewater sources are assumptions. A larger number of simulations does not compensate for uncertain input distributions, and the "
          "robustness analysis of Section 6.6 is the only protection against that. The model is lumped: the motor, the relief valve and the hose are not simulated as a transient system, the relief valve acts as "
          "an override with sampled overshoot, the hose compliance is represented by a sampled wave speed, and the stem is a single strength with a sampled yield margin. The inputs are independent, although "
          "valve size, age, stem strength and breakaway torque are correlated in reality. The reaction arm, the bearings and the gearbox are not checked against the stall torque. The comparison with "
          "conventional operators uses ratings that are assumed. The model is verified numerically, not validated physically [@Oberkampf2002], and the paper's numbers should not be quoted as field reliability."))
add(("p", "A validation programme that would replace the assumed priors with data has six steps. (i) A survey of breakaway, running and allowable stem torques of the valves to be served, for "
          "the 2 to 16 inch range of the challenge, calibrates the valve classes and the stem strengths. (ii) A bench rig with a torque transducer measures the motor torque and leakage against the pressure "
          "drop and speed, including the loss at start-up, and calibrates the efficiencies. (iii) An instrumented stall test with fast pressure transducers measures the surge, the wave speed and the response of the "
          "relief valve, with and without an accumulator, and calibrates the inputs on which the over-torque probability depends most. (iv) Hydrant and firewater flow tests [@NFPA291] give the spare flows of shared "
          "sources. (v) A field pilot on a range of valves, with a hazard identification, tests the operating procedure. (vi) A hazardous-area assessment closes the certification path."))

add(("h1", "9. Conclusions"))
add(("num", "A simulation of a firewater-powered portable valve operator, with an explicit hydraulic circuit and the surge on stall, shows that a stroke without exceeding the allowable stem torque "
            "occurs in %s of the draws for the baseline tool, against the 80%% success reported by the first-order model; the over-torque probability is %s, not 5%%, and the stem-damage probability is %s. "
            "These are simulation outputs under assumed priors." % (pc(BASE["success_safe"]["p"], 0), pc(BASE["overtorque"]["p"], 0), pc(BASE["damage"]["p"], 1))))
add(("num", "The surge on stall is the main source of over-torque, and it is largest in relative terms for small valves, whose relief pressure is low. A hose-side accumulator lowers the over-torque "
            "probability of the baseline tool from %s to %s." % (pc(R["accumulator"]["0.0"]["overtorque"], 0), pc(R["accumulator"]["0.75"]["overtorque"], 0))))
add(("num", "Under a 1%% limit on the over-torque probability, which is an illustrative constraint, a design exists in every family searched, and it holds out of sample; the cost is %s to %s percentage points of "
            "the safe-stroke probability. A single configuration is almost as good as valve-class-specific ones; the relief chart is what has to be specific."
            % (n(100 * (BASE["success_safe"]["p"] - o75["safe"]), 0), n(100 * (BASE["success_safe"]["p"] - o0["safe"]), 0))))
add(("num", "A stroke uses about %s L of water at the 60 gpm limit; the 50 to 100 L/min of the first-order study is the flow for 1 to 2 rpm, too slow for a 15-minute stroke. The firefighting reserve "
            "is protected only if the spare flow of a shared source is known, and a dedicated source is the safe default for large valves." % n(round(BASE["volume_median_L"], -2))))
add(("num", "The optimum is robust to wrong priors for valve torque, supply, seizure, efficiency and fouling, but not to a weaker stem or a larger surge; the data sheet of the stem and an instrumented "
            "stall test are the first measurements to make."))
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
