#!/bin/zsh
# genera_tutti.sh - L47c2a: the supply's decks on today's psu.net (no LDR drive).
#   /bin/zsh genera_tutti.sh
# timer (nom, min), rete, guasti, and the load's counterfactual (L42b's).
set -eu
D=${0:A:h}
L=$D:h
G=$D/genera_tb_psu.py
/usr/bin/python3 "$G" --uscita "$L/timer" --nome timer
/usr/bin/python3 "$G" --uscita "$L/timer" --nome timer --angolo min --v5 4.9
/usr/bin/python3 "$G" --uscita "$L/rete" --nome rete
/usr/bin/python3 "$G" --uscita "$L/guasti" --nome guasti
/usr/bin/python3 "$G" --uscita "$L/carico_l41a/rete" --nome rete --carico l41a
/usr/bin/python3 "$G" --uscita "$L/carico_l41a/guasti" --nome guasti --carico l41a
