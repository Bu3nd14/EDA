#!/usr/bin/env python3
"""L45d2b3b2a: la potenza massima delle parti nuove di rv2 (R161, R162, R167, R169, Q168) e di quelle
che cambiano valore (R101, R123), su tutti i modi e le posizioni del banco del calore, e il caso che
la da'. Per la taglia in distinta (L45d2b3b2b). Solo stdlib, /usr/bin/python3 -I.

Uso: nuove_max.py [variante]     (default rv2) stampa e scrive nuove_max_<v>.csv
"""
import csv
import glob
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = sys.argv[1] if len(sys.argv) > 1 else "rv2"
PARTI = ("r101", "r123", "r161", "r162", "r167", "r169", "q168")
RTH = {"q168": 403}

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
out = []
for p in PARTI:
    x, dove = m[p]
    g = "Tj %.0f C a 60 C d'aria" % (60 + x * RTH[p]) if p in RTH else "%.3f W contro 0,25 W" % x
    out.append({"parte": p.upper(), "P_max_W": "%.4f" % x, "giudizio": g, "caso": dove})
    print("%-5s %8.4f W  %-28s %s" % (p.upper(), x, g, dove))
with open(os.path.join(L, "nuove_max_%s.csv" % V), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
