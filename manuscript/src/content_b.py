# -*- coding: utf-8 -*-
"""Manuscript, part B: probabilistic methodology, verification and optimization problem (Sections 4-5)."""
from common import *

M = R["meta"]
ST = R["selftest"]

add(("h1", "4. Probabilistic methodology"))
add(("h2", "4.1 Inputs and sampling"))
add(("p", "Every input of the model is a random variable with an assumed distribution (Table @T:inputs@). Three groups are sampled for each trial. The supply: the source type (firewater ring, fire truck, "
          "municipal hydrant) with its static pressure and flow capacity, the hose size and length, the elevation difference, the strainer fouling with a 3% chance of severe fouling, and the spare flow "
          "of shared sources. The valve: a lognormal breakaway torque by valve class, seizure events that multiply the torque by 1.5 to 3, a running torque of 30 to 60% of breakaway (the stem packing alone can add a force that is a sizeable part of the actuation load [@Drago2017]), the number of "
          "handwheel turns to stroke, an allowable stem torque, and the ratio between yield and allowable torque. The tool: motor, volumetric and gearbox efficiencies, the loss of efficiency at "
          "stall, the tolerance and overshoot of the relief valve, and the wave speed, stopping time and unrelieved fraction of the surge. The valve classes are a 12-inch gate valve, a 24-inch gate "
          "valve, a 36-inch butterfly valve, a 16-inch plug valve and a legacy seized valve, weighted 30, 25, 15, 10 and 20% in the reference mix; a separate class represents the 1,500 N.m valve of "
          "the industrial challenge [@YPF2026]."))
add(("p", "Latin-hypercube sampling is used for the design search [@McKay1979;@Helton2003], and plain random sampling for every reported probability. All designs are evaluated on the same random "
          "draws (common random numbers [@Glasserman1992]), so that differences between designs are not blurred by sampling noise. Correlations between inputs are not imposed, which is a limitation; "
          "rank-correlation methods are available if data on correlated inputs are obtained [@Iman1982]. Probabilities are reported with Wilson 95%% intervals, which describe only the Monte Carlo "
          "sampling error of the %s draws of each case. They are not confidence intervals for the performance of a real tool, because the input distributions are assumptions."
          % n(M["n"])))
add(("table", "Table @T:inputs@. Input distributions of the model (all assumed priors; none is a measurement).",
     ["Input", "Distribution", "Basis"],
     [["Supply source", "Firewater ring 50% (N 140, sd 20 psi); fire truck 30% (N 120, sd 25); municipal hydrant 20% (N 60, sd 15); clipped to 20–250 psi", "Assumed"],
      ["Source flow capacity at 20 psi residual", "Lognormal, median 2,000 (ring), 500 (truck), 1,000 (hydrant) gpm; sigma 0.5, 0.4, 0.5", "Assumed"],
      ["Spare flow of a shared source", "Lognormal, median 400 (ring), 200 (hydrant) gpm, sigma 0.6, 0.5; unlimited for a truck", "Assumed"],
      ["Hose", "1.75 in 30%, 2.5 in 50%, 3 in 20%; length uniform 50–400 ft; friction coefficients 15.5, 2.0, 0.8", "Fire-service practice [@Benfer2016]"],
      ["Elevation, fouling", "Elevation N(0, 15 ft); fouling lognormal median 2 psi, sigma 0.8, plus 3% chance of 20–60 psi", "Assumed"],
      ["Breakaway torque", "Lognormal by class: gate 12 in 400 N.m (sigma 0.45); gate 24 in 1,200 (0.50); butterfly 36 in 1,500 (0.45); plug 16 in 800 (0.50); legacy 2,000 (0.60); challenge valve 1,500 (0.35)", "Assumed; no published distribution was found"],
      ["Seizure, running torque", "Probability 5–25% by class, multiplier uniform 1.5–3; running torque 30–60% of breakaway", "Assumed"],
      ["Allowable stem torque", "3 x class median, lognormal sigma 0.25; ratio of yield to allowable uniform 1.3–2.0", "Assumed"],
      ["Efficiencies", "Motor N(0.85, 0.03); gearbox and interface N(0.70, 0.05); volumetric N(0.92, 0.02); loss at stall uniform 0.05–0.20", "Typical ranges; assumed"],
      ["Relief valve", "Set-point tolerance sd 5%; override above the set point uniform 5–25%; unrelieved surge fraction uniform 0–30%", "Assumed"],
      ["Surge", "Wave speed uniform 150–400 m/s; stopping time uniform 0.05–0.5 s", "Assumed [@Ghidaoui2005]"]],
     [1.5, 4.5, 1.6], 16))
add(("h2", "4.2 Verification and its limits"))
add(("p", "The model is verified in five ways, none of which validates its physical assumptions. First, with all six added mechanisms switched off the engine reproduces the concept-stage model "
          "draw for draw (identical outcomes for every valve class). Second, with all random inputs fixed except the valve demand, the simulated breakaway probability agrees with the closed form for "
          "a mixture of lognormal valve classes to within %s (absolute probability) over supply pressures of 40 to 200 psi (Fig. @F:verify@a); the over-torque probability of a relief-limited tool agrees "
          "with the closed form $P(T_{\\rm allow}<\\mu\\,T_{\\rm med})$ to within 0.004. Third, the mechanical output power never exceeds the hydraulic power delivered to the motor (maximum ratio %s), "
          "and the hydraulic power at the tap is never smaller than the power at the motor. Fourth, unit conversions, the hose-friction form, the Joukowsky value, the monotonic behavior of the "
          "outcomes in the supply pressure, the accumulator fraction and the relief setting, and the creep logic (a creep flow above the running flow changes nothing; end creep lowers the surge and adds time; start creep acts only on valves that do not break free; the water of the phases adds up) are checked by automated tests (%s tests in the repository). Fifth, the convergence of the estimates "
          "is checked by batch means: the standard error of the baseline probability of a safe stroke over ten blocks is %s percentage points (Supplementary Fig. S1)."
          % (n(ST["closed_form_max_dev"], 4), n(ST["energy_ratio_max"], 3), "25", n(100 * R["baseline_se"]["success_safe"], 2))))
add(("p", "Numerical verification is distinguished from physical validation. The simulation is consistent with its own assumptions; whether those assumptions describe real valves, hoses, motors "
          "and relief valves can only be decided by measurement [@Oberkampf2002]. The input distributions in particular are not calibrated. For that reason the conclusions are tested against "
          "deliberately wrong distributions (Section 4.3)."))
add(("h2", "4.3 Assumption shifts"))
add(("p", "Eight shifts are applied to the draws, one at a time and then together, to see whether a conclusion survives a wrong prior: breakaway torques multiplied by 1.5; the scatter of the "
          "breakaway torque increased by 0.15 in log units; supply pressure lowered by 30 psi; seizure probabilities doubled; motor and gearbox efficiencies lowered by 0.10; fouling tripled; allowable stem "
          "torque multiplied by 0.7; and a combined stress with all of them at reduced strength. The shifts change the distributions, not the design, so the same design can be evaluated "
          "under each; the worst case over the shifts is a robustness measure [@Beyer2007]."))

add(("h1", "5. Multi-objective optimization"))
add(("p", "The design problem has four variables: the displacement $D$ (60 to 500 cc), the ratio $R$ (60 to 600), the relief multiple $\\mu$ (0.2 to 1.0 of the nominal allowable stem torque, or 0.6 to 4 "
          "times the class median breakaway torque), and the flow limit $Q_{\\rm lim}$ (15 to 100 gpm), and, when creep is allowed, two more: the creep flows at the start and at the end of travel (5 to 60 gpm; a value above the flow limit means no creep), "
          "held for one and two turns. The adaptive reserve rule is applied. Eight families of designs are searched: two relief bases, each "
          "without an accumulator and with an accumulator that absorbs 75% of the surge, each with and without creep. The objectives are to maximize the probability of a safe stroke, to minimize the probability of exceedance "
          "and to minimize the median water used in a stroke. The decision constraint is"))
add(("eq", r"P\left(T_{\rm peak}>T_{\rm allow}\right)\le 0.01", 8))
add(("p", "The limit of 1%% is an illustrative research constraint, not an established acceptable industrial safety limit; an operator or regulator would set its own, and Section @S:opt@ shows how the "
          "result moves with it. Each family is searched with %s Latin-hypercube designs evaluated on %s common draws; the non-dominated set is found by exhaustive comparison [@Marler2004;@Deb2002]. "
          "The best design of a family is the one with the largest probability of a safe stroke among those that meet the constraint. The search is a sampling method, not a proof of "
          "optimality; its purpose is to show the structure of the trade-off. To control the optimizer's curse, the chosen designs are re-evaluated on independent draws (%s draws), and a robust design is chosen "
          "by taking the best candidates and maximizing the worst-case probability of a safe stroke over the assumption shifts, subject to a limit of 2%% on the worst-case over-torque probability."
          % (n(M["designs"]), n(M["n_opt"]), n(M["n"]))))
