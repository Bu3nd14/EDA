#!/usr/bin/env python3
"""L48b: un manifesto senza le righe che usano corse escluse (come file o come riferimento).
Uso: filtra_manifesto.py <manifest_sel.csv> <uscita.csv> <corsa> [<corsa> ...]"""
import csv
import sys

ingresso, uscita, *escluse = sys.argv[1:]
righe = list(csv.DictReader(open(ingresso)))
fuori = set(escluse)
tenute = [r for r in righe
          if r["file"][:-4] not in fuori and r["rif_ins"] not in fuori and r["rif_rel"] not in fuori]
with open(uscita, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(tenute)
print("%d righe su %d; tolte: %s" % (len(tenute), len(righe),
                                     sorted(r["cella"] for r in righe if r not in tenute)))
