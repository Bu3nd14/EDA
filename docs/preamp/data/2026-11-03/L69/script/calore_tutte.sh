#!/bin/zsh
# L69 (from L68): calore_5v.py (U504, U512) on every fault run of lista_sorgente.txt (seq/oggi) -> calore_5v.csv
set -u
L=${0:A:h:h}
CASI=(${(f)"$(/usr/bin/grep '^f_' $L/lista_sorgente.txt | /usr/bin/cut -d' ' -f1)"})
/usr/bin/nice -n 15 /usr/bin/python3 -I $L/script/calore_5v.py $L/seq/oggi $L/calore_5v.csv $CASI
