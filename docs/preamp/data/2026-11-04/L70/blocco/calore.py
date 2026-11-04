#!/usr/bin/env python3
"""L70: the heat of the single-rail decks, with L66's rules (analizza_L62b.RTH and P7_TJ, the finals on
the WA-T220-101E at 24.5 C/W and Q193 at 403 C/W as analizza_diss.py): Tj = Ta + |P| * R_thJA at 27 and
60 C of air; the resistors' mean power against 0.25 W (0207), the diodes against analizza_calore's
RTH_DIODO. The meas of each log (p_<part> = value, the mean over the last 10 ms of the run).

    /usr/bin/python3 -I blocco/calore.py > blocco/calore.txt ; writes blocco/calore.csv
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(os.path.dirname(os.path.dirname(QUI)))
sys.path.insert(0, os.path.join(DATA, "2026-10-19", "L62b", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
import analizza_L62b as a62  # noqa: E402

RTH = dict(a62.RTH)
RTH.update({"q193": 403, "q132": 24.5, "q133": 24.5})
RTH_DIODO = 350.0     # analizza_calore.py of L45d2b3b1, line 27


def leggi(log):
    v = {}
    for ln in open(log):
        m = re.match(r"^\s*([a-z0-9_]+)\s*=\s*([-+0-9.eE]+)", ln)
        if m:
            v[m.group(1)] = float(m.group(2))
    return v


righe = []
for caso in ("rif", "m0", "m06", "p0", "p06"):
    log = os.path.join(QUI, "A_%s" % caso, "A_%s.log" % caso)
    if not os.path.exists(log):
        continue
    v = leggi(log)
    r = {"caso": caso, "I_piu_mA": "%.1f" % (-v.get("ipp_avg", 0) * 1e3), "I_meno_mA": "%.1f" % (v.get("imm_avg", 0) * 1e3)}
    for ta in (27.0, 60.0):
        tj = {k: ta + abs(v["p_" + k]) * rt for k, rt in RTH.items() if "p_" + k in v}
        k = max(tj, key=tj.get)
        r["Tj_max_%d" % ta] = "%.0f %s" % (tj[k], k)
    res = {k[2:]: abs(x) for k, x in v.items() if k.startswith("p_r")}
    k = max(res, key=res.get)
    r["R_max_W"] = "%.3f %s" % (res[k], k)
    dio = {k[2:]: abs(x) for k, x in v.items() if k.startswith("p_d")}
    if dio:
        k = max(dio, key=dio.get)
        r["D_max"] = "%.4f W %s, %.0f C a 60" % (dio[k], k, 60 + dio[k] * RTH_DIODO)
    oltre = ["%s %.0f C" % (k, 60 + abs(v["p_" + k]) * rt) for k, rt in RTH.items()
             if "p_" + k in v and 60 + abs(v["p_" + k]) * rt > a62.P7_TJ]
    oltre += ["%s %.3f W" % (k, x) for k, x in res.items() if x > 0.25]
    r["oltre_a_60C"] = "; ".join(oltre) or "nessuna"
    r["n_meas"] = len(v)
    righe.append(r)
with open(os.path.join(QUI, "calore.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(righe)
for r in righe:
    print(r)
