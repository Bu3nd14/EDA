#!/usr/bin/env python3
"""L45c2: the list of the sequence cases, one per line, on stdout: the base cases the rows
compare against (perdita and guasto_u501 were run first, alone, to check the copy against L45c1;
the others are L41c's: the soft power-down, U502, U503 off and its output shorted, and the
counterfactual without D), then every simulated fault of modi.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

BASI = ["perdita", "guasto_u501", "spegnimento_l", "guasto", "guasto_u503", "corto_u503", "cf_nodelta"]
for c in BASI + [x[0] for x in modi.SIMULATI]:
    print(c)
