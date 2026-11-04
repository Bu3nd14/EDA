#!/usr/bin/env python3
"""L71: print a CSV as an aligned table, '-' for an empty cell (column -t collapses them).
    /usr/bin/python3 -I mostra.py <file.csv> [colonna ...]"""
import csv
import sys
r = list(csv.reader(open(sys.argv[1])))
if len(sys.argv) > 2:
    k = [r[0].index(c) for c in sys.argv[2:]]
    r = [[x[i] for i in k] for x in r]
r = [[c if c != "" else "-" for c in x] for x in r]
w = [max(len(x[i]) for x in r) for i in range(len(r[0]))]
for x in r:
    print("  ".join(c.ljust(n) for c, n in zip(x, w)))
