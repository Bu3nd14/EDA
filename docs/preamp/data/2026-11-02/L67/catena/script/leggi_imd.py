#!/usr/bin/env python3
"""L67 (NC-055): legge l'IMD CCIF della catena (genera_imd.py). Per ogni caso: il prodotto a 1 kHz
(armonica 1 della fourier a 1 kHz) contro il tono a 20 kHz (armonica 20), alla principale (bout) e,
col volume in cima e il modo 0, alla fissa 1 (f1out). Tetto di V4 (ADR-055): <= -110 dB.

Rifiuta: i log con errori; un op non convergente (#57, come leggi_catena.py); un tono a 20 kHz alla
principale lontano piu' del 5 % da picco/2 (una `alter` persa). Il prodotto in dB SPL: a 0,2 V la
principale da' ~99 dB SPL a 1 m (ADR-055), ogni tono a picco/2 ~93 dB SPL; il prodotto sta a
93 + d2 dB SPL.

Uso: /usr/bin/python3 -I leggi_imd.py <blocco>... -> ../../imd_catena.csv
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
LOTTO = os.path.dirname(BASE)
out = []
for blocco in sys.argv[1:]:
    run = os.path.join(BASE, "run", "imd_" + blocco)
    nomi = sorted(d for d in os.listdir(run) if os.path.isdir(os.path.join(run, d)))
    if len(nomi) != 8:
        raise SystemExit("%s: %d corse invece di 8" % (run, len(nomi)))
    for d in nomi:
        log = os.path.join(run, d, d + ".log")
        casi, cur, nodo, fallito = [], None, None, False
        for r in open(log, errors="replace").read().split("\n"):
            for x in ("Error", "aborted", "Timestep too small", "too many args"):
                if x in r:
                    raise SystemExit("%s: %s" % (log, r))
            if "source stepping failed" in r:
                fallito = True
            m = re.search(r"L67_IMD (.*)$", r)
            if m:
                if fallito:
                    raise SystemExit("%s: op non convergente nel caso %s (#57)" % (log, m.group(1)))
                cur = dict(kv.split("=") for kv in m.group(1).split())
                cur["_t"] = {}
                casi.append(cur)
                continue
            m = re.match(r"Fourier analysis for (\S+):", r.strip())
            if m:
                nodo = m.group(1)
                continue
            m = re.search(r"THD: ([-+0-9.eE]+) %", r)
            if m and nodo and cur is not None:
                cur["_t"][nodo] = []
                continue
            m = re.match(r"\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+", r)
            if m and nodo and cur is not None and nodo in cur["_t"]:
                cur["_t"][nodo].append(float(m.group(3)))
        for c in casi:
            mag = c["_t"]["v(bout)"]
            if len(mag) < 21:
                raise SystemExit("%s: %s con %d armoniche" % (log, c, len(mag)))
            atteso = float(c["picco_main"]) / 2
            if abs(mag[20] / atteso - 1) > 0.05:
                raise SystemExit("%s: tono a 20 kHz %.4g contro %.4g (%s)" % (log, mag[20], atteso, c))
            uscite = [("bout", mag)]
            if c["vol"] == "cima" and c["modo"] == "0":
                uscite.append(("f1out", c["_t"]["v(f1out)"]))
            for u, mg in uscite:
                d2 = 20 * math.log10(mg[1] / mg[20])
                out.append({"blocco": blocco, "uscita": u, "modo": c["modo"], "vol": c["vol"], "rs": c["rs"],
                            "livello_A_V": "%.3g" % (2 * float(c["ampin"]) / 2 ** 0.5),
                            "imd_d2_db": "%.1f" % d2, "margine_dB": "%.1f" % (-110 - d2),
                            "prodotto_db_spl": "%.0f" % (93 + d2),
                            "verdetto": "dentro" if d2 <= -110 else "FUORI"})
p = os.path.join(LOTTO, "imd_catena.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(blocco)-15s %(uscita)-5s modo=%(modo)-2s vol=%(vol)-4s rs=%(rs)-5s A=%(livello_A_V)-5s d2 %(imd_d2_db)7s dB margine %(margine_dB)5s dB  %(prodotto_db_spl)4s dB SPL %(verdetto)s" % r)
print("-> %s, %d fuori su %d" % (p, sum(r["verdetto"] != "dentro" for r in out), len(out)))
