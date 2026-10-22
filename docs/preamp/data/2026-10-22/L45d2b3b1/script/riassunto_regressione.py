#!/usr/bin/env python3
"""L45d2b3b1: regressione/misure.csv per deck: quante misure oltre 1e-3 relativo, e quante di queste
hanno un valore che conta (|prima| o |dopo| oltre SOGLIA nella loro unita': sotto e' rumore
numerico, potenze a 1e-24 W, correnti a 1e-13 A), con la peggiore. Solo stdlib, /usr/bin/python3 -I.
"""
import csv
import os
from collections import defaultdict

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOGLIA = 1e-6
per = defaultdict(lambda: [0, 0, None])
for r in csv.DictReader(open(os.path.join(L, "regressione", "misure.csv"))):
    try:
        rel = float(r["relativa"])
        a, b = float(r["prima"]), float(r["dopo"])
    except ValueError:
        continue
    if rel <= 1e-3:
        continue
    s = per[r["deck"]]
    s[0] += 1
    if max(abs(a), abs(b)) > SOGLIA:
        s[1] += 1
        if s[2] is None or rel > s[2][0]:
            s[2] = (rel, r["misura"], a, b)
for d, (n, m, w) in sorted(per.items()):
    print("%-26s oltre 1e-3: %4d, di cui sopra %g: %4d%s" % (
        d, n, SOGLIA, m, "   peggiore %s %.4g -> %.4g (%.3g)" % (w[1], w[2], w[3], w[0]) if w else ""))
