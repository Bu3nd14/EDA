#!/usr/bin/env python3
"""L53 (NC-058): l'intermodulazione CCIF del blocco con ogni giunzione alla sua temperatura.

Il deck di L51c (`L51c/distorsione/deck/oggi/imd.cir`: 19 + 20 kHz, tre modi, 0,2 e 2 V di picco
composto, sorgente 2,5 kOhm) con due sole modifiche:
  - il blocco incluso: `temp/inc/aut_t<T>_rame.inc` (temp/autoriscaldamento.py), ogni BJT e JFET
    alla sua Tj con l'aria a T gradi e il VAS su 15x15 mm di rame;
  - `.temp T` per il resto (resistenze, diodi).
Il tetto di V4: il prodotto a 1 kHz <= -110 dB a 0,2 V.

Uso: /usr/bin/python3 genera.py -> ../deck/t27/imd.cir, ../deck/t57/imd.cir, ../deck/lista.txt
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(BASE, *[".."] * 6))
SRC = os.path.join(REPO, "docs", "preamp", "data", "2026-10-10", "L51c", "distorsione", "deck", "oggi", "imd.cir")
VECCHIO = ".include @REPO@/docs/preamp/data/2026-10-10/L51c/distorsione/inc/oggi.inc"
NUOVO = ".include @REPO@/docs/preamp/data/2026-10-12/L53/temp/inc/aut_t%d_rame.inc"

testo = open(SRC).read()
if testo.count(VECCHIO) != 1:
    raise SystemExit("la riga del blocco non c'e' una volta sola")
lista = []
for t in (27, 57):
    s = testo.replace(VECCHIO, NUOVO % t)
    s = s.replace(".options reltol", ".temp %d\n.options reltol" % t, 1)
    s = s.replace(s.split("\n")[0], "imd - L53: IMD CCIF col blocco autoriscaldato, aria %d gradi (da L51c)" % t, 1)
    p = os.path.join(BASE, "deck", "t%d" % t, "imd.cir")
    open(p, "w").write(s)
    lista.append(p)
open(os.path.join(BASE, "deck", "lista.txt"), "w").write("\n".join(lista) + "\n")
print("\n".join(lista))
