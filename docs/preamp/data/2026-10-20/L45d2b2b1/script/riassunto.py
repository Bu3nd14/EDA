#!/usr/bin/env python3
"""L45d2b2b1: the columns of analizza_074.py that ADR-074 reads, one line per case.

    riassunto.py <analisi.csv> [<out.txt>]
"""
import csv
import sys

COL = [("caso", "%-24s"), ("t_jack_ms", "%7s"), ("t_10_6_ms", "%7s"), ("jack_prima", "%4s"),
       ("vp_al_jack", "%7s"), ("vm_al_jack", "%7s"), ("oi_pin_p", "%7s"), ("oi_pin_m", "%7s"),
       ("t_oi_m_ms", "%7s"), ("id510_pk_A", "%7s"), ("id511_pk_A", "%7s"), ("i2t_510", "%8s"),
       ("i2t_511", "%8s"), ("pr550_pk_W", "%7s"), ("er550_J", "%7s"), ("pr551_pk_W", "%7s"),
       ("er551_J", "%7s"), ("t_mute_g_ms", "%6s"), ("vp_fine", "%7s"), ("vm_fine", "%7s")]


def corto(x):
    try:
        return "%.3g" % float(x)
    except ValueError:
        return x


righe = [" ".join(f % c[:24] if c == "caso" else f % c[:7] for c, f in COL)]
for r in csv.DictReader(open(sys.argv[1])):
    righe.append(" ".join(f % (r[c] if c == "caso" else corto(r.get(c, ""))) for c, f in COL))
t = "\n".join(righe)
print(t)
if len(sys.argv) > 2:
    open(sys.argv[2], "w").write(t + "\n")
