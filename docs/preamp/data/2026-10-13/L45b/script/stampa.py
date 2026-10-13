#!/usr/bin/env python3
"""L45b: stampa compatta di un analisi_*.csv (diagnostica). Uso: stampa.py ANALISI.csv [--fuori]"""
import csv
import sys

solo_fuori = "--fuori" in sys.argv
for r in csv.DictReader(open(sys.argv[1])):
    if solo_fuori and r.get("p10", "").startswith("entro"):
        continue
    print("%-14s %-16s main g=%-9s A=%-9s %7sms | fix1 g=%-9s %7sms | fix2 g=%-9s %7sms | %s | %s %s" % (
        r["modo"][:14], r["variante"][-16:], r.get("main_grezzo_V"), r.get("main_A_V"),
        r.get("main_sopra_ms"), r.get("fix1_grezzo_V"), r.get("fix1_sopra_ms"),
        r.get("fix2_grezzo_V"), r.get("fix2_sopra_ms"), r.get("p10"), r.get("stato"), r.get("t_fine")))
