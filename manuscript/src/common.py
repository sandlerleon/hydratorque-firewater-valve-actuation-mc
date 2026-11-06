# -*- coding: utf-8 -*-
"""Shared helpers for the manuscript builders: results, number formatting, block lists."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "manuscript")
R = json.load(open(os.path.join(ROOT, "results", "results.json"), encoding="utf-8"))
DOIS = json.load(open(os.path.join(HERE, "dois.json"), encoding="utf-8"))
GITHUB = "https://github.com/sandlerleon/hydratorque-firewater-valve-actuation-mc"
VERSION = "2.1.0"
TITLE = "Probabilistic Design and Safety-Constrained Optimization of a Firewater-Powered Portable Valve Actuation System"


def n(x, d=0):
    s = "{:,.{d}f}".format(x, d=d)
    if set(s) <= set("-0.,"):
        return s.lstrip("-")
    return s.replace("-", "−")


def sg(x, d=0):
    s = n(x, d)
    return s if s.startswith("−") or float(x) == 0 else "+" + s


def pc(x, d=0):
    """probability (0-1) as a percentage string"""
    return n(100.0 * x, d) + "%"


def pp(x, d=1):
    """percentage points"""
    return n(100.0 * x, d)


def ci(d, dd=1):
    """Wilson interval of a probability record {p, lo, hi} as 'p% (lo to hi)'"""
    return "%s%% (%s to %s)" % (n(100 * d["p"], dd), n(100 * d["lo"], dd), n(100 * d["hi"], dd))


FIGNUM = {"arch": 1, "verify": 2, "cap": 3, "relief": 4, "creep": 5, "grid": 6, "flow": 7, "pareto": 8, "robust": 9, "surgehet": 10, "sens": 11, "time": 12, "bench": 13}
TABNUM = {"inputs": 1, "base": 2, "ladder": 3, "creep": 4, "designs": 5, "limits": 6, "robust": 7}
SECNUM = {"base": "6.1", "relief": "6.2", "creep": "6.3", "grid": "6.4", "reserve": "6.5", "opt": "6.6", "robust": "6.7", "sens": "6.8", "bench": "6.9", "ypf": "6.10"}
_TOK = re.compile(r"@([FTS]):(\w+)@")


def _sub(x):
    """replace the symbolic figure, table and section numbers in a block"""
    if isinstance(x, str):
        return _TOK.sub(lambda m: str({"F": FIGNUM, "T": TABNUM, "S": SECNUM}[m.group(1)][m.group(2)]), x)
    if isinstance(x, tuple):
        return tuple(_sub(i) for i in x)
    if isinstance(x, list):
        return [_sub(i) for i in x]
    return x


B = []      # manuscript blocks
BS = []     # supplementary blocks


def add(b):
    B.append(_sub(b))


def adds(b):
    BS.append(_sub(b))
BASE = R["baseline"]
LAD = R["ladder"]
OPT = R["optimization"]
ROB = R["robust"]
