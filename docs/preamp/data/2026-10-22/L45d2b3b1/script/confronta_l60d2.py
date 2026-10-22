#!/usr/bin/env python3
"""L45d2b3b1: il caso noto del banco della Stax. p10_controllo.csv (la variante l60d2: il blocco di
L60d2 sul banco di oggi, sei casi) deve ridare le stesse righe di p10.csv di L60d2, cella per cella.
Solo stdlib, /usr/bin/python3 -I. Esce con 1 se una cella e' diversa o manca una riga.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L60D2 = os.path.abspath(os.path.join(L, "..", "..", "2026-10-19", "L60d2"))


def main():
    nuovo = {r["modo"]: r for r in csv.DictReader(open(os.path.join(L, "p10_controllo.csv")))}
    vecchio = {r["modo"]: r for r in csv.DictReader(open(os.path.join(L60D2, "p10.csv")))}
    diversi = mancanti = celle = 0
    for m, r in sorted(nuovo.items()):
        if m not in vecchio:
            print("  %s: manca in L60d2" % m)
            mancanti += 1
            continue
        for c, x in r.items():
            if c == "variante" or c not in vecchio[m]:
                continue
            celle += 1
            if x != vecchio[m][c]:
                diversi += 1
                print("  %s %s: %s contro %s" % (m, c, x, vecchio[m][c]))
    print("stax: %d righe, %d celle confrontate, %d diverse, %d righe mancanti"
          % (len(nuovo), celle, diversi, mancanti))
    sys.exit(1 if diversi + mancanti else 0)


if __name__ == "__main__":
    main()
