#!/usr/bin/env python3
"""L45c1: the list of the sequence cases, one per line, on stdout: the four base cases the
welded-NO rows need (perdita and guasto_u501 were run first, alone, to check the copy against
L56; spegnimento_l and guasto with the faults), then every simulated fault of modi.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modi  # noqa: E402

for c in ["perdita", "guasto_u501", "spegnimento_l", "guasto"] + [x[0] for x in modi.SIMULATI]:
    print(c)
