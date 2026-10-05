#!/usr/bin/env python3
"""L47c1 (copiato da L47b2b1): confronto grezzo della regressione, ogni .csv di ogni deck,
L47b2b1/regressione/dopo (le celle NSL-32SR3 in tb_e3_e5_ldr) contro L47c1/regressione/dopo
(ADR-062: niente celle; il deck si chiama tb_e3_e5).

Per ogni coppia di file: righe, e la massima differenza relativa cella per cella fra i
numeri. Atteso: cambia SOLO la colonna zmin_ohm di tb_trim_e3.csv (limitations #45:
`meas min` saltava il punto a 20 kHz); tb_e3_e5_ldr di L47b2b1 non ha un omologo con lo
stesso nome e si confronta a parte (README). Scrive ../regressione/confronto.csv.
Uso: /usr/bin/python3 confronta_regressione.py
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
PRIMA = os.path.join(LOTTO, "..", "..", "2026-10-03", "L47b2b1", "regressione", "dopo")
DOPO = os.path.join(LOTTO, "regressione", "dopo")


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
    for deck in sorted(set(os.listdir(DOPO)) | set(os.listdir(PRIMA))):
        d1, d0 = os.path.join(DOPO, deck), os.path.join(PRIMA, deck)
        if not os.path.isdir(d1) and not os.path.isdir(d0):
            continue
        if not os.path.isdir(d1):
            righe.append([deck, "*", "solo in L47b2b1", "", ""])
            continue
        if not os.path.isdir(d0):
            righe.append([deck, "*", "solo in L47c1", "", ""])
            continue
        for f in sorted(os.listdir(d1)):
            if not f.endswith(".csv"):
                continue
            p0 = os.path.join(d0, f)
            if not os.path.isfile(p0):
                righe.append([deck, f, "manca in L47b2b1", "", ""])
                continue
            a, b = numeri(p0), numeri(os.path.join(d1, f))
            if len(a) != len(b):
                righe.append([deck, f, "righe %d -> %d" % (len(a), len(b)), "", ""])
                continue
            mx, testo, dove, cols = 0.0, 0, "", set()
            for i, (ra, rb) in enumerate(zip(a, b)):
                for j, (x, y) in enumerate(zip(ra, rb)):
                    if isinstance(x, float) and isinstance(y, float):
                        rel = abs(y - x) / max(abs(x), 1e-30)
                        if rel > 0:
                            cols.add(a[0][j] if isinstance(a[0][j], str) else j)
                        if rel > mx:
                            mx, dove = rel, "riga %d col %d: %.6g -> %.6g" % (i, j, x, y)
                    elif x != y:
                        testo += 1
            righe.append([deck, f, "uguale" if mx == 0 and not testo else "diverso",
                          "%.3e" % mx, dove + (" colonne %s" % sorted(map(str, cols)) if cols else "")
                          + (" (+%d celle di testo)" % testo if testo else "")])
    out = os.path.join(LOTTO, "regressione", "confronto.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["deck", "file", "esito", "max_diff_rel", "dove"])
        w.writerows(righe)
    for r in righe:
        if r[2] != "uguale":
            print(",".join(r))
    print("file confrontati: %d, diversi o spaiati: %d"
          % (len(righe), sum(r[2] != "uguale" for r in righe)))


if __name__ == "__main__":
    main()
