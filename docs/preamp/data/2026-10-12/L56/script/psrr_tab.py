#!/usr/bin/env python3
"""L46b: PSRR+ e PSRR- per variante, minimo fra i tre modi di guadagno, a
50 / 100 Hz e 1 / 10 / 20 kHz (interpolato in log f, come limiti_psrr.py di L40).

Legge run/<v>/tb_zout_psrr_noise/tb_zout_psrr_noise_psrr{p,m}_{0,3,10}db.csv.
Scrive psrr.csv nella cartella del lotto e lo stampa.

Uso: /usr/bin/python3 psrr_tab.py <variante>...
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
MODI = ("0db", "3db", "10db")
TONI = (50, 100, 1000, 10000, 20000)


def curva(v, rail, modo):
    p = os.path.join(LOTTO, "run", v, "tb_zout_psrr_noise",
                     "tb_zout_psrr_noise_psrr%s_%s.csv" % (rail, modo))
    return [(float(a), float(b)) for a, b in list(csv.reader(open(p)))[1:]]


def interp(c, x):
    lx = math.log10(x)
    for (f0, y0), (f1, y1) in zip(c, c[1:]):
        a, b = math.log10(f0), math.log10(f1)
        if a <= lx <= b:
            return y0 + (y1 - y0) * (lx - a) / (b - a)
    raise ValueError(x)


def minimo(v, rail, x):
    return min(interp(curva(v, rail, m), x) for m in MODI)


righe = []
for v in sys.argv[1:]:
    r = {"variante": v}
    for rail in ("p", "m"):
        for x in TONI:
            r["psrr%s_%g" % (rail, x)] = "%.2f" % minimo(v, rail, x)
    righe.append(r)
campi = list(righe[0])
with open(os.path.join(LOTTO, "psrr.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, campi)
    w.writeheader()
    w.writerows(righe)
print("%-22s %s" % ("variante", "  ".join("%9s" % c[4:] for c in campi[1:])))
for r in righe:
    print("%-22s %s" % (r["variante"], "  ".join("%9s" % r[c] for c in campi[1:])))
