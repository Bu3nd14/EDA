#!/usr/bin/env python3
"""L60d2: la corsa di V2 ferma (off_r10m_d20_iii, lo spegnimento, "Timestep too small" a 1,02 s) col
metodo gear, insieme al suo riferimento (g10sempre_lz_iii): A e' la differenza fra le due corse, e i
due metodi del solutore non si mescolano (come in L60c2, sonda_v2.py). Solo stdlib.

Uso: gear_v2.py   -> run/v2_gear/corsa_<c>.cir e manifest.csv; poi corri_gear_v2.sh
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(L, "run", "v2")
OUT = os.path.join(L, "run", "v2_gear")
CORSE = ("off_r10m_d20_iii", "g10sempre_lz_iii")
os.makedirs(OUT, exist_ok=True)
for c in CORSE:
    t = open(os.path.join(V2, "corsa_%s.cir" % c)).read()
    assert t.count("\ntran ") == 1, c
    t = t.replace("\ntran ", "\noption method=gear\ntran ")
    open(os.path.join(OUT, "corsa_%s.cir" % c), "w").write(t)
righe = list(csv.DictReader(open(os.path.join(V2, "manifest_sel.csv"))))
sel = [r for r in righe if r["cella"] in CORSE]
assert len(sel) == 2, [r["cella"] for r in sel]
with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, list(righe[0].keys()))
    w.writeheader()
    w.writerows(sel)
print(OUT)
