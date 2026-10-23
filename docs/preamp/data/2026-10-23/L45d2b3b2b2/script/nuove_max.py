#!/usr/bin/env python3
"""L45d2b3b2b2: la potenza massima delle parti nuove del sorgente (R190, R191, R192, R194, Q193) e di
R101 / R123 sui modi di una variante, da run/<v>_*/<modo>/<modo>_fine.csv; e il confronto con
nuove_max_rv2.csv di L45d2b3b2a con la mappa delle sigle (limitations #22). Solo stdlib,
/usr/bin/python3 -I.

Uso: nuove_max.py [variante=sorg]     stampa e scrive nuove_max_<v>.csv
"""
import csv
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
A = os.path.join(os.path.dirname(os.path.dirname(L)), "2026-10-22", "L45d2b3b2a")
V = sys.argv[1] if len(sys.argv) > 1 else "sorg"
MAPPA = {"R161": "R190", "R162": "R191", "R167": "R192", "Q168": "Q193", "R169": "R194"}
PARTI = ("r101", "r123", "r190", "r191", "r192", "r194", "q193")
RTH = {"q193": 403}

m = {p: (0.0, "") for p in PARTI}
for f in glob.glob(os.path.join(L, "run", V + "_*", "*", "*_fine.csv")):
    cart, modo = f.split(os.sep)[-3:-1]
    for r in csv.reader(open(f)):
        if len(r) == 2 and r[0].startswith("p_") and r[0][2:] in m:
            try:
                x = abs(float(r[1]))
            except ValueError:
                continue
            if x > m[r[0][2:]][0]:
                m[r[0][2:]] = (x, "%s %s" % (cart[len(V) + 1:], modo))
banco = {MAPPA.get(r["parte"], r["parte"]): r for r in csv.DictReader(open(os.path.join(A, "nuove_max_rv2.csv")))}
out = []
for p in PARTI:
    x, dove = m[p]
    g = "Tj %.0f C a 60 C d'aria" % (60 + x * RTH[p]) if p in RTH else "%.3f W" % x
    b = banco.get(p.upper(), {})
    caso_b = b.get("caso", "")
    for k, n in MAPPA.items():
        caso_b = caso_b.replace(k, n)
    out.append({"parte": p.upper(), "P_max_W": "%.4f" % x, "giudizio": g, "caso": dove,
                "banco_rv2_W": b.get("P_max_W", ""), "banco_rv2_caso": caso_b})
    print("%-5s %8.4f W  %-24s %-22s banco %s W %s" % (p.upper(), x, g, dove, b.get("P_max_W", ""), caso_b))
with open(os.path.join(L, "nuove_max_%s.csv" % V), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
