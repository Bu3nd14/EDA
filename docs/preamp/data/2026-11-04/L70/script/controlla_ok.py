#!/usr/bin/env python3
"""L64b: every run of lista_l64b.txt / lista_consumo.txt has an ok.txt with EXACTLY the options of
its line (corri_an.sh writes "<timer> <options>" there). The list of the missing was rewritten once
while xargs read it (a line came through cut: «struttore»); a cut that still parses would run with
an option less, and this finds it. Prints the runs that do not agree; exit 1 if any.
    /usr/bin/python3 -I script/controlla_ok.py
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
male = []
for f in ("lista_l64b.txt", "lista_consumo.txt"):
    for ln in open(os.path.join(L, f)):
        x = ln.split()
        if not x:
            continue
        ok = os.path.join(L, "seq", x[1], x[0], "ok.txt")
        if not os.path.exists(ok):
            male.append(f"{x[1]}/{x[0]}: manca ok.txt")
        elif open(ok).read().split() != x[2:]:
            male.append(f"{x[1]}/{x[0]}: ok.txt {open(ok).read().strip()!r}")
print("\n".join(male) or "tutte le corse hanno le opzioni della loro riga")
sys.exit(1 if male else 0)
