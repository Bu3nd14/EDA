#!/usr/bin/env python3
"""L45d2b2c: ADR-078's cases of modi.py (RIGHE_078 and BASE_078 at the three mains levels, events
musm10 / mus / musp10), one per line on stdout."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

basi = tuple(b for b, *_ in modi.RIGHE_078 + modi.BASE_078)
for c in modi.SIMULATI:
    n = c[0]
    if n.rsplit("_", 1)[0] in basi and n.rsplit("_", 1)[1] in ("musm10", "mus", "musp10"):
        print(n)
