#!/usr/bin/env python3
"""
normalize_wrdata.py - Normalize ngspice `wrdata` output into clean CSV/JSON.

ngspice's `wrdata` writes, for each requested vector, a pair of columns
(x, y) where x is the sweep/scale variable (frequency, time, sweep index,
etc.) repeated once per vector. This script collapses that into one shared
x column plus one column per requested vector, and also emits JSON.

Usage:
    python3 normalize_wrdata.py <input.csv> <xname> <yname1> [<yname2> ...]

Example:
    python3 normalize_wrdata.py results/02_dc.csv v_sweep v_in v_mid i_v1
"""
import sys
import json
import csv


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    infile = sys.argv[1]
    xname = sys.argv[2]
    ynames = sys.argv[3:]

    rows = []
    with open(infile) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.replace(",", " ").split()
            vals = [float(p) for p in parts]
            n = len(ynames)
            if len(vals) != 2 * n:
                raise ValueError(
                    f"Expected {2*n} columns (x,y pairs for {n} vectors), "
                    f"got {len(vals)} in line: {line!r}"
                )
            x = vals[0]  # x should be identical across all pairs
            row = {xname: x}
            for i, yn in enumerate(ynames):
                row[yn] = vals[2 * i + 1]
            rows.append(row)

    out_csv = infile.rsplit(".", 1)[0] + ".normalized.csv"
    out_json = infile.rsplit(".", 1)[0] + ".normalized.json"

    fieldnames = [xname] + ynames
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"Wrote {len(rows)} rows to {out_csv} and {out_json}")
    print(f"Columns: {fieldnames}")
    if rows:
        print(f"First row: {rows[0]}")
        print(f"Last row:  {rows[-1]}")


if __name__ == "__main__":
    main()
