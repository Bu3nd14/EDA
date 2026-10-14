#!/usr/bin/env python3
"""L45d1: the instrument on a known case. motore.py recomputes the ADR-070 columns of L45c2's table
(fmea_comando.csv) from the table's own rows - verdict, filtered peaks, cases pointed at - and
L45c2's classes (classi_l45c2.py, read where it is). Every column must come out equal; the script
exits 1 on the first list of differences. Solo stdlib.

    verifica_l45c2.py <data/2026-10-14/L45c2> [--sabota]
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore  # noqa: E402

L = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(L, "script"))
import classi_l45c2 as K  # noqa: E402

# what tabella_l45c2.py keeps outside the classes module, copied as it is there
K.N_FUORI = {"U503": K.N_FUORI_U503}
K.funzione = lambda ref, modo: ""
BASI_CLASSI = {"guasto_u503": (1, 2, "nessuno"), "corto_u503": (1, 2, "delta"),
               "cf_nodelta": (3, 1, "delta_latente"), "f_base_niente_ins": (2, 2, "funzione")}

pubblicata = list(csv.DictReader(open(os.path.join(L, "fmea_comando.csv"))))
COLONNE = ["G", "tipo", "fit_parte", "fonte", "frazione", "fit_modo", "P", "R", "priorita", "rimedi"]
righe = [{k: v for k, v in r.items() if k not in COLONNE} for r in pubblicata]
# the published 'nota' of a simulated row carries the class's note appended: take it back off
for r in righe:
    if r["come"].startswith("simulato") and r["ref"] != "-":
        n = K.SIM[r["caso"]][2]
        if n and r["nota"].endswith(n):
            r["nota"] = r["nota"][:-len(n)].rstrip("; ")
if "--sabota" in sys.argv:
    # the check must be able to fail: the 2 mV target moved to 10 mV (L45c2 has no peak between 1
    # and 2 mV, so 1 mV would change nothing; 10 mV takes the 6,44 mV rows of a lost Delta to 2)
    motore.OBIETTIVO = 1e-2
motore.classifica(righe, K, BASI_CLASSI)

diverse = []
for a, b in zip(pubblicata, righe):
    for k in COLONNE + ["nota"]:
        if str(a.get(k, "")) != str(b.get(k, "")):
            diverse.append("%s / %s / %s: pubblicata %r, ricalcolata %r" % (
                a["ref"], a["modo"], k, a.get(k, ""), b.get(k, "")))
n = sum(1 for r in pubblicata if r["priorita"])
print("L45c2: %d righe, %d classificate; colonne confrontate %s" % (len(pubblicata), n, COLONNE + ["nota"]))
if diverse:
    print("DIVERSE: %d" % len(diverse))
    for d in diverse:
        print("  " + d)
    sys.exit(1)
print("tutte uguali")
