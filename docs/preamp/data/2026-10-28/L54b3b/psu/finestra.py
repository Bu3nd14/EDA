#!/usr/bin/env python3
"""L54b3a: some probes of one run between two instants, every <passo> samples.
Solo stdlib. /usr/bin/python3 -I finestra.py <out.txt> <t0> <t1> <passo> <sonda> [...]"""
import sys

path, t0, t1, passo = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
sonde = sys.argv[5:]
with open(path) as f:
    nomi = f.readline().split()
    ks = [nomi.index(s) for s in sonde]
    print("t " + " ".join(sonde))
    n = 0
    for r in f:
        x = r.split()
        if not x:
            continue
        t = float(x[0])
        if t0 <= t <= t1:
            if n % passo == 0:
                print("%.4f " % t + " ".join("%.3f" % float(x[k]) for k in ks))
            n += 1
