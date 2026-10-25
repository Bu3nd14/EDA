#!/usr/bin/env python3
"""Dopo L57b: il secondo caso noto. La protezione generata (che ora chiama DI_BAV199) con la stima di
L57b rinominata (dio=fit) deve ridare rca.csv di L57b/rca/reti/out_lim_rete10 cella per cella, entro
lo 0,5 % o 1 mV / 0,01 mA come verifica_noto.py. Prova che il cambio di nome del modello e dei banchi
non ha cambiato nient'altro.

Uso: /usr/bin/python3 verifica_fit.py      esce col numero di celle diverse
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(QUI)
A = os.path.join(D, "..", "L57b", "rca", "reti", "out_lim_rete10", "rca.csv")
B = os.path.join(D, "rca", "noto", "out_lim_fit_rete10", "rca.csv")
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
            print("DIVERSA %s %s m%s %s: L57b %g, ora %g" % (x["caso"], x["vol"], x["modo"], k, a, b))
print("caso noto 2 (la stima di L57b): %d celle, %d diverse" % (celle, diverse))
sys.exit(diverse)
