#!/usr/bin/env python3
"""L39 esplorazione: dal tb_loop_comp.csv il minimo del margine per (C_f, Miller,
modo) su carichi, sorgenti e cavo, e il crossover della cella a vuoto (1 mohm,
100 k, 1 fF). Controllo: la coppia (330p, 470p) a 0 dB deve ridare 55,55 gradi
di dopo/tb_loop (2,611 k, 3,3 nF, 100 k). Uso: /usr/bin/python3 riassumi_comp.py
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE, "esplorazione", "tb_loop_comp", "tb_loop_comp.csv")
r = list(csv.DictReader(open(p)))
g = {}
for x in r:
    k = (x["cf"], x["cm"], x["mode"])
    pm = float(x["pm_deg"])
    if k not in g or pm < g[k][0]:
        g[k] = (pm, x)
vuoto = {(x["cf"], x["cm"], x["mode"]): x for x in r
         if x["rsrc"] == "1m" and x["rload"] == "100k" and x["cprobe"] == "1f"}
print("%-6s %-6s %-5s %8s  %-28s %12s" % ("C_f", "Miller", "modo", "pm_min", "cella", "fc a vuoto"))
for k in sorted(g, key=lambda k: (k[2], r.index(g[k][1]))):
    pm, x = g[k]
    print("%-6s %-6s %-5s %8.2f  rl=%-5s rs=%-6s c=%-5s %12.4g  %s" % (
        k[0], k[1], k[2], pm, x["rload"], x["rsrc"], x["cprobe"],
        float(vuoto[k]["fcross_hz"]), "OK" if pm >= 60 else "sotto 60"))
