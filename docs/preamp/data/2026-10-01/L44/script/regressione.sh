#!/bin/zsh
# regressione.sh <fase> : i 21 deck veloci di L40 (script/deck_veloci.txt di L40,
# qui ripuntati al worktree corrente) con run_simulation.sh in
# regressione/<fase>/<deck>/, 8 in parallelo. L44 (copiato da L46b senza altre
# modifiche): <fase> = dopo, i modelli col flicker di ADR-057; il «prima» e'
# ../../L46b/regressione/dopo (stesso blocco, modelli senza flicker).
# rc e durata in regressione/<fase>/esiti.tsv.
L46A=${0:A:h:h}
ROOT=${L46A:h:h:h:h:h}
OUT=$L46A/regressione/$1
rm -rf $OUT
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local b=$1 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $ROOT/spice/preamp/tb/$b.cir $OUT/$b > $OUT/$b.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for b in tb_ac tb_bias_sweep tb_blockA_carichi tb_dc_headroom tb_e3_e5_ldr tb_e4_uscite \
         tb_idss_loop tb_idss_op_noise tb_loop_blockA tb_loop_bufferfissa tb_loop \
         tb_mute_corto tb_noise_breakdown tb_noise_vectors tb_op \
         tb_switch_v2_counterfactual tb_switch_v2 tb_trim tb_uscite_fisse tb_v3_overload \
         tb_zout_psrr_noise; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $b &
done
wait
sort $OUT/esiti.tsv
