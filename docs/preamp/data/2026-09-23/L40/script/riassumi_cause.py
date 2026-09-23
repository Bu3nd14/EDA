#!/usr/bin/env python3
"""L40: riassunto della separazione delle cause (separa_cause.py). Per ogni
variante: margine minimo (pos 1, cavo 1 fF - 4,7 nF, sorgenti 1 mohm e 2,611 k),
crossover a vuoto (1 mohm, 1 fF), guadagno d'anello a 10 Hz e I_q di Q132/Q133
dal log. Controlli: tutti_costruttore = 55,55 (L39/dopo), tutti_segnaposto =
61,80 (L39/prima). Uso: /usr/bin/python3 riassumi_cause.py
"""
import csv
import os
import re

L40 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(L40, "cause")
ORD = ["tutti_costruttore", "seg_jfet", "seg_mmbt", "seg_mje",
       "seg_diodo", "tutti_segnaposto"]
righe = []
for v in ORD:
    r = list(csv.DictReader(open(os.path.join(D, "tb_loop_" + v, "tb_loop_%s.csv" % v))))
    m = min(r, key=lambda x: float(x["pm_deg"]))
    vu = [x for x in r if x["rsrc"] == "1m" and x["cprobe"] == "1f"][0]
    log = open(os.path.join(D, "tb_loop_" + v, "tb_loop_%s.log" % v)).read()
    iq = re.findall(r"@q13[23]\[ic\]\s*=\s*(\S+)", log)
    righe.append([v, float(m["pm_deg"]), m["rsrc"] + "/" + m["cprobe"],
                  float(vu["fcross_hz"]), float(vu["tdb_10hz"]),
                  "/".join("%.2f" % (abs(float(x)) * 1e3) for x in iq)])
base = righe[0][1]
with open(os.path.join(D, "cause.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["variante", "pm_min_deg", "cella", "fcross_vuoto_hz", "tdb_10hz", "iq_ma",
                "delta_vs_costruttore"])
    for x in righe:
        w.writerow(x + [round(x[1] - base, 2)])
        print("%-18s %7.2f  %-12s %10.4g Hz %6.2f dB  Iq %-12s  %+6.2f" % tuple(x + [x[1] - base]))
