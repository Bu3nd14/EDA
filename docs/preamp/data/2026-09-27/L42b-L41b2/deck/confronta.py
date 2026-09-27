#!/usr/bin/env python3
"""L41b2: two passes of the core's outputs agree? /usr/bin/python3 confronta.py <a.csv> <b.csv>

The same rows, the same values (requests, DAC codes, state), every time
within 0.2 ms: two samples of the 100 us grid the bridge reads, where the
interrupt's crossing time moves by microseconds from one pass to the next
(the interpolation on the grid sees the new output after the crossing).
Exit 0 if they agree; prints the first difference otherwise.
"""
import sys

TOL = 2e-4


def righe(p):
    out = []
    for r in open(p):
        if r.startswith("t,"):
            continue
        v = r.strip().split(",")
        out.append((float(v[0]), tuple(v[1:9])))
    return out


a, b = righe(sys.argv[1]), righe(sys.argv[2])
if len(a) != len(b):
    print("righe diverse: %d contro %d" % (len(a), len(b)))
    sys.exit(1)
worst = 0.0
for (ta, va), (tb, vb) in zip(a, b):
    if va != vb:
        print("valori diversi a %.6f / %.6f: %s contro %s" % (ta, tb, va, vb))
        sys.exit(1)
    worst = max(worst, abs(ta - tb))
    if abs(ta - tb) > TOL:
        print("tempo diverso: %.6f contro %.6f" % (ta, tb))
        sys.exit(1)
print("uguali: %d righe, scarto massimo dei tempi %.1f us" % (len(a), worst * 1e6))
