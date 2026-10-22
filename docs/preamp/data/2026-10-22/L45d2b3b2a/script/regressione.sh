#!/bin/zsh
# L45d2b3b2a (copiato da L45d2b3b1/script/regressione.sh): regressione.sh <variante> : i 21 deck
# veloci di regressione/deck_<variante>/ (prepara_regressione.py) con run_simulation.sh in
# regressione/<variante>/<deck>/, 6 in parallelo. rc e durata in regressione/<variante>/esiti.tsv.
zmodload zsh/parameter
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
IN=$LOTTO/regressione/deck_$1
OUT=$LOTTO/regressione/$1
rm -rf $OUT
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local b=$1 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $IN/$b.cir $OUT/$b > $OUT/$b.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for f in $IN/*.cir; do
  while (( ${#jobstates} >= 6 )); do sleep 1; done
  uno ${f:t:r} &
done
wait
sort $OUT/esiti.tsv
