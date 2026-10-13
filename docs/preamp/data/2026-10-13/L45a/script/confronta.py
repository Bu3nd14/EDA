#!/usr/bin/env python3
"""L45a: i verdetti che cambiano fra due sintesi (diradamento 0,1 us contro un quinto del passo).
Uso: confronta.py VECCHIA.csv NUOVA.csv"""
import csv
import sys

old = {r["modo"]: r for r in csv.DictReader(open(sys.argv[1]))}
new = {r["modo"]: r for r in csv.DictReader(open(sys.argv[2]))}
n = 0
for m, r in new.items():
    o = old.get(m)
    if o and o["verdetto"] != r["verdetto"]:
        n += 1
        j = r["jack_peggiore"]
        print("%-10s %-18s -> %-18s %s %s -> %s V" % (m, o["verdetto"], r["verdetto"], j,
                                                     o.get(j + "_A_V"), r.get(j + "_A_V")))
print("cambiati: %d su %d" % (n, len(new)))
