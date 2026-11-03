#!/usr/bin/env python3
"""L64a: di quanto cambiano le onde di una cella di V2 coi .nodeset del blocco, contro la corsa
senza (prova_nodeset_v2.sh). Per ogni colonna dei due .dat (onde e stati): lo scarto assoluto
massimo, campione per campione, e il valore assoluto massimo della colonna. Se il numero di
campioni cambia (il passo adattivo), confronta per interpolazione lineare sul tempo della corsa
senza. Uso: scarto_nodeset_v2.py <cartella delle corse> <cella> [...]
Scrive ../prova_nodeset/scarti.csv.
"""
import bisect
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(QUI), "prova_nodeset")


def leggi(p):
    righe = []
    for ln in open(p):
        x = ln.split()
        if not x:
            continue
        try:
            righe.append([float(v) for v in x])
        except ValueError:
            continue
    return righe


def colonna(rr, j):
    return [r[j] for r in rr]


def interp(t, y, x):
    i = bisect.bisect_left(t, x)
    if i <= 0:
        return y[0]
    if i >= len(t):
        return y[-1]
    t0, t1 = t[i - 1], t[i]
    return y[i - 1] if t1 == t0 else y[i - 1] + (y[i] - y[i - 1]) * (x - t0) / (t1 - t0)


righe_out = []
d = sys.argv[1]
for c in sys.argv[2:]:
    for suf in ("", "_stati"):
        a = leggi(os.path.join(OUT, f"{c}{suf}_senza.dat"))
        b = leggi(os.path.join(d, f"{c}{suf}_nb.dat")) if os.path.exists(
            os.path.join(d, f"{c}{suf}_nb.dat")) else None
        if b is None:
            sys.exit(f"manca {c}{suf}_nb.dat")
        ncol = len(a[0])
        ta, tb = colonna(a, 0), colonna(b, 0)
        # wrdata ripete la colonna del tempo prima di ogni vettore: le colonne pari sono tempi
        for j in range(1, ncol, 2):
            ya, yb = colonna(a, j), colonna(b, j)
            if len(a) == len(b) and ta == tb:
                sc = max(abs(p - q) for p, q in zip(ya, yb))
            else:
                sc = max(abs(interp(tb, yb, x) - v) for x, v in zip(ta, ya))
            righe_out.append([c, suf or "onde", j, len(a), len(b), "%.3e" % sc,
                              "%.3e" % max(abs(v) for v in ya)])
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "scarti.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cella", "file", "colonna", "campioni_senza", "campioni_con", "scarto_max_V",
                "max_abs_V"])
    w.writerows(righe_out)
for r in righe_out:
    print(*r)
