#!/bin/zsh
# L51a, il dossier rigenerato: la scheda audio. ricorsa.sh <fase>
# I 21 deck veloci (la lista di L48b/script/regressione.sh, invariata) piu' il
# selettore (tb_f1_selettore.cir, F1, L48a) con run_simulation.sh in
# L51a/<fase>/<deck>/, 8 in parallelo; poi le due copie di L48b col
# bilanciamento (E5 girato di 3 dB, V1 fino a 5,6 kOhm di sorgente), dalle loro
# cartelle di L48b, in L51a/<fase>/bilanciamento/. rc e durata in esiti.tsv.
# Dopo L48b (c098be70) circuito, deck e modelli non sono cambiati: la seconda
# strada del dossier e' L48b/regressione/dopo (e L48a/misure per il selettore,
# L48b/{e5,v1}_bilanciamento/out per le copie), file per file.
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
L48B=$ROOT/docs/preamp/data/2026-10-07/L48b
OUT=$LOTTO/$1
rm -rf $OUT
mkdir -p $OUT/bilanciamento
: > $OUT/esiti.tsv
uno() {
  local deck=$1 dir=$2 b=${1:t:r} t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $deck $dir > $dir.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $OUT/esiti.tsv
}
for b in tb_ac tb_bias_sweep tb_blockA_carichi tb_dc_headroom tb_e3_e5 tb_e4_uscite \
         tb_idss_loop tb_idss_op_noise tb_loop_blockA tb_loop_bufferfissa tb_loop \
         tb_mute_corto tb_noise_breakdown tb_noise_vectors tb_op \
         tb_switch_v2_counterfactual tb_switch_v2 tb_trim tb_uscite_fisse tb_v3_overload \
         tb_zout_psrr_noise tb_f1_selettore; do
  while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
  uno $ROOT/spice/preamp/tb/$b.cir $OUT/$b &
done
uno $L48B/e5_bilanciamento/tb_e5_bilanciamento.cir $OUT/bilanciamento/tb_e5_bilanciamento &
uno $L48B/v1_bilanciamento/tb_loop_bilanciamento.cir $OUT/bilanciamento/tb_loop_bilanciamento &
wait
sort $OUT/esiti.tsv
