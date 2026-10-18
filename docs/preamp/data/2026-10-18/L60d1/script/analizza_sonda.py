#!/usr/bin/env python3
"""L60d1, NC-070: lettura di run/sonda/<variante>/sonda.dat (sonda_blocco.py). Stampa il massimo
di |jack| e, attorno al picco massimo dopo T0, ogni colonna a -2 / -0,5 / 0 / +0,5 / +2 us: la
grandezza del blocco che salta insieme al jack. Poi, su un periodo intero da T0, il minimo e il
massimo di ogni colonna. Solo stdlib.

Uso: analizza_sonda.py <variante> [T0=0.02]
"""
import bisect
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
var = sys.argv[1]
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.02
d = os.path.join(L, "run", "sonda", var)
nomi = open(os.path.join(d, "colonne.txt")).read().split()
T, C = [], [[] for _ in nomi]
for riga in open(os.path.join(d, "sonda.dat")):
    x = riga.split()
    if not x:
        continue
    T.append(float(x[0]))
    for j in range(len(nomi)):
        C[j].append(float(x[2 * j + 1]))
print("%s: %d punti, t fino a %.4g s" % (var, len(T), T[-1]))
i0 = bisect.bisect_left(T, T0)
ip = max(range(i0, len(T)), key=lambda i: abs(C[0][i]))
print("max |jack| dopo %.3g s: %.4g V a t = %.7f s" % (T0, C[0][ip], T[ip]))


def a(tt, j):
    i = min(max(bisect.bisect_left(T, tt), 1), len(T) - 1)
    t1, t2 = T[i - 1], T[i]
    y1, y2 = C[j][i - 1], C[j][i]
    return y1 if t2 == t1 else y1 + (y2 - y1) * (tt - t1) / (t2 - t1)


passi = (-2e-6, -0.5e-6, 0.0, 0.5e-6, 2e-6)
print("%-18s" % "colonna" + "".join("%14s" % ("%+.1f us" % (p * 1e6)) for p in passi))
for j, n in enumerate(nomi):
    print("%-18s" % n + "".join("%14.6g" % a(T[ip] + p, j) for p in passi))
i1 = bisect.bisect_left(T, T0 + 1e-3)
print("su un periodo da %.3g s: min / max" % T0)
for j, n in enumerate(nomi):
    s = C[j][i0:i1]
    print("%-18s %14.6g %14.6g" % (n, min(s), max(s)))
