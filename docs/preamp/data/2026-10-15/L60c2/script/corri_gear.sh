#!/bin/zsh
# corri_gear.sh <corsa>... : le corse di V2 nella variante gear di sonda_v2.py, tutte in parallelo,
# nella cartella run/sonda_v2/gear (wrdata scrive nella cartella corrente). L60c2.
L=${0:A:h:h}
cd $L/run/sonda_v2/gear
for c in "$@"; do
  ( t0=$SECONDS; /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1; print -r -- "gear $c rc=$? $((SECONDS-t0))s" >> $L/run/sonda_v2/esiti.txt ) &
done
wait
print -r -- "fine gear"
