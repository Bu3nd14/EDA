#!/usr/bin/env python3
"""L55: le parti oltre i limiti nei guasti dei finali, per variante (calore_<v>.csv, colonne
«oltre_i_limiti_60C» e «oltre_diodi_60C» di analizza_calore.py). ATTENZIONE: quella colonna giudica i
finali con la R_thJA del MJE nudo (62,5 C/W, analizza_tr.RTH): per i finali vale dissipatore_l55.py.
Qui conta il resto (le 22 ohm, i diodi di ADR-095, il VAS, Q127). Solo stdlib, /usr/bin/python3 -I.

Uso: oltre_limiti.py fmje c243 c243m
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for v in sys.argv[1:]:
    n = 0
    for r in csv.DictReader(open(os.path.join(L, "calore_%s.csv" % v))):
        a, b = r.get("oltre_i_limiti_60C", ""), r.get("oltre_diodi_60C", "")
        if a or b:
            n += 1
            print("%-6s %-6s %-8s P132 %s P133 %s P_d158 %s P_d159 %s | %s | %s" % (
                v, r["posizione"], r["modo"], r["P_q132_W"], r["P_q133_W"], r["P_d158_W"],
                r["P_d159_W"], a, b))
    print("%s: %d righe con qualcosa oltre" % (v, n))
