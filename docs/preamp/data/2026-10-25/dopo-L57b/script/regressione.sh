#!/bin/zsh
# L57b: regressione.sh <prima|dopo> : i deck canonici di spice/preamp/tb/ che modellano l'ingresso
# del blocco A (E3, E5, il trim, il selettore, il margine del blocco A: V1), con run_simulation.sh in
# regressione/<fase>/<deck>/, 3 in parallelo (limitations #75). «prima» sui deck di main, «dopo» coi
# deck che includono il limitatore generato (spice/preamp/input_limiter.subckt, ADR-101).
# rc e durata in regressione/<fase>/esiti.tsv.
zmodload zsh/parameter
FASE=$1
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
IN=$ROOT/spice/preamp/tb
OUT=$LOTTO/regressione/$FASE
TB=(tb_e3_e5 tb_trim tb_f1_selettore tb_loop_blockA)
rm -rf $OUT
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local b=$1 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $IN/$b.cir $OUT/$b > $OUT/$b.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for b in $TB; do
  while (( ${#jobstates} >= 3 )); do sleep 1; done
  uno $b &
done
wait
sort $OUT/esiti.tsv
