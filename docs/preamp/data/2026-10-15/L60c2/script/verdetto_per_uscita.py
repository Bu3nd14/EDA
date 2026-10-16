#!/usr/bin/env python3
"""L60c2: il verdetto di V2 (verdetto.csv di verdetto.py, L47c2b1) diviso per uscita, e per la fissa 2
(Stax) confrontato riga per riga con L48b. Solo stdlib, /usr/bin/python3 -I.

Uso: verdetto_per_uscita.py VERDETTO.csv [VERDETTO_L48b.csv]   scrive verdetto_per_uscita.txt accanto
"""
import collections
import csv
import os
import sys

righe = list(csv.DictReader(open(sys.argv[1])))
prima = {}
if len(sys.argv) > 2:
    for r in csv.DictReader(open(sys.argv[2])):
        prima[(r["cella"], r["grandezza"], r["uscita"])] = r
out = []
for u in ("FIXJACK2", "FIXJACK1", "MAINJACK"):
    sub = [r for r in righe if r["uscita"] == u]
    c = collections.Counter(r["esito"] for r in sub)
    out.append("%s: %d righe, %s" % (u, len(sub), dict(c)))
    for g in sorted({r["grandezza"] for r in sub}):
        gg = [r for r in sub if r["grandezza"] == g]
        w = max(gg, key=lambda r: float(r["picco"]))
        p = prima.get((w["cella"], g, u))
        out.append("   %-10s peggiore %10.4g uV  %-10s %s   [L48b stessa cella: %s]"
                   % (g, float(w["picco"]) * 1e6, w["esito"], w["cella"],
                      "%.4g uV" % (float(p["picco"]) * 1e6) if p else "-"))
st = [r for r in righe if r["uscita"] == "FIXJACK2" and r["soglia"] != "-"]
d = []
for r in st:
    p = prima.get((r["cella"], r["grandezza"], "FIXJACK2"))
    if p:
        d.append((float(r["picco"]) - float(p["picco"]), r["cella"], r["grandezza"], r["picco"], p["picco"]))
if d:
    d.sort()
    out.append("Stax, righe con soglia confrontabili con L48b: %d; la differenza piu' grande (L60c2 - L48b):" % len(d))
    for x in d[-5:]:
        out.append("   %+.4g uV  %s %s  (%s contro %s V)" % (x[0] * 1e6, x[1], x[2], x[3], x[4]))
dest = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "verdetto_per_uscita.txt")
open(dest, "w").write("\n".join(out) + "\n")
print("\n".join(out))
