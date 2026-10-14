#!/usr/bin/env python3
"""L45c2: a look at a sequence pass's waveforms (wrdata, the probes of genera_tb_psu.py).
Solo stdlib.

    guarda.py <out.txt> <t0> <t1> <dt> <col> [<col> ...]

Prints one row every dt seconds from t0 to t1 (the nearest sample), the columns by their probe
name without v( ): e.g. vplus mute_g mute_cmd vrelay. The last row is the file's last sample."""
import sys

path, t0, t1, dt = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
cols = sys.argv[5:]
f = open(path)
head = f.readline().split()
idx = [head.index("v(%s)" % c) for c in cols]
print("%10s " % "t" + " ".join("%10s" % c for c in cols))
prossimo = t0
ultima = None
for r in f:
    v = r.split()
    if len(v) != len(head):
        continue
    t = float(v[0])
    ultima = v
    if t >= prossimo and t <= t1:
        print("%10.5f " % t + " ".join("%10.4f" % float(v[i]) for i in idx))
        prossimo += dt
if ultima is not None:
    print("%10.5f " % float(ultima[0]) + " ".join("%10.4f" % float(ultima[i]) for i in idx) + "  (ultima)")
