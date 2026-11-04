#!/usr/bin/env python3
"""L45d2b2b2: ADR-075's cases of modi.py (RIGHE_075 at the three mains levels), one per line on
stdout. With --nominale only the event mus."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

nom = "--nominale" in sys.argv
basi = tuple(b for b, *_ in modi.RIGHE_075)
for c in modi.SIMULATI:
    n = c[0]
    if n.rsplit("_", 1)[0] in basi and n.rsplit("_", 1)[1] in ("musm10", "mus", "musp10") and (not nom or n.endswith("_mus")):
        print(n)
