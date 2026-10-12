#!/usr/bin/env python3
"""L53: la THD con l'autoriscaldamento (deck/aut) contro i tetti di V4 a 20 kHz.

Per ogni caso: THD di v(out), il tetto (0,001 % a 0,2 V; 0,01 % a 2 V) e il margine in dB. Rifiuta
un log con Error/aborted, con un numero di THD diverso dai casi, o con la temperatura del circuito
diversa da quella dell'aria dichiarata nel nome del deck.

Uso: /usr/bin/python3 leggi_aut.py -> run/aut/aut.csv
"""
import csv
import math
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(QUI, "run", "aut")
out = []
for d in sorted(os.listdir(RUN)):
    log = os.path.join(RUN, d, d + ".log")
    if not os.path.exists(log):
        continue
    t = open(log, errors="replace").read()
    for x in ("Error", "aborted", "Timestep too small", "too many args"):
        if x in t:
            raise SystemExit("%s: %s" % (log, x))
    ta = re.search(r"aut_t(\d+)_", d).group(1)
    temps = re.findall(r"Doing analysis at TEMP = (\S+)", t)
    casi = re.findall(r"L46A_CASO modo=(\d+) livello=(\w+) .* rs=(\S+)", t)
    thd = re.findall(r"Fourier analysis for v\(out\):\s*\n\s*No\. Harmonics: \d+, THD: (\S+) %", t)
    if not (len(temps) == len(casi) == len(thd)) or any(x != ta + ".000000" for x in temps):
        raise SystemExit("%s: %d temperature (%s), %d casi, %d THD" % (log, len(temps), set(temps), len(casi), len(thd)))
    for (m, liv, rs), th in zip(casi, thd):
        tetto = 0.001 if liv == "lo" else 0.01
        x = float(th)
        out.append({"deck": d, "modo": m, "livello": liv, "rs": rs, "thd20k_pct": "%.4g" % x,
                    "tetto_pct": tetto, "margine_dB": "%.1f" % (20 * math.log10(tetto / x)),
                    "verdetto": "dentro" if x <= tetto else "FUORI"})
p = os.path.join(RUN, "aut.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(deck)-16s modo=%(modo)-2s %(livello)s rs=%(rs)-5s THD=%(thd20k_pct)-10s margine %(margine_dB)6s dB  %(verdetto)s" % r)
print("-> %s, %d fuori su %d" % (p, sum(r["verdetto"] != "dentro" for r in out), len(out)))
