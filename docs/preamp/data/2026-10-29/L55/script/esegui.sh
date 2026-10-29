#!/bin/zsh
# esegui.sh <lista.txt> : esegue ogni deck della lista (deck/<variante>/<nome>.cir)
# con run_simulation.sh in run/<variante>/<nome>/, 8 in parallelo, e aggiunge
# rc e durata a run/esiti.tsv. L46a, da L40/script/esegui.sh.
# La cartella d'uscita di un deck si svuota prima della corsa (#35).
L46A=${0:A:h:h}
ROOT=${L46A:h:h:h:h:h}
OUT=$L46A/run
mkdir -p $OUT
uno() {
  local d=$1 v=${1:h:t} b=${1:t:r} t0=$SECONDS
  rm -rf $OUT/$v/$b
  mkdir -p $OUT/$v
  /bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$v/$b > $OUT/$v/$b.stdout 2>&1
  local rc=$?
  print -r -- "$v	$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for d in ${(f)"$(<$1)"}; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $d &
done
wait
print -r -- "fine: $1"
