# -*- coding: utf-8 -*-
"""Builds manuscript/HydraTorque_JBSMSE_Manuscript.docx and the Supplementary Information from results/results.json, so that every number in the text
is the simulation's.

    python build_manuscript.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx_engine as E                      # noqa: E402
from common import *                         # noqa: E402,F401
from hydratorque_references import LIB       # noqa: E402
import content_front, content_a, content_b, content_c, content_d, content_si      # noqa: E402,F401


def build(path, blocks, cit, journal=False, line_numbers=True):
    doc = E.Doc(cit, journal)
    num = 0
    for b in blocks:
        k = b[0]
        if k == "title":
            doc.title(b[1])
        elif k == "author":
            doc.centered(b[1], 24)
        elif k == "small":
            doc.centered(b[1], 19)
        elif k == "blank":
            doc.blank()
        elif k == "h1":
            doc.h1(b[1])
        elif k == "h2":
            doc.h2(b[1])
        elif k == "p":
            doc.p(b[1])
        elif k in ("p0", "bullet", "num"):
            t = b[1]
            if k == "bullet":
                t = "• " + t
            elif k == "num":
                num += 1
                t = "%d. %s" % (num, t)
            doc.p(t, indent=False)
        elif k == "eq":
            doc.eq(b[1], b[2])
        elif k == "fig":
            doc.fig(os.path.join(FIG, b[1]), b[2], b[3] if len(b) > 3 else 6.4)
        elif k == "table":
            doc.table(b[1], b[2], b[3], b[4] if len(b) > 4 else None, size=b[5] if len(b) > 5 else 16)
        elif k == "refs":
            doc.h1("References")
            for i, text in cit.entries():
                par = doc.d.add_paragraph()
                E._spacing(par, 0, 60)
                if journal:
                    doc._ds(par)
                par.paragraph_format.left_indent = E.Emu(400 * 635)
                par.paragraph_format.first_line_indent = E.Emu(-400 * 635)
                E.add_runs(par, "[%d] %s" % (i, text), 24 if journal else 18)
    doc.save(path)


def scan_all(cit):
    for b in B + BS:
        for x in b[1:]:
            if isinstance(x, str):
                cit.scan(x)
            elif isinstance(x, list):
                for row in x:
                    for c in (row if isinstance(row, list) else [row]):
                        if isinstance(c, str):
                            cit.scan(c)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cit = E.Citations(LIB)
    scan_all(cit)
    build(os.path.join(OUT, "HydraTorque_JBSMSE_Manuscript.docx"), B, cit, journal=True)
    build(os.path.join(OUT, "HydraTorque_Supplementary_Information.docx"), BS, cit)
    skip = ("CRediT", "Declaration", "Funding", "Data and", "Code and", "Competing", "Author contributions", "Availability", "Use of generative")
    words = sum(len(b[1].split()) for b in B if b[0] in ("p", "p0", "num") and not b[1].startswith(skip))
    abstract = [b[1] for b in B if b[0] == "p0"][0]
    print("built; %d references; abstract %d words; text ~%d words" % (len(LIB), len(abstract.split()), words))
    assert len(abstract.split()) <= 250, "abstract too long"
