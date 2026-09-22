#!/usr/bin/env python3
"""L29b2: gli stati delle due celle (log10 R) e la profondita' in una finestra, da <corsa>_stati.dat
di build.py (colonne v(xls.xs) v(xlp.xs) v(dep) v(ina)). Con il livello relativo all'ingresso
del blocco A calcolato dalle resistenze: R_p || R_IN / (R_s + 1,5 + R_p || R_IN).

Uso:  /usr/bin/python3 stati.py FILE_stati.dat T0 T1 [PASSO=0.05]
"""
import math
import sys

f, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
dt = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
RIN = 1e6
prossimo = t0
print("   t [s]      d   log10Rs  log10Rp   livello [dB]")
with open(f) as fh:
    for line in fh:
        p = line.split()
        if len(p) < 8:
            continue
        try:
            t = float(p[0])
        except ValueError:
            continue
        if t < prossimo:
            continue
        if t > t1:
            break
        xs, xp, d = float(p[1]), float(p[3]), float(p[5])
        rs, rp = 10 ** xs, 10 ** xp
        par = rp * RIN / (rp + RIN)
        g = par / (rs + 1.5 + par)
        print("%8.3f  %5.3f  %7.3f  %7.3f   %8.2f" % (t, d, xs, xp, 20 * math.log10(g)))
        prossimo += dt
