#!/bin/zsh
# esegui.sh : corre i 21 deck veloci di spice/preamp/tb/ (l'elenco di
# L40/script/deck_veloci.txt, per nome) con run_simulation.sh in
# docs/preamp/data/2026-09-27/L42/dopo/<deck>/, 8 in parallelo, e scrive rc e
# durata in dopo/esiti.tsv. L42a, da L40/script/esegui.sh: i deck si leggono
# dal repo che contiene questo script, non da un percorso cablato.
ROOT=${0:A:h:h:h:h:h:h:h}
OUT=$ROOT/docs/preamp/data/2026-09-27/L42/dopo
LISTA=$ROOT/docs/preamp/data/2026-09-23/L40/script/deck_veloci.txt
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local d=$1 b=${1:t:r} t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$b > $OUT/$b.stdout 2>&1
  local rc=$?
  print -r -- "$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for l in ${(f)"$(<$LISTA)"}; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $ROOT/spice/preamp/tb/${l:t} &
done
wait
sort $OUT/esiti.tsv
