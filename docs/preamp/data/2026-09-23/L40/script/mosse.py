#!/usr/bin/env python3
"""L40: dal confronto_grezzo.csv, per ogni deck, quante cifre si muovono oltre
una soglia relativa, e le chiavi (senza l'indice #n) che si muovono, col delta
relativo massimo. Uso: /usr/bin/python3 mosse.py [soglia=0.005] [deck]
"""
import csv
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = float(sys.argv[1]) if len(sys.argv) > 1 else 0.005
solo = sys.argv[2] if len(sys.argv) > 2 else None
g = {}
tot = {}
for r in csv.DictReader(open(os.path.join(BASE, "confronto_grezzo.csv"))):
    if solo and r["deck"] != solo:
        continue
    tot[r["deck"]] = tot.get(r["deck"], 0) + 1
    try:
        dr = abs(float(r["delta_rel"]))
    except ValueError:
        continue
    if dr <= s:
        continue
    k = (r["deck"], r["sorgente"], re.sub(r"#\d+$", "", r["chiave"]))
    n, m, ex = g.get(k, (0, 0.0, None))
    g[k] = (n + 1, max(m, dr), ex if ex and m >= dr else (r["prima"], r["dopo"]))
for d in sorted(tot):
    ks = [(k, v) for k, v in g.items() if k[0] == d]
    print("%-28s %5d cifre, %4d oltre %.1f %%" % (d, tot[d], sum(v[0] for _, v in ks), s * 100))
    for k, v in sorted(ks, key=lambda x: -x[1][1])[:12]:
        print("    %-6s %-26s n=%-4d max %6.1f %%   es. %s -> %s" % (k[1], k[2], v[0], v[1] * 100, v[2][0], v[2][1]))
