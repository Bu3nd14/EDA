#!/bin/zsh
# L64a, il dossier rigenerato: la scheda audio. ricorsa.sh <fase>
# Come L51a/script/ricorsa.sh: i 21 deck veloci (la lista di L48b/script/regressione.sh, la
# stessa di L66/regressione) piu' il selettore (tb_f1_selettore.cir) con run_simulation.sh in
# L64a/<fase>/<deck>/, 8 in parallelo; poi le due copie col bilanciamento rigenerate OGGI dai
# deck canonici (genera_bilanciamento.py) in L64a/<fase>/bilanciamento/. rc e durata in
# esiti.tsv. La seconda strada (confronta.py): le misure della corsa di L66 sulla variante
# lim365, cioe' il sorgente di oggi (L67 non ha cambiato il circuito).
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
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
while (( $(jobs -r | wc -l) >= 8 )); do sleep 1; done
uno $LOTTO/bilanciamento/tb_e5_bilanciamento.cir $OUT/bilanciamento/tb_e5_bilanciamento &
uno $LOTTO/bilanciamento/tb_loop_bilanciamento.cir $OUT/bilanciamento/tb_loop_bilanciamento &
wait
sort $OUT/esiti.tsv
