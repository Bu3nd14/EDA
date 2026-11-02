#!/usr/bin/env python3
"""L64a: la matrice di V2 di L60d2 vale ancora per il blocco di oggi? Il criterio di L62b.

    /usr/bin/python3 -I v2_da_l60d2.py

L62b non ha rifatto la matrice di V2 (L60d2, 2026-10-19) perche' il banco della regressione di V2,
tb_switch_v2, cambiava al piu' di 4e-4 relativo: «il blocco non cambia dove V2 guarda». Dopo
L62b il blocco e' cambiato ancora (R153 sdoppiata, i rimedi del calore, il limitatore del VAS di
ADR-111) e l'ingresso ha il limitatore di ADR-101. Qui lo stesso criterio, dal blocco su cui L60d2
ha corso la matrice (la colonna `prima` di L62b/regressione/misure.csv, il main 5036d8e3) al blocco
di oggi (la ricorsa di L64a/dopo), sulle misure di tb_switch_v2 e di tb_switch_v2_counterfactual
lette con misure() di L45d2b3b1. Scrive ../v2_da_l60d2.csv e stampa la variazione massima.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
DATA = os.path.dirname(os.path.dirname(L))
sys.path.insert(0, os.path.join(DATA, "2026-10-22", "L45d2b3b1", "script"))
import misure_regressione as mr   # noqa: E402

prima = {}
with open(os.path.join(DATA, "2026-10-19", "L62b", "regressione", "misure.csv")) as f:
    for r in csv.DictReader(f):
        if r["prima"] != "":
            prima[(r["deck"], r["misura"])] = float(r["prima"])
righe, peggio = [], {}
for deck in ("tb_switch_v2", "tb_switch_v2_counterfactual"):
    oggi = mr.misure(os.path.join(L, "dopo", deck, deck + ".log"))
    chiavi = sorted(k for d, k in prima if d == deck)
    if not chiavi:
        print(f"{deck}: nessuna misura in L62b", file=sys.stderr)
        sys.exit(1)
    for k in chiavi:
        if k not in oggi:
            print(f"{deck}: {k} manca oggi", file=sys.stderr)
            sys.exit(1)
        x, y = prima[(deck, k)], oggi[k]
        rel = abs(y - x) / max(abs(x), abs(y), 1e-30)
        righe.append([deck, k, "%.6g" % x, "%.6g" % y, "%.3e" % rel])
        if rel > peggio.get(deck, (0, ""))[0]:
            peggio[deck] = (rel, k, x, y)
with open(os.path.join(L, "v2_da_l60d2.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["deck", "misura", "blocco_L60d2", "blocco_oggi", "relativa"])
    w.writerows(righe)
for deck, (rel, k, x, y) in peggio.items():
    n = sum(1 for r in righe if r[0] == deck)
    print(f"{deck}: {n} misure, la variazione massima {rel:.2e} relativa ({k}: {x:.6g} -> {y:.6g})")
