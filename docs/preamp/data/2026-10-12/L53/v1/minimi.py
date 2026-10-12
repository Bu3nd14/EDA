#!/usr/bin/env python3
"""L53: il margine di fase minimo del blocco B per variante e impedenza di sorgente, sonda al jack
(pos 1, ADR-024), su ogni modo, carico e cavo. Copia di L48b/v1_bilanciamento/minimi.py estesa
alle varianti di genera.py; in piu' controlla nel log la temperatura del circuito.

Uso: /usr/bin/python3 minimi.py -> minimi.txt
"""
import csv
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
TEMP = {"t27": "27", "t57": "57", "aut_t27_rame": "27", "aut_t57_rame": "57", "aut_t57_minima": "57"}
out = []
for v, ta in TEMP.items():
    d = os.path.join(QUI, v, "out")
    log = open(os.path.join(d, "tb_loop_%s.log" % v), errors="replace").read()
    temps = set(re.findall(r"Doing analysis at TEMP = (\S+)", log))
    if temps != {ta + ".000000"}:
        raise SystemExit("%s: temperature %s, attesa %s" % (v, temps, ta))
    righe = list(csv.DictReader(open(os.path.join(d, "tb_loop_margini.csv"))))
    for rs in sorted({r["rsrc"] for r in righe}, key=lambda s: float(s.replace("k", "e3"))):
        sel = [r for r in righe if r["rsrc"] == rs and r["pos"] == "1"]
        m = min(sel, key=lambda r: float(r["pm_deg"]))
        out.append("%-15s rsrc %-6s minimo %.2f deg (modo %s, carico %s, cavo %s); %d celle"
                   % (v, rs, float(m["pm_deg"]), m["mode"], m["rload"], m["cprobe"], len(sel)))
print("\n".join(out))
open(os.path.join(QUI, "minimi.txt"), "w").write("\n".join(out) + "\n")
