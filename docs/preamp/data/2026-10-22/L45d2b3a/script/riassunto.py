#!/usr/bin/python3
"""L45d2b3a: the envelope summed up - per rail and regulator crossover, the worst and best phase
margin of the rail form, how many cases are under 60 and under 45 degrees, and the worst case's row.
Then the same at the rail's own load only (no 0.1 / 0.03 A).

usage: riassunto.py <inviluppo.csv> <out csv>
"""
import csv
import sys

rows = list(csv.DictReader(open(sys.argv[1])))
out = ["rail,carico,fc_Hz,casi,pm_min_deg,pm_max_deg,sotto_60,sotto_45,caso_peggiore"]
for carico in ("tutti", "regime"):
    for rail in ("piu", "meno"):
        fcs = sorted(set(float(r["fc_Hz"]) for r in rows if r["rail"] == rail))
        for fc in fcs:
            sel = [r for r in rows if r["rail"] == rail and r["forma"] == "rail"
                   and float(r["fc_Hz"]) == fc and (carico == "tutti" or float(r["i_A"]) > 0.2)]
            pm = [float(r["pm_min_deg"]) for r in sel]
            w = min(sel, key=lambda r: float(r["pm_min_deg"]))
            out.append("%s,%s,%g,%d,%.1f,%.1f,%d,%d,esr_hold %s esr_audio %s cavo %s/%s i %s T %s" % (
                rail, carico, fc, len(sel), min(pm), max(pm), sum(x < 60 for x in pm),
                sum(x < 45 for x in pm), w["esr_hold_ohm"], w["esr_audio_ohm"], w["r_cavo_ohm"],
                w["l_cavo_H"], w["i_A"], w["temp_C"]))
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print("\n".join(out))
