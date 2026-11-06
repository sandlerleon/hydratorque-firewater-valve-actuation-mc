# -*- coding: utf-8 -*-
"""Manuscript, part A: Introduction, system architecture and mathematical formulation (Sections 1-3)."""
from common import *

M = R["meta"]

# ============================================================================================ 1 Introduction
add(("h1", "1. Introduction"))
add(("p", "Large industrial valves must sometimes be operated when the plant has lost the services that normally move them. In an emergency, refineries, tank farms, terminals, "
          "pipeline stations and offshore platforms may need to close or open a gate, plug or butterfly valve whose handwheel is stiff or seized, while electrical power, instrument air "
          "and hydraulic supply are unavailable. Manual effort is limited, and the operator is exposed to injury when improvised extensions or cheater bars are used [@Olsen2024]. The reliability of emergency valves is usually assessed by partial-stroke testing of the installed actuator [@Ahmad2016], which does not cover the case in which the actuator itself has no power. Portable "
          "operators powered by batteries, compressed air, gasoline or an oil-hydraulic power pack exist, but each has a weakness at the moment it is needed: a battery tool depends on a charged "
          "pack and is an ignition-source concern in classified areas, a pneumatic tool depends on plant air, and a hydraulic power pack is heavy and needs oil. The need is recognised by industry: "
          "an energy company has recently sought a portable, preferably non-electric device that multiplies an operator's torque four- to six-fold for valves of 2 to 16 inches, ready for deployment "
          "in remote, cold regions [@YPF2026]."))
add(("p", "Almost every hazardous facility already owns a pressurized, distributed and regularly inspected source of hydraulic power: the firewater system. A hose at 100 psi and 150 gpm carries about "
          "6.5 kW of hydraulic power, far more than a portable valve tool needs. Water-hydraulic motors are an established technology [@Seabrook1994;@Yang2015;@Majdic2019], pressure "
          "relief of water circuits has been studied [@Majdic2021], and the hydraulics of fire hoses [@Benfer2016] and of hydrant supplies [@NFPA291;@Nolan2017] are well characterised. Patents describe "
          "hydrant-mounted operating apparatus with hose couplers and drive sockets [@Jackman1985], hydrant-attached remote-controlled valves [@Kolacz2014] and oscillatory actuators for fire-truck "
          "valves [@Leete1992]. To the author's knowledge, based on a search that was not exhaustive, none of these treats the question that a designer of a firewater-powered "
          "portable valve operator has to answer: with uncertain supply, uncertain valve demand and a torque limiter whose setting protects the valve but can also prevent the stroke, "
          "how often does the tool complete the stroke without exceeding the allowable stem torque and without taking water that firefighting needs, and which design and operating rules make that "
          "probability high?"))
add(("p", "The question matters because the three requirements conflict. Raising the relief setting lets the tool break stiff valves free but raises the probability that the stem is overloaded. "
          "Raising the flow limit shortens the stroke but draws water that a fire may need. Lowering the gear ratio speeds the stroke and lowers the torque. A first-order calculation shows that "
          "pressurized firewater can drive a valve operator, which follows from established hydraulic principles; the contribution that can be defended is a reproducible design and operating envelope "
          "that treats valve actuation success, stem overload, stroke time, water consumption and preservation of firefighting capacity together, and says how far it can be trusted."))
add(("p", "This paper provides that envelope for a concept-stage tool, in four steps. First, it formulates a probabilistic model of the tool with an explicit hydraulic circuit (source characteristic, hose, "
          "motor leakage and efficiency, relief override, and the pressure surge on stall), in which each added mechanism can be switched off so that the earlier first-order model is recovered exactly. "
          "Second, it defines the safety criteria separately: success of the stroke, exceedance of the allowable stem torque, damage to the stem, and violation of the firefighting reserve. Third, it "
          "formulates a multi-objective design problem, in which the motor, the ratio, the relief chart, the flow limit and a slow creep flow at the start and the end of travel are chosen to maximize the probability of a safe stroke subject to a limit on the over-torque probability and on water use, and tests the optimum out of "
          "sample and under deliberately wrong input distributions. Fourth, it compares the tool with an idealised water-hydraulic benchmark and with capability-limited conventional operators. All "
          "input distributions are assumed priors for a concept-stage study, and the paper states which of its conclusions depend on them."))
add(("p", "Section 2 describes the architecture and the operating rule, Section 3 the model, Section 4 the probabilistic methodology and its verification, Section 5 the optimization problem, "
          "Section 6 the results, Section 7 their interpretation and Section 8 the limitations and the validation that is needed. Section 9 concludes."))

# ============================================================================================ 2 System architecture
add(("h1", "2. System architecture and operating rule"))
add(("p", "The tool (Fig. @F:arch@) is a portable water-hydraulic torque operator. A hose connects a hydrant, a firewater tap, a fire truck or a portable pump to a Smart Power Coupling "
          "that carries a cleanable strainer, a flow limiter, a slow-opening shut-off valve and a mechanical pressure gauge. Water drives a gerotor, piston or vane motor of 150 to 400 cc per revolution "
          "[@Yang2015;@Majdic2019]. A multi-stage planetary reducer of 100:1 to 500:1 multiplies the torque, and a universal interface with a reaction arm engages handwheels, operating nuts and part-turn "
          "valves in the manner of the standard actuator attachments [@ISO5210]. An adjustable inlet relief valve limits the pressure drop across the motor, and therefore the torque, because motor "
          "torque is proportional to that pressure drop; a stall shows as a pressure rise, which tells the operator that the end of travel has been reached. A hose-side accumulator is an option "
          "to absorb the pressure surge on stall, and the flow limiter can be made adjustable so that the tool runs at a slow creep flow for the first turns of the stroke, to build torque gradually against a stuck valve, and for the last turns before the end of travel, to approach the stop slowly. The motor passes water continuously while it turns, so a discharge hose routes the exhaust to a drain. Everything in the baseline is mechanical, "
          "which keeps it clear of the electrical ignition concerns of classified areas and places it under the assessment of non-electrical equipment [@ISO80079]."))
add(("fig", "Fig1_architecture.png", "Fig. @F:arch@. Architecture of the firewater-powered valve operator. Water from a shared or dedicated source reaches the Smart Power Coupling "
            "(strainer and flow limiter, slow-opening shut-off, inlet relief valve that limits the torque, optional accumulator), drives the motor and gearbox, and is discharged "
            "through a hose. The torque is delivered to the valve stem through the interface and a reaction arm.", 6.6))
add(("p", "Two design variables are discrete in practice and are treated as such: the motor displacement $D$ and the gear ratio $R$ are chosen from a kit. Four are operating variables: the relief setting, "
          "which is read from a torque chart, the flow limit, and the creep flows at the start and at the end of travel, each held for a few turns (one at the start and two at the end in the study). The chart is the safety-critical document of the tool. Two bases are compared: a chart expressed as a multiple of the median "
          "breakaway torque of the valve class, which is what a designer who knows only the operating torque of the valve would use, and a chart expressed as a fraction of the nominal "
          "allowable stem torque, which requires the valve data sheet."))
add(("p", "The tool is subject to one operating rule that the model enforces: it must not draw water from a fire-protection system when doing so could compromise the performance that system must "
          "deliver. A shared source (a firewater ring or a municipal hydrant) may therefore be used only up to the flow that it can spare without cutting its firefighting reserve; a dedicated source "
          "(a fire truck or a portable pump) carries no such limit. The model evaluates the rule in two forms: the event that the tool draws more than the spare flow of a shared source "
          "(a reserve violation), and an adaptive rule in which the flow limit is lowered to the spare flow of the source in use."))

# ============================================================================================ 3 Mathematical formulation
add(("h1", "3. Mathematical formulation"))
add(("h2", "3.1 Hydraulic power and torque"))
add(("p", "The hydraulic power of a supply at pressure $\\Delta p$ and flow $Q$ is"))
add(("eq", r"P_{\rm h}=\Delta p\,Q", 1))
add(("p", "and the torque at the valve stem of a motor of displacement $D$ operating at a pressure drop $\\Delta p_{\\rm m}$ through a gearbox of ratio $R$ is"))
add(("eq", r"T_{\rm out}=\frac{D\,\Delta p_{\rm m}}{2\pi}\,\eta_{\rm m}\,R\,\eta_{\rm g}", 2))
add(("p", "where $\\eta_{\\rm m}$ and $\\eta_{\\rm g}$ are the motor and gearbox efficiencies. The efficiency at breakaway and at stall is lower than the running efficiency because of static friction and "
          "start-up leakage, so the breakaway and stall torque uses $\\eta_{\\rm m}-\\delta$, with $\\delta$ a sampled loss; this is the mechanism by which the concept-stage model, which used one efficiency, "
          "overstated the stall torque. For the baseline $D=200$ cc, $R=250$, $\\eta_{\\rm m}=0.85$, $\\eta_{\\rm g}=0.70$ and $\\Delta p_{\\rm m}=100$ psi, Eq. (2) gives %s N.m."
          % n(R["selftest"]["baseline_torque_Nm"])))
add(("h2", "3.2 Supply, hose and circuit pressure balance"))
add(("p", "The pressure available at the tap falls as flow is drawn. In the form used in hydrant flow tests [@NFPA291], with a static pressure $p_{\\rm s}$ and a flow capacity $Q_{\\rm a}$ at the "
          "residual pressure $p_{\\rm r}=20$ psi,"))
add(("eq", r"p_{\rm src}(Q)=p_{\rm s}-(p_{\rm s}-p_{\rm r})\left(\frac{Q}{Q_{\rm a}}\right)^{1.85}", 3))
add(("p", "The hose loses pressure as $C\\,(Q/100)^2\\,(L/100)$ psi for a hose of length $L$ in feet and a flow in gpm, with a coefficient $C$ that depends on the hose size [@Benfer2016]. The coupling, the strainer "
          "and the exhaust hose add losses that are proportional to the square of the flow. The flow in operation is the largest flow at which the pressure balance"))
add(("eq", r"p_{\rm src}(Q)-\Delta p_{\rm z}-\left(\frac{C L}{10^{6}}+k_{\rm spc}+\frac{c_{\rm f}}{Q_{\rm ref}^{2}}+\frac{C_{\rm d}L_{\rm d}}{10^{6}}\right)Q^{2}\ \ge\ \Delta p_{\rm run}", 4))
add(("p", "holds, limited by the flow limiter $Q_{\\rm lim}$, where $\\Delta p_{\\rm z}$ is the elevation head, $k_{\\rm spc}$ the coupling coefficient, $c_{\\rm f}$ the fouling loss at the reference flow $Q_{\\rm ref}$, "
          "$C_{\\rm d}L_{\\rm d}$ the exhaust-hose term, and $\\Delta p_{\\rm run}=T_{\\rm run}/k_{\\rm T}$ the pressure drop that the running torque $T_{\\rm run}$ requires. Eq. (4) is solved by bisection for every draw."))
add(("h2", "3.3 Motor speed, leakage, stroke time and water use"))
add(("p", "A water-hydraulic motor leaks through its clearances, and the leakage is nearly proportional to the pressure drop because the viscosity of water is low. The flow into the motor is therefore"))
add(("eq", r"Q=D\,n_{\rm m}+c_{\rm L}\,\Delta p_{\rm m},\qquad c_{\rm L}=\left(\frac{1}{\eta_{\rm v}}-1\right)\frac{D\,n_{\rm ref}}{\Delta p_{\rm ref}}", 5))
add(("p", "where $n_{\\rm m}$ is the motor speed, $\\eta_{\\rm v}$ the volumetric efficiency at the reference point ($\\Delta p_{\\rm ref}=100$ psi, $n_{\\rm ref}=100$ rpm) and $c_{\\rm L}$ the leakage coefficient. "
          "The output speed is $n_{\\rm out}=n_{\\rm m}/R$, the stroking time is $t=N_{\\rm turns}/n_{\\rm out}$ for $N_{\\rm turns}$ handwheel turns, and the water used in one stroke is $V=Q\\,t$. With creep flows $Q_{\\rm s}$ and $Q_{\\rm e}$ held for $N_{\\rm s}$ and $N_{\\rm e}$ turns, at output speeds $n_{\\rm s}$ and $n_{\\rm e}$, the time is $t=(N_{\\rm turns}-N_{\\rm s}-N_{\\rm e})/n_{\\rm out}+N_{\\rm s}/n_{\\rm s}+N_{\\rm e}/n_{\\rm e}$ and the water is the sum of the three phases. A stroke is "
          "required to be completed within 15 minutes of operating time, excluding set-up."))
add(("h2", "3.4 Relief valve, stall and the pressure surge"))
add(("p", "The relief valve opens at the set pressure $p_{\\rm set}$, which the chart derives from the valve class: $p_{\\rm set}=\\mu\\,T_{\\rm ref}/k_{\\rm T}^{\\rm nom}$ for a multiple $\\mu$ of a reference torque "
          "$T_{\\rm ref}$, which is the median breakaway torque or the nominal allowable stem torque. The set point has a tolerance, and the relief valve overshoots by a fraction $\\varepsilon_{\\rm r}$ at full "
          "flow. When the motor stops abruptly, at the end of travel or against an obstruction, the moving column of water produces a surge, estimated by the Joukowsky relation for "
          "an instantaneous stop and reduced when the stop takes longer than the wave takes to travel the hose and return [@Ghidaoui2005],"))
add(("eq", r"\Delta p_{\rm J}=\rho\,a\,v\,\min\left\{1,\frac{2L}{a\,t_{\rm c}}\right\}\left(1-\chi\right)", 6))
add(("p", "where $a$ is the wave speed in the compliant hose, $v=Q_{\\rm stall}/A_{\\rm h}$ the velocity in the hose of cross-section $A_{\\rm h}$ just before the stall, $t_{\\rm c}$ the stopping time and $\\chi$ the fraction absorbed by an "
          "accumulator. The flow before the stall is the end creep flow $Q_{\\rm e}$ when the stroke proceeds to its end, the start creep flow $Q_{\\rm s}$ when the valve does not break free (the tool then stalls at the start), and the running flow when there is no creep. The peak pressure at the motor is the smaller of the unrelieved surge and the relief override,"))
add(("eq", r"p_{\rm peak}=\min\left\{p_{\rm s}+\Delta p_{\rm J},\ \ p_{\rm set}\left(1+\varepsilon_{\rm r}\right)+\kappa\,\Delta p_{\rm J}\right\}", 7))
add(("p", "where $\\kappa$ is the fraction of the surge that the relief valve does not relieve in time. The peak torque is $T_{\\rm peak}=k_{\\rm T}^{\\rm st}\\,p_{\\rm peak}$, with the stall "
          "constant $k_{\\rm T}^{\\rm st}$ of Eq. (2) and the reduced efficiency. Without a relief valve $p_{\\rm peak}=p_{\\rm s}+\\Delta p_{\\rm J}$."))
add(("h2", "3.5 Events and the metrics reported"))
add(("p", "Five events are defined for every draw. A stroke succeeds if the tool delivers the breakaway torque ($T_{\\rm cap}=k_{\\rm T}^{\\rm st}\\min\\{\\Delta p_{\\rm s},p_{\\rm set}\\}\\ge T_{\\rm break}$), sustains the running "
          "torque, and completes the stroke within the time limit. An exceedance occurs when the peak stall torque $T_{\\rm peak}$ is greater than the allowable stem torque $T_{\\rm allow}$, which "
          "is a design limit that already contains a safety factor. Damage occurs when $T_{\\rm peak}$ is greater than $T_{\\rm allow}$ times a sampled ratio between yield and allowable torque. "
          "A safe stroke is a successful stroke without exceedance. A reserve violation occurs on a shared source when the flow is greater than the spare flow. The concept-stage study reported "
          "a success probability of about 80% and, separately, an over-torque probability of about 5.5%; they were not combined, and the abstract of that study described the 80% as success without "
          "exceeding the allowable stem torque, which it was not. The safe stroke is the combined measure used here."))
