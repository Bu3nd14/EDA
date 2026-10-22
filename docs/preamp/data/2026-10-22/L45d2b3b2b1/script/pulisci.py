#!/usr/bin/env python3
"""L45d2b3b2b1: toglie da regressione/dopo/ le forme d'onda che si rifanno (come L45d2b3b2a): i .json,
i .txt (wrdata) e i .csv oltre 1 MB. Restano i .log, i _resolved.cir, i .csv piccoli, esiti.tsv e gli
.stdout. Solo stdlib, /usr/bin/python3 -I.

Uso: pulisci.py
"""
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(L, "regressione", "dopo")
via, tot = 0, 0
for radice, _, file in os.walk(D):
    for f in file:
        p = os.path.join(radice, f)
        n = os.path.getsize(p)
        if radice == D:
            continue
        if f.endswith((".json", ".txt")) or (f.endswith(".csv") and n > 1_000_000):
            os.remove(p)
            via += 1
            tot += n
print("tolti %d file, %.1f MB" % (via, tot / 1e6))
