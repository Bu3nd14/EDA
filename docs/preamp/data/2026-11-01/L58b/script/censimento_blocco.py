#!/usr/bin/env python3
"""L58b: what a tester sees of the 28 block faults of ADR-071, from analisi_jack_sorg.csv /
calore_sorg.csv of THIS folder (the bench of L45d2b3b2b2 on the source's block, the fault at 0.3 s,
ideal rails; the figures at the run's end, t_fine).

Per fault and position, against that position's rif:
  out_mV / d_out_mV   the DC at the block's output (out_avg: the node of the output test point,
                      ADR-107) and its difference from rif
  ip_mA / d_ip_mA     the block's + rail current (I_rail_piu_mA, the quiescent) and its difference
  im_mA / d_im_mA     the same on the - rail
Solo stdlib. /usr/bin/python3 -I censimento_blocco.py -> censimento_blocco.csv (and a print)
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = {(r["variante"], r["modo"]): r for r in csv.DictReader(open(os.path.join(L, "analisi_jack_sorg.csv")))}
C = list(csv.DictReader(open(os.path.join(L, "calore_sorg.csv"))))


def chiave_c(r):
    return ("%s_%s" % (r["variante"], r["posizione"]), r["modo"])


CC = {chiave_c(r): r for r in C}
out = []
for (v, m), r in sorted(J.items()):
    if m == "rif":
        continue
    rif, c, crif = J[(v, "rif")], CC.get((v, m)), CC.get((v, "rif"))
    x = {"posizione": v.replace("sorg_", ""), "modo": m}
    x["out_mV"] = round(float(r["out_avg"]) * 1e3, 2)
    x["d_out_mV"] = round((float(r["out_avg"]) - float(rif["out_avg"])) * 1e3, 2)
    if c and crif:
        for k, n in (("ip", "I_rail_piu_mA"), ("im", "I_rail_meno_mA")):
            x[k + "_mA"] = float(c[n])
            x["d_" + k + "_mA"] = round(float(c[n]) - float(crif[n]), 1)
    x["rif_out_mV"] = round(float(rif["out_avg"]) * 1e3, 2)
    x["rif_ip_mA"] = crif and float(crif["I_rail_piu_mA"])
    x["stato"] = r["stato"]
    out.append(x)
campi = ["posizione", "modo", "out_mV", "d_out_mV", "ip_mA", "d_ip_mA", "im_mA", "d_im_mA", "rif_out_mV",
         "rif_ip_mA", "stato"]
with open(os.path.join(L, "censimento_blocco.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(out)
for x in out:
    print(",".join(str(x.get(c, "")) for c in campi))
