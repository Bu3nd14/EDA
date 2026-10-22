#!/bin/zsh
# L45d2b3b2b1: regressione.sh : i 21 deck veloci (la lista di prepara_regressione.py di L45d2b3b2a)
# di spice/preamp/tb/, cioe' il blocco del sorgente (ADR-099), con run_simulation.sh in
# regressione/dopo/<deck>/, 6 in parallelo. rc e durata in regressione/dopo/esiti.tsv.
# Il «prima» e' regressione/oggi/ di L45d2b3b2a (lo stesso blocco di main, confronta_rv2.py).
zmodload zsh/parameter
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
IN=$ROOT/spice/preamp/tb
OUT=$LOTTO/regressione/dopo
TB=(tb_ac tb_bias_sweep tb_blockA_carichi tb_dc_headroom tb_e3_e5 tb_e4_uscite tb_idss_loop
    tb_idss_op_noise tb_loop_blockA tb_loop_bufferfissa tb_loop tb_mute_corto tb_noise_breakdown
    tb_noise_vectors tb_op tb_switch_v2_counterfactual tb_switch_v2 tb_trim tb_uscite_fisse
    tb_v3_overload tb_zout_psrr_noise)
rm -rf $OUT
mkdir -p $OUT
: > $OUT/esiti.tsv
uno() {
  local b=$1 t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $IN/$b.cir $OUT/$b > $OUT/$b.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for b in $TB; do
  while (( ${#jobstates} >= 6 )); do sleep 1; done
  uno $b &
done
wait
sort $OUT/esiti.tsv
