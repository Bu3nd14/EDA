#!/usr/bin/env python3
"""L60d2: il metodo nuovo di v2_metodo.py (la media con la correzione, ADR-087 / ADR-088) su corse vere
della matrice, prima della matrice intera: `analizza` su un sottoinsieme del manifesto, e B1 accanto
a b1_confronto.py di L60d1 (la media SENZA correzione, e il metodo di prima). Solo stdlib.

Uso: prova_metodo.py <cella>...      (celle di run/v2/manifest.csv con la corsa finita)
     -> run/prova_metodo/{manifest,analisi}.csv e la stampa
"""
import csv
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
R = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
V2 = os.path.join(L, "run", "v2")
OUT = os.path.join(L, "run", "prova_metodo")
os.makedirs(OUT, exist_ok=True)
celle = set(sys.argv[1:])
righe = list(csv.DictReader(open(os.path.join(V2, "manifest.csv"))))
sel = [r for r in righe if r["cella"] in celle]
with open(os.path.join(OUT, "manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, list(righe[0].keys()))
    w.writeheader()
    w.writerows(sel)
an = os.path.join(OUT, "analisi.csv")
subprocess.run(["/usr/bin/python3", os.path.join(R, "scripts", "v2_metodo.py"), "analizza",
                os.path.join(OUT, "manifest.csv"), V2, an], check=True)
for r in csv.DictReader(open(an)):
    print("%-22s %-3s %-9s media corretta %10s V   puntuale %10s V" % (
        r["cella"], r["grandezza"], r["uscita"], r["picco_V"], r["picco_puntuale_V"]))
B1C = os.path.join(R, "docs", "preamp", "data", "2026-10-18", "L60d1", "script", "b1_confronto.py")
for r in sel:
    if r["tipo"] == "rif_sempre":
        for col in ("0", "1", "2"):
            subprocess.run(["/usr/bin/python3", "-I", B1C, os.path.join(V2, r["file"]), "0.5", col])
