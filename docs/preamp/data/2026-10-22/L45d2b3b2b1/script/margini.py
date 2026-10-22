#!/usr/bin/env python3
"""L45d2b3b2b1: V1, il margine di fase minimo per deck, prima (il blocco di main) e dopo (il sorgente),
da regressione/misure_oggi.csv. Solo stdlib, /usr/bin/python3 -I.

Uso: margini.py      stampa e scrive margini.csv
"""
import csv
import os
import re

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = {}
for r in csv.DictReader(open(os.path.join(L, "regressione", "misure_oggi.csv"))):
    if not re.fullmatch(r"pmarg(#\d+)?", r["misura"]) or not r["relativa"][:1].isdigit():
        continue
    d = m.setdefault(r["deck"], [1e9, 1e9, 0])
    d[0] = min(d[0], float(r["oggi"]))
    d[1] = min(d[1], float(r["sorgente"]))
    d[2] += 1
with open(os.path.join(L, "margini.csv"), "w", newline="") as fo:
    w = csv.writer(fo)
    w.writerow(["deck", "misure", "min_prima_deg", "min_dopo_deg", "differenza_deg"])
    for k, (a, b, n) in sorted(m.items()):
        w.writerow([k, n, "%.3f" % a, "%.3f" % b, "%+.3f" % (b - a)])
        print("%-22s %4d  %8.3f -> %8.3f  (%+.3f)" % (k, n, a, b, b - a))
