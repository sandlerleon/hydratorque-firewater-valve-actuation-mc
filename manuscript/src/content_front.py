# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, abstract, keywords."""
from common import *

M = R["meta"]
OOS = R["robust"]
b0 = BASE
o0 = OOS["optimized allowable|0"]["out_of_sample"]
o75 = OOS["optimized allowable|0.75"]["out_of_sample"]
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: leon.sandler@alumni.swinburne.edu"))
add(("blank",))
add(("h1", "Abstract"))
add(("p0", "Large valves must sometimes be operated when plant power, air and hydraulic supply are lost, and almost every hazardous facility already owns a pressurized, regularly inspected source of "
           "hydraulic power: its firewater system. This study asks whether a portable water-hydraulic operator driven through a fire hose can stroke seized or stiff valves without overloading the stem or taking "
           "the water that firefighting needs, and which design and operating rules make that likely. A Monte Carlo model with an explicit hydraulic circuit, motor leakage, a relief valve and the surge on stall "
           "is evaluated on %s draws, with every added mechanism switchable so that the earlier first-order model is recovered exactly. Under assumed input distributions, a baseline tool (200 cc, 250:1, 60 gpm) completes the stroke in %s "
           "of the draws but gives a stroke without exceeding the allowable stem torque in only %s, because a median surge of %s psi accompanies the stall; the stroke needs about %s L of water, not "
           "the 50 to 100 L/min first assumed. A hose-side accumulator and a relief chart set from the stem strength reduce the over-torque probability to 1%% at a cost of %s to %s percentage points of safe strokes. "
           "The optimum holds out of sample but not under a weaker stem or a larger surge, and the firefighting reserve is protected only if the spare flow of the source is known. "
           "The results are simulation outputs under assumed priors, not measurements; the model is verified numerically, not validated physically."
           % (n(M["n"]), pc(b0["success"]["p"], 0), pc(b0["success_safe"]["p"], 0), n(R["surge"]["median_psi"]), n(round(b0["volume_median_L"], -2)),
              n(100 * (b0["success_safe"]["p"] - o75["safe"]), 0), n(100 * (b0["success_safe"]["p"] - o0["safe"]), 0))))
add(("h1", "Keywords"))
add(("p0", "Water hydraulics; Valve actuation; Firewater; Monte Carlo simulation; Multi-objective optimization; Emergency response"))
