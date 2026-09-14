#!/usr/bin/env python3
"""v1_trim.py - V1 readings for L16 (the trim on the variable-output branch).

  1. tb_loop (block B): every row L27 had must come back with the SAME value
     (the attenuator sources 1m / 1k / 2.5k are unchanged); then the minimum
     margin at the jack (pos 1, ADR-024) per mode and source, including the two
     new sources the trim gives block B at mid-travel, (10 k + R_th)/4.
  2. tb_loop_blockA_trim: the minimum over CWIRE <= 1 nF (ADR-024) per
     candidate ladder, trim position and source; and the same minimum of the
     no-trim table for reference.

Usage: v1_trim.py <L27 tb_loop_margini.csv> <new tb_loop_margini.csv>
                  <new tb_loop_blockA.csv> <new tb_loop_blockA_trim.csv>
"""
import csv
import sys

CAP = {"1f": 1e-15, "47p": 47e-12, "100p": 100e-12, "220p": 220e-12,
       "470p": 470e-12, "1n": 1e-9, "1.5n": 1.5e-9, "2.2n": 2.2e-9,
       "2.7n": 2.7e-9, "3.3n": 3.3e-9, "4.7n": 4.7e-9}


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


old, new = rows(sys.argv[1]), rows(sys.argv[2])
key = ("mode", "rsrc", "pos", "cprobe", "rload")
newd = {tuple(r[k] for k in key): r for r in new}
assert old and new, "tabella vuota"
worst, missing = 0.0, 0
for r in old:
    k = tuple(r[c] for c in key)
    if k not in newd:
        missing += 1
        continue
    worst = max(worst, abs(float(r["pm_deg"]) - float(newd[k]["pm_deg"])))
print(f"tb_loop: {len(old)} righe L27, {len(new)} righe nuove, {missing} chiavi "
      f"L27 mancanti, scarto massimo di margine sulle chiavi comuni {worst:.3g} deg")
empty = [r for r in new if not r["pm_deg"]]
print(f"tb_loop: celle di margine vuote {len(empty)}")

print("\nblocco B, sonda al jack (pos 1), minimo sulla spazzata fino a 4.7 nF:")
for mode in ("0db", "3db", "10db"):
    for rs in ("2.5k", "2.571k", "2.611k"):
        sel = [r for r in new if r["mode"] == mode and r["rsrc"] == rs
               and r["pos"] == "1"]
        m = min(sel, key=lambda r: float(r["pm_deg"]))
        print(f"  {mode:>4} rsrc {rs:>6}: {float(m['pm_deg']):8.3f} deg "
              f"(C {m['cprobe']}, carico {m['rload']}, {len(sel)} righe)")

base = rows(sys.argv[3])
trim = rows(sys.argv[4])
print(f"\nblocco A: {len(base)} righe senza trim, {len(trim)} righe col trim, "
      f"celle vuote {sum(1 for r in trim if not r['pm_deg'])}")
sel = [r for r in base if r["carico"] == "1" and CAP[r["cwire"]] <= 1e-9]
m = min(sel, key=lambda r: float(r["pm_deg"]))
print(f"  senza trim (carico 1, CWIRE <= 1 nF): {float(m['pm_deg']):.3f} deg "
      f"(rsrc {m['rsrc']}, C {m['cwire']})")
for cand in ("1", "2"):
    for pos in ("0", "6", "12"):
        sel = [r for r in trim if r["cand"] == cand and r["pos"] == pos
               and CAP[r["cwire"]] <= 1e-9]
        m = min(sel, key=lambda r: float(r["pm_deg"]))
        tdc = min(float(r["tdb_10hz"]) for r in sel)
        print(f"  cand {cand} pos {pos:>2}: {float(m['pm_deg']):8.3f} deg "
              f"(rsrc {m['rsrc']}, C {m['cwire']}); |T| a 10 Hz >= {tdc:.2f} dB")
