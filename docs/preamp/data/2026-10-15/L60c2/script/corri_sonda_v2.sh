#!/bin/zsh
# corri_sonda_v2.sh <corsa> : le varianti di sonda_v2.py di una corsa di V2, in parallelo, ciascuna
# nella sua cartella (wrdata scrive nella cartella corrente). L60c2.
L=${0:A:h:h}
c=$1
for v in ck01 gear; do
  ( cd $L/run/sonda_v2/$v && /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1; print -r -- "$v $c rc=$?" >> $L/run/sonda_v2/esiti.txt ) &
done
wait
print -r -- "fine sonda $c"
