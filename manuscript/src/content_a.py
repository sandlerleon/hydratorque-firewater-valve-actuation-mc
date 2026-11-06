# -*- coding: utf-8 -*-
"""Manuscript, part A: Introduction, system architecture and mathematical formulation (Sections 1-3)."""
from common import *

M = R["meta"]

# ============================================================================================ 1 Introduction
add(("h1", "1. Introduction"))
add(("p", "Large valves must sometimes be operated when plant power, instrument air and hydraulic supply are lost. Manual effort is limited, and improvised extensions expose the operator to injury [@Olsen2024]. "
          "The reliability of emergency valves is usually assessed by partial-stroke testing of the installed actuator [@Ahmad2016], which does not cover an actuator that has no power. Portable operators powered by batteries, compressed air, "
          "gasoline or an oil-hydraulic pack exist, but a battery tool depends on a charged pack and is an ignition-source concern in classified areas, a pneumatic tool depends on plant air, and a hydraulic pack is heavy and needs oil. "
          "An energy company has recently sought a portable, preferably non-electric device that multiplies an operator's torque four- to six-fold for valves of 2 to 16 inches, deployable in remote, cold regions [@YPF2026]."))
add(("p", "Almost every hazardous facility already owns a pressurized, regularly inspected source of hydraulic power: the firewater system. A hose at 100 psi and 150 gpm carries about 6.5 kW, far more than a portable valve tool needs. "
          "Water-hydraulic motors are an established technology [@Seabrook1994;@Yang2015;@Majdic2019], the pressure relief of water circuits has been studied [@Majdic2021], and the hydraulics of fire hoses [@Benfer2016] and hydrant supplies [@NFPA291;@Nolan2017] are well characterised. Patents describe "
          "hydrant-mounted operating apparatus [@Jackman1985], hydrant-attached remote-controlled valves [@Kolacz2014] and oscillatory actuators for fire-truck valves [@Leete1992]. To the author's knowledge, in a search that was not exhaustive, none treats the question "
          "that a designer of a firewater-powered valve operator has to answer: with uncertain supply, valve demand and torque-limiter setting, how often does the tool complete the stroke without exceeding the allowable stem torque and without taking water "
          "that firefighting needs, and which design and operating rules make that likely?"))

add(("p", "The three requirements conflict: a higher relief setting breaks stiff valves free but overloads stems, a higher flow limit shortens the stroke but draws water that a fire may need, and a lower gear ratio speeds the stroke and lowers the torque. "
          "That pressurized firewater can drive a valve operator follows from established hydraulic principles; the contribution that can be defended is a reproducible design and operating envelope that treats these requirements together and says how far it can be trusted. "
          "The paper formulates a probabilistic model with an explicit hydraulic circuit and the pressure surge on stall, in which each added mechanism can be switched off so that the earlier first-order model is recovered exactly; defines the safety criteria separately "
          "(success of the stroke, exceedance of the allowable stem torque, damage to the stem, violation of the firefighting reserve); poses a multi-objective design problem (motor, ratio, relief chart, flow limit and slow creep flows at the start and end of travel) under a limit on the "
          "over-torque probability; and tests the optimum out of sample, under deliberately wrong input distributions, and against a transient simulation. All input distributions are assumed priors for a concept-stage study."))


# ============================================================================================ 2 System architecture
add(("h1", "2. System architecture and operating rule"))
add(("p", "The tool (Fig. @F:arch@) is a portable water-hydraulic torque operator. A hose connects a hydrant, tap, fire truck or portable pump to a Smart Power Coupling with a cleanable strainer, a flow limiter, a slow-opening shut-off valve and a pressure gauge. "
          "Water drives a gerotor, piston or vane motor of 150 to 400 cc per revolution [@Yang2015;@Majdic2019]; a planetary reducer of 100:1 to 500:1 multiplies the torque; a universal interface with a reaction arm engages handwheels, operating nuts and part-turn valves in the manner of the "
          "standard actuator attachments [@ISO5210]. An adjustable inlet relief valve limits the pressure drop across the motor, and therefore the torque; a stall shows as a pressure rise. Options are a hose-side accumulator to absorb the surge on stall and an adjustable flow limiter that runs "
          "at a slow creep flow for the first turns of the stroke, to build torque gradually against a stuck valve, and for the last turns, to approach the stop slowly. A discharge hose routes the exhaust water to a drain. The baseline is purely mechanical, which keeps it clear of the electrical "
          "ignition concerns of classified areas, under the assessment of non-electrical equipment [@ISO80079]."))
add(("fig", "@FILE:arch@", "Fig. @F:arch@. Architecture of the firewater-powered valve operator. Water from a shared or dedicated source reaches the Smart Power Coupling "
            "(strainer and flow limiter, slow-opening shut-off, inlet relief valve that limits the torque, optional accumulator), drives the motor and gearbox, and is discharged "
            "through a hose. The torque is delivered to the valve stem through the interface and a reaction arm.", 6.6))
add(("p", "The displacement $D$ and the gear ratio $R$ are chosen from a kit; the relief setting, the flow limit and the creep flows are operating variables. The relief setting is read from a torque chart, the safety-critical document of the tool, on one of two bases: "
          "a multiple of the median breakaway torque of the valve class, which is what a designer who knows only the operating torque would use, or a fraction of the nominal allowable stem torque, which requires the valve data sheet. The tool is subject to one operating rule "
          "that the model enforces: it must not draw water from a fire-protection system when doing so could compromise the performance that system must deliver. A shared source (a firewater ring or hydrant) may be used only up to the flow that it can spare without cutting its "
          "firefighting reserve; a dedicated source (a fire truck or portable pump) carries no such limit. The model evaluates the rule as an event (a reserve violation) and as an adaptive flow limit."))


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
          "constant $k_{\\rm T}^{\\rm st}$ of Eq. (2) and the reduced efficiency. Without a relief valve $p_{\\rm peak}=p_{\\rm s}+\\Delta p_{\\rm J}$. The surge model is a screening approximation: Section @S:moc@ checks its relations against a transient simulation, and an instrumented stall test is the validation that it still needs."))
add(("h2", "3.5 Events and the metrics reported"))
add(("p", "Five events are defined for every draw. A stroke succeeds if the tool delivers the breakaway torque ($T_{\\rm cap}=k_{\\rm T}^{\\rm st}\\min\\{\\Delta p_{\\rm s},p_{\\rm set}\\}\\ge T_{\\rm break}$), sustains the running "
          "torque, and completes the stroke within the time limit. An exceedance occurs when the peak stall torque $T_{\\rm peak}$ is greater than the allowable stem torque $T_{\\rm allow}$, which "
          "is a design limit that already contains a safety factor. Damage occurs when $T_{\\rm peak}$ is greater than $T_{\\rm allow}$ times a sampled ratio between yield and allowable torque. "
          "A safe stroke is a successful stroke without exceedance. A reserve violation occurs on a shared source when the flow is greater than the spare flow. The concept-stage study reported "
          "a success probability of about 80% and, separately, an over-torque probability of about 5.5%; they were not combined, and the abstract of that study described the 80% as success without "
          "exceeding the allowable stem torque, which it was not. The safe stroke is the combined measure used here."))
