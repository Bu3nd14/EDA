#!/usr/bin/env python3
"""toll_L16.py - minimum phase margin over L27's tolerance corners (C124 and
C137 +/-5 %, R_iso +/-1 %, loads 100 k / 10 k, cable 2 - 4.7 nF) for the
attenuator source 2.5 k (L27's worst) and 2.611 k (the worst the trim adds,
(10 k + 442 ohm)/4). Input: toll_L16_tab.csv from deck/toll_L16.cir.

Usage: toll_L16.py <toll_L16_tab.csv>
"""
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1])))
empty = sum(1 for r in rows for v in r.values() if v.strip() == "")
print(f"{len(rows)} righe; celle vuote: {empty}")
assert rows and not empty
for mode in ("0", "3"):
    for rs in ("2.5k", "2.611k"):
        sel = [r for r in rows if r["mode"] == mode and r["rsrc"] == rs]
        w = min(sel, key=lambda r: abs(float(r["pm_deg"])))
        print(f"mode {mode} rsrc {rs}: min {abs(float(w['pm_deg'])):.3f} deg "
              f"({len(sel)} righe) | C124 {w['c124']} C137 {w['c137']} "
              f"R_iso {w['riso']} carico {w['rload']} cavo {w['ccable']}")
