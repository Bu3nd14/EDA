#!/usr/bin/env python3
"""L45a: quante volte ogni parte esce dai suoi limiti di calore nella FMEA (dalla colonna calore di
fmea_blocco.csv), e i casi oltre il tetto che NON hanno un secondo guasto per calore."""
import csv
import os
import re

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
righe = list(csv.DictReader(open(os.path.join(L, "fmea_blocco.csv"))))
conta = {}
for r in righe:
    for pezzo in r["calore"].split(";"):
        m = re.match(r"\s*(\w+)", pezzo)
        if m:
            conta[m.group(1)] = conta.get(m.group(1), 0) + 1
for k, v in sorted(conta.items(), key=lambda x: -x[1]):
    print("%-6s %d modi" % (k, v))
print("modi con calore oltre i limiti: %d su %d" % (sum(1 for r in righe if r["calore"]), len(righe)))
print("oltre il tetto al jack principale (B, 0 dB): %d" % sum(1 for r in righe if r["B_esito"] == "SOPRA IL TETTO"))
print("di cui senza calore oltre i limiti: %d" % sum(1 for r in righe if r["B_esito"] == "SOPRA IL TETTO" and not r["calore"]))
print("entro il tetto ma con calore oltre i limiti: %s" % ", ".join(
    r["modo"] for r in righe if r["B_esito"] != "SOPRA IL TETTO" and r["calore"]))
