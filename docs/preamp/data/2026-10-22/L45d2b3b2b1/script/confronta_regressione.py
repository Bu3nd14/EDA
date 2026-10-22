#!/usr/bin/env python3
"""L45d2b3b2b1: la regressione del blocco del sorgente (regressione/dopo/) contro le due di L45d2b3b2a,
sulle MISURE (le righe `nome = valore` dei .log, misure() di misure_regressione.py di L45d2b3b1).
Solo stdlib, /usr/bin/python3 -I.

Uso: confronta_regressione.py
     scrive regressione/misure_oggi.csv (il blocco di main: che cosa cambia) e
     regressione/misure_rv2.csv (la variante di ADR-099: deve coincidere), e stampa i riassunti.

Nei nomi delle misure le sigle del banco diventano quelle del sorgente (q168 -> q193, r161 -> r190,
r162 -> r191, r167 -> r192, r169 -> r194).
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(L)
sys.path.insert(0, os.path.join(DATA, "L45d2b3b1", "script"))
import misure_regressione as mr   # noqa: E402

REG = os.path.join(L, "regressione")
A = os.path.join(DATA, "L45d2b3b2a", "regressione")
MAPPA = {"q168": "q193", "r161": "r190", "r162": "r191", "r167": "r192", "r169": "r194"}


def rinomina(d):
    out = {}
    for k, v in d.items():
        for a, b in MAPPA.items():
            k = re.sub(r"(?<![a-z0-9])%s(?![0-9])" % a, b, k)
        out[k] = v
    return out


def confronta(rif):
    righe = []
    for deck in sorted(os.listdir(os.path.join(REG, "dopo"))):
        d1 = os.path.join(REG, "dopo", deck, deck + ".log")
        d0 = os.path.join(A, rif, deck, deck + ".log")
        if not (os.path.isfile(d1) and os.path.isfile(d0)):
            continue
        a, b = rinomina(mr.misure(d0)), mr.misure(d1)
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                righe.append([deck, k, a.get(k, ""), b.get(k, ""), "", "solo da una parte"])
                continue
            x, y = a[k], b[k]
            rel = abs(y - x) / max(abs(x), abs(y), 1e-30)
            righe.append([deck, k, "%.6g" % x, "%.6g" % y, "%.4g" % (y - x), "%.3e" % rel])
    righe.sort(key=lambda r: -float(r[5]) if r[5][0].isdigit() else -9)
    with open(os.path.join(REG, "misure_%s.csv" % rif), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["deck", "misura", rif, "sorgente", "differenza", "relativa"])
        w.writerows(righe)
    num = [r for r in righe if r[5][0].isdigit()]
    sole = [r for r in righe if not r[5][0].isdigit()]
    fmt = "  %-26s %-30s %14s %14s %12s %s"
    print("== contro %s: %d misure, %d oltre 1e-3, %d oltre 1e-6, %d da una parte sola" %
          (rif, len(righe), sum(float(r[5]) > 1e-3 for r in num), sum(float(r[5]) > 1e-6 for r in num),
           len(sole)))
    for deck in sorted({r[0] for r in num}):
        r = next(r for r in num if r[0] == deck)
        if float(r[5]) > 1e-6:
            print(fmt % tuple(r))
    tipi = {}
    for r in sole:
        tipi.setdefault(r[0], []).append(r[1])
    for deck, ks in sorted(tipi.items()):
        print("  solo da una parte, %s: %d (%s%s)" % (deck, len(ks), ", ".join(ks[:6]),
                                                      ", ..." if len(ks) > 6 else ""))


if __name__ == "__main__":
    confronta("rv2")
    confronta("oggi")
