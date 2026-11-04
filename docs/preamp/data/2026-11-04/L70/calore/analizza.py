#!/usr/bin/env python3
"""L70: L66's script/analizza_diss.py pointed at calore/ - the output devices WITH the heatsink of
ADR-099 (Q132 / Q133 24.5 C/W), Q193 403 C/W, every other R_thJA L45d2b3b1's (analizza_calore.py).
Solo stdlib, /usr/bin/python3 -I.

    /usr/bin/python3 -I calore/analizza.py   -> calore/calore_rail.csv, calore/analisi_jack_rail.csv
"""
import os
import sys

C = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(os.path.dirname(C)))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import analizza_calore as ac   # noqa: E402

ac.L = C
ac.a62.RTH.update({"q193": 403, "q132": 24.5, "q133": 24.5})

if __name__ == "__main__":
    ac.main(["analizza", "rail"])
