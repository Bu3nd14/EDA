#!/bin/zsh
# L47c1 (copiato da L47b2b1; la sola modifica: tb_e3_e5_ldr -> tb_e3_e5, il deck
# rinominato senza celle, ADR-062). regressione.sh <fase> : i 21 deck veloci di L40
# con run_simulation.sh in regressione/<fase>/<deck>/, 8 in parallelo.
# rc e durata in regressione/<fase>/esiti.tsv.
# Atteso, contro L47b2b1/regressione/dopo: cambiano tb_e3_e5 (le celle tolte, E3
# col minimo vero: limitations #45) e la colonna zmin di tb_trim_e3.csv (#45);
# nient'altro: le celle stavano solo in tb_e3_e5_ldr.
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
OUT=$LOTTO/regressione/$1
rm -rf $OUT
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local b=$1 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $ROOT/spice/preamp/tb/$b.cir $OUT/$b > $OUT/$b.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for b in tb_ac tb_bias_sweep tb_blockA_carichi tb_dc_headroom tb_e3_e5 tb_e4_uscite \
         tb_idss_loop tb_idss_op_noise tb_loop_blockA tb_loop_bufferfissa tb_loop \
         tb_mute_corto tb_noise_breakdown tb_noise_vectors tb_op \
         tb_switch_v2_counterfactual tb_switch_v2 tb_trim tb_uscite_fisse tb_v3_overload \
         tb_zout_psrr_noise; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $b &
done
wait
sort $OUT/esiti.tsv
