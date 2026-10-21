#!/usr/bin/env python3
"""L45d2b2b1: the control - this lot's bench on the netlist before ADR-092, with L45c1's options and
load, against L45c1's analisi_psu.csv, column by column.

    confronta_l45c1.py <controllo.csv> [<out.txt>]
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L45C1 = os.path.join(QUI, "..", "..", "..", "2026-10-13", "L45c1", "analisi_psu.csv")
COL = ["t_fuori_ms", "t_mute_g_ms", "t_jack_ms", "t_guadagno_ms", "t_10_6_ms", "jack_prima",
       "vp_min", "vm_max", "out_meno_in_max_p", "out_meno_in_max_m", "raw_p_min", "raw_m_max"]
NUOVE = ["in_p", "in_m", "oi_pin_p", "oi_pin_m", "t_oi_p_ms", "t_oi_m_ms", "id510_pk_A", "id511_pk_A",
         "i2t_510", "i2t_511", "q510_mC", "q511_mC"]

a = {r["caso"]: r for r in csv.DictReader(open(L45C1))}
righe = []
for r in csv.DictReader(open(sys.argv[1])):
    c = r["caso"]
    righe.append("== %s" % c)
    for k in COL:
        x, y = a[c].get(k, ""), r.get(k, "")
        try:
            d = "%+.3g" % (float(y) - float(x))
        except ValueError:
            d = "uguale" if x == y else "DIVERSO"
        righe.append("  %-20s L45c1 %-10s qui %-10s %s" % (k, x, y, d))
    righe.append("  nuove: " + ", ".join("%s=%s" % (k, r.get(k, "")) for k in NUOVE))
testo = "\n".join(righe)
print(testo)
if len(sys.argv) > 2:
    open(sys.argv[2], "w").write(testo + "\n")
