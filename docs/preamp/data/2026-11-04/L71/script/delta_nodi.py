#!/usr/bin/env python3
"""L71: the nodes of Delta (the permissive's delay after the mute) around the music in one run: the
mute's request AT_MRQ, its hold AT_PRT (C550 from AT_MRQ through a diode, 4.7 MOhm to ground, against
VREF), PERMIT_REQ, PERMIT_T (C528's node), PERMIT_G, and the two coils' drive, every <passo> ms
from <da> to <a> ms after TE.
    /usr/bin/python3 -I script/delta_nodi.py <seq_dir>/<etichetta>/<caso> <da_ms> <a_ms> [passo_ms]"""
import os
import sys

d, da, a = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
passo = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
f = [x for x in os.listdir(d) if x.endswith("_g1_out.txt")][0]
C = ["time", "v(front_in)", "v(at_mrq)", "v(at_prt)", "v(permit_req)", "v(permit_t)", "v(permit_g)",
     "v(mute_req)", "v(mute_g)", "v(vrelay)", "v(mute_cmd)", "v(permit_cmd)"]
with open(os.path.join(d, f)) as h:
    n = h.readline().split()
    I = [n.index(c) for c in C]
    R = [[float(r.split()[i]) for i in I] for r in h if len(r.split()) == len(n)]
TE = 3.0
print("   ms   front at_mrq at_prt p_req permit_t permit_g m_req mute_g  jack(V) perm(V)")
t = da
while t <= a + 1e-9:
    r = min(R, key=lambda q: abs(q[0] - TE - t * 1e-3))
    print("%7.1f %5.2f %6.3f %6.3f %5.2f %8.3f %8.3f %5.2f %6.3f %8.2f %7.2f" % (
        t, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9] - r[10], r[9] - r[11]))
    t += passo
