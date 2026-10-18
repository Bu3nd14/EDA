#!/usr/bin/env python3
"""L56: le cifre di verdetto della regressione, prima (main 96bacb07) e dopo (ADR-067).

  E5   il rumore peggiore di tb_e3_e5_e5.csv (tetto 9,95 uV)
  E3   il minimo vero dell'impedenza d'ingresso, z20k e zmin (limitations #45), tetto 100 kOhm
  E4   Re(Z) massima al jack (main, fisse), tetto 100 Ohm; e al nodo del blocco a 1 / 20 kHz
  op   da tb_op.log: VAS, coda, finali, correnti dei rail, continua all'uscita

Uso: /usr/bin/python3 cifre.py   -> stampa e cifre.csv accanto a prima/ e dopo/
"""
import csv
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tab(fase, deck, f):
    return list(csv.DictReader(open(os.path.join(BASE, fase, deck, f))))


def op(fase):
    t = open(os.path.join(BASE, fase, "tb_op", "tb_op.log"), errors="replace").read()
    v = {}
    for m in re.finditer(r"^(\S+)\s*=\s*([-+0-9.eE]+)\s*$", t, re.M):
        v[m.group(1).lower()] = float(m.group(2))
    return v


righe = []
for fase in ("prima", "dopo"):
    e5 = tab(fase, "tb_e3_e5", "tb_e3_e5_e5.csv")
    w = max(e5, key=lambda r: float(r["onoise_uv"]))
    e3 = tab(fase, "tb_e3_e5", "tb_e3_e5_e3.csv")
    z = min(e3, key=lambda r: min(float(r["zmin_ohm"]), float(r["z20k_ohm"])))
    e4 = tab(fase, "tb_e4_uscite", "tb_e4_uscite_tab.csv")
    zm = max(float(r["zrmax"]) for r in e4 if r["out"] == "main")
    zf = max(float(r["zrmax"]) for r in e4 if r["out"] != "main")
    zn1 = max(float(r["zn1k"]) for r in e4)
    zn20 = max(float(r["zn20k"]) for r in e4)
    o = op(fase)
    r = {"fase": fase,
         "E5_uV": "%.3f" % float(w["onoise_uv"]),
         "E5_dove": "%s/%s/%s/%s" % (w["pos"], w["mode"], w["att"], w["rsrc"]),
         "E3_min_kohm": "%.1f" % (min(float(z["zmin_ohm"]), float(z["z20k_ohm"])) / 1e3),
         "E3_dove": "pos%s csel %s" % (z["pos"], z["csel"]),
         "E4_main_ohm": "%.2f" % zm, "E4_fisse_ohm": "%.2f" % zf,
         "Zblocco_1k_ohm": "%.4f" % zn1, "Zblocco_20k_ohm": "%.3f" % zn20}
    for k in sorted(o):
        if k.startswith(("@q", "i(", "v(out", "out", "vos", "offset")) or "branch" in k:
            r["op_" + k] = "%.5g" % o[k]
    righe.append(r)
chiavi = []
for r in righe:
    for k in r:
        if k not in chiavi:
            chiavi.append(k)
with open(os.path.join(BASE, "cifre.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, chiavi)
    wr.writeheader()
    wr.writerows(righe)
for k in chiavi:
    print("%-24s %-28s %s" % (k, righe[0].get(k, ""), righe[1].get(k, "")))
