#!/usr/bin/env python3
"""L68: confronto_l68.csv per case (the events grouped): which events differ from the healthy run, and how.
Also the runs that took the numerical fallback (ripiego.txt). Solo stdlib.
    /usr/bin/python3 -I script/riassunto.py [filtro]
"""
import collections
import csv
import glob
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rip = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(L, "seq", "oggi", "*", "ripiego.txt")))
print("ripieghi:", len(rip), " ".join(rip))
per = collections.OrderedDict()
for r in csv.DictReader(open(os.path.join(L, "confronto_l68.csv"))):
    b = r["caso"].rsplit("_", 1)[0]
    per.setdefault(b, []).append(r)
f = sys.argv[1] if len(sys.argv) > 1 else ""
n_ok = 0
for b, rr in per.items():
    if f and f not in b:
        continue
    diff = [r for r in rr if r["difetti"]]
    if not diff:
        n_ok += 1
        print("%-22s %-6s tutti gli eventi come la corsa sana" % (b, rr[0]["ref"]))
        continue
    print("%-22s %-6s %s" % (b, rr[0]["ref"], rr[0]["modo"]))
    for r in diff:
        print("      %-16s %s" % (r["evento"], r["difetti"]))
print(len(per), "casi,", n_ok, "come la corsa sana in tutti gli eventi")
