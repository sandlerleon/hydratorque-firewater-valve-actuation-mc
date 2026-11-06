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
add(("p", "The model is verified in five ways, none of which validates its physical assumptions. First, with all six added mechanisms switched off the engine reproduces the concept-stage model draw for draw. Second, with all random inputs fixed except the valve demand, "
          "the simulated breakaway probability agrees with the closed form for a mixture of lognormal valve classes to within %s over supply pressures of 40 to 200 psi (Fig. @F:verify@a), and the over-torque probability of a relief-limited tool agrees with its closed form to within 0.004. "
          "Third, the mechanical output power never exceeds the hydraulic power at the motor (maximum ratio %s). Fourth, %s automated tests check unit conversions, the hose-friction form, the Joukowsky value, monotonic behavior in the supply pressure, the accumulator and the relief setting, "
          "and the creep logic. Fifth, convergence is checked by batch means: the standard error of the baseline probability of a safe stroke over ten blocks is %s percentage points (Supplementary Fig. S1)."
          % (n(ST["closed_form_max_dev"], 4), n(ST["energy_ratio_max"], 3), "30", n(100 * R["baseline_se"]["success_safe"], 2))))
add(("p", "Numerical verification is distinguished from physical validation. The simulation is consistent with its own assumptions; whether those assumptions describe real valves, hoses, motors "
          "and relief valves can only be decided by measurement [@Oberkampf2002]. The input distributions in particular are not calibrated. For that reason the conclusions are tested against "
          "deliberately wrong distributions (Section @S:shifts@)."))
add(("h2", "@S:moc@ Check of the surge model against a transient simulation"))
MC = R["moc"]; CMP = MC["compare"]; RRS = MC["relief_response"]
add(("p", "The surge relations of Eqs. (6) and (7) are classical, but the model applies them to an unusual system: a compliant hose between a flow-limited source and a stalling motor with a fast relief valve. They are therefore checked against a one-dimensional "
          "transient simulation of the hose by the method of characteristics [@Ghidaoui2005], with a source behind a resistance (the flow limiter), a motor end that stops linearly in time, and a relief valve that opens linearly over a response time and passes the running flow at its override "
          "pressure. It omits friction, hose-wall dynamics, cavitation, motor inertia and the true characteristic of a relief valve."))
add(("p", "Three comparisons are made (Fig. @F:moc@). First, the solver reproduces the classical results: the Joukowsky surge for an instantaneous stop (%s, %s and %s psi for wave speeds of 150, 250 and 400 m/s in a 2.5-inch hose at 60 gpm), the Michaud relation "
          "for slow stops, and the reduction factor of Eq. (6) for short stops. Second, for %s random combinations of hose, flow, relief setting, stopping time and relief response time, the peak pressure of the screening model is at or above the simulated peak in %s of the cases, "
          "with a median ratio of %s. Third, the unrelieved fraction $\\kappa$ implied by the simulation is below the upper bound of the prior (0.3) for relief valves that respond within 0.1 s (95th percentile %s), but not for slower ones: at 0.3 s the 95th percentile is %s and %s of the "
          "cases exceed the bound. The response time of the relief valve is therefore a requirement of the design: the results of Section @S:opt@ hold only for a relief valve that responds within about 0.1 s."
          % (n(MC["classical"][0]["moc"], 1), n(MC["classical"][1]["moc"], 1), n(MC["classical"][2]["moc"], 1), n(CMP["n"]), pc(CMP["model_ge_moc"], 0), n(CMP["median_ratio"], 2), n(RRS[2]["p95"], 2), n(RRS[3]["p95"], 2), pc(RRS[3]["share_above_prior"], 0))))
add(("p", "The check compares the model's relations with a more detailed model of the same physics; it is not an experimental validation. No experimental record of a stall surge in a fire hose behind a water-hydraulic motor was found in a search that was not exhaustive, "
          "so the surge model is a screening approximation that is verified, not validated, and the instrumented stall test of Section @S:mech@ is the experiment that it needs."))
add(("fig", "@FILE:moc@", "Fig. @F:moc@. Check of the surge model. (a) Surge at the motor end: classical relations (Joukowsky for an instantaneous stop at wave speeds of 150, 250 and 400 m/s; Michaud for slow stops; the reduction factor of Eq. (6) for short stops) "
            "and the transient simulation. (b) Peak pressure of the screening model against the peak pressure of the simulation for random hoses, flows, relief settings and valve response times; the dotted line is equality. "
            "(c) Unrelieved fraction of the surge implied by the simulation against the response time of the relief valve; the dotted line is the upper bound of the prior of the model.", 6.8))
add(("h2", "@S:shifts@ Assumption shifts"))
add(("p", "Eight shifts are applied to the draws, one at a time, and then a combined stress, to see whether a conclusion survives a wrong prior: breakaway torques multiplied by 1.5; the scatter of the "
          "breakaway torque increased by 0.15 in log units; supply pressure lowered by 30 psi; seizure probabilities doubled; motor and gearbox efficiencies lowered by 0.10; fouling tripled; allowable stem "
          "torque multiplied by 0.7; the stall surge doubled; and all of them at a reduced strength together. The shifts change the distributions, not the design, so the same design can be evaluated "
          "under each; the worst case over the shifts is a robustness measure [@Beyer2007]."))

add(("h1", "5. Multi-objective optimization"))
add(("p", "The design problem has four variables: the displacement $D$ (60 to 500 cc), the ratio $R$ (60 to 600), the relief multiple $\\mu$ (0.2 to 1.0 of the nominal allowable stem torque, or 0.6 to 4 times the class median breakaway torque) and the flow limit "
          "$Q_{\\rm lim}$ (15 to 100 gpm), plus, when creep is allowed, the creep flows at the start and end of travel (5 to 60 gpm, held for one and two turns). The adaptive reserve rule is applied. Eight families are searched: two relief bases, each without and with an accumulator that "
          "absorbs 75% of the surge, each without and with creep. The objectives are to maximize the probability of a safe stroke and to minimize the probability of exceedance and the median water used in a stroke, under the decision constraint"))
add(("eq", r"P\left(T_{\rm peak}>T_{\rm allow}\right)\le 0.01", 8))
add(("p", "The limit of 1%% is an illustrative research constraint, not an established acceptable industrial safety limit; Section @S:opt@ shows how the result moves with it. Each family is searched with %s Latin-hypercube designs on %s common draws; the non-dominated set is found by "
          "exhaustive comparison [@Marler2004;@Deb2002]. The search is a sampling method, not a proof of optimality. To control the optimizer's curse the chosen designs are re-evaluated on %s independent draws, and a robust design is chosen by maximizing the worst-case probability of a safe stroke "
          "over the assumption shifts subject to a 2%% limit on the worst-case over-torque probability." % (n(M["designs"]), n(M["n_opt"]), n(M["n"]))))
add(("p", "A design chosen because its estimated over-torque probability is at most 1% has an uncertain estimate, and the selection favors designs whose estimate happened to fall below the limit. Wilson 95% limits are therefore reported on the independent draws "
          "(Table @T:ci@), together with a strict rule that admits a design only if the upper limit of its in-sample estimate is at most 1%."))
