#!/usr/bin/env python3
"""L53: le cifre del blocco contro i tetti di V4 (ADR-055), per temperatura, modo e sorgente.

Tetti: THD a 20 kHz a 0,2 V <= 0,001 %; h5 in su a 0,2 V a 1/10/20 kHz <= -140 dB; THD a 20 kHz
a 2 V <= 0,01 %. (L'IMD non e' in questi deck.) Il margine e' in dB sotto il tetto.

Uso: /usr/bin/python3 sintesi.py rs t57 t80  -> ../run/sintesi.csv, e la tabella a schermo
"""
import csv
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(os.path.dirname(QUI), "run")
righe = []
for v in sys.argv[1:]:
    with open(os.path.join(RUN, v, "distorsione.csv")) as fh:
        righe += list(csv.DictReader(fh))

chiavi = sorted({(r["temp"], int(r["modo"]), float(r["rs"])) for r in righe})
out = []
for t, m, rs in chiavi:
    sel = [r for r in righe if r["temp"] == t and int(r["modo"]) == m and float(r["rs"]) == rs]
    def una(liv, f):
        x = [r for r in sel if r["livello"] == liv and int(r["freq"]) == f]
        return x[0] if x else None
    lo20, hi20 = una("lo", 20000), una("hi", 20000)
    h5 = [float(una("lo", f)["h5su_db"]) for f in (1000, 10000, 20000) if una("lo", f)]
    if not (lo20 and hi20 and len(h5) == 3):
        continue
    a, b, c = float(lo20["thd_pct"]), float(hi20["thd_pct"]), max(h5)
    out.append({"temp": t, "modo": m, "rs": "%g" % rs,
                "thd20k_02V_pct": "%.4g" % a, "margine_dB": "%.1f" % (20 * math.log10(0.001 / a)),
                "h5su_02V_peggiore_dB": "%.1f" % c, "margine_h5_dB": "%.1f" % (-140 - c),
                "thd20k_2V_pct": "%.4g" % b, "margine_stress_dB": "%.1f" % (20 * math.log10(0.01 / b)),
                "verdetto": "dentro" if a <= 0.001 and c <= -140 and b <= 0.01 else "FUORI"})
p = os.path.join(RUN, "sintesi.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
print(" ".join(out[0]))
for r in out:
    print(" ".join(str(r[k]) for k in out[0]))
print("-> %s (%d righe, %d fuori)" % (p, len(out), sum(r["verdetto"] != "dentro" for r in out)))
