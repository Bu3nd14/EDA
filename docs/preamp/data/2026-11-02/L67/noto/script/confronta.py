#!/usr/bin/env python3
"""L67, caso noto 4: le THD di v(out) dei deck `piatto` e `avvolto`, caso per caso.

Per ogni condizione stampa le 12 THD delle due copie e la massima differenza relativa; rifiuta i
log con errori. Il massimo per livello si confronta a occhio con L66/sintesi_caldo.csv.

Uso: /usr/bin/python3 -I confronta.py -> ../../noto_caldo.csv
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
LOTTO = os.path.dirname(BASE)
RIFIUTI = ("Error", "aborted", "too many args", "Timestep too small")


def thd(copia, cond):
    log = os.path.join(BASE, "run", copia, "thd20k_" + cond, "thd20k_%s.log" % cond)
    casi, cur, nodo = [], None, None
    for r in open(log, errors="replace").read().split("\n"):
        for x in RIFIUTI:
            if x in r:
                raise SystemExit("%s: %s" % (log, r))
        m = re.search(r"L46A_CASO (.*)$", r)
        if m:
            cur = m.group(1).strip()
            continue
        m = re.match(r"Fourier analysis for (\S+):", r.strip())
        if m:
            nodo = m.group(1)
            continue
        m = re.search(r"THD: ([-+0-9.eE]+) %", r)
        if m and nodo == "v(out)" and cur:
            casi.append((cur, float(m.group(1))))
    if len(casi) != 12:
        raise SystemExit("%s: %d casi invece di 12" % (log, len(casi)))
    return casi


out = []
for cond in ("t27_rame", "t27_minima", "t57_rame", "t57_minima"):
    a, b = thd("piatto", cond), thd("avvolto", cond)
    for (ca, ta), (cb, tb) in zip(a, b):
        if ca != cb:
            raise SystemExit("casi in ordine diverso: %s / %s" % (ca, cb))
        out.append({"cond": cond, "caso": ca, "thd_piatto_pct": "%.6g" % ta, "thd_avvolto_pct": "%.6g" % tb,
                    "diff_rel": "%.2e" % abs(tb / ta - 1)})
    lo = max(t for c, t in a if "livello=lo" in c)
    hi = max(t for c, t in a if "livello=hi" in c)
    dmax = max(float(r["diff_rel"]) for r in out if r["cond"] == cond)
    print("%-11s piatto: lo max %.6g %%, hi max %.6g %%; avvolto contro piatto: diff rel max %.2e" % (cond, lo, hi, dmax))
p = os.path.join(LOTTO, "noto_caldo.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
print("-> %s" % p)
