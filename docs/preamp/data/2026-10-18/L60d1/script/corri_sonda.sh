#!/bin/zsh
# corri_sonda.sh <variante ...> : le corse di sonda_blocco.py, in parallelo, nelle loro cartelle
# run/sonda/<variante>/. L60d1.
L=${0:A:h:h}
for x in $@; do
  (
    cd $L/run/sonda/$x
    t0=$SECONDS
    /opt/homebrew/bin/ngspice -b corsa.cir > corsa.log 2>&1
    print -r -- "$x rc=$? $((SECONDS-t0))s"
  ) &
done
wait
