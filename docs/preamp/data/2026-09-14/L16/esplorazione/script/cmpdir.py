#!/usr/bin/env python3
"""cmpdir.py - byte comparison of every .csv of a reference directory against
the file of the same name in another directory (L16 regression of the decks
it extended). For files that differ, prints the largest relative difference
over numeric cells, so a last-digit change is told apart from a real one.

Usage: cmpdir.py <reference_dir> <new_dir>
"""
import csv
import sys
from pathlib import Path

ref, new = Path(sys.argv[1]), Path(sys.argv[2])
files = sorted(ref.glob("*.csv"))
assert files, f"nessun .csv in {ref}"
for f in files:
    g = new / f.name
    if not g.is_file():
        print(f"MANCANTE {f.name}")
        continue
    if f.read_bytes() == g.read_bytes():
        print(f"IDENTICO {f.name}")
        continue
    a = list(csv.reader(f.open()))
    b = list(csv.reader(g.open()))
    worst = 0.0
    for ra, rb in zip(a, b):
        for x, y in zip(ra, rb):
            try:
                fx, fy = float(x), float(y)
            except ValueError:
                continue
            den = max(abs(fx), abs(fy), 1e-30)
            worst = max(worst, abs(fx - fy) / den)
    print(f"DIVERSO  {f.name}: righe {len(a)} / {len(b)}, "
          f"scarto relativo massimo {worst:.3g}")
