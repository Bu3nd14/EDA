#!/usr/bin/env python3
# L40: copiato da L39/script senza modifiche al codice. Qui prima/ e' il main di
# L39 (C124 470 p, modelli del costruttore), dopo/ e' L40 (C124 1 nF, ADR-042).
"""L39: la classe A di ADR-023 prima e dopo. Da tb_blockA_carichi.csv la colonna
classe_a per blocco (A, F1, F2) col minimo di icmin_q132; da
tb_mute_corto_regime.csv le righe del caso 0 (niente corto, niente mute) in
classe A, cioe' icmin_q132 > 0 e icmax_q133 < 0.
Uso: /usr/bin/python3 classe_a.py
"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fase in ("prima", "dopo"):
    r = list(csv.DictReader(open(os.path.join(BASE, fase, "tb_blockA_carichi",
                                              "tb_blockA_carichi.csv"))))
    per = {}
    for x in r:
        tot, ok, mn = per.get(x["blk"], (0, 0, 9.0))
        per[x["blk"]] = (tot + 1, ok + (float(x["classe_a"]) > 0),
                         min(mn, float(x["icmin_q132"])))
    print(fase, "tb_blockA_carichi:", ", ".join(
        "%s %d/%d in A (icmin_q132 min %.4g A)" % (k, v[1], v[0], v[2]) for k, v in per.items()))
    m = list(csv.DictReader(open(os.path.join(BASE, fase, "tb_mute_corto",
                                              "tb_mute_corto_regime.csv"))))
    q = [x for x in m if x["caso"] == "0"]
    ina = sum(float(x["icmin_q132"]) > 0 and float(x["icmax_q133"]) < 0 for x in q)
    mn = min(float(x["icmin_q132"]) for x in q)
    print("     tb_mute_corto caso 0: %d/%d in classe A (icmin_q132 min %.4g A)"
          % (ina, len(q), mn))
