#!/bin/zsh
# L64c (da L64b): l'analisi delle 42 sequenze nuove della FMEA (psu/analizza_mc.py, le colonne di L54b3b).
set -u
L=${0:A:h:h}
cd $L || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_l64c.csv seq/oggi/* || exit 1
