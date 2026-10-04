#!/bin/zsh
# corri_sonda.sh - L47b2b1: corre in parallelo le varianti di varianti.py (ogni *__*.cir di questa
# cartella), dalla cartella stessa (i .dat restano qui), e scrive esito.txt: rc, «Timestep too
# small» e l'istante dove si ferma, «Transient op».
QUI=${0:A:h}
cd $QUI
: > esito.txt
for f in *__*.cir; do
  n=${f%.cir}
  ( /opt/homebrew/bin/ngspice -b $f > $n.log 2>&1
    rc=$?
    ts=$(grep -o 'Timestep too small; time = [0-9.e+-]*' $n.log | head -1)
    op=$(grep -c 'Transient op started' $n.log)
    print -r -- "$n rc=$rc topstart=$op ${ts:-completa}" >> esito.txt ) &
done
wait
sort esito.txt
