#!/usr/bin/env python3
"""L45d2b2b2: the source's cases of modi.py after ADR-094 (RIGHE_SORGENTE at the three mains levels,
events musm10s / muss / musp10s), one per line on stdout. With --nominale only muss."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

nom = "--nominale" in sys.argv
basi = tuple(b for b, *_ in modi.RIGHE_SORGENTE)
for c in modi.SIMULATI:
    n = c[0]
    if n.rsplit("_", 1)[0] in basi and n.rsplit("_", 1)[1] in ("musm10s", "muss", "musp10s") and (not nom or n.endswith("_muss")):
        print(n)
