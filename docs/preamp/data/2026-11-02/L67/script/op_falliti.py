#!/usr/bin/env python3
"""L67: i casi della catena il cui op non converge (#57: «source stepping failed», poi il
«Transient op» di ngspice), per blocco, con il livello e la THD della principale: per giudicare se
il punto di partenza trovato in transitorio e' sano (livello giusto, THD come lo stesso caso degli
altri blocchi) o no (L67: col volume a -10 dB esatti la principale a 4,8 uV).

Uso: /usr/bin/python3 -I op_falliti.py <blocco>...  -> ../op_falliti.csv
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
RUN = os.path.join(LOTTO, "catena", "run")
out = []
for b in sys.argv[1:]:
    for d in sorted(os.listdir(os.path.join(RUN, b))):
        log = os.path.join(RUN, b, d, d + ".log")
        if not os.path.exists(log):
            continue
        fallito, nodo, cur = False, None, None
        for r in open(log, errors="replace").read().split("\n"):
            if "source stepping failed" in r:
                fallito = True
            m = re.search(r"L53_CATENA (.*)$", r)
            if m:
                cur = dict(kv.split("=") for kv in m.group(1).split())
                cur["fallito"] = fallito
                fallito = False
                continue
            m = re.match(r"Fourier analysis for (\S+):", r.strip())
            if m:
                nodo = m.group(1)
                continue
            m = re.search(r"THD: ([-+0-9.eE]+) %", r)
            if m and nodo == "v(bout)" and cur and cur["fallito"]:
                cur["thd"] = m.group(1)
                continue
            m = re.match(r"\s*1\s+\S+\s+([-+0-9.eE]+)", r)
            if m and nodo == "v(bout)" and cur and cur["fallito"] and "thd" in cur and "vpk" not in cur:
                cur["vpk"] = m.group(1)
                out.append({"blocco": b, "deck": d, "freq": cur["freq"], "livello": cur["livello"],
                            "modo": cur["modo"], "vol": cur["vol"], "rs": cur["rs"],
                            "main_vpk": cur["vpk"], "main_atteso": cur["main_atteso"], "thd_pct": cur["thd"]})
p = os.path.join(LOTTO, "op_falliti.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, ["blocco", "deck", "freq", "livello", "modo", "vol", "rs", "main_vpk",
                            "main_atteso", "thd_pct"])
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(blocco)-17s %(deck)-18s %(freq)5s %(livello)s modo=%(modo)-2s vol=%(vol)-4s rs=%(rs)-5s main %(main_vpk)s / %(main_atteso)s THD %(thd_pct)s %%" % r)
print("-> %s, %d casi" % (p, len(out)))
