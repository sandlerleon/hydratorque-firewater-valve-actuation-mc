# -*- coding: utf-8 -*-
"""Cover letter for the submission to the Journal of the Brazilian Society of Mechanical Sciences and Engineering (numbers from results/results.json; DOIs from dois.json).

    python build_cover_letter.py   -> manuscript/HydraTorque_Cover_Letter.docx
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Inches

from common import *

OOS = R["robust"]
o0, o75 = OOS["optimized allowable|0"]["out_of_sample"], OOS["optimized allowable|0.75"]["out_of_sample"]
oc0, oc75 = OOS["optimized allowable|0|creep"]["out_of_sample"], OOS["optimized allowable|0.75|creep"]["out_of_sample"]
d = Document()
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(8)
for s in d.sections:
    s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.9)


def para(t, bold=False, after=None):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


para("Leon Sandler", True, 0)
for t in ("Independent Researcher", "Northbrook, Illinois, USA", "leon.sandler@alumni.swinburne.edu", "ORCID 0009-0007-4584-808X"):
    para(t, after=0)
para("")
para(datetime.date.today().strftime("%d %B %Y").lstrip("0"))
para("The Editor-in-Chief", after=0); para("Journal of the Brazilian Society of Mechanical Sciences and Engineering", after=0); para("Springer Nature")
para("Dear Editor,")
para("I submit the manuscript “%s” as a Technical Paper for consideration in the Journal of the Brazilian Society of Mechanical Sciences and Engineering." % TITLE)
para("Large valves must sometimes be operated when plant power, instrument air and hydraulic supply are lost. Almost every hazardous facility already owns a pressurized, regularly inspected "
     "source of hydraulic power, its firewater system, and the manuscript studies a portable water-hydraulic valve operator driven through a fire hose. It does not argue for a product. It treats "
     "the tool as a computational engineering problem with three conflicting requirements, completing the stroke, not exceeding the allowable stem torque, and not taking the water that firefighting needs, "
     "and asks which design and operating rules satisfy them, and how far the answer can be trusted.")
para("The manuscript makes four contributions. (i) A probabilistic model with an explicit hydraulic circuit (source characteristic, hose, motor leakage and start-up efficiency, relief valve, and the "
     "pressure surge on stall), in which each added mechanism can be switched off so that the earlier first-order model is recovered exactly. (ii) Separate safety criteria: a safe stroke, exceedance "
     "of the allowable stem torque, stem damage and violation of the firefighting reserve. The model shows that the first-order estimate of about 80%% success was optimistic: a safe stroke occurs in %s "
     "of the draws for the baseline tool, with an over-torque probability of %s. (iii) A safety-constrained multi-objective design study, whose optimum is re-evaluated out of sample and under deliberately "
     "wrong input distributions: with a hose-side accumulator and a relief chart set from the stem strength, the over-torque probability can be brought to 1%% at a cost of %s to %s percentage points of "
     "safe strokes, a cost that a slow creep flow at the start and at the end of travel recovers in part (%s to %s points), but the optimum does not survive a weaker stem or a larger surge. (iv) A reconciliation of the water budget: a stroke uses about %s L of water, not the 50 to 100 L/min first assumed."
     % (pc(BASE["success_safe"]["p"], 0), pc(BASE["overtorque"]["p"], 0), n(100 * (BASE["success_safe"]["p"] - o75["safe"]), 0), n(100 * (BASE["success_safe"]["p"] - o0["safe"]), 0), n(100 * (oc75["safe"] - o75["safe"]), 0), n(100 * (oc0["safe"] - o0["safe"]), 0), n(round(BASE["volume_median_L"], -2))))
para("The study is explicit about what it is. Every input distribution is an assumed prior, because no published distribution of breakaway torques, surge parameters or spare firewater flows was found; "
     "the model is verified numerically (draw-for-draw equivalence with the earlier model, closed-form checks, energy balance, %s automated tests) but not validated physically; and the results are "
     "simulation outputs under those assumptions, not measurements. The manuscript lists the measurements that would replace the assumptions, and it makes no claim of superiority over conventional operators."
     % "25")
para("The code and results are openly available at %s and archived at https://doi.org/%s (code, all versions); the manuscript and its Supplementary Information are archived at https://doi.org/%s "
     "(all versions). One command regenerates every number and figure." % (GITHUB, DOIS["code_concept"], DOIS["paper_concept"]))
para("Disclosure. The concept originated as a white paper that I prepared for an industrial scouting challenge; I have filed no patent, and no contract or payment has resulted. "
     "The work received no external funding.")
para("Author affiliation and email address. I am an independent researcher with no current institutional affiliation, and I am the sole author. My contact and corresponding-author address is the alumni "
     "email address provided by my former university (Swinburne University of Technology, leon.sandler@alumni.swinburne.edu); it identifies me as a graduate and does not indicate a current "
     "affiliation or employer.")
para("A generative AI tool (Claude, Anthropic) assisted with code development, analysis, drafting and editing; I reviewed and checked all of it and take full responsibility for the content, as "
     "disclosed in the manuscript. The manuscript is original, has not been published elsewhere and is not under consideration at any other journal. I am the sole author and have no competing interests.")
para("Thank you for considering this submission.")
para("Sincerely,")
para("Leon Sandler", True)
out = os.path.join(OUT, "HydraTorque_Cover_Letter.docx")
d.save(out)
print("saved", out)
