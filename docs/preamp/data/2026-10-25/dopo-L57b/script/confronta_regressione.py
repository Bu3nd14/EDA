#!/usr/bin/env python3
"""L57b: la regressione dei quattro deck canonici dell'ingresso, prima (main) e dopo (il limitatore).

Per ogni CSV di regressione/prima/<deck>/ lo stesso file in regressione/dopo/<deck>/: stesse righe,
stesse chiavi; per colonna numerica la differenza massima assoluta e relativa, e la riga dove cade.
Conta anche gli avvisi di convergenza nei log («stepping failed», «Timestep too small», «Transient
op») prima e dopo: un deck che ripiega da' cifre plausibili e false (L57a, limitations #75 e #76).

Uso: /usr/bin/python3 confronta_regressione.py   -> regressione/confronto.csv (e la stampa)
"""
import csv
import glob
import os

QUI = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(os.path.dirname(QUI), "regressione")
# dopo L57b: il «prima» e' il «dopo» di L57b (la stima del BAV199), il «dopo» il modello di Diodes Inc.
PRIMA = os.path.join(os.path.dirname(os.path.dirname(QUI)), "L57b", "regressione", "dopo")
AVVISI = ("stepping failed", "Timestep too small", "Transient op", "aborted")


def num(x):
    try:
        return float(x)
    except ValueError:
        return None


out = []
for deck in sorted(os.listdir(PRIMA)):
    dp = os.path.join(PRIMA, deck)
    if not os.path.isdir(dp):
        continue
    for nome, d in (("prima", dp), ("dopo", os.path.join(R, "dopo", deck))):
        log = open(os.path.join(d, deck + ".log"), errors="replace").read()
        print("%-16s %-5s avvisi: %s" % (deck, nome, ", ".join("%s %d" % (a, log.count(a)) for a in AVVISI)))
    for f in sorted(glob.glob(os.path.join(dp, "*.csv"))):
        g = os.path.join(R, "dopo", deck, os.path.basename(f))
        a, b = list(csv.reader(open(f))), list(csv.reader(open(g)))
        assert a[0] == b[0] and len(a) == len(b), (f, len(a), len(b))
        for j, col in enumerate(a[0]):
            peggio = None
            for i in range(1, len(a)):
                x, y = num(a[i][j]), num(b[i][j])
                if x is None or y is None:
                    assert a[i][j] == b[i][j], (f, i, col, a[i][j], b[i][j])
                    continue
                d_abs = abs(y - x)
                d_rel = d_abs / abs(x) if x else (0.0 if y == 0 else float("inf"))
                if peggio is None or d_rel > peggio[1]:
                    peggio = (d_abs, d_rel, i, x, y)
            if peggio and peggio[0] > 0:
                out.append({"deck": deck, "csv": os.path.basename(f), "colonna": col,
                            "riga": peggio[2], "prima": "%.6g" % peggio[3], "dopo": "%.6g" % peggio[4],
                            "diff_rel": "%.3g" % peggio[1]})
with open(os.path.join(R, "confronto.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, ["deck", "csv", "colonna", "riga", "prima", "dopo", "diff_rel"])
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(deck)-16s %(csv)-28s %(colonna)-14s riga %(riga)4s  %(prima)12s -> %(dopo)12s  (%(diff_rel)s)" % r)
