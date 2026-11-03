#!/bin/zsh
# L68 (da L64c): l'analisi delle sequenze della FMEA del temporizzatore (psu/analizza_mc.py, le colonne di
# L54b3b), poi il confronto con la corsa sana di ogni evento (psu/confronta_l68.py).
set -u
L=${0:A:h:h}
cd $L || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_l68.csv seq/oggi/* > /dev/null || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_base.csv seq/base/* > /dev/null || exit 1
/usr/bin/python3 -I psu/confronta_l68.py an_l68.csv confronto_l68.csv > confronto_l68.txt || exit 1
echo "an_l68.csv: $(($(wc -l < an_l68.csv) - 1)) corse; confronto_l68.csv: $(($(wc -l < confronto_l68.csv) - 1))"
