#!/usr/bin/env python3
"""L51c: la variante `oggi` per il banco di distorsione di L46b.

    /usr/bin/python3 docs/preamp/data/2026-10-10/L51c/distorsione/script/oggi.py

Scrive ../inc/oggi.inc: spice/preamp/gain_block_flat.inc com'e' oggi (rigenerato da
circuits/preamp/gain_block.py il 2026-10-10 e uguale byte per byte a quello versionato),
nessuna riga cambiata, con una riga di provenienza in testa (#29). Il confronto con la
variante sv_r10_esr0_r120_226 di L46b (il blocco scelto, ADR-056, col condensatore ideale come
nel sorgente) sta nel generatore del dossier, non qui.
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L51D = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L51D, *[".."] * 6))
SRC = os.path.join(ROOT, "spice", "preamp", "gain_block_flat.inc")

with open(SRC) as f:
    body = f.read()
with open(os.path.join(L51D, "inc", "oggi.inc"), "w") as f:
    f.write("* L51c, la variante oggi: spice/preamp/gain_block_flat.inc del 2026-10-10, nessuna modifica\n")
    f.write(body)
print("scritto inc/oggi.inc")
