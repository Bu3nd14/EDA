#!/usr/bin/env python3
"""L69b: the second road against L64b - every result of today (the source of ADR-116: AT_MRQ's and AT_ON's
pull-ups in two halves, R572 + R588 and R576 + R589) against the file of the same name in L64b (the
same bench, the same lists, the source of before), cell by cell.

The circuit changes only in those two pull-ups (200k -> 100k + 100k; 10k -> 4.99k + 4.99k = 9.98k), so
the expectation is the same figure in every cell, but for what reads AT_MRQ / AT_ON. Nothing is forgiven
here: every cell that is not the same string goes to confronto_l64b.csv, and the README explains it.

  CSV, one row per key:  an_l64b.csv (caso), censimento_psu.csv (caso), rete/analisi.csv and
                         guasti/analisi.csv (file), tabella_<rete>.csv (caso, uscita),
                         corse/<rete>/analisi.csv (cella, variante, grandezza, uscita)
  text, number by number: consumo.txt, termica/stima_telaio_l64b.txt

    /usr/bin/python3 -I script/confronta_l64b.py
writes confronto_l64b.csv (file, chiave, colonna, l64b, l69b, scarto) and prints one line per file.
Exit 1 if a file, a row or a column is missing on either side (the structure differs); the differing
cells alone do not fail.
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
L64B = os.path.join(DATA, "2026-11-03", "L64b")
RETI = ("nom", "m10", "p10")
CSVS = ([("an_l64b.csv", ("caso",)), ("censimento_psu.csv", ("caso",)),
         ("rete/analisi.csv", ("file",)), ("guasti/analisi.csv", ("file",))]
        + [("tabella_%s.csv" % r, ("caso", "uscita")) for r in RETI]
        + [("corse/%s/analisi.csv" % r, ("cella", "variante", "grandezza", "uscita")) for r in RETI])
TESTI = ("consumo.txt", os.path.join("termica", "stima_telaio_l64b.txt"))
NUM = re.compile(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?")

errori, diverse, riassunto = [], [], []


def scarto(a, b):
    try:
        return "%.6g" % (float(b) - float(a))
    except ValueError:
        return ""


def leggi_csv(p, chiave):
    with open(p, newline="") as f:
        rd = csv.DictReader(f)
        righe = {}
        for r in rd:
            k = " / ".join(r[c] for c in chiave)
            if k in righe:
                errori.append("%s: la chiave %s due volte" % (os.path.relpath(p, DATA), k))
            righe[k] = r
        return rd.fieldnames, righe


for nome, chiave in CSVS:
    a, b = os.path.join(L64B, nome), os.path.join(L, nome)
    if not (os.path.isfile(a) and os.path.isfile(b)):
        errori.append("%s: manca in %s" % (nome, "L64b" if not os.path.isfile(a) else "L69b"))
        continue
    ca, ra = leggi_csv(a, chiave)
    cb, rb = leggi_csv(b, chiave)
    if ca != cb:
        errori.append("%s: le colonne non sono le stesse" % nome)
        continue
    for k in sorted(set(ra) ^ set(rb)):
        errori.append("%s: la riga %s solo in %s" % (nome, k, "L64b" if k in ra else "L69b"))
    n = d = 0
    for k in sorted(set(ra) & set(rb)):
        for c in ca:
            if c in chiave:
                continue
            n += 1
            if ra[k][c] != rb[k][c]:
                d += 1
                diverse.append((nome, k, c, ra[k][c], rb[k][c], scarto(ra[k][c], rb[k][c])))
    riassunto.append("%s: %d righe, %d celle, %d diverse" % (nome, len(rb), n, d))

for nome in TESTI:
    a, b = os.path.join(L64B, nome), os.path.join(L, nome)
    if not (os.path.isfile(a) and os.path.isfile(b)):
        errori.append("%s: manca in %s" % (nome, "L64b" if not os.path.isfile(a) else "L69b"))
        continue
    la = [x for x in open(a).read().splitlines() if x.strip()]
    lb = [x for x in open(b).read().splitlines() if x.strip()]
    if len(la) != len(lb):
        errori.append("%s: %d righe contro %d" % (nome, len(la), len(lb)))
        continue
    n = d = 0
    for i, (x, y) in enumerate(zip(la, lb), 1):
        # the label of a line is its text without the numbers; the title names the lot
        if NUM.sub("#", x).replace("L64b", "L") != NUM.sub("#", y).replace("L64b", "L"):
            errori.append("%s, riga %d: il testo cambia (%r / %r)" % (nome, i, x[:60], y[:60]))
            continue
        etich = NUM.sub("#", x).strip()[:50]
        for j, (u, v) in enumerate(zip(NUM.findall(x), NUM.findall(y)), 1):
            n += 1
            if u != v:
                d += 1
                diverse.append((nome, "riga %d (%s)" % (i, etich), "numero %d" % j, u, v, scarto(u, v)))
    riassunto.append("%s: %d righe, %d numeri, %d diversi" % (nome, len(lb), n, d))

with open(os.path.join(L, "confronto_l64b.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(("file", "chiave", "colonna", "l64b", "l69b", "scarto"))
    w.writerows(diverse)

print("\n".join(riassunto))
print("in tutto: %d celle diverse da L64b (confronto_l64b.csv)" % len(diverse))
if errori:
    print("RIFIUTATO, la struttura non coincide:\n  " + "\n  ".join(errori))
    sys.exit(1)
