#!/usr/bin/env python3
"""L45d2b3b2a: il caso noto del banco. La variante b1 (il blocco di b1 prima di ADR-097) deve ridare
calore_oggi.csv e analisi_jack_oggi.csv di L45d2b3b1 cella per cella, sui quindici modi e su rif,
nelle cinque posizioni. Solo stdlib, /usr/bin/python3 -I.

Uso: confronta_b1.py      stampa le celle diverse; esce 1 se ce n'e' una
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B1 = os.path.join(os.path.dirname(L), "L45d2b3b1")


def carica(p, chiave):
    return {chiave(r): r for r in csv.DictReader(open(p))}


diverse = celle = 0
for nome, chiave in (("calore_%s.csv", lambda r: (r["posizione"], r["modo"])),
                     ("analisi_jack_%s.csv", lambda r: (r["variante"].split("_", 1)[1], r["modo"]))):
    nuovo = carica(os.path.join(L, nome % "b1"), chiave)
    vecchio = carica(os.path.join(B1, nome % "oggi"), chiave)
    mancano = set(nuovo) - set(vecchio)
    if mancano:
        sys.exit("RIFIUTATO: %s senza riscontro in b1: %s" % (nome, sorted(mancano)[:5]))
    for k, r in sorted(nuovo.items()):
        for c, x in r.items():
            if c == "variante" or c not in vecchio[k]:
                continue
            celle += 1
            if x != vecchio[k][c]:
                diverse += 1
                print("DIVERSA %s %s %s: b1 %r, qui %r" % (nome % "", k, c, vecchio[k][c], x))
print("caso noto: %d celle, %d diverse (%d righe)" % (celle, diverse, len(nuovo)))
sys.exit(1 if diverse else 0)
