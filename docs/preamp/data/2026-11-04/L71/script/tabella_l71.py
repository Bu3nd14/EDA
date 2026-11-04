#!/usr/bin/env python3
"""L71 (NC-083): the table of the chain to the jack on the sequences with the front moved, from
v2_metodo's analisi.csv of one deck of nine slots (ponte/estrai_ponte_l71.py, posti.csv).
Copied from script/tabella.py (L41c / L47c2b2 / L69b), which stays as it was.

THE CRITERION, WRITTEN BEFORE THE RUNS: every slot is a sequence the USER causes with the front
switch or SW3, as spegnimento_l is: the criterion is spegnimento_l's, V2, <= 100 uV at the jack
(33.45 dB SPL peak at 1 m, the formula of NC-028: 100 uV = 33.45 dB, then 20 log10 of the ratio).
There is no counterfactual in these decks (the slot named cf_nodelta holds a real case).

    tabella_l71.py ANALISI.csv FALLITE.txt POSTI.csv OUT.csv
For each slot: the worst A_ins peak over the three outputs. Exits 1 if a slot exceeds 100 uV or is
missing.
"""
import csv
import math
import sys

DB0, V0 = 33.45, 100e-6
SOGLIA = 100e-6


def db(v):
    return DB0 + 20 * math.log10(v / V0) if v > 0 else float("-inf")


def main(argv):
    ana, fallite, posti, out = argv[1:5]
    picco = {}
    for r in csv.DictReader(open(ana)):
        if r["grandezza"] != "A_ins":
            continue
        v, c = float(r["picco_V"]), r["cella"]
        if v > picco.get(c, (0, ""))[0]:
            picco[c] = (v, r["uscita"])
    ko = [x.split()[0] for x in open(fallite) if x.strip()]
    rc = 0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["posto", "caso", "uscita", "picco_V", "dB_SPL_picco_1m", "criterio", "esito"])
        for p in csv.DictReader(open(posti)):
            cella = p["posto"] + "_l41c"
            if cella not in picco:
                w.writerow([p["posto"], p["caso"], "-", "-", "-", "-",
                            "MANCA (%s)" % ("non corsa" if cella in ko else "assente")])
                rc = 1
                continue
            v, u = picco[cella]
            esito = "sotto" if v <= SOGLIA else "SOPRA"
            rc |= v > SOGLIA
            w.writerow([p["posto"], p["caso"], u, "%.4g" % v, "%.1f" % db(v), "<= %g V" % SOGLIA, esito])
    print(open(out).read())
    return int(rc)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
