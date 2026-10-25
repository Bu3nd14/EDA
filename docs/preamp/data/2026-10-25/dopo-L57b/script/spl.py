#!/usr/bin/env python3
"""L57a: i picchi dell'RCA a caldo (out_*/rca.csv di genera.py modo oggi) in dB SPL di picco a 1 m e
contro i limiti dell'LSK489. La convenzione e' quella di L53/rca/spl.py (NC-028, PR-23):

  SPL = 96 + 20 log10(Vjack_picco x 21,1 / 2,83)     (finale x21,1, Heresy 96 dB / 1 W / 1 m)
  il finale non va oltre 21,9 V di picco (30 W su 8 Ohm): oltre, «clip», ~113,8 dB SPL;
  il tetto di non-danno di PR-23: 112,2 dB SPL (0,87 V al jack).
  Le fisse: nessuna metrica in dB SPL (NC-046); i volt e il rapporto col picco del K11 a piena
  scala (3,8 V), come in L53.
  LSK489 (datasheet p. 2): gate-gate +/-30 V minimo; gate-source -60 V minimo; IG(F) 10 mA.

Uso: /usr/bin/python3 spl.py <out_dir>...   -> <out_dir>/rca_spl.csv per ciascuno
"""
import csv
import math
import os
import sys

CLIP, TETTO_V, GG, GS = 21.9, 0.87, 30.0, 60.0


def spl(v):
    return 96 + 20 * math.log10(max(min(v * 21.1, CLIP), 1e-9) / 2.83)


for d in sys.argv[1:]:
    righe = list(csv.DictReader(open(os.path.join(d, "rca.csv"))))
    out = []
    for r in righe:
        v = float(r["main_pk_v"])
        f = float(r["fix_pk_v"])
        gg = max(abs(float(r["gg_max_v"])), abs(float(r["gg_min_v"])))
        gs = min(float(r["gs_min_v"]), 0.0)
        out.append({
            "caso": r["caso"], "vol": r["vol"], "modo": r["modo"], "rete": r["rete"],
            "main_pk_v": "%.4g" % v, "main_dbspl": "%.1f" % spl(v),
            "clip_finale": "si" if v * 21.1 > CLIP else "no",
            "sopra_tetto": "si" if v > TETTO_V else "no",
            "fisse_pk_v": "%.4g" % f, "fisse_vs_k11_db": "%+.1f" % (20 * math.log10(max(f, 1e-9) / 3.8)),
            "ain_pk_v": "%.4g" % float(r["ain_pk_v"]),
            "gg_v": "%.2f" % gg, "gg_margine_v": "%.2f" % (GG - gg),
            "gs_min_v": "%.2f" % gs, "gs_margine_v": "%.2f" % (GS + gs),
            "ig_max_ma": "%.3g" % max(abs(float(r["ig_max_ma"])), abs(float(r["ig_min_ma"]))),
            "ig_dopo_ma": "%.3g" % float(r["ig_dopo_ma"]),
            "id_max_ma": "%.3g" % float(r["id_max_ma"]),
            "vin_oltre_rail_v": "%.2f" % float(r["vin_rail_v"]),
            # gate-drain: in avanti oltre ~0,6 V la giunzione conduce (la corrente e' ig);
            # in inversa contro VGDS 60 V. Q117 (MMBT5551) emettitore-base in inversa: VEBO 6 V.
            "gd_max_v": "%.2f" % float(r["gd_max_v"]),
            "gd_min_v": "%.2f" % float(r["gd_min_v"]),
            "veb117_v": "%.2f" % float(r["veb117_max_v"]),
        })
    p = os.path.join(d, "rca_spl.csv")
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("==", p)
    for r in out:
        print("%(caso)-14s %(vol)-4s m%(modo)-2s rete %(rete)-4s main %(main_pk_v)8s V %(main_dbspl)6s dB SPL clip=%(clip_finale)-2s"
              " fisse %(fisse_vs_k11_db)6s | ain %(ain_pk_v)7s gg %(gg_v)6s (marg %(gg_margine_v)6s) gs %(gs_min_v)7s"
              " ig %(ig_max_ma)6s/%(ig_dopo_ma)6s mA id %(id_max_ma)6s gd %(gd_max_v)6s/%(gd_min_v)7s veb %(veb117_v)5s" % r)
