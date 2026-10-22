#!/usr/bin/env python3
"""L45d2b3b2a: la regressione di una variante contro la base di oggi, sulle MISURE (le righe
`nome = valore` dei .log, misure() di misure_regressione.py di L45d2b3b1). Solo stdlib,
/usr/bin/python3 -I.

Uso: confronta_regressione.py <variante> [...]
     scrive regressione/misure_<v>.csv (deck, misura, oggi, variante, differenza, relativa) e stampa,
     per deck, la misura che cambia di piu' e quelle oltre 1e-3.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
sys.path.insert(0, os.path.join(os.path.dirname(L), "L45d2b3b1", "script"))
import misure_regressione as mr   # noqa: E402

REG = os.path.join(L, "regressione")


def confronta(v):
    righe = []
    for deck in sorted(os.listdir(os.path.join(REG, v))):
        d1 = os.path.join(REG, v, deck, deck + ".log")
        d0 = os.path.join(REG, "oggi", deck, deck + ".log")
        if not (os.path.isfile(d1) and os.path.isfile(d0)):
            continue
        a, b = mr.misure(d0), mr.misure(d1)
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                righe.append([deck, k, a.get(k, ""), b.get(k, ""), "", "solo da una parte"])
                continue
            x, y = a[k], b[k]
            rel = abs(y - x) / max(abs(x), abs(y), 1e-30)
            righe.append([deck, k, "%.6g" % x, "%.6g" % y, "%.4g" % (y - x), "%.3e" % rel])
    righe.sort(key=lambda r: -float(r[5]) if r[5][0].isdigit() else -9)
    with open(os.path.join(REG, "misure_%s.csv" % v), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["deck", "misura", "oggi", v, "differenza", "relativa"])
        w.writerows(righe)
    num = [r for r in righe if r[5][0].isdigit()]
    sole = [r for r in righe if not r[5][0].isdigit()]
    fmt = "  %-26s %-30s %14s %14s %12s %s"
    print("== %s: %d misure, %d oltre 1e-3, %d da una parte sola" %
          (v, len(righe), sum(float(r[5]) > 1e-3 for r in num), len(sole)))
    for deck in sorted({r[0] for r in num}):
        r = next(r for r in num if r[0] == deck)
        if float(r[5]) > 1e-3:
            print(fmt % tuple(r))


if __name__ == "__main__":
    for v in sys.argv[1:]:
        confronta(v)
