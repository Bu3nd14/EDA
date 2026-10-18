#!/usr/bin/env python3
"""L60d1: i casi peggiori di run/p7_l56/<fase>/tb_mute_corto_l56.csv (p7_l56.py) per Q146
(l'inseguitore davanti al VAS) e Q148 (l'aiuto sullo specchio): potenza media, potenza di picco,
corrente di collettore, con la cella che li da'. Casi di tb_mute_corto: 0 normale, 1 mute,
2 / 3 corto sulla fissa 1 / 2, 4 corto sulla principale, 5 / 6 carico 10 / 100 ohm sulla fissa 1.
Solo stdlib.

Uso: sintesi_p7_l56.py <fase>
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
p = os.path.join(L, "run", "p7_l56", sys.argv[1], "tb_mute_corto_l56.csv")
rr = list(csv.DictReader(open(p)))
print("%d righe" % len(rr))


def cella(r):
    return "%s/%sdB/%sHz/vin %s/k %s/caso %s" % (r["blk"], r["modo_db"], r["f_hz"], r["vin_pk"],
                                                 r["k_att"], r["caso"])


for col, segno in (("p_q146", 1), ("pmax_q146", 1), ("icmin_q146", -1), ("p_q148", 1),
                   ("pmax_q148", 1), ("p_r153", 1), ("pmax_r153", 1)):
    if col not in rr[0]:
        continue  # p_r153: solo col blocco di ADR-087 (p7_l56.py ... r153)
    r = max(rr, key=lambda r: segno * float(r[col]))
    print("%-11s %12.4g   %s" % (col, float(r[col]), cella(r)))
print("per caso, il massimo della potenza media di Q146:")
for c in sorted({r["caso"] for r in rr}):
    s = [r for r in rr if r["caso"] == c]
    r = max(s, key=lambda r: float(r["p_q146"]))
    print("  caso %s: %.4g W media, %.4g W picco   %s" %
          (c, float(r["p_q146"]), float(r["pmax_q146"]), cella(r)))
