#!/usr/bin/env python3
"""L55, il caso noto del banco dei guasti: calore_fmje.csv (questa cartella) contro calore_sorg.csv di
L45d2b3b2b2, cella per cella, sulle righe comuni (rif e i modi di Q132 / Q133, nelle cinque
posizioni). Una cella numerica e' diversa se lo scarto supera 1e-3 relativo (come confronta_rv2.py).
Solo stdlib, /usr/bin/python3 -I.
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(os.path.dirname(L), "..", "2026-10-23", "L45d2b3b2b2", "calore_sorg.csv")


def tab(p):
    return {(r["posizione"], r["modo"]): r for r in csv.DictReader(open(p))}


a, b = tab(os.path.join(L, "calore_fmje.csv")), tab(B)
celle = diverse = 0
for k in sorted(a):
    if k not in b:
        print("manca nel banco:", k)
        continue
    for c, x in a[k].items():
        if c in ("variante",) or c not in b[k]:
            continue
        y = b[k][c]
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            celle += 1
            if x != y:
                diverse += 1
                print("%s %s %s: %r contro %r" % (k[0], k[1], c, x, y))
            continue
        celle += 1
        if abs(fx - fy) > 1e-3 * max(abs(fx), abs(fy), 1e-12):
            diverse += 1
            print("%s %s %s: %s contro %s" % (k[0], k[1], c, x, y))
print("righe %d, celle %d, diverse %d" % (len(a), celle, diverse))
