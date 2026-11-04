#!/usr/bin/env python3
"""L70: a variant's sequences against L69b's on today's circuit, by the columns of analizza_mc.py.

    /usr/bin/python3 -I script/confronta_eventi.py <an_variante.csv> <variante> > confronto_<variante>.txt

Rows paired by case and mains (L69b oggi[_m10|_p10]/<caso> against <variante>[_m10|_p10]/<caso>).
Prints, for each case, the columns that differ (beyond 0.15 ms / 1 mV / the last printed digit), and the
key ones always: t_jack_ms, t_mus_ms, dmus_ms, n_giu, mus_end, k501_end, t_k501_ms, ritenuta.
"""
import csv
import os
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(os.path.dirname(L), "L69b", "an_l64b.csv")
CHIAVE = ("t_jack_ms", "t_gain_ms", "t_k501_ms", "t_mus_ms", "dmus_ms", "n_giu", "mus_end", "k501_end",
          "ritenuta")
IGNORA = ("caso", "esito", "bn_max0", "bn_max", "on_min", "t_arm_ms", "arm_pg_ms")
an, v = sys.argv[1], sys.argv[2]


def chiave(caso, pre):
    lab, c = caso.split("/")
    suff = lab[len(pre):]
    return c + suff


base = {chiave(r["caso"], "oggi"): r for r in csv.DictReader(open(BASE))}
nuovi = {chiave(r["caso"], v): r for r in csv.DictReader(open(an))}
uguali = 0
for k in sorted(nuovi):
    n, b = nuovi[k], base.get(k)
    if b is None:
        print("%-28s nessuna riga in L69b" % k)
        continue
    diff = []
    for col in n:
        if col in IGNORA:
            continue
        x, y = n[col], b.get(col, "")
        if x == y:
            continue
        try:
            if abs(float(x) - float(y)) <= 0.15:
                continue
        except ValueError:
            pass
        diff.append("%s %s->%s" % (col, y or "-", x or "-"))
    if diff:
        print("%-28s %s" % (k, "; ".join(diff)))
    else:
        uguali += 1
print("\n%d casi, %d uguali a L69b entro 0,15 ms / 0,15 V" % (len(nuovi), uguali))
