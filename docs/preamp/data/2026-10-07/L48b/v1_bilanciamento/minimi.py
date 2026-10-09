#!/usr/bin/env python3
"""L48b: il margine di fase minimo del blocco B per impedenza di sorgente, sonda al jack (pos 1,
quella che conta per ADR-024), su ogni modo, carico e cavo. Legge out/tb_loop_margini.csv."""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
righe = list(csv.DictReader(open(os.path.join(QUI, "out", "tb_loop_margini.csv"))))
out = []
for rs in sorted({r["rsrc"] for r in righe}, key=lambda s: float(s.replace("k", "e3"))):
    sel = [r for r in righe if r["rsrc"] == rs and r["pos"] == "1"]
    m = min(sel, key=lambda r: float(r["pm_deg"]))
    out.append("rsrc %-7s minimo %.2f deg (modo %s, carico %s, cavo %s); %d celle"
               % (rs, float(m["pm_deg"]), m["mode"], m["rload"], m["cprobe"], len(sel)))
print("\n".join(out))
open(os.path.join(QUI, "minimi.txt"), "w").write("\n".join(out) + "\n")
