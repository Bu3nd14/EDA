#!/usr/bin/env python3
"""L45d2b3b1: the cases of RIGHE_NUOVE (modi.py) at the three mains levels, one per line on stdout."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

basi = tuple(b for b, *_ in modi.RIGHE_NUOVE)
for c in modi.SIMULATI:
    n = c[0]
    if n.rsplit("_", 1)[0] in basi and n.rsplit("_", 1)[1] in ("musm10s", "muss", "musp10s"):
        print(n)
