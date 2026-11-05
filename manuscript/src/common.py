# -*- coding: utf-8 -*-
"""Shared helpers for the manuscript builders: results, number formatting, block lists."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "manuscript")
R = json.load(open(os.path.join(ROOT, "results", "results.json"), encoding="utf-8"))
DOIS = json.load(open(os.path.join(HERE, "dois.json"), encoding="utf-8"))
GITHUB = "https://github.com/sandlerleon/hydratorque-firewater-valve-actuation-mc"
VERSION = "2.0.0"
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


B = []      # manuscript blocks
BS = []     # supplementary blocks
add = B.append
adds = BS.append
BASE = R["baseline"]
LAD = R["ladder"]
OPT = R["optimization"]
ROB = R["robust"]
