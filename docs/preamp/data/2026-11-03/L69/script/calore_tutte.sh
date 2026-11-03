#!/bin/zsh
# L68: calore_5v.py (U504, U512) su tutte le corse di lista_l68.txt -> calore_5v.csv
set -u
L=${0:A:h:h}
CASI=(${(f)"$(/usr/bin/cut -d' ' -f1 $L/lista_l68.txt)"})
/usr/bin/nice -n 15 /usr/bin/python3 -I $L/script/calore_5v.py $L/seq/oggi $L/calore_5v.csv $CASI
