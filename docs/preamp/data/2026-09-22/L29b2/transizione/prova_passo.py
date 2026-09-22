#!/usr/bin/env python3
"""L29b2: il passo delle celle in cerca.py (0,1 ms) contro 1/96000 s, sulla v3: rilascio."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerca  # noqa: E402
import c2np  # noqa: E402

p = dict(cerca.v3(), td=6.0, acc=1e-3)
T = 7.0
for dt in (1e-4, 2e-5, 1.0 / 96000):
    cerca.DT = dt
    d, g, _ = cerca.corsa(p, 7.0 + 1.0, 8.0 + T + 1.5)
    gg, t0 = cerca.a_fs(g, 7.2, 8.0 + T)
    v = c2np.c2(gg, 8.0, T - 0.5, 1000.0, cerca.A, rif=g[0], t0=t0)[0]
    k = int(8.9 / dt)
    print("dt %.3g s: rilascio C2 %.3f mV   xs_s a 8,9 s? g(9,3 s) = %.4g" % (
        dt, v * 1e3, g[int(9.3 / dt)]), flush=True)
