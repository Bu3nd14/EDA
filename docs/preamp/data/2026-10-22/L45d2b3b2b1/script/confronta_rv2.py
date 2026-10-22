#!/usr/bin/env python3
"""L45d2b3b2b1: il blocco generato dal sorgente contro la variante rv2 di L45d2b3b2a (ADR-099), a meno
delle sigle. Solo stdlib, /usr/bin/python3 -I.

Uso: confronta_rv2.py      exit 0 se coincidono riga per riga (come insiemi, commenti esclusi), 1 se no.

Le sigle del banco -> quelle del sorgente (base + 90, gain_block.py sezione 14): R161 -> R190, R162 -> R191,
R167 -> R192, Q168 -> Q193, R169 -> R194. Si confrontano gain_block.subckt e gain_block_flat.inc.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, "..", "..", "..", "..", "..", ".."))
RV2 = os.path.join(REPO, "docs", "preamp", "data", "2026-10-22", "L45d2b3b2a", "varianti", "rv2")
SP = os.path.join(REPO, "spice", "preamp")
MAPPA = {"R161": "R190", "R162": "R191", "R167": "R192", "Q168": "Q193", "R169": "R194"}


def righe(path, mappa=None):
    out = set()
    for r in open(path).read().splitlines():
        r = r.strip()
        if not r or r.startswith("*"):
            continue
        c = r.split()
        if mappa and c[0] in mappa:
            c[0] = mappa[c[0]]
        out.add(" ".join(c))
    return out


esito = 0
for f in ("gain_block.subckt", "gain_block_flat.inc"):
    a, b = righe(os.path.join(RV2, f), MAPPA), righe(os.path.join(SP, f))
    solo_rv2, solo_src = sorted(a - b), sorted(b - a)
    print("%s: %d righe rv2, %d sorgente, %d solo rv2, %d solo sorgente"
          % (f, len(a), len(b), len(solo_rv2), len(solo_src)))
    for r in solo_rv2:
        print("  solo rv2:      " + r)
    for r in solo_src:
        print("  solo sorgente: " + r)
    if solo_rv2 or solo_src:
        esito = 1
print("COINCIDONO" if esito == 0 else "DIVERSI")
sys.exit(esito)
