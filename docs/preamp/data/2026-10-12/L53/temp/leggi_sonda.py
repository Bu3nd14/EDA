#!/usr/bin/env python3
"""L53: la tabella della sonda di temperatura (THD di v(out) per deck e livello, con la temperatura
letta dal log). Rifiuta un log con Error/aborted o con un numero di analisi diverso dai casi.

Uso: /usr/bin/python3 leggi_sonda.py  -> run/sonda/sonda.csv
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(QUI, "run", "sonda")
out = []
for d in sorted(os.listdir(RUN)):
    log = os.path.join(RUN, d, d + ".log")
    if not os.path.exists(log):
        continue
    t = open(log, errors="replace").read()
    for x in ("Error", "aborted", "Timestep too small", "too many args"):
        if x in t:
            raise SystemExit("%s: %s" % (log, x))
    temps = re.findall(r"Doing analysis at TEMP = (\S+)", t)
    casi = re.findall(r"L46A_CASO .*livello=(\w+).*gruppo=(\w+)", t)
    thd = re.findall(r"Fourier analysis for v\(out\):\s*\n\s*No\. Harmonics: \d+, THD: (\S+) %", t)
    if not (len(temps) == len(casi) == len(thd) == 2):
        raise SystemExit("%s: %d temperature, %d casi, %d THD" % (log, len(temps), len(casi), len(thd)))
    for (liv, gruppo), tt, th in zip(casi, temps, thd):
        out.append({"deck": d, "gruppo_a_27": gruppo, "temp": tt.split(".")[0], "livello": liv,
                    "thd20k_pct": th})
p = os.path.join(RUN, "sonda.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%-20s temp=%s %s THD=%s %%" % (r["deck"], r["temp"], r["livello"], r["thd20k_pct"]))
