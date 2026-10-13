#!/usr/bin/env python3
"""L45a: massimo e minimo di ogni colonna di un .dat da T0 in poi, con l'istante: picchi.py DAT [T0]."""
import sys

NOMI = ["mainjack", "fix1jack", "fix2jack", "outa", "outf1", "outf2", "outb", "ipp", "imm"]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
mx = [(-1e99, 0)] * 9
mn = [(1e99, 0)] * 9
n = 0
for line in open(sys.argv[1]):
    try:
        v = [float(x) for x in line.split()]
    except ValueError:
        continue
    if v[0] < t0:
        continue
    n += 1
    for k, y in enumerate(v[1::2]):
        if y > mx[k][0]:
            mx[k] = (y, v[0])
        if y < mn[k][0]:
            mn[k] = (y, v[0])
print("punti: %d" % n)
for k, nm in enumerate(NOMI):
    print("%-9s max %10.4g a %.5f   min %10.4g a %.5f" % (nm, mx[k][0], mx[k][1], mn[k][0], mn[k][1]))
