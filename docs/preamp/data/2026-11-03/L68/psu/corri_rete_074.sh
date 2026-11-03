#!/bin/zsh
# corri_rete_074.sh <etichetta> [opzioni di genera_tb_psu.py] - L45d2b2b1: the rete deck (regime and
# mains loss at -10 % / nominal / +10 %) on today's netlist with an option of ADR-074, in
# rete/<etichetta>; then analizza.py (the hold). riassunto_rete_074.py reads the folders.
set -u
D=${0:A:h}
etich=$1
shift
R=$D:h/rete/$etich
mkdir -p "$R"
/usr/bin/python3 -I "$D/genera_tb_psu.py" --uscita "$R" --nome rete "$@" > /dev/null || exit 1
/opt/homebrew/bin/ngspice -b "$R/tb_psu_rete.cir" -o "$R/tb_psu_rete.log" > /dev/null 2>&1
/usr/bin/python3 -I "$D/analizza.py" "$R" > /dev/null
print -r -- "fine rete $etich"
