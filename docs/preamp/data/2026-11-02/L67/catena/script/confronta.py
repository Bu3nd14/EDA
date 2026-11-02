#!/usr/bin/env python3
"""L67: confronta due tabelle della catena cella per cella, sulle chiavi
(uscita, freq, livello, modo, vol, rs) e sulle colonne vpk, thd_pct, h5su_db, verdetto.

  confronta.py noto            catena_l56.csv (griglia l56) contro L56/catena/run/catena/catena.csv:
                               il caso noto, devono essere uguali tutte le celle
  confronta.py <a> <b>         catena_<a>.csv contro catena_<b>.csv (per esempio oggi oggi_avv)

Uguali = stessa stringa (le cifre sono gia' a 4 significative). Stampa le celle diverse.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(os.path.dirname(QUI))
ROOT = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
CHIAVE = ("uscita", "freq", "livello", "modo", "vol", "rs")
COL = ("vpk", "thd_pct", "h5su_db", "verdetto")


def carica(p, solo_l56=False):
    d = {}
    for r in csv.DictReader(open(p)):
        if solo_l56 and r.get("griglia", "l56") != "l56":
            continue
        d[tuple(r[k] for k in CHIAVE)] = r
    return d


if sys.argv[1:] == ["noto"]:
    a = carica(os.path.join(ROOT, "docs/preamp/data/2026-10-12/L56/catena/run/catena/catena.csv"))
    b = carica(os.path.join(LOTTO, "catena_l56.csv"), solo_l56=True)
    nomi = ("L56", "l56")
else:
    a = carica(os.path.join(LOTTO, "catena_%s.csv" % sys.argv[1]))
    b = carica(os.path.join(LOTTO, "catena_%s.csv" % sys.argv[2]))
    nomi = tuple(sys.argv[1:3])
if set(a) != set(b):
    raise SystemExit("chiavi diverse: solo in %s %s; solo in %s %s"
                     % (nomi[0], sorted(set(a) - set(b)), nomi[1], sorted(set(b) - set(a))))
diverse = 0
for k in sorted(a):
    for c in COL:
        if a[k][c] != b[k][c]:
            diverse += 1
            print("%s %s: %s %s, %s %s" % (k, c, nomi[0], a[k][c], nomi[1], b[k][c]))
print("%s contro %s: %d righe, %d celle, %d diverse" % (nomi[0], nomi[1], len(a), len(a) * len(COL), diverse))
