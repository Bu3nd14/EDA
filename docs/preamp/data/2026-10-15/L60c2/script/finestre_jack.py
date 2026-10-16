#!/usr/bin/env python3
"""L60c2: il massimo di |jack| per finestre di tempo in un .dat di V2 (wrdata: mainjack fixjack1
fixjack2). Solo stdlib, /usr/bin/python3 -I.

Uso: finestre_jack.py FILE.dat [PASSO_s=0.1] [T_MAX_s]
"""
import sys

path = sys.argv[1]
passo = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
tmax = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
mx = {}
for riga in open(path):
    x = riga.split()
    if not x:
        continue
    t = float(x[0])
    if t > tmax:
        break
    k = int(t / passo)
    m = mx.setdefault(k, [0.0, 0.0, 0.0])
    for j in range(3):
        v = abs(float(x[2 * j + 1]))
        if v > m[j]:
            m[j] = v
for k in sorted(mx):
    print("%6.2f-%6.2f s  main %.4g  fix1 %.4g  fix2 %.4g" % (k * passo, (k + 1) * passo, *mx[k]))
