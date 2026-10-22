#!/usr/bin/env python3
"""L45d2b3b2b1: dove il blocco del sorgente differisce dalla variante rv2 (regressione/misure_rv2.csv),
per deck. Solo stdlib, /usr/bin/python3 -I.

Uso: riassunto_rv2.py [soglia_rel=1e-3]
Per ogni deck: le misure, quante oltre la soglia relativa e, fra quelle, quante su una grandezza
«grande» (|valore| > 1e-3 volte il massimo |valore| della stessa misura nel deck: le altre sono zeri
numerici, dove la relativa non dice niente), e la peggiore delle grandi.
"""
import csv
import os
import re
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = float(sys.argv[1]) if len(sys.argv) > 1 else 1e-3
righe = [r for r in csv.DictReader(open(os.path.join(L, "regressione", "misure_rv2.csv")))
         if r["relativa"][:1].isdigit()]
scala = {}
for r in righe:
    k = (r["deck"], re.sub(r"#\d+$", "", r["misura"]))
    scala[k] = max(scala.get(k, 0.0), abs(float(r["rv2"])), abs(float(r["sorgente"])))
per = {}
for r in righe:
    d = per.setdefault(r["deck"], {"n": 0, "oltre": 0, "grandi": []})
    d["n"] += 1
    if float(r["relativa"]) > S:
        d["oltre"] += 1
        k = (r["deck"], re.sub(r"#\d+$", "", r["misura"]))
        if max(abs(float(r["rv2"])), abs(float(r["sorgente"]))) > 1e-3 * scala[k]:
            d["grandi"].append(r)
print("%-28s %7s %7s %7s  %s" % ("deck", "misure", "oltre", "grandi", "la peggiore delle grandi"))
for deck, d in sorted(per.items()):
    g = sorted(d["grandi"], key=lambda r: -float(r["relativa"]))
    w = ("%s %s -> %s (%s)" % (g[0]["misura"], g[0]["rv2"], g[0]["sorgente"], g[0]["relativa"])) if g else ""
    print("%-28s %7d %7d %7d  %s" % (deck, d["n"], d["oltre"], len(g), w))
