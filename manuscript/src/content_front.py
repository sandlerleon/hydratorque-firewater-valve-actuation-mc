# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, abstract, keywords."""
from common import *

M = R["meta"]
OOS = R["robust"]
b0 = BASE
o0 = OOS["optimized allowable|0"]["out_of_sample"]
o75 = OOS["optimized allowable|0.75"]["out_of_sample"]
oc0 = OOS["optimized allowable|0|creep"]["out_of_sample"]
oc75 = OOS["optimized allowable|0.75|creep"]["out_of_sample"]
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: leon.sandler@alumni.swinburne.edu"))
add(("blank",))
add(("h1", "Abstract"))
add(("p0", "Almost every hazardous facility owns a pressurized, regularly inspected source of hydraulic power: its firewater system. This study asks whether a portable water-hydraulic operator driven through a fire hose can stroke "
           "seized or stiff valves without overloading the stem or taking the water that firefighting needs, and which design and operating rules make that likely. A Monte Carlo model with an explicit hydraulic circuit, motor leakage, "
           "a relief valve and the surge on stall is evaluated on %s draws; every added mechanism can be switched off, recovering the earlier first-order model exactly. Under assumed input distributions a baseline tool "
           "(200 cc, 250:1, 60 gpm) completes the stroke in %s of the draws but without exceeding the allowable stem torque in only %s, because a median surge of %s psi accompanies the stall; a stroke needs about %s L of water. "
           "A hose-side accumulator and a relief chart set from the stem strength reduce the over-torque probability to 1%% (motor speed at most 3,000 rpm) at a cost of %s to %s percentage points of safe strokes, of which a slow creep flow at the start and end of travel recovers %s to %s. "
           "The surge model reproduces classical water-hammer results. The optimum holds out of sample but not under a stem 30%% weaker than its data sheet (%s over-torque), "
           "and the firefighting reserve is protected only if the spare flow of the source is known. The results are simulation outputs under assumed priors, not measurements."
           % (n(M["n"]), pc(b0["success"]["p"], 0), pc(b0["success_safe"]["p"], 0), n(R["surge"]["median_psi"]), n(round(b0["volume_median_L"], -2)),
              n(100 * (b0["success_safe"]["p"] - o75["safe"]), 0), n(100 * (b0["success_safe"]["p"] - o0["safe"]), 0), n(100 * (oc75["safe"] - o75["safe"]), 0), n(100 * (oc0["safe"] - o0["safe"]), 0),
              pc([r for r in R["stem"]["curves"]["optimized allowable|0.75|creep"] if r["f"] == 0.7][0]["overtorque"], 0))))
add(("h1", "Keywords"))
add(("p0", "Water hydraulics; Valve actuation; Firewater; Monte Carlo simulation; Multi-objective optimization; Emergency response"))
