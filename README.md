# HydraTorque: probabilistic design and safety-constrained optimization of a firewater-powered portable valve operator

Leon Sandler, Independent Researcher — leon.sandler@alumni.swinburne.edu — ORCID 0009-0007-4584-808X

Code, results and manuscript for *"Probabilistic Design and Safety-Constrained Optimization of a Firewater-Powered Portable Valve Actuation System,"* prepared for the **Journal of the Brazilian Society of Mechanical Sciences and Engineering** (Springer Nature).

A portable water-hydraulic operator (motor displacement D, planetary ratio R, torque-limiting relief valve, flow limiter) is driven through a fire hose from existing firewater infrastructure. `HydraTorque_MC.py` (numpy and matplotlib only) is a Monte Carlo model with an explicit hydraulic circuit, motor leakage and start-up efficiency, a relief valve and the **pressure surge on stall**, evaluated on 200,000 draws. Each added mechanism can be switched off; with all switched off the engine reproduces the concept-stage model (`legacy_v1/`, the Wazoku white-paper script) draw for draw.

**Every input distribution is an assumed prior for a concept-stage study (no measured data). All results are simulation outputs under those assumptions; the model is verified numerically, not validated physically.**

## Headline results (baseline tool: 200 cc, 250:1, 60 gpm, relief at 2 x median breakaway; valve-class mix)

| Quantity | Concept-stage model (v1) | Model 2 |
|---|---|---|
| Stroke completed within 15 min | 80.0% | 75.3% |
| Stroke completed without exceeding the allowable stem torque ("safe stroke") | 75.3% (not reported in v1) | 62.6% |
| Over-torque probability | 5.5% | 15.2% |
| Stem-damage probability | 0.1% | 1.1% |
| Water per successful stroke (median) | "50–100 L/min" | 1,601 L (60 gpm limiter; the 13–26 gpm of v1 is the flow at 1–2 rpm, too slow for a 15-minute stroke) |

Under a 1% limit on the over-torque probability (an illustrative constraint) the best design of each family holds out of sample (1.0% and 1.0% over-torque) at a safe-stroke probability of 53.8% (no accumulator) and 59.9% (hose-side accumulator absorbing 75% of the surge), against 62.6% for the baseline. The optimum survives wrong priors for valve torque, supply, seizure, efficiency and fouling, but **not** a stem 30% weaker than its data sheet (13% over-torque) or a surge twice the prior.

**Creep (v2.1.0).** An adjustable flow limiter that runs slowly for the first turn and the last two turns of the stroke lowers the flow that the stall has to stop, and with it the surge: on the baseline tool two turns at 20 gpm lower the over-torque probability from 15.2% to 8.9% and raise the safe-stroke probability from 62.7% to 67.6% at a cost of about 0.8 min of stroking time. Under the 1% over-torque limit, allowing creep raises the best safe-stroke probability from 53.8% to 59.5% (no accumulator) and from 59.9% to 63.7% (accumulator).

## Quick start

```
pip install -r requirements.txt
python HydraTorque_MC.py --demo                          # verification suite (about 1 minute)
python -m pytest -q tests                                # 25 automated checks
python HydraTorque_MC.py --reproduce --outdir results    # every result of the paper (about 10 minutes, seed 2026)
python make_figures.py                                   # figures 1-13 and S1-S2 from results/results.json
python manuscript/src/build_manuscript.py                # manuscript + Supplementary Information (needs python-docx)
python HydraTorque_MC.py --legacy --outdir legacy_out    # the concept-stage study, unchanged
```

## Verification

Draw-for-draw equivalence with the concept-stage model when the six added mechanisms are off; closed-form breakaway probability (max deviation 0.0024); closed-form over-torque probability of a relief-limited tool; mechanical output power never above the hydraulic power at the motor (max ratio 0.791) and tap power never below motor power; unit, hose-friction and Joukowsky checks; monotonicity in supply pressure, accumulator fraction and relief setting; adaptive reserve rule removes reserve violations; common-random-number reproducibility. These check the model against its own assumptions; they do not validate the assumptions.

## Contents

| Path | Contents |
|---|---|
| `HydraTorque_MC.py` | the model, studies and optimization (numpy + matplotlib) |
| `tests/` | pytest checks |
| `results/results.json` | all results of the paper (seed 2026) |
| `figures/` | figures 1–13 and S1–S2 |
| `manuscript/` | manuscript, Supplementary Information, cover letter (docx + pdf), ChemRxiv copy, builders in `manuscript/src` |
| `legacy_v1/` | the concept-stage script and its results (unchanged) |

## Versions

* **v2.1.0** (2026-11-05) — creep at the start and at the end of travel (`Tool2.creep_*`, `study_creep`, six-variable design search, 5 new tests); eight design families; figures and tables of the manuscript numbered in order of citation; `HydraTorque_MC.py` version 2.1.0.
* **v2.0.0** (2026-11-04) — model 2: surge on stall, motor leakage, start-up efficiency, source characteristic, exhaust back-pressure; safe-stroke criterion; firefighting-reserve model with adaptive rule; safety-constrained multi-objective optimization with out-of-sample, robustness and chart-basis studies; benchmarks; water-budget reconciliation. Corrects two statements of the concept-stage white paper (see above).

## Archive and citation

Software (all versions): https://doi.org/10.5281/zenodo.23969346 · Manuscript (all versions): https://doi.org/10.5281/zenodo.23969344.

Code is MIT-licensed (`LICENSE`); the manuscript is CC BY 4.0. Tested with Python 3.11, numpy 2.4.6, matplotlib 3.11.1.
