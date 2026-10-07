#!/usr/bin/env python3
"""L48b: the 21 decks against L48a/regressione/dopo, file by file (copied from L48a).

    /usr/bin/python3 confronta.py

Every CSV of each run: equal (byte for byte), or the columns that differ
with their largest relative change. Writes ../regressione/confronto.txt.
Also the rc of each deck from esiti.tsv.
"""
import csv
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
L = QUI.parent
PRIMA = L.parent.parent / "2026-10-06" / "L48a" / "regressione" / "dopo"
DOPO = L / "regressione" / "dopo"


def num(x):
    try:
        return float(x)
    except ValueError:
        return None


righe, n_file, n_uguali = [], 0, 0
for f in sorted(PRIMA.glob("*/*.csv")):
    rel = f.relative_to(PRIMA)
    g = DOPO / rel
    n_file += 1
    if not g.exists():
        righe.append(f"MANCA  {rel}")
        continue
    if f.read_bytes() == g.read_bytes():
        n_uguali += 1
        continue
    a = list(csv.reader(f.open()))
    b = list(csv.reader(g.open()))
    if len(a) != len(b) or a[0] != b[0]:
        righe.append(f"FORMA  {rel}: righe {len(a)} -> {len(b)}")
        continue
    diff = {}
    for ra, rb in zip(a[1:], b[1:]):
        for h, x, y in zip(a[0], ra, rb):
            if x == y:
                continue
            fx, fy = num(x), num(y)
            if fx is None or fy is None:
                diff[h] = max(diff.get(h, 0), float("inf"))
            else:
                d = abs(fy - fx) / max(abs(fx), 1e-30)
                diff[h] = max(diff.get(h, 0), d)
    righe.append(f"CAMBIA {rel}: " + ", ".join(
        f"{h} {d:.3g}" for h, d in sorted(diff.items())))
nuovi = sorted(set(p.relative_to(DOPO) for p in DOPO.glob("*/*.csv"))
               - set(p.relative_to(PRIMA) for p in PRIMA.glob("*/*.csv")))
for n in nuovi:
    righe.append(f"NUOVO  {n}")
esiti = (DOPO / "esiti.tsv").read_text().split("\n")
rc = [e for e in esiti if e and e.split("\t")[1] != "0"]
righe.append("")
righe.append(f"{n_uguali} file su {n_file} uguali a L47c2b2; deck con rc != 0: "
             f"{rc or 'nessuno'}")
(L / "regressione" / "confronto.txt").write_text("\n".join(righe) + "\n")
print("\n".join(righe))
