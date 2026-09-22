#!/usr/bin/env python3
"""L39: P7 da tb_mute_corto_regime.csv (prima e dopo). Per ogni colonna p_*
(potenza media su 4-8 ms) il massimo su tutte le righe, con la riga che lo da;
e la classe A dei percorsi a riposo (icmin_q132 > 0 e icmax_q133 < 0) contata
sulle righe a vin_pk = 0. I limiti sono quelli gia' scritti: 1,04 W per MJE a
60 C senza dissipatore (ADR-021, L11); 310 mW per un MMBT in SOT-23 sul pad
minimo (ADR-017). Uso: /usr/bin/python3 p7.py
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIM = {"p_q132": 1.04, "p_q133": 1.04, "p_q122": 0.310, "p_q125": 0.310, "p_q127": 0.310,
       "p_q117": 0.310, "p_q118": 0.310, "p_q106": 0.310}
res = {}
for fase in ("prima", "dopo"):
    rows = list(csv.DictReader(open(os.path.join(BASE, fase, "tb_mute_corto",
                                                 "tb_mute_corto_regime.csv"))))
    res[fase] = {}
    for c in rows[0]:
        if not c.startswith("p_") or c in ("p_rail",):
            continue
        best = max(rows, key=lambda r: float(r[c] or 0))
        res[fase][c] = (float(best[c]), "%s/%sdB/%sHz/caso%s" % (best["blk"], best["modo_db"],
                                                                best["f_hz"], best["caso"]))
    res[fase]["_n"] = len(rows)
print("righe: prima %d, dopo %d" % (res["prima"]["_n"], res["dopo"]["_n"]))
for c in sorted(k for k in res["dopo"] if not k.startswith("_")):
    a, b = res["prima"].get(c, (None, "")), res["dopo"][c]
    lim = LIM.get(c)
    v = "" if lim is None else ("OK" if b[0] <= lim else "SOPRA %.3g W" % lim)
    print("%-10s prima %9.4g W  dopo %9.4g W  (%s)  %s" % (c, a[0], b[0], b[1], v))
