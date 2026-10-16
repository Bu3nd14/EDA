#!/usr/bin/env python3
"""L60c2: dove salta il jack della Stax in una corsa di guasto. Solo stdlib, /usr/bin/python3 -I.

Uso: salti.py MODO T0 T1      stampa i punti fra T0 e T1 (s, assoluti) in cui fix2jack o outf2
                              cambiano di piu' di 50 mV da un campione al successivo.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
modo, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
prec = None
n = 0
for riga in open(os.path.join(L60C2, "run", "guasti", modo, modo + ".dat")):
    x = riga.split()
    if not x:
        continue
    t = float(x[0])
    if t < t0 or t > t1:
        continue
    jk, oa, f2 = float(x[5]), float(x[7]), float(x[11])
    if prec is not None and (abs(jk - prec[1]) > 0.05 or abs(f2 - prec[3]) > 0.05):
        print("t=%.6f  dt=%.2e  outa %.3f -> %.3f  outf2 %.3f -> %.3f  jack %.3f -> %.3f"
              % (t, t - prec[0], prec[2], oa, prec[3], f2, prec[1], jk))
        n += 1
        if n > 40:
            break
    prec = (t, jk, oa, f2)
