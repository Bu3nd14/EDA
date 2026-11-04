#!/usr/bin/env python3
"""L54a: some columns of a sequence run at some instants.
/usr/bin/python3 -I sonda.py <out.txt> <col,col,...> <t> [<t> ...]   (columns without v( ))"""
import sys

path, cols, ts = sys.argv[1], sys.argv[2].split(","), [float(x) for x in sys.argv[3:]]
with open(path) as f:
    nomi = f.readline().split()
    righe = [list(map(float, r.split())) for r in f if r.strip()]
idx = [nomi.index("v(%s)" % c) for c in cols]
print("t      " + " ".join("%10s" % c for c in cols))
for t in ts:
    r = min(righe, key=lambda x: abs(x[0] - t))
    print("%.4f " % r[0] + " ".join("%10.4f" % r[i] for i in idx))
