#!/usr/bin/env python3
"""L60d2: P7 con R153 in corto (run/p7_r153cc/, p7_r153cc.py). Q146 e Q148 nel caso peggiore (come
sintesi_p7_l56.py di L60d1), e ogni potenza di P7 contro il blocco sano (p7/dopo/). Casi di
tb_mute_corto: 0 normale, 1 mute, 2 / 3 corto sulla fissa 1 / 2, 4 corto sulla principale,
5 / 6 carico 10 / 100 ohm sulla fissa 1. Solo stdlib.

Uso: sintesi_p7_r153cc.py [cartella di run/, p7_r153cc_1]   -> stampa, e p7_r153cc.txt
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
# la corsa con R153 a 1 ohm: con 1 mOhm le dieci celle a +10 dB, 3,818 V, attenuatore 0,79 finiscono in un punto di
# lavoro sbagliato, rail a 48 W e i blocchi sani spenti (limitations #59); a 1 ohm no
RUN = os.path.join(L, "run", sys.argv[1] if len(sys.argv) > 1 else "p7_r153cc_1")
out = []


def cella(r):
    return "%s/%sdB/%sHz/caso %s" % (r["blk"], r["modo_db"], r["f_hz"], r["caso"])


rr = list(csv.DictReader(open(os.path.join(RUN, "tb_mute_corto_l56.csv"))))
out.append("R153 in corto, %d righe di Q146 / Q148 (SOT-23: 0,31 W)" % len(rr))
for col, segno in (("p_q146", 1), ("pmax_q146", 1), ("icmin_q146", -1), ("p_q148", 1),
                   ("pmax_q148", 1)):
    r = max(rr, key=lambda r: segno * float(r[col]))
    out.append("  %-11s %10.4g   %s" % (col, float(r[col]), cella(r)))
sano = list(csv.DictReader(open(os.path.join(L, "p7", "dopo", "tb_mute_corto",
                                             "tb_mute_corto_regime.csv"))))
gu = list(csv.DictReader(open(os.path.join(RUN, "tb_mute_corto_regime.csv"))))
out.append("P7, massimo di ogni potenza media: blocco sano / R153 in corto")
for c in sorted(k for k in sano[0] if k.startswith("p_")):
    a = max(float(r[c] or 0) for r in sano)
    rb = max(gu, key=lambda r: float(r[c] or 0))
    out.append("  %-10s %10.4g W  %10.4g W   %s" % (c, a, float(rb[c] or 0), cella(rb)))
print("\n".join(out))
open(os.path.join(L, "p7_r153cc.txt"), "w").write("\n".join(out) + "\n")
