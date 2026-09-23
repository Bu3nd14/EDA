#!/bin/zsh
# genera_b_cf.sh : strada (b) a +1,5 dB (RG0 7.87k, R138 6.49k) col C_f (C137,
# 330p da ADR-025) spazzato: con una R_g presente anche nel modo basso, C_f fa
# uno zero (1/(2 pi 1.5k C137)) sopra cui il guadagno di rumore torna verso 1, e
# il guadagno in piu' compra poco margine al crossover. R128 1.69k e 1.33k.
S=${0:A:h}
mkdir -p $S/../strada_b_cf
: > $S/../strada_b_cf/lista.txt
for cf in 100p 150p 220p 330p 470p; do
  for cm in 470p 560p; do
   for r in 1.69k 1.33k; do
    e=g15_cf${cf}_cm${cm}_r${r}
    /usr/bin/python3 $S/varianti.py strada_b_cf tb_loop $e "+RG0L40 FB 0 7.87k" "alter r138 = 6.49k" "alter c137 = $cf" "alter c124 = $cm" "alter r128 = $r" >> $S/../strada_b_cf/lista.txt
    for d in tb_loop_blockA tb_loop_bufferfissa; do
      /usr/bin/python3 $S/varianti.py strada_b_cf $d $e "+RG0L40 FB 0 7.87k" "alter c137 = $cf" "alter c124 = $cm" "alter r128 = $r" >> $S/../strada_b_cf/lista.txt
    done
   done
  done
done
wc -l $S/../strada_b_cf/lista.txt
