#!/bin/zsh
# genera_tutti.sh - L51b: the supply's decks on today's psu.net, with the load of
# carico.txt at the root of the lot. Copied from L47c2a's deck/; the load's
# counterfactual (--carico l41a) is no longer here: it is L41a's only on the
# load before, and corri_controfattuale.sh runs it in L51b-prima/ alone.
#   /bin/zsh genera_tutti.sh
set -eu
D=${0:A:h}
L=$D:h
G=$D/genera_tb_psu.py
/usr/bin/python3 "$G" --uscita "$L/timer" --nome timer
/usr/bin/python3 "$G" --uscita "$L/timer" --nome timer --angolo min --v5 4.9
/usr/bin/python3 "$G" --uscita "$L/rete" --nome rete
/usr/bin/python3 "$G" --uscita "$L/guasti" --nome guasti
