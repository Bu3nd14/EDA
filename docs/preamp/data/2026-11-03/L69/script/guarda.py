#!/usr/bin/env python3
"""L68: a few nodes of one run at a few instants (s after TE = 3.0), to read a case by eye. Solo stdlib.
    /usr/bin/python3 -I script/guarda.py <caso> <t1,t2,...> [nodo ...]
"""
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caso, tt = sys.argv[1], [float(x) for x in sys.argv[2].split(",")]
nodi = sys.argv[3:] or ["v(vrelay)", "v(mute_cmd)", "v(permit_cmd)", "v(mute_g)", "v(permit_g)", "v(mute_req)",
                        "v(permit_req)", "v(vplus)", "v(k501_f)", "v(at_mrq)", "v(at_pg)"]
d = os.path.join(L, "seq", "oggi", caso)
f = [x for x in os.listdir(d) if x.endswith("_out.txt")][0]
with open(os.path.join(d, f)) as h:
    nomi = h.readline().split()
    idx = [nomi.index(n) for n in nodi]
    righe = [list(map(float, r.split())) for r in h if r.strip()]
t = [r[0] for r in righe]
print("%8s " % "t-TE" + " ".join("%12s" % n for n in nodi))
for x in tt:
    k = min(range(len(t)), key=lambda j: abs(t[j] - 3.0 - x))
    print("%8.4f " % (t[k] - 3.0) + " ".join("%12.4f" % righe[k][i] for i in idx))
