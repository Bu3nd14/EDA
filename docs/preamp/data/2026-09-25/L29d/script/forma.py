#!/usr/bin/env python3
"""L29d: la forma grezza attorno a un picco: FIXJACK1 dal .dat e FIXC1 dagli stati, campionati.
Diagnostica.  Uso: forma.py DIR CORSA T0 T1 [N=25]"""
import os
import sys

d, c, t0, t1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
n = int(sys.argv[5]) if len(sys.argv) > 5 else 25


def leggi(p, col):
    out = []
    with open(p) as f:
        for r in f:
            x = r.split()
            t = float(x[0])
            if t < t0:
                continue
            if t > t1:
                break
            out.append((t, float(x[col])))
    return out


j = leggi(os.path.join(d, c + ".dat"), 3)
s = leggi(os.path.join(d, c + "_stati.dat"), 17)
print("%d punti jack, %d punti stati" % (len(j), len(s)))
passo = max(1, len(j) // n)
pk = max(j, key=lambda x: abs(x[1]))
print("picco FIXJACK1 %.4g V a %.7f" % (pk[1], pk[0]))
for k in range(0, len(j), passo):
    t, v = j[k]
    fc = min(s, key=lambda x: abs(x[0] - t))[1] if s else float("nan")
    print("t %.7f  FIXJACK1 %+.4e  FIXC1 %+.4e" % (t, v, fc))
