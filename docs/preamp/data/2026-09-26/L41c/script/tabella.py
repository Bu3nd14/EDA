#!/usr/bin/env python3
"""L41c: la tabella del banco di L30 col circuito vero (NC-036), da analisi.csv di v2_metodo.
Solo stdlib, /usr/bin/python3. Copiata da data/2026-09-26/L30/script/tabella.py, coi criteri di
L41c, SCRITTI PRIMA DELLE CORSE:

  spegnimento_l            V2: <= 100 uV (~33 dB SPL di picco a 1 m)
  perdita, perdita_min,
  guasto (U502), guasto_u501,
  guasto_u503, guasto_u503_min
                           obiettivo di ADR-046: <= 2 mV (~60 dB), e sotto il tetto 0,87 V (~112 dB)
  cf_nodelta               controfattuale: DEVE superare 2 mV (L30: 69 mV). Se non lo fa, il banco
                           non vede Δ e il resto non vale
  corto_u503               nessun verdetto: il criterio e' la decisione dell'utente (NC-036)

Per ogni corsa: il picco A_ins peggiore fra le tre uscite, in V e in dB SPL di picco a 1 m con
la formula di NC-028 (100 uV = 33,45 dB, poi 20 log10 del rapporto: limite superiore).
Esce 1 se una corsa con soglia la supera, se il controfattuale non fallisce, o se ne manca una.

Uso: tabella.py ANALISI.csv FALLITE.txt OUT.csv [CF_FINO_ALL_ABORTO.txt]

AGGIUNTO DOPO LE CORSE (e detto qui perche' lo si veda): cf_nodelta si ferma su «Timestep too
small» nel JFET all'apertura del contatto del jack, anche con gear, passo di 1 us o reltol 1e-5.
Il suo .dat dopo l'aborto e' tutto zeri (limitations #35) e v2_metodo non lo legge. Col quarto
argomento la tabella prende il picco grezzo fino all'aborto (script/cf_fino_all_aborto.py): un
LIMITE INFERIORE, che basta per un criterio che chiede di superare 2 mV.
"""
import re
import csv
import math
import sys

DB0, V0 = 33.45, 100e-6
TETTO = 0.87
SOGLIA = {"spegnimento_l": 100e-6}
for c in ("perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503", "guasto_u503_min"):
    SOGLIA[c] = 2e-3
CONTRO = {"cf_nodelta": 2e-3}
INFO = ("corto_u503",)
CASI = tuple(SOGLIA) + tuple(CONTRO) + INFO


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
    cf_parziale = {}
    if len(argv) > 4:
        m = re.search(r"picco grezzo .*?: ([0-9.eE+-]+) V su (\w+)", open(argv[4]).read())
        cf_parziale["cf_nodelta_l41c"] = (float(m.group(1)), m.group(2))
    rc = 0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["caso", "uscita", "picco_V", "dB_SPL_picco_1m", "criterio", "esito"])
        for caso in CASI:
            cella = caso + "_l41c"
            parziale = cella not in picco and cella in cf_parziale
            if parziale:
                picco[cella] = cf_parziale[cella]
            if cella not in picco:
                w.writerow([caso, "-", "-", "-", "-", "MANCA (%s)" % ("non corsa" if cella in ko else "assente")])
                if caso not in INFO:
                    rc = 1
                continue
            v, u = picco[cella]
            if caso in SOGLIA:
                s = SOGLIA[caso]
                crit = "<= %g V" % s
                esito = "sotto" if v <= s else "SOPRA"
                if v > s:
                    rc = 1
                if s == 2e-3 and v > TETTO:
                    esito += " e oltre il tetto"
            elif caso in CONTRO:
                crit = "> %g V (deve fallire)" % CONTRO[caso]
                esito = "fallisce, come deve" if v > CONTRO[caso] else "NON FALLISCE: il banco non vede Delta"
                if parziale:
                    esito += " (fino all'aborto: limite inferiore, grezzo)"
                if v <= CONTRO[caso]:
                    rc = 1
            else:
                crit = "decisione dell'utente"
                esito = "tetto %s" % ("sotto" if v <= TETTO else "SOPRA")
            w.writerow([caso, u, "%.4g" % v, "%.1f" % db(v), crit, esito])
    print(open(out).read())
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
