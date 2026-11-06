# -*- coding: utf-8 -*-
"""Selective merge of the Rubriq language edit of the HydraTorque manuscript (no tracked changes) into the build.
Hunks are accepted (American spelling, commas, articles, plain wording) unless a hand review found a change of meaning, a typo, a broken name or a
changed technical term: those paragraphs / hunks are listed in REJECT_PARAS / DENY. Equations, figures, tables and the reference list are never taken from the edit.

    python merge_rub_ht.py <build.docx> <rubriq.docx> <out.docx>
"""
import io
import re
import sys

sys.path.insert(0, "C:/YouTube/damage-repair-xy-stiffness/manuscript")
import docx
import merge_rubriq as MR

REJECT_PARAS = {
    50: "restructures the verification sentence ( 'the concept-stage model draw for draw is reproduced')",
    7: "abstract: 'does not exceed ... by only 63%' and 'rules are likely' change the meaning",
    12: "'best of the authors' knowledge' (sole author), 'no one has addressed' (wrong subject)",
    15: "'keeps it clear of' -> 'highlights' reverses the meaning",
    17: "'smart power coupling' (proper name)",
    57: "caption: 'Check the surge model', 'equal'",
    72: "caption typo 'Breakway'",
    74: "heading 'surge in stall' and 'limiter and'",
    75: "'regardless of safety, the chart is paid for' is garbled",
    86: "'strokes ending in 15 minutes' changes the meaning",
    91: "heading 'reserves ... limits' (plural)",
    112: "'data sheet value' and garbled punctuation in the caption",
    114: "'data sheet value' and garbled punctuation in the caption",
    123: "caption: 'by valve class and baseline tool' changes the meaning",
    134: "drops the 'neither ... nor' limitation of the novelty claim",
    138: "deletes 'yield', 'safety factor' and 'arm length' labels",
    173: "reference title", 174: "reference title", 183: "reference title",
}
DENY = {
    ("over-torque", "overtorque"), ("-", "‒"), ("-", "–"), ("-", " "), ("on", "in"), ("stated", "revealed"), ("found", "revealed"), ("brings", "increases"),
    ("have", "are"), ("correlations", "correlated"), ("technology", "technological"), ("accumulator", "cumulative"), ("operating time,", "operation,"),
    ("off the engine reproduces", "off,"), ("draw.", "draw is reproduced."), ("in", "respectively, at"), (" of", ""), ("equality.", "equal."), ("Smart", "smart"), ("Power", "power"),
    ("Coupling", "coupling"), ("Breakaway", "Breakway"), ("", "for"), ("in", "is"), ("of the", "an"),
}


def hunk_ok(old, new):
    return (old.strip(), new.strip()) not in DENY and (old, new) not in DENY


def main(build, rub, out):
    A = docx.Document(build).paragraphs
    Cd = docx.Document(build)
    C = Cd.paragraphs
    B = docx.Document(rub).paragraphs
    assert len(A) == len(B) == len(C), (len(A), len(B), len(C))
    report, n_acc, n_rej, n_par = [], 0, 0, 0
    for i, (pa, pb) in enumerate(zip(A, B)):
        if pa.text == pb.text:
            continue
        head = pa.text[:60].replace("\n", " ")
        if i in REJECT_PARAS:
            report.append("REJECT paragraph #%d (%s) | %s" % (i, REJECT_PARAS[i], head))
            continue
        pc = C[i]
        if MR.has_math(pc) or not MR.plain_runs(pc):
            report.append("SKIP equation or field paragraph #%d | %s" % (i, head))
            continue
        chars = MR.char_formats(pc)
        assert "".join(c for c, _ in chars) == pa.text, head
        acc = []
        for (s0, s1, rep, old, new) in MR.hunks(pa.text, pb.text):
            if hunk_ok(old, new):
                acc.append((s0, s1, rep)); n_acc += 1
                report.append("  accept  [%s] -> [%s]" % (old, new))
            else:
                n_rej += 1
                report.append("  reject  [%s] -> [%s]" % (old, new))
        if acc:
            n_par += 1
            nc = list(chars)
            for s0, s1, rep in sorted(acc, reverse=True):
                fmt = chars[s0 - 1][1] if s0 > 0 else (chars[s1][1] if s1 < len(chars) else None)
                if s1 > s0:
                    fmt = chars[s0][1]
                nc[s0:s1] = [(c, fmt) for c in rep]
            MR.rebuild_runs(pc, nc)
        report.append("PARAGRAPH #%d | %s" % (i, head))
    Cd.save(out)
    rp = out.rsplit(".", 1)[0] + "_merge_report.txt"
    io.open(rp, "w", encoding="utf-8").write("accepted %d hunks in %d paragraphs, rejected %d hunks; %d paragraphs kept as built\n\n" % (n_acc, n_par, n_rej, len(REJECT_PARAS)) + "\n".join(report) + "\n")
    print("accepted %d hunks in %d paragraphs, rejected %d hunks -> %s" % (n_acc, n_par, n_rej, out))


if __name__ == "__main__":
    main(*sys.argv[1:4])
