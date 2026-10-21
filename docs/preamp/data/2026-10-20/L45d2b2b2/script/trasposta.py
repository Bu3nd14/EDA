#!/usr/bin/env python3
"""L45d2b2b2: a CSV of analizza_075.py printed one column per line (cases side by side), the empty
columns left out; with a third argument, only the columns whose name contains it. Solo stdlib.

    trasposta.py <csv> [filtro]
"""
import csv
import sys

righe = list(csv.DictReader(open(sys.argv[1])))
filtro = sys.argv[2] if len(sys.argv) > 2 else ""
print("%-26s" % "colonna" + "".join("%14s" % r["caso"][2:16] for r in righe))
for c in righe[0]:
    if c == "caso" or filtro not in c or all(r[c] == "" for r in righe):
        continue
    print("%-26s" % c + "".join("%14s" % r[c] for r in righe))
