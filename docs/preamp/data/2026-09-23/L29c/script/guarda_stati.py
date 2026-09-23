#!/usr/bin/env python3
"""L29c: stampa rail, uscita del blocco B (MAIN_A) e jack principale di una corsa in una finestra
di tempo, dai file _stati.dat e .dat (colonne a coppie tempo/valore di wrdata).

Uso: guarda_stati.py DIR CORSA T0 T1 [N=25]"""
import os
import sys

import numpy as np

d, c, t0, t1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
N = int(sys.argv[5]) if len(sys.argv) > 5 else 25


def leggi(p, ncol):
    rows = []
    with open(p) as f:
        for l in f:
            x = l.split()
            t = float(x[0])
            if t < t0:
                continue
            if t > t1:
                break
            rows.append([t] + [float(x[2 * k + 1]) for k in range(ncol)])
    return np.array(rows)


# stati: xls.xs xlp.xs dep ina vplus vminus main_a
s = leggi(os.path.join(d, c + "_stati.dat"), 7)
j = leggi(os.path.join(d, c + ".dat"), 3)
idx = np.linspace(0, len(s) - 1, N).astype(int)
print("%10s %8s %8s %9s %11s" % ("t", "vplus", "vminus", "main_a", "mainjack"))
for i in idx:
    t = s[i, 0]
    k = min(np.searchsorted(j[:, 0], t), len(j) - 1)
    print("%10.5f %8.3f %8.3f %9.4f %11.4g" % (t, s[i, 5], s[i, 6], s[i, 7], j[k, 1]))
print("main_a: min %.4f max %.4f; mainjack: min %.4g max %.4g" % (
    s[:, 7].min(), s[:, 7].max(), j[:, 1].min(), j[:, 1].max()))
