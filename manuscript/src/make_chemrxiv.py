# -*- coding: utf-8 -*-
"""ChemRxiv copy of the manuscript: line numbers removed, equations as pictures (ChemRxiv's Word-to-PDF conversion mishandles Office Math).
    python make_chemrxiv.py <out.docx>"""
import os
import re
import sys
import tempfile

import docx
from docx.oxml.ns import qn
from docx.shared import Inches
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "HydraTorque_JBSMSE_Manuscript.docx"))
OUT = sys.argv[1]

TEX = []
for fn in ("content_a.py", "content_b.py"):
    for ln in open(os.path.join(HERE, fn), encoding="utf-8"):
        m = re.match(r'add\(\("eq", r"(.*)", (\d+)\)\)\s*$', ln.strip())
        if m:
            TEX.append((m.group(1), int(m.group(2))))
assert len(TEX) == 8, len(TEX)
plt.rcParams["mathtext.fontset"] = "stix"


def render(tex, k):
    t = re.sub(r"\{\\rm ([^}]*)\}", lambda m: "\\mathrm{" + m.group(1) + "}", tex)
    t = t.replace("\\qquad", "\\quad\\quad").replace("\\ ", "\\,")
    t = re.sub(r"\\le(?![a-zA-Z])", r"\\leq", t)
    t = re.sub(r"\\ge(?![a-zA-Z])", r"\\geq", t)
    fig = plt.figure(figsize=(0.2, 0.2))
    fig.text(0, 0, "$" + t + "$", fontsize=14)
    fn = os.path.join(tempfile.gettempdir(), "hydratorque_eq%d.png" % k)
    fig.savefig(fn, dpi=300, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    return fn


d = docx.Document(SRC)
for sp in d.element.body.iter(qn("w:sectPr")):
    for ln in sp.findall(qn("w:lnNumType")):
        sp.remove(ln)
body_w = None
for s in d.sections:
    body_w = (s.page_width - s.left_margin - s.right_margin) / 914400.0
n = 0
for p in d.paragraphs:
    maths = p._p.findall(".//" + M + "oMath")
    if not maths:
        continue
    tex, num = TEX[n]
    fn = render(tex, n)
    wpx = Image.open(fn).size[0]
    win = min(wpx / 300.0, body_w * 0.78)
    top = maths[0]
    while top.getparent() is not p._p:
        top = top.getparent()
    r = p.add_run()
    r.add_picture(fn, width=Inches(win))
    run_el = r._r
    p._p.remove(run_el)
    top.addprevious(run_el)
    for mm in p._p.findall(M + "oMathPara") + p._p.findall(M + "oMath"):
        p._p.remove(mm)
    n += 1
assert n == 8, n
d.save(OUT)
print("saved", OUT, "equations as images:", n)
