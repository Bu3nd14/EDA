#!/usr/bin/env python3
"""L45a: la forma d'onda di una corsa, campionata: forma.py DAT [t1 t2 ...].
Colonne del .dat: mainjack fix1jack fix2jack outa outf1 outf2 outb i(vpp) i(vmm)."""
import sys

NOMI = ["mainjack", "fix1jack", "fix2jack", "outa", "outf1", "outf2", "outb", "ipp", "imm"]
t, rows = [], []
for line in open(sys.argv[1]):
    p = line.split()
    try:
        v = [float(x) for x in p]
    except ValueError:
        continue
    t.append(v[0])
    rows.append(v[1::2])
tempi = [float(x) for x in sys.argv[2:]] or [0.299, 0.3001, 0.301, 0.303, 0.31, 0.33, 0.4, 0.6, 1.0, 2.0, 2.29]
print("t      " + " ".join("%10s" % n for n in NOMI))
for tq in tempi:
    i = min(range(len(t)), key=lambda k: abs(t[k] - tq))
    print("%.4f " % t[i] + " ".join("%10.4g" % x for x in rows[i]))
