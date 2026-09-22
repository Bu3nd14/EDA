#!/usr/bin/env python3
"""L29b2: C2 di inviluppi sintetici puri al jack principale (nessuna cella): quale FORMA di
dissolvenza tiene C2 sotto 1 mV, e in quanto tempo. Uso: /usr/bin/python3 forme.py"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sur  # noqa: E402

FS = sur.FS
T0 = 0.5


def env(forma, T, n):
    g = [1.0] * n
    for k in range(n):
        u = min(max((k / FS - T0) / T, 0.0), 1.0)
        if forma == "lineare":
            g[k] = 1 - u
        elif forma == "coseno":
            g[k] = 0.5 + 0.5 * math.cos(math.pi * u)
        elif forma.startswith("db"):            # lineare in dB fino a -X dB, poi zero di colpo
            x = float(forma[2:])
            g[k] = 10 ** (-x * u / 20) if u < 1 else 0.0
        elif forma.startswith("dbc"):
            pass
    return g


for forma in ("lineare", "coseno", "db60", "db80", "db100"):
    for T in (0.5, 1.0, 2.0, 3.0, 6.0):
        n = int((T0 + T + 0.5) * FS)
        g = env(forma, T, n)
        v, i = sur.c2(g, T0, T, rif=0.0)
        print("%-8s T = %4.1f s   C2 %.3f mV  a %.3f s" % (forma, T, v * 1e3, i / FS), flush=True)
