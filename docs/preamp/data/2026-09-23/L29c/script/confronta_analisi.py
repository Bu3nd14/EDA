#!/usr/bin/env python3
"""L29c: confronta due analisi.csv di v2_metodo.py cella per cella (cella, grandezza, uscita).
Stampa le grandezze del verdetto (A, B, S) e lo scarto piu' grande per grandezza.

Uso: confronta_analisi.py prima.csv dopo.csv [out.csv]
"""
import csv
import sys

a_p, b_p = sys.argv[1:3]
out = sys.argv[3] if len(sys.argv) > 3 else None


def leggi(p):
    with open(p) as f:
        return {(r["cella"], r["grandezza"], r["uscita"]): r for r in csv.DictReader(f)}


A, B = leggi(a_p), leggi(b_p)
solo_a = sorted(set(A) - set(B))
solo_b = sorted(set(B) - set(A))
righe = []
peg = {}
for k in sorted(set(A) & set(B)):
    va, vb = A[k]["picco_V"], B[k]["picco_V"]
    if not va or not vb:
        righe.append(list(k) + [va, vb, "", ""])
        continue
    x, y = float(va), float(vb)
    d = y - x
    rel = d / abs(x) if x else (0.0 if y == 0 else float("inf"))
    righe.append(list(k) + [va, vb, "%.4g" % d, "%.4g" % rel])
    g = k[1]
    if g not in peg or abs(d) > abs(peg[g][2]):
        peg[g] = (k, x, d, rel)
if out:
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cella", "grandezza", "uscita", "prima", "dopo", "diff", "rel"])
        w.writerows(righe)
print("comuni %d, solo in prima %d, solo in dopo %d" % (len(set(A) & set(B)), len(solo_a), len(solo_b)))
for g in sorted(peg):
    k, x, d, rel = peg[g]
    print("  %-7s scarto max %.4g (rel %.3g) su %s %s, valore %.6g" % (g, d, rel, k[0], k[2], x))
for g in ("A_ins", "A_rel", "B2", "S_ins", "S_rel"):
    for k in sorted(k for k in set(A) & set(B) if k[1] == g):
        print("  %-7s %-22s %-9s %s -> %s" % (g, k[0], k[2], A[k]["picco_V"], B[k]["picco_V"]))
