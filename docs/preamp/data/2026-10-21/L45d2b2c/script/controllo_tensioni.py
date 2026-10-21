#!/usr/bin/env python3
"""L45d2b2c: the known case of genera_massimi.py's terminal voltages. In rif (no fault, DC sources,
no signal) every resistor of block B is at a constant voltage, so V^2 / R from <modo>_tensioni.csv
(the larger of |max| and |min|) must equal ngspice's own @r[p] averaged over the last 10 ms
(<modo>_fine.csv), within 2 %, for every resistor above 1 mW. The sabotage: the same with every R
10 % off must FAIL on every one of them. Solo stdlib, /usr/bin/python3 -I controllo_tensioni.py
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
MULT = {"k": 1e3, "meg": 1e6}


def valore(s):
    s = s.lower()
    for k, m in sorted(MULT.items(), key=lambda x: -len(x[0])):
        if s.endswith(k):
            return float(s[:-len(k)]) * m
    return float(s)


def leggi(p):
    return dict((r[0], float(r[1])) for r in csv.reader(open(p)) if len(r) == 2 and r[0] != "grandezza")


def prova(cartella, scala):
    t = leggi(os.path.join(cartella, "rif_tensioni.csv"))
    f = leggi(os.path.join(cartella, "rif_fine.csv"))
    ok = ko = 0
    for r in open(os.path.join(REPO, "spice", "preamp", "gain_block.subckt")):
        p = r.split()
        if not p or p[0][0] != "R":
            continue
        n = p[0].lower()
        pw = abs(f["p_" + n])
        if pw < 1e-3:
            continue
        v = max(abs(t["t_%s_12_max" % n]), abs(t["t_%s_12_min" % n]))
        calc = v * v / (valore(p[3]) * scala)
        if abs(calc - pw) <= 0.02 * pw:
            ok += 1
        else:
            ko += 1
    return ok, ko


def main():
    esito = 0
    for rail in ("nom", "p", "m", "pm"):
        c = os.path.join(LOTTO, "run", "%s_B" % rail, "rif")
        ok, ko = prova(c, 1.0)
        sok, sko = prova(c, 1.1)
        print("%-4s rif: %d resistenze dentro il 2 %%, %d fuori; sabotaggio (R +10 %%): %d prese, %d sfuggite"
              % (rail, ok, ko, sko, sok))
        if ko or sok or not ok:
            esito = 1
    sys.exit(esito)


if __name__ == "__main__":
    main()
