#!/usr/bin/env python3
"""L57b: il caso noto. La protezione presa dal subckt generato, coi modelli del banco di L57a (1N4148,
riferimenti ideali a 5 V), deve ridare rca.csv di L57a/rca/strade/out_r1k_lim5 cella per cella:
entro lo 0,5 % o 1 mV / 0,01 mA (la tolleranza di L57a/verifica_noto.py).

Uso: /usr/bin/python3 verifica_noto.py      esce col numero di celle diverse
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L57B = os.path.dirname(QUI)
A = os.path.join(L57B, "..", "L57a", "rca", "strade", "out_r1k_lim5", "rca.csv")
B = os.path.join(L57B, "rca", "noto", "out_noto_r1k_lim5", "rca.csv")
ra, rb = list(csv.DictReader(open(A))), list(csv.DictReader(open(B)))
assert len(ra) == len(rb) == 16, (len(ra), len(rb))
celle = diverse = 0
for x, y in zip(ra, rb):
    for k in x:
        if k in ("caso", "vol", "modo", "rete"):
            assert x[k] == y[k], (k, x[k], y[k])
            continue
        a, b = float(x[k]), float(y[k])
        tol = 0.01 if k.endswith("_ma") else 1e-3
        celle += 1
        if abs(a - b) > max(tol, 0.005 * abs(a)):
            diverse += 1
            print("DIVERSA %s %s m%s %s: L57a %g, L57b %g" % (x["caso"], x["vol"], x["modo"], k, a, b))
print("caso noto: %d celle, %d diverse" % (celle, diverse))
sys.exit(diverse)
