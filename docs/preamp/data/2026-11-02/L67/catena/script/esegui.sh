#!/bin/zsh
# esegui.sh <lista.txt> [n] : esegue ogni deck della lista (deck/<blocco>/<nome>.cir)
# con run_simulation.sh in run/<blocco>/<nome>/, n in parallelo (8 se omesso), e aggiunge
# rc e durata a run/esiti.tsv. L67, da L56/catena (L46b) con il conteggio dei job di L60d1
# (${#jobstates}: `jobs -r | wc -l` in una sostituzione non vede i job del padre).
# La cartella d'uscita di un deck si svuota prima della corsa (#35).
zmodload zsh/parameter
BASE=${0:A:h:h}
# BASE = L67/catena: la radice sta sei livelli sopra (catena, L67, 2026-11-02, data, preamp, docs)
ROOT=${BASE:h:h:h:h:h:h}
OUT=$BASE/run
N=${2:-8}
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
  while (( ${#jobstates} >= N )); do sleep 1; done
  uno $d &
done
wait
print -r -- "fine: $1"
