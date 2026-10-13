#!/bin/zsh
# analizza_vuoto.sh : le analisi P10 delle corse di L45a rifatte a vuoto (run/vuoto_tr_*), una
# famiglia per processo, poi sintesi_p10.py. L45b.
L=${0:A:h:h}
S=$L/script
R=$L/run
P=/usr/bin/python3
for v in A F1 F2 B B_g10; do
  $P $S/analizza_p10.py $L/analisi_vuoto_$v.csv $R/vuoto_tr_$v/*(/) &
done
$P $S/analizza_p10.py $L/analisi_vuoto_rifatte.csv $R/vuoto_tr_corta_*/*(/) $R/vuoto_tr_gear_*/*(/) $R/vuoto_tr_r120_B/*(/) &
$P $S/analizza_p10.py $L/analisi_vuoto_taglio.csv $R/vuoto_tr_taglio*/*(/) $R/vuoto_tr_ctrl_*/*(/) &
wait
$P $S/sintesi_p10.py
print -r -- "fine analisi"
