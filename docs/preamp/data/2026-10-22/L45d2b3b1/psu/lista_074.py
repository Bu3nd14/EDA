#!/usr/bin/env python3
"""L45d2b2b1: ADR-074's cases of modi.py (RIGHE_074 at the three mains levels, D510 / D511 shorted),
one per line on stdout. With --nominale only the event mus."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

nom = "--nominale" in sys.argv
basi = tuple(b for b, *_ in modi.RIGHE_074) + ("f_d510_corto", "f_d511_corto")
for c in modi.SIMULATI:
    n = c[0]
    if n.rsplit("_", 1)[0] in basi and (not nom or n.endswith("_mus")):
        print(n)
