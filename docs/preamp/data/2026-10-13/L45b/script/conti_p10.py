#!/usr/bin/env python3
"""L45b: numeri per il report da p10_blocco.csv - durate per jack dei modi fuori da P10, e i modi
fuori per classe di L45a. Solo stdlib."""
import collections
import csv
import os
import statistics

L45B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
righe = list(csv.DictReader(open(os.path.join(L45B, "p10_blocco.csv"))))
for j in ("main", "fix1", "fix2"):
    t = [float(r[j + "_sopra_ms"]) for r in righe if float(r[j + "_sopra_ms"] or 0) > 100]
    if t:
        print("%s: %d modi oltre 100 ms, mediana %.0f, min %.0f, max %.0f ms" % (
            j, len(t), statistics.median(t), min(t), max(t)))
cls = collections.defaultdict(lambda: [0, 0])
for r in righe:
    c = r["classe_L45a"].split(" ")[0] or "?"
    cls[c][0] += 1
    cls[c][1] += r["p10"].startswith("FUORI")
for c, (n, f) in sorted(cls.items()):
    print("classe %-10s modi %3d  fuori P10 %3d" % (c, n, f))
# entro P10 ma col grezzo oltre 0,87 V: il colpo che torna in meno di 100 ms
brevi = [r for r in righe if r["p10"] == "entro" and max(float(r[j + "_grezzo_V"] or 0) for j in
                                                         ("main", "fix1", "fix2")) > 0.87]
print("entro P10 col grezzo oltre 0,87 V: %d" % len(brevi))
for r in brevi:
    print("  %s %s %s: %s / %s / %s ms" % (r["posizione"], r["modo"], r["classe_L45a"],
                                           r["main_sopra_ms"], r["fix1_sopra_ms"], r["fix2_sopra_ms"]))
