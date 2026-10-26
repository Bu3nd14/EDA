#!/bin/zsh
# L54b1: the mains loss at -10 % on a 10 us grid (tran 10u instead of 100u, the rest as
# genera_tb_psu.py writes it): L54a's deck (psu_prima.net, --timer comparatori) and the source's
# (--timer sorgente), side by side. One argument: the folder.
set -u
cd "$1" || exit 1
/opt/homebrew/bin/ngspice -b tb_psu_seq_perdita_g1.cir -o tb_psu_seq_perdita_g1.log > /dev/null 2>&1
echo "$1: ngspice rc $?"
