#!/usr/bin/env python3
"""L57a: il caso noto. Le corse del banco di L57a in modo l53, col blocco di L53
(noto/gain_block_L53.subckt, da git 96bacb07), contro i CSV pubblicati da L53.

Tolleranza dichiarata: 0,5 % relativo o 1 mV / 0,01 mA assoluto, il piu' largo dei due (stesso
ngspice 47 e stessi modelli: ci si aspetta l'identita'; la tolleranza assorbe solo l'ultima cifra).

Uso: /usr/bin/python3 verifica_noto.py  -> esce col numero di celle fuori
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L57A = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(L57A, "..", "..", "..", "..", ".."))
L53 = os.path.join(REPO, "docs", "preamp", "data", "2026-10-12", "L53", "rca")
COPPIE = [(os.path.join(L53, "out", "rca.csv"), os.path.join(L57A, "rca", "noto", "out", "rca.csv"), 3),
          (os.path.join(L53, "out_gate", "gate.csv"), os.path.join(L57A, "rca", "noto", "out_gate", "gate.csv"), 2)]
fuori = 0
celle = 0
for ref, nuovo, nchiave in COPPIE:
    a = list(csv.reader(open(ref)))
    b = list(csv.reader(open(nuovo)))
    if a[0] != b[0] or len(a) != len(b):
        print("FUORI: intestazione o righe diverse in %s" % nuovo)
        fuori += 1
        continue
    for ra, rb in zip(a[1:], b[1:]):
        if ra[:nchiave] != rb[:nchiave]:
            print("FUORI: chiave %s contro %s" % (ra[:nchiave], rb[:nchiave]))
            fuori += 1
            continue
        for col, x, y in zip(a[0][nchiave:], ra[nchiave:], rb[nchiave:]):
            celle += 1
            x, y = float(x), float(y)
            tol = max(0.005 * abs(x), 0.01 if col.endswith("_ma") else 1e-3)
            if abs(x - y) > tol:
                fuori += 1
                print("FUORI: %s %s %s: L53 %g, oggi %g" % (os.path.basename(ref), ra[:nchiave], col, x, y))
print("caso noto: %d celle, %d fuori" % (celle, fuori))
sys.exit(fuori)
