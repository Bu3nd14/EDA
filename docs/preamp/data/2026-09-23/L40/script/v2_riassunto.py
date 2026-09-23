#!/usr/bin/env python3
"""L40: la cella V2 (1 kHz, 100 k) prima e dopo, da <fase>/v2_1k_100k/analisi.csv
di v2_metodo.py. Per ogni grandezza e uscita il massimo di picco_V fra le righe
(S_* e' in dB, il resto in V), con la cella che lo da'. A senza segnale si legge
sulle celle lz* (ADR-036).
Uso: /usr/bin/python3 v2_riassunto.py
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leggi(fase):
    g = {}
    for r in csv.DictReader(open(os.path.join(BASE, fase, "v2_1k_100k", "analisi.csv"))):
        k = (r["grandezza"], r["uscita"])
        if k[0].startswith("A_") and not r["cella"].startswith("lz"):
            k = (k[0] + "(con segnale)", k[1])
        try:
            v = float(r["picco_V"])
        except ValueError:
            continue
        if k not in g or v > g[k][0]:
            g[k] = (v, r["cella"])
    return g


a, b = leggi("prima"), leggi("dopo")
print("%-22s %-9s %14s %14s   cella (dopo)" % ("grandezza", "uscita", "prima", "dopo"))
for k in sorted(set(a) | set(b)):
    va, vb = a.get(k, (float("nan"), "")), b.get(k, (float("nan"), ""))
    u = "dB" if k[0].startswith("S_") else "V"
    print("%-22s %-9s %12.4g%s %12.4g%s   %s" % (k[0], k[1], va[0], u, vb[0], u, vb[1]))
