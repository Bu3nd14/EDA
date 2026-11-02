#!/usr/bin/env python3
"""L56: per ogni variante e condizione, la distorsione a 20 kHz e l'intermodulazione contro V4, e
il gradino della corrente di coda.

Da run/<spec>/distorsione.csv (leggi_four.py) e dai log run/<spec>/coda_<cond>/:
  thd   casi fuori dai tetti di V4 a 20 kHz (0,001 % a 0,2 V, 0,01 % a 2 V; 3 modi x 2 sorgenti
        x 2 livelli = 12 per condizione) e il margine peggiore in dB (positivo = dentro)
  imd   il prodotto CCIF a 1 kHz peggiore sui tre modi a 0,2 V (tetto -110 dB) e il margine
  coda  la THD a 20 kHz (0 dB, 2,5 kOhm, 0,2 V) contro la corrente di coda; il gradino e' il primo
        punto in cui la THD supera il doppio di quella alla corrente piu' bassa della scansione;
        il margine e' quel punto contro la corrente al valore di R107 della variante, in %.
        «>+N %» se il gradino non arriva dentro la scansione (fino a R107 -20 %).

Uso: /usr/bin/python3 sintesi_caldo.py <spec>...  -> sintesi_caldo.csv (nella cartella del lotto)
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
COND = ["u27", "t27_rame", "t27_minima", "t57_rame", "t57_minima"]


def r107_della(spec):
    v = spec.split("--")[0]
    for r in open(os.path.join(LOTTO, "inc", v + ".inc")):
        if r.startswith("R107 "):
            return float(r.split()[3])
    sys.exit("R107 non trovata in %s" % v)


def coda(spec, cond):
    log = os.path.join(LOTTO, "run", spec, "coda_" + cond, "coda_" + cond + ".log")
    if not os.path.exists(log):
        return ""
    t = open(log, errors="replace").read()
    for x in ("Error", "aborted", "Timestep too small"):
        if x in t:
            sys.exit("%s: %s" % (log, x))
    pezzi = t.split("L56_CODA r107=")[1:]
    # ogni pezzo: un op e un caso (il blocco CODA di caldo.py si ripete per livello)
    punti = []
    for p in pezzi:
        r = float(p.split()[0])
        i = float(re.search(r"@q106\[ic\] = ([-+0-9.eE]+)", p).group(1))
        thd = re.findall(r"Fourier analysis for v\(out\):\s*\n\s*No\. Harmonics: \d+, THD: (\S+) %", p)
        casi = re.findall(r"L46A_CASO modo=0 livello=(\w+)", p)
        if len(thd) != 1 or len(casi) != 1:
            sys.exit("%s: r107=%s, %d THD e %d casi" % (log, r, len(thd), len(casi)))
        if casi[0] == "lo":
            punti.append((i, r, float(thd[0])))
    if len(punti) != 7:
        sys.exit("%s: %d punti a 0,2 V" % (log, len(punti)))
    punti.sort()
    # il punto della scansione piu' vicino al valore della variante, entro l'1 % (coda_bassa:
    # R107 150, il punto 150,7)
    rv = r107_della(spec)
    nom = [i for i, r, _ in punti if abs(r / rv - 1) < 0.01]
    if len(nom) != 1:
        sys.exit("%s: il punto nominale non c'e'" % log)
    base = punti[0][2]
    for i, r, x in punti:
        if x > 2 * base:
            return "%+.1f %%" % (100 * (i / nom[0] - 1))
    return ">%+.1f %%" % (100 * (punti[-1][0] / nom[0] - 1))


out = []
for spec in sys.argv[1:]:
    righe = list(csv.DictReader(open(os.path.join(LOTTO, "run", spec, "distorsione.csv"))))
    for cond in COND:
        th = [r for r in righe if r["deck"] == "thd20k_" + cond]
        im = [r for r in righe if r["deck"] == "imd_" + cond and r["livello"] == "lo"]
        if not th:
            continue
        if len(th) != 12 or len(im) != 3:
            sys.exit("%s %s: %d THD, %d IMD" % (spec, cond, len(th), len(im)))
        marg = [20 * math.log10((0.001 if r["livello"] == "lo" else 0.01) / float(r["thd_pct"]))
                for r in th]
        lo = max(float(r["thd_pct"]) for r in th if r["livello"] == "lo")
        hi = max(float(r["thd_pct"]) for r in th if r["livello"] == "hi")
        d2 = max(float(r["imd_d2_db"]) for r in im)
        out.append({"spec": spec, "cond": cond, "thd_fuori": sum(m < 0 for m in marg),
                    "thd_margine_min_dB": "%.1f" % min(marg), "thd_lo_max_pct": "%.3g" % lo,
                    "thd_hi_max_pct": "%.3g" % hi, "imd_lo_max_dB": "%.1f" % d2,
                    "imd_margine_dB": "%.1f" % (-110 - d2), "gradino_coda": coda(spec, cond)})
p = os.path.join(LOTTO, "sintesi_caldo.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(spec)-14s %(cond)-11s THD fuori %(thd_fuori)2s/12 margine %(thd_margine_min_dB)6s dB"
          "  lo %(thd_lo_max_pct)-9s hi %(thd_hi_max_pct)-9s IMD %(imd_lo_max_dB)6s dB"
          " (margine %(imd_margine_dB)6s)  gradino %(gradino_coda)s" % r)
print("->", p)
