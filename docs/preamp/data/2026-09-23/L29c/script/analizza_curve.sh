#!/bin/zsh
# analizza_curve.sh: analisi e verdetto delle quattro coppie di curve della LDR (punto 6), una dopo
# l'altra; aspetta che la coppia sia corsa per intero (18 righe in tempi.txt).
L=${0:A:h:h}
for c in AA AD DA DD; do
  while [ ! -f $L/curve/$c/tempi.txt ] || [ $(wc -l < $L/curve/$c/tempi.txt) -lt 18 ]; do
    sleep 30
  done
  /usr/bin/python3 $L/script/analizza_par.py $L/curve/$c/manifest_sel.csv $L/curve/$c $L/curve/$c/analisi.csv 3
  /usr/bin/python3 $L/script/verdetto.py $L/curve/$c/manifest_sel.csv $L/curve/$c/analisi.csv $L/curve/$c/verdetto.csv
done
