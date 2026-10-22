#!/usr/bin/env python3
"""L62b: la regressione letta sulle MISURE, non cella per cella. confronta_regressione.py (di
L60d1) confronta ogni numero di ogni .csv, e ne escono soprattutto fasi che saltano da +180 a -180
gradi e valori vicini a zero; qui si confrontano le righe `nome = valore` dei .log di ogni deck
(le .meas e i print), prima (il blocco di main 5036d8e3) contro dopo (coi quattro diodi di
ADR-090). Scrive ../regressione/misure.csv (deck, misura, prima, dopo, differenza, relativa),
ordinato per differenza relativa, e stampa quelle oltre 1e-3.
Uso: /usr/bin/python3 -I misure_regressione.py
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
REG = os.path.join(LOTTO, "regressione")
# il nome a inizio riga e uno spazio prima di «=»: non i frammenti «from=», «at=» delle .meas
RIGA = re.compile(r"^([A-Za-z_@][^\s=]*)\s+=\s+([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)", re.M)


def misure(log):
    out, visti = {}, {}
    for nome, val in RIGA.findall(open(log, errors="replace").read()):
        k = visti.get(nome, 0)
        visti[nome] = k + 1
        out["%s#%d" % (nome, k) if k else nome] = float(val)
    return out


def main():
    righe = []
    for deck in sorted(os.listdir(os.path.join(REG, "dopo"))):
        d1 = os.path.join(REG, "dopo", deck, deck + ".log")
        d0 = os.path.join(REG, "prima", deck, deck + ".log")
        if not (os.path.isfile(d1) and os.path.isfile(d0)):
            continue
        a, b = misure(d0), misure(d1)
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                righe.append([deck, k, a.get(k, ""), b.get(k, ""), "", "solo da una parte"])
                continue
            x, y = a[k], b[k]
            rel = abs(y - x) / max(abs(x), abs(y), 1e-30)
            righe.append([deck, k, "%.6g" % x, "%.6g" % y, "%.4g" % (y - x), "%.3e" % rel])
    righe.sort(key=lambda r: -float(r[5]) if r[5][0].isdigit() else -9)
    with open(os.path.join(REG, "misure.csv"), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["deck", "misura", "prima", "dopo", "differenza", "relativa"])
        w.writerows(righe)
    fmt = "%-26s %-30s %14s %14s %12s %s"
    sole = [r for r in righe if not r[5][0].isdigit()]
    num = [r for r in righe if r[5][0].isdigit()]
    print("== per deck, la misura che cambia di piu'")
    for deck in sorted({r[0] for r in num}):
        print(fmt % tuple(next(r for r in num if r[0] == deck)))
    print("== le 40 che cambiano di piu'")
    for r in num[:40]:
        print(fmt % tuple(r))
    print("%d misure, %d oltre 1e-3, %d da una parte sola" %
          (len(righe), sum(float(r[5]) > 1e-3 for r in num), len(sole)))
    for r in sole[:20]:
        print(fmt % tuple(r))


if __name__ == "__main__":
    main()
