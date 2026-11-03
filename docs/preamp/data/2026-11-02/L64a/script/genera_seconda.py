#!/usr/bin/env python3
"""L64a: i deck della seconda strada che la regressione di L66 non copre.

    /usr/bin/python3 -I genera_seconda.py

Il selettore e le due copie col bilanciamento non hanno una corsa precedente sul circuito di
oggi. La seconda strada e' lo stesso deck col blocco preso dalla variante lim365 di L66
(docs/preamp/data/2026-11-02/L66/varianti/lim365/), il blocco che L66 ha corso e misurato e che
ADR-111 ha portato nel sorgente: un altro file sul disco, che deve dare gli stessi byte.
Scrive ../seconda/deck/<deck>.cir; ogni sostituzione deve trovare la sua riga una volta.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
OUT = os.path.join(L, "seconda", "deck")
VAR = "@REPO@/docs/preamp/data/2026-11-02/L66/varianti/lim365/"
DECK = {
    "tb_f1_selettore.cir": os.path.join(REPO, "spice", "preamp", "tb", "tb_f1_selettore.cir"),
    "tb_e5_bilanciamento.cir": os.path.join(L, "bilanciamento", "tb_e5_bilanciamento.cir"),
    "tb_loop_bilanciamento.cir": os.path.join(L, "bilanciamento", "tb_loop_bilanciamento.cir"),
}
errori, testi = [], {}
for nome, p in DECK.items():
    t = open(p).read()
    n = 0
    for f in ("gain_block.subckt", "gain_block_flat.inc"):
        riga = f".include @REPO@/spice/preamp/{f}\n"
        n += t.count(riga)
        t = t.replace(riga, f".include {VAR}{f}\n")
    if n != 1:
        errori.append(f"{nome}: {n} include del blocco, atteso 1")
    testi[nome] = t
if errori:
    print("RIFIUTATO:", *errori, sep="\n  - ", file=sys.stderr)
    sys.exit(1)
os.makedirs(OUT, exist_ok=True)
for nome, t in testi.items():
    open(os.path.join(OUT, nome), "w").write(t)
    print("scritto", os.path.relpath(os.path.join(OUT, nome), REPO))
