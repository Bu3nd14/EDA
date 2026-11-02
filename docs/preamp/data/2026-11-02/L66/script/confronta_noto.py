#!/usr/bin/env python3
"""L66: il caso noto. Le righe rif / Q132_ce / R126_cc / Q132_be di calore_sorg.csv di QUESTA cartella
contro le stesse di L58b (calore_sorg.csv, rif / Q132_ce / R126_cc / Q132_be ci sono tutte: Q132_be e'
uno dei 28) e, per Q132_be, contro calore_fmje.csv di L55 (variante fmje = il blocco di oggi).
Cella per cella, tolta la colonna variante. Solo stdlib, /usr/bin/python3 -I.
Esce 1 se una cella e' diversa.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L, "..", ".."))
NOTI = ("rif", "Q132_ce", "R126_cc", "Q132_be")


def righe(p, modi):
    out = {}
    for r in csv.DictReader(open(p)):
        if r["modo"] in modi:
            r = dict(r)
            r.pop("variante")
            out[(r["posizione"], r["modo"])] = r
    return out


qui = righe(os.path.join(L, "calore_sorg.csv"), NOTI)
diverse = 0
for nome, p, modi in (("L58b", os.path.join(DATA, "2026-11-01", "L58b", "calore_sorg.csv"), NOTI),
                      ("L55", os.path.join(DATA, "2026-10-29", "L55", "calore_fmje.csv"), ("Q132_be",))):
    rif = righe(p, modi)
    celle = 0
    for k, r in rif.items():
        if k not in qui:
            print("%s: manca qui %s" % (nome, k))
            diverse += 1
            continue
        for c, x in r.items():
            celle += 1
            if qui[k].get(c) != x:
                diverse += 1
                print("%s %s %s: %s contro %s" % (nome, k, c, qui[k].get(c), x))
    print("%s: %d righe, %d celle confrontate" % (nome, len(rif), celle))
print("diverse: %d" % diverse)
sys.exit(1 if diverse else 0)
