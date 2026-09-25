#!/usr/bin/env python3
"""L29d: il controfattuale. La geometria N della sonda (serie sempre chiusa, bleed 1 T) deve ridare
L29c cella per cella. Toglie il suffisso _N dalle celle della sonda e confronta con
confronta_analisi.py le celle comuni con l'analisi di L29c (matrice/veloci/analisi_a.csv).

Uso: controfattuale_N.py sonda/analisi.csv out.csv
"""
import csv
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
L29C = os.path.join(REPO, "docs", "preamp", "data", "2026-09-23", "L29c")
ana, out = sys.argv[1:3]
tmp = os.path.join(os.path.dirname(os.path.abspath(out)), "_analisi_N.csv")
with open(ana) as f:
    r = csv.DictReader(f)
    campi = r.fieldnames
    righe = []
    for x in r:
        c = x["cella"]
        # gm0x10_lz_N_c -> gm0x10_lz_c ; mev_lz_N -> mev_lz ; on_r300p_N -> on_r300p
        for suf in ("_N_i", "_N_c", "_N"):
            if c.endswith(suf):
                x["cella"] = c[:-len(suf)] + suf[2:]
                righe.append(x)
                break
with open(tmp, "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(righe)
subprocess.run(["/usr/bin/python3", os.path.join(L29C, "script", "confronta_analisi.py"),
                os.path.join(L29C, "matrice", "veloci", "analisi_a.csv"), tmp, out], check=True)
