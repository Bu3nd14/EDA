#!/usr/bin/env python3
"""L64a: le due copie col bilanciamento di L48b, rigenerate dai deck canonici di OGGI.

    /usr/bin/python3 -I genera_bilanciamento.py

L48b le aveva fatte con un `sed` sui deck canonici di allora (README di L48b): da allora
tb_e3_e5.cir ha preso il limitatore d'ingresso (ADR-101) e il blocco e' cambiato, quindi le
copie versionate in L48b non sono piu' il circuito di oggi. Qui le stesse sostituzioni, sui
deck di oggi; ognuna deve trovare la sua riga UNA volta, altrimenti rifiuta e non scrive.
  - E5 col bilanciamento girato di 3 dB: RBAL ATT 0 50k -> RBALH ATT VTOP 14.6k / RBALL VTOP 0
    35.4k, e RATTH portata su VTOP;
  - V1 del blocco B con le sorgenti che il bilanciamento puo' dare: la sola riga `foreach rs`.
Scrive ../bilanciamento/tb_e5_bilanciamento.cir e tb_loop_bilanciamento.cir.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
TB = os.path.join(REPO, "spice", "preamp", "tb")
OUT = os.path.join(L, "bilanciamento")

COPIE = {
    "tb_e5_bilanciamento.cir": (
        "tb_e3_e5.cir",
        "tb_e5_bilanciamento.cir - L64a (come L48b): E5 col bilanciamento MN girato di 3 dB "
        "(k 0,708 su 50k: 14,6k in alto, 35,4k in basso), copia di spice/preamp/tb/tb_e3_e5.cir di oggi",
        [("RBAL  ATT 0 50k\n", "RBALH ATT VTOP 14.6k\nRBALL VTOP 0 35.4k\n"),
         ("RATTH ATT BIN 1m\n", "RATTH VTOP BIN 1m\n")]),
    "tb_loop_bilanciamento.cir": (
        "tb_loop.cir",
        "tb_loop_bilanciamento.cir - L64a (come L48b): V1 del blocco B con l impedenza di sorgente "
        "che il bilanciamento MN puo dare (ADR-065), copia di spice/preamp/tb/tb_loop.cir di oggi "
        "con le sole sorgenti cambiate",
        [("    foreach rs 1m 1k 2.5k 2.571k 2.611k\n", "    foreach rs 2.611k 3.77k 5.07k 5.6k\n")]),
}

errori = []
testi = {}
for nome, (base, titolo, sost) in COPIE.items():
    with open(os.path.join(TB, base)) as f:
        t = f.read()
    righe = t.split("\n", 1)
    t = titolo + "\n" + righe[1]
    for vecchio, nuovo in sost:
        n = t.count(vecchio)
        if n != 1:
            errori.append(f"{base}: «{vecchio.strip()}» trovata {n} volte, attesa 1")
            continue
        t = t.replace(vecchio, nuovo)
    testi[nome] = t
if errori:
    print("RIFIUTATO:", *errori, sep="\n  - ", file=sys.stderr)
    sys.exit(1)
os.makedirs(OUT, exist_ok=True)
for nome, t in testi.items():
    with open(os.path.join(OUT, nome), "w") as f:
        f.write(t)
    print("scritto", os.path.relpath(os.path.join(OUT, nome), REPO))
