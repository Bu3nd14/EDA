#!/bin/zsh
# esegui.sh <fase> <deck>... : esegue ogni deck con run_simulation.sh in
# docs/preamp/data/2026-09-23/L40/<fase>/<deck>/, 8 in parallelo, e scrive
# rc e durata in <fase>/esiti.tsv. L40, da L39/script/esegui_deck.sh.
ROOT=${0:A:h:h:h:h:h:h:h}
FASE=$1; shift
[ "$1" = "-f" ] && { set -- ${(f)"$(<$2)"}; }
OUT=$ROOT/docs/preamp/data/2026-09-23/L40/$FASE
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local d=$1 b=${1:t:r} t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$b > $OUT/$b.stdout 2>&1
  local rc=$?
  print -r -- "$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for d in "$@"; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $d &
done
wait
sort $OUT/esiti.tsv
