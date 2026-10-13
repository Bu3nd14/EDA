#!/bin/zsh
# analizza_tutto.sh : tutte le analisi e le sintesi di L45a, dalle corse in run/. Ordine e
# famiglie come nel README. Le famiglie senza musica in parallelo (una per processo).
L=${0:A:h:h}
S=$L/script
R=$L/run
P=/usr/bin/python3
$P $S/analizza_tr.py $L/analisi_ctrl.csv $R/tr_ctrl_A/CTRL_OUT_VP $R/tr_ctrl_F2/CTRL_OUT_VP $R/tr_ctrl_B/CTRL_OUT_VP &
for v in A F1 F2 B B_g10; do
  $P $S/analizza_tr.py $L/analisi_$v.csv $R/tr_$v/*/(/) &
done
$P $S/analizza_tr.py $L/analisi_rifatte.csv $R/tr_corta_A/Q133_ae $R/tr_corta_A/R135_ap $R/tr_gear_A/C124_cc $R/tr_gear_A/R109_ap $R/tr_gear_A/R131_ap $R/tr_gear_F2/Q146_ce $R/tr_r120_B/R120_cc &
$P $S/analizza_tr.py $L/analisi_mute.csv $R/tr_mute_B/Q132_ce $R/tr_mute_B/Q122_ce $R/tr_mute_B/Q146_ae $R/tr_mute_A/Q122_ce $R/tr_mute_A/Q146_ae &
$P $S/analizza_tr.py $L/analisi_musica_B.csv $R/tr_musica_B/Q132_ce $R/tr_musica_B/Q133_ce $R/tr_musica_B/Q122_ce $R/tr_musica_B/Q146_ae --rif $R/tr_musica_B/rif &
$P $S/analizza_tr.py $L/analisi_musica_A.csv $R/tr_musica_A/Q122_ce $R/tr_musica_A/Q146_ae --rif $R/tr_musica_A/rif &
wait
for v in A F1 F2 B B_g10 rifatte; do
  $P $S/sintesi.py $L/sintesi_$v.csv $L/analisi_$v.csv
done
print -r -- "fine analisi"
