#!/usr/bin/env python3
"""L29d2: toglie dal manifesto le righe delle corse che non hanno rc=0 in tempi.txt (spegnimento:
7 corse su 24 si fermano su 'Timestep too small'). Le corse fallite restano elencate a parte.

Uso: solo_riuscite.py DIR   ->  DIR/manifest_ok.csv, DIR/fallite.txt
"""
import csv
import os
import sys

d = sys.argv[1]
ok, ko = set(), []
for r in open(os.path.join(d, "tempi.txt")):
    p = r.split()
    (ok.add(p[0]) if p[1] == "rc=0" else ko.append(r.strip()))
with open(os.path.join(d, "manifest_sel.csv")) as f:
    rd = csv.DictReader(f)
    righe = [x for x in rd if x["file"][:-4] in ok]
    campi = rd.fieldnames
with open(os.path.join(d, "manifest_ok.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(righe)
open(os.path.join(d, "fallite.txt"), "w").write("\n".join(ko) + "\n")
print("%d righe tenute, %d corse fallite" % (len(righe), len(ko)))
