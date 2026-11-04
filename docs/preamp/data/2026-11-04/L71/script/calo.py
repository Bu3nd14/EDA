#!/usr/bin/env python3
"""L71: V+ / V- around the jack's return in one run: the minimum after TE, when, and the values
every 5 ms in the 60 ms before the closure and 30 ms after it.
    /usr/bin/python3 -I script/calo.py <seq_dir>/<etichetta>/<caso>"""
import os, sys
d = sys.argv[1]
f = [x for x in os.listdir(d) if x.endswith("_g1_out.txt")][0]
with open(os.path.join(d, f)) as h:
    n = h.readline().split()
    I = [n.index(c) for c in ("time", "v(vplus)", "v(vminus)", "v(vrelay)", "v(mute_cmd)", "v(k501_f)")]
    R = [[float(r.split()[i]) for i in I] for r in h if len(r.split()) == len(n)]
TE = 3.0
dopo = [r for r in R if r[0] >= TE]
mn = min(dopo, key=lambda r: r[1])
mx = max(dopo, key=lambda r: r[2])
print("V+ min %.4f V a %.1f ms; V- max %.4f V a %.1f ms" % (mn[1], (mn[0]-TE)*1e3, mx[2], (mx[0]-TE)*1e3))
ch = next(r[0] for i, r in enumerate(dopo[1:], 1) if dopo[i-1][3]-dopo[i-1][4] < 9.6 <= r[3]-r[4])
k5 = [r[0] for i, r in enumerate(dopo[1:], 1) if (dopo[i-1][5] > 0.5) != (r[5] > 0.5)]
print("chiusura del jack %.1f ms; K501 cambia a %s ms" % ((ch-TE)*1e3, ", ".join("%.1f" % ((x-TE)*1e3) for x in k5)))
for dt in range(-60, 35, 5):
    r = min(R, key=lambda q: abs(q[0] - ch - dt*1e-3))
    print("  %+4d ms  V+ %.4f  V- %.4f" % (dt, r[1], r[2]))
print("  fine     V+ %.4f  V- %.4f" % (R[-1][1], R[-1][2]))
