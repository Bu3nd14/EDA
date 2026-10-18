#!/bin/zsh
# corri_shunt.sh : le corse di prepara_shunt.py (shunt/lista.txt) con run_simulation.sh, in
# shunt/<variante>/run/<deck>/, 6 in parallelo. rc e durata in shunt/esiti.tsv. L60d1.
zmodload zsh/parameter
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
: > $L/shunt/esiti.tsv
uno() {
  local v=$1 k=$2 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $L/shunt/$v/deck/$k.cir $L/shunt/$v/run/$k > $L/shunt/$v/$k.stdout 2>&1
  print -r -- "$v	$k	$?	$((SECONDS-t0))" >> $L/shunt/esiti.tsv
}
for riga in ${(f)"$(cat $L/shunt/lista.txt)"}; do
  while (( ${#jobstates} >= 6 )); do sleep 1; done
  uno ${=riga} &
done
wait
sort $L/shunt/esiti.tsv
