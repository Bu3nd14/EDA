#!/usr/bin/env python3
"""L62b: P7 della regressione (tb_mute_corto_regime.csv, una riga per caso) prima / dopo i diodi:
il massimo su tutti i casi di ogni colonna di potenza e di corrente, e lo scarto peggiore caso per
caso. Uso: /usr/bin/python3 -I p7_massimi.py"""
import csv
import os

LOTTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leggi(fase):
    p = os.path.join(LOTTO, "regressione", fase, "tb_mute_corto", "tb_mute_corto_regime.csv")
    return list(csv.reader(open(p)))


a, b = leggi("prima"), leggi("dopo")
if len(a) != len(b):
    raise SystemExit("righe %d -> %d" % (len(a), len(b)))
cols = {i: n for i, n in enumerate(a[0])}
print("%-8s %12s %12s %12s" % ("colonna", "max prima", "max dopo", "scarto max"))
for i, n in cols.items():
    if not (n.startswith("p") or n.startswith("ic") or n == "vpk"):
        continue
    xa = [float(r[i]) for r in a[1:]]
    xb = [float(r[i]) for r in b[1:]]
    print("%-8s %12.5g %12.5g %12.3g" % (n, max(xa), max(xb), max(abs(p - q) for p, q in zip(xa, xb))))
