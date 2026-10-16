#!/usr/bin/env python3
"""L60c2: il manifesto delle corse di V2 rifatte col gear, coi loro riferimenti anch'essi col gear
(il gear e il default differiscono di ~50 uV sul jack: non si mescolano). Solo stdlib.

Uso: manifesto_gear.py      scrive run/sonda_v2/gear/manifest_gear.csv
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L60C2 = os.path.dirname(QUI)
GEAR = os.path.join(L60C2, "run", "sonda_v2", "gear")
righe = list(csv.DictReader(open(os.path.join(L60C2, "run", "v2", "manifest_sel.csv"))))
presenti = {f[:-4] for f in os.listdir(GEAR) if f.endswith(".dat") and not f.endswith("_stati.dat")}
eventi = [r for r in righe if r["file"][:-4] in ("mh01_1k_iii", "mev_1k_iii", "gm10x0_1k_iii")]
rif = {r["rif_ins"] for r in eventi} | {r["rif_rel"] for r in eventi}
rif.discard("-")
tenute = eventi + [r for r in righe if r["cella"] in rif]
mancano = sorted({r["file"][:-4] for r in tenute} - presenti)
assert not mancano, mancano
with open(os.path.join(GEAR, "manifest_gear.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(tenute)
print(len(tenute), "righe:", sorted(r["cella"] for r in tenute))
