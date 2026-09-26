#!/usr/bin/env python3
"""L30: la tabella del banco di spegnimento e failsafe (ADR-046), da analisi.csv di v2_metodo.
Solo stdlib, /usr/bin/python3.

Per ogni corsa: il picco A_ins peggiore fra le tre uscite, in V e in dB SPL di picco a 1 m con
la formula di NC-028 (100 uV = 33,45 dB, poi 20 log10 del rapporto: limite superiore), e la
soglia della sua classe:
  n_*   spegnimento morbido          V2, 100 uV
  f_*/g_*  guasto                    obiettivo 2 mV (tetto di non-danno 0,87 V)
  cf_*  controfattuale               nessuna: deve andare male
Esce 1 se una corsa n/f/g supera la sua soglia, o se manca.

Uso: tabella.py ANALISI.csv FALLITE.txt OUT.csv
"""
import csv
import math
import sys

DB0, V0 = 33.45, 100e-6
SOGLIA = {"n": 100e-6, "f": 2e-3, "g": 2e-3}
TETTO = 0.87


def db(v):
    return DB0 + 20 * math.log10(v / V0)


def main(argv):
    ana, fallite, out = argv[1:4]
    picco = {}
    for r in csv.DictReader(open(ana)):
        if r["grandezza"] != "A_ins":
            continue
        v = float(r["picco_V"])
        c = r["cella"]
        if v > picco.get(c, (0, ""))[0]:
            picco[c] = (v, r["uscita"])
    ko = [x.split()[0] for x in open(fallite) if x.strip()]
    rc = 0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["corsa", "classe", "uscita", "picco_V", "dB_SPL_picco_1m", "soglia_V", "esito"])
        for c in sorted(picco):
            v, u = picco[c]
            k = c.split("_")[0]
            s = SOGLIA.get(k)
            if s is None:
                esito = "controfattuale"
            elif v <= s:
                esito = "sotto"
            else:
                esito = "SOPRA"
                rc = 1
            if k in "fg" and v > TETTO:
                esito += " oltre il tetto"
            w.writerow([c, k, u, "%.4g" % v, "%.1f" % db(v), s if s else "-", esito])
        for c in ko:
            k = c.split("_")[0]
            w.writerow([c, k, "-", "-", "-", SOGLIA.get(k, "-"), "non corsa (Timestep too small)"])
            if k in SOGLIA:
                rc = 1
    print(open(out).read())
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
