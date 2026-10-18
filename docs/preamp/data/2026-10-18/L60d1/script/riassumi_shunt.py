#!/usr/bin/env python3
"""L60d1: il margine di fase minimo per deck e gruppo nelle varianti di prepara_shunt.py, contro
regressione/dopo (R150 10k, R109 al suo posto). Gruppi come margini.py (ADR-024): blocco B e
buffer posizione 1 e 2, blocco A carico 1 e 2 su tutto il cavo e col cavo fino a 1 nF.
Scrive shunt/margini_shunt.csv. Solo stdlib.
"""
import csv
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
TAB = [("tb_loop", "tb_loop_margini.csv", ("mode", "pos"), None),
       ("tb_loop_blockA", "tb_loop_blockA.csv", ("carico",), None),
       ("tb_loop_blockA", "tb_loop_blockA.csv", ("carico",),
        lambda r: r["cwire"] in ("1f", "47p", "100p", "220p", "470p", "1n")),
       ("tb_loop_bufferfissa", "tb_loop_bufferfissa.csv", ("pos",), None)]


def minimi(cartella):
    m = {}
    for deck, f, chiave, filtro in TAB:
        p = os.path.join(cartella, deck, f)
        for r in csv.DictReader(open(p)):
            if filtro and not filtro(r):
                continue
            k = "%s%s/%s" % (deck, " (cavo<=1n)" if filtro else "", "/".join(r[c] for c in chiave))
            pm = float(r["pm_deg"])
            if k not in m or pm < m[k]:
                m[k] = pm
    return m


varianti = sorted(d for d in os.listdir(os.path.join(L, "shunt"))
                  if os.path.isdir(os.path.join(L, "shunt", d)))
tab = {"dopo": minimi(os.path.join(L, "regressione", "dopo"))}
for v in varianti:
    tab[v] = minimi(os.path.join(L, "shunt", v, "run"))
chiavi = list(tab["dopo"])
col = ["dopo"] + varianti
with open(os.path.join(L, "shunt", "margini_shunt.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["gruppo"] + col)
    for k in chiavi:
        w.writerow([k] + ["%.2f" % tab[c][k] for c in col])
print("%-34s" % "gruppo" + "".join("%13s" % c[:13] for c in col))
for k in chiavi:
    print("%-34s" % k[:34] + "".join("%13.2f" % tab[c][k] for c in col))
