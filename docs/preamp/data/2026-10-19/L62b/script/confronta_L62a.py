#!/usr/bin/env python3
"""L62b: il blocco del sorgente (variante `base` di L62b, D154-D157) contro la variante `diodi` di
L62a (D160-D163, righe aggiunte al subckt generato), sui tre CSV versionati di L62a:
  sintesi.csv       modo per modo (D160 -> D154 ... D163 -> D157), ogni colonna
  temperatura.csv   sorgente <-> diodi, senza_diodi <-> base, sorgente_D157_cc <-> diodi_D163_cc
  blocco_sano.csv   base (L62b) <-> diodi (L62a); le colonne di scarto di V1 hanno riferimenti
                    diversi (L62a: la base corsa nello stesso lotto; L62b: la regressione prima)
Scrive ../confronto_L62a.csv (file, chiave, colonna, L62a, L62b, uguale) e stampa le differenze.
Uso: /usr/bin/python3 -I confronta_L62a.py
"""
import csv
import os

L62B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L62A = os.path.join(os.path.dirname(L62B), "L62a")
NOMI = {"D160": "D154", "D161": "D155", "D162": "D156", "D163": "D157"}


def leggi(lotto, f):
    return list(csv.DictReader(open(os.path.join(lotto, f))))


def modo_b(m):
    parte, s = m.rsplit("_", 1) if "_" in m else (m, "")
    return "%s_%s" % (NOMI[parte], s) if parte in NOMI else m


righe = []


def confronta(f, chiave, a, b, salta=()):
    for k in a:
        if k in salta:
            continue
        x, y = a[k], b.get(k, "<manca>")
        righe.append([f, chiave, k, x, y, "si" if x == y else "NO"])


for r in leggi(L62A, "sintesi.csv"):
    if r["variante"] != "diodi":
        continue
    m = modo_b(r["modo"])
    b = [s for s in leggi(L62B, "sintesi.csv") if s["modo"] == m]
    if len(b) != 1:
        raise SystemExit("sintesi: %s trovato %d volte in L62b" % (m, len(b)))
    a = dict(r)
    a["modo"] = m
    a["oltre_i_limiti_60C"] = a["oltre_i_limiti_60C"]
    confronta("sintesi.csv", m, a, b[0], salta=("variante",))

TEMP = {"sorgente": "diodi", "senza_diodi": "base", "sorgente_D157_cc": "diodi_D163_cc"}
ta = {(r["caso"], r["T_C"]): r for r in leggi(L62A, "temperatura.csv")}
for r in leggi(L62B, "temperatura.csv"):
    a = ta[(TEMP[r["caso"]], r["T_C"])]
    confronta("temperatura.csv", "%s@%s" % (r["caso"], r["T_C"]), a, r, salta=("caso", "I_diodi_uA"))

sa = [r for r in leggi(L62A, "blocco_sano.csv") if r["variante"] == "diodi"][0]
sb = leggi(L62B, "blocco_sano.csv")[0]
confronta("blocco_sano.csv", "base<-diodi", sa, sb, salta=("variante",))

with open(os.path.join(L62B, "confronto_L62a.csv"), "w", newline="") as fo:
    w = csv.writer(fo)
    w.writerow(["file", "chiave", "colonna", "L62a_diodi", "L62b_sorgente", "uguale"])
    w.writerows(righe)
diverse = [r for r in righe if r[5] == "NO"]
print("%d confronti, %d diversi" % (len(righe), len(diverse)))
for r in diverse:
    print("  %-16s %-24s %-22s %14s -> %s" % tuple(r[:5]))
