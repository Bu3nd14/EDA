#!/usr/bin/env python3
"""L53: i picchi dell'RCA a caldo (out/rca.csv) in dB SPL di picco a 1 m, con la catena di NC-028.

Jack principale: finale x21,1, Heresy 96 dB / 1 W / 1 m ;
SPL = 96 + 20 log10(Vjack_picco x 21,1 / 2,83), la convenzione di NC-028 e PR-23 (0,87 V -> 112,2 dB SPL), con il finale che non va oltre 30 W su 8 Ohm (21,9 V di
picco): oltre, il gradino si scrive «clip del finale» e vale ~113,8 dB SPL. Uscite fisse: non c'e'
una metrica in dB SPL (NC-046); si danno i volt e il rapporto col picco del K11 a piena scala
(3,8 V), che e' il segnale piu' alto che quelle uscite vedono.

Uso: /usr/bin/python3 spl.py -> out/rca_spl.csv
"""
import csv
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
CLIP = 21.9
out = []
for r in csv.DictReader(open(os.path.join(QUI, "out", "rca.csv"))):
    v = float(r["main_pk_v"])
    alto = v * 21.1
    spl = 96 + 20 * math.log10(min(alto, CLIP) / 2.83)
    f = float(r["fix_pk_v"])
    out.append({"caso": r["caso"], "vol": r["vol"], "modo": r["modo"],
                "main_pk_v": "%.4g" % v, "main_dbspl": "%.1f" % spl,
                "clip_finale": "si" if alto > CLIP else "no",
                "fisse_pk_v": "%.4g" % f, "fisse_vs_k11_db": "%+.1f" % (20 * math.log10(f / 3.8)),
                "ingresso_blocco_pk_v": r["ain_pk_v"]})
p = os.path.join(QUI, "out", "rca_spl.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, list(out[0]))
    w.writeheader()
    w.writerows(out)
for r in out:
    print("%(caso)-14s vol=%(vol)-4s modo=%(modo)-2s main %(main_pk_v)8s V = %(main_dbspl)6s dB SPL clip=%(clip_finale)-2s  fisse %(fisse_pk_v)7s V (%(fisse_vs_k11_db)s dB sul K11)" % r)
