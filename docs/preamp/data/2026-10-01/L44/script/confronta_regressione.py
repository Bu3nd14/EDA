#!/usr/bin/env python3
"""L44 - confronto grezzo della regressione: ogni .csv di ogni deck, L46b/dopo (senza
flicker fuori dalla coppia) contro L44/dopo (col tetto di ADR-057).

Per ogni coppia di file: righe, e la massima differenza relativa cella per cella fra i
numeri. L'atteso: cambiano SOLO i deck che fanno un'analisi `noise` (il KF non entra in
op, dc, ac, tran), e lì solo le colonne di rumore. Scrive ../regressione/confronto.csv.
Uso: /usr/bin/python3 confronta_regressione.py
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L44 = os.path.dirname(QUI)
PRIMA = os.path.join(L44, "..", "L46b", "regressione", "dopo")
DOPO = os.path.join(L44, "regressione", "dopo")


def numeri(p):
    out = []
    for riga in csv.reader(open(p)):
        r = []
        for c in riga:
            try:
                r.append(float(c))
            except ValueError:
                r.append(c)
        out.append(r)
    return out


def main():
    righe = []
    for deck in sorted(os.listdir(DOPO)):
        d1, d0 = os.path.join(DOPO, deck), os.path.join(PRIMA, deck)
        if not os.path.isdir(d1):
            continue
        for f in sorted(os.listdir(d1)):
            if not f.endswith(".csv"):
                continue
            p0 = os.path.join(d0, f)
            if not os.path.isfile(p0):
                righe.append([deck, f, "manca in L46b", "", ""])
                continue
            a, b = numeri(p0), numeri(os.path.join(d1, f))
            if len(a) != len(b):
                righe.append([deck, f, "righe %d -> %d" % (len(a), len(b)), "", ""])
                continue
            mx, testo, dove = 0.0, 0, ""
            for i, (ra, rb) in enumerate(zip(a, b)):
                for j, (x, y) in enumerate(zip(ra, rb)):
                    if isinstance(x, float) and isinstance(y, float):
                        rel = abs(y - x) / max(abs(x), 1e-30)
                        if rel > mx:
                            mx, dove = rel, "riga %d col %d: %.6g -> %.6g" % (i, j, x, y)
                    elif x != y:
                        testo += 1
            righe.append([deck, f, "uguale" if mx == 0 and not testo else "diverso",
                          "%.3e" % mx, dove + (" (+%d celle di testo)" % testo if testo else "")])
    out = os.path.join(L44, "regressione", "confronto.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["deck", "file", "esito", "max_diff_rel", "dove"])
        w.writerows(righe)
    for r in righe:
        if r[2] != "uguale":
            print(",".join(r))
    print("file confrontati: %d, diversi: %d" % (len(righe), sum(r[2] != "uguale" for r in righe)))


if __name__ == "__main__":
    main()
