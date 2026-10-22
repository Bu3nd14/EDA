#!/usr/bin/env python3
"""L45d2b3b1: il caso noto del banco del calore. La variante l62b (il blocco di L62b, posizione A)
deve ridare calore.csv e analisi_jack.csv di L62b, cella per cella, sulle colonne comuni.
Solo stdlib, /usr/bin/python3 -I. Esce con 1 se una cella e' diversa o manca una riga.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L62B = os.path.abspath(os.path.join(L, "..", "..", "2026-10-19", "L62b"))


def carica(p, chiave):
    return {chiave(r): r for r in csv.DictReader(open(p))}


def confronta(nome, nuovo, vecchio, saltare=()):
    diversi = mancanti = celle = 0
    for k, r in sorted(nuovo.items()):
        if k not in vecchio:
            print("  %s %s: manca in L62b" % (nome, k))
            mancanti += 1
            continue
        for c, x in r.items():
            if c in saltare or c not in vecchio[k]:
                continue
            celle += 1
            if x != vecchio[k][c]:
                diversi += 1
                print("  %s %s %s: %s contro %s" % (nome, k, c, x, vecchio[k][c]))
    print("%s: %d righe, %d celle confrontate, %d diverse, %d righe mancanti"
          % (nome, len(nuovo), celle, diversi, mancanti))
    return diversi + mancanti


def main():
    n = 0
    cal = carica(os.path.join(L, "calore_l62b.csv"), lambda r: (r["posizione"], r["modo"]))
    cal62 = carica(os.path.join(L62B, "calore.csv"), lambda r: (r["posizione"], r["modo"]))
    n += confronta("calore", cal, cal62, saltare=("variante",))
    jk = carica(os.path.join(L, "analisi_jack_l62b.csv"),
                lambda r: (r["variante"].replace("l62b_", ""), r["modo"]))
    jk62 = carica(os.path.join(L62B, "analisi_jack.csv"),
                  lambda r: (r["variante"].replace("base_", ""), r["modo"]))
    n += confronta("jack", jk, jk62, saltare=("variante",))
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
