#!/usr/bin/env python3
"""L29d: la tabella delle geometrie dal verdetto.csv della sonda. Una riga per cella, una colonna
per geometria; in ogni casella il peggiore sulle tre uscite (uV) e l'uscita. Scrive tabella.csv.

Uso: tabella.py sonda/verdetto.csv tabella.csv
"""
import csv
import sys

src, out = sys.argv[1:3]
GEO = ("N", "iA", "iB", "ii", "iii")
with open(src) as f:
    V = list(csv.DictReader(f))
T = {}
for r in V:
    c = r["cella"]
    for g in GEO:
        for suf in ("_%s_i" % g, "_%s_c" % g, "_%s" % g):
            if c.endswith(suf):
                base = c[:-len(suf)] + suf[len(g) + 1:]
                T.setdefault((base, r["grandezza"]), {})[g] = r
                break
        else:
            continue
        break
righe = []
for (base, gr) in sorted(T):
    d = T[(base, gr)]
    riga = [base, gr]
    for g in GEO:
        r = d.get(g)
        riga.append("%.4g %s%s" % (float(r["picco"]) * 1e6, r["uscita"], "" if r["esito"] == "regge" else " FUORI")
                    if r else "-")
    righe.append(riga)
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cella", "grandezza"] + ["%s_uV" % g for g in GEO])
    w.writerows(righe)
for r in righe:
    print("%-14s %-6s " % (r[0], r[1]) + " | ".join("%-24s" % x for x in r[2:]))
