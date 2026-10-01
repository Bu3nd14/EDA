#!/usr/bin/env python3
"""L46a: dal confronto grezzo, le cifre che si muovono oltre una soglia relativa,
per deck, esclusi i deck d'anello (letti da margini.py) e le chiavi di `meas`
spezzate da una Note (#37: from, om, rom...). Per ogni deck al piu' N righe,
ordinate per |delta_rel|.

Uso: /usr/bin/python3 mosse.py [soglia=0.01] [N=12]
"""
import csv
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
soglia = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
SALTA = {"tb_loop", "tb_loop_blockA", "tb_loop_bufferfissa", "tb_idss_loop"}
per = {}
for r in csv.DictReader(open(os.path.join(BASE, "confronto_grezzo.csv"))):
    if r["deck"] in SALTA or r["delta_rel"] == "":
        continue
    if abs(float(r["delta_rel"])) >= soglia:
        per.setdefault(r["deck"], []).append(r)
for d in sorted(per):
    rr = sorted(per[d], key=lambda r: -abs(float(r["delta_rel"])))
    print("== %s: %d cifre oltre %.0f%%" % (d, len(rr), soglia * 100))
    for r in rr[:n]:
        print("   %-26s %-34s %12s -> %-12s (%+.1f%%)" % (
            r["sorgente"][:26], r["chiave"][:34], r["prima"], r["dopo"], 100 * float(r["delta_rel"])))
