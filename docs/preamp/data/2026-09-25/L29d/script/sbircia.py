#!/usr/bin/env python3
"""L29d: sbirciata GREZZA (nessun filtro di V2) di una corsa: il picco di |v| ai tre jack in una
finestra, e il lato condensatore (MAINC / FIXC1 / FIXC2) all'istante dato. Diagnostica, non verdetto.

Uso: sbircia.py DIR CORSA T0 T1 [T_STATO]
"""
import os
import sys

d, c, t0, t1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
ts = float(sys.argv[5]) if len(sys.argv) > 5 else None
nomi = ("MAINJACK", "FIXJACK1", "FIXJACK2")
pk = [(0.0, 0.0)] * 3
with open(os.path.join(d, c + ".dat")) as f:
    for r in f:
        x = r.split()
        t = float(x[0])
        if t < t0:
            continue
        if t > t1:
            break
        for k in range(3):
            v = abs(float(x[2 * k + 1]))
            if v > pk[k][0]:
                pk[k] = (v, t)
print("%s  [%g, %g] s: " % (c, t0, t1) + "  ".join("%s %.4g V @ %.6f" % (n, v, t) for n, (v, t) in zip(nomi, pk)))
if ts is not None:
    ultimo = None
    with open(os.path.join(d, c + "_stati.dat")) as f:
        for r in f:
            x = r.split()
            if float(x[0]) > ts:
                break
            ultimo = x
    if ultimo and len(ultimo) >= 20:
        print("   a t = %g s: MAINC %.4g  FIXC1 %.4g  FIXC2 %.4g V" % (ts, float(ultimo[15]), float(ultimo[17]), float(ultimo[19])))
