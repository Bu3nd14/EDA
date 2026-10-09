#!/usr/bin/env python3
"""Stampa v(wip), v(bin), v(bout), v(jack) attorno allo scatto da un file wrdata (colonne
x ripetute: t wip t bin t bout t jack). Uso: leggi_onde.py <file> [t0 t1]"""
import sys

f = sys.argv[1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0195
t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0240
righe = []
for r in open(f):
    c = r.split()
    try:
        v = [float(x) for x in c]
    except ValueError:
        continue
    righe.append((v[0], v[1], v[3], v[5], v[7]))
print("%12s %12s %12s %12s %12s" % ("t_ms", "wip_mV", "bin_mV", "bout_mV", "jack_uV"))
ult = None
for t, w, b, o, j in righe:
    if t0 <= t <= t1:
        if ult is None or t - ult >= (t1 - t0) / 60:
            print("%12.5f %12.5f %12.5f %12.5f %12.3f" % (t * 1e3, w * 1e3, b * 1e3, o * 1e3, j * 1e6))
            ult = t
fin = righe[-1]
print("fine: t=%.4f ms wip=%.5f mV bin=%.5f mV jack=%.3f uV" % (fin[0] * 1e3, fin[1] * 1e3, fin[2] * 1e3, fin[4] * 1e6))
