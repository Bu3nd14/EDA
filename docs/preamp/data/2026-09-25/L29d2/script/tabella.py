#!/usr/bin/env python3
"""L29d2: la tabella della geometria iii contro L29c. Una riga per cella x grandezza di verdetto,
una colonna per L29c e per ogni variante di L29d2 ("" = 0 pF di cavo e 100 k, c100, r10k, k5).
In ogni casella il peggiore sulle tre uscite (uV, o dB per S) e l'uscita; FUORI se non regge.

Le celle di L29d2 sono quelle di L29c con _<variante>_iii prima del suffisso di riga (_i / _c):
  gm0x10_lz_iii_c -> gm0x10_lz_c ; x01000_dpamax_c100_iii_c -> x01000_dpamax_c

Uso: tabella.py tabella.csv verdetto.csv [verdetto.csv ...]
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
L29C = os.path.join(REPO, "docs", "preamp", "data", "2026-09-23", "L29c", "matrice")
out, srcs = sys.argv[1], sys.argv[2:]
VAR = ("", "c100", "r10k", "k5")
RX = re.compile(r"^(.*?)(?:_(c100|r10k|k5))?_iii(_[ic])?$")


def leggi(p):
    with open(p) as f:
        return list(csv.DictReader(f))


T = {}
for p in ("veloci/verdetto_a.csv", "veloci/verdetto_off.csv", "disp/verdetto.csv"):
    for r in leggi(os.path.join(L29C, p)):
        T.setdefault((r["cella"], r["grandezza"]), {})["L29c"] = r
for s in srcs:
    for r in leggi(s):
        m = RX.match(r["cella"])
        if not m:
            continue
        base = m.group(1) + (m.group(3) or "")
        T.setdefault((base, r["grandezza"]), {})["iii" + ("_" + m.group(2) if m.group(2) else "")] = r
COL = ["L29c"] + ["iii" + ("_" + v if v else "") for v in VAR]


def casella(r):
    if not r:
        return "-"
    k = 1.0 if r["grandezza"].startswith("S") else 1e6
    v = "%.4g" % (float(r["picco"]) * k) if r["picco"] else "?"
    return "%s %s%s" % (v, r["uscita"], "" if r["esito"] == "regge" else " FUORI")


righe = []
for (base, gr) in sorted(T):
    d = T[(base, gr)]
    if not any(c != "L29c" for c in d):
        continue   # celle di L29c che L29d2 non corre (inversioni, 20 kHz, curve)
    righe.append([base, gr, d[next(iter(d))]["gruppo"]] + [casella(d.get(c)) for c in COL])
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cella", "grandezza", "gruppo"] + COL)
    w.writerows(righe)
for r in righe:
    print("%-26s %-6s %s  " % (r[0], r[1], r[2]) + " | ".join("%-22s" % x for x in r[3:]))
