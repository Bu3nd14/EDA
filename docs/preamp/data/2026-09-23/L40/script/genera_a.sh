#!/bin/zsh
# genera_a.sh : strada (a), banda ridotta. Il Miller C124 (470p generato) e il
# moltiplicatore R128 (1.69k generato: I_q 20,3 mA; 1.33k: 14,6 mA) sulle tre
# istanze a guadagno unitario (tb_loop ha anche +3 e +10 dB). La coppia
# (470p, 1.69k) e' il controllo: deve ridare le tabelle di L39/dopo.
# Scrive i deck in strada_a/ e la loro lista in strada_a/lista.txt.
S=${0:A:h}
mkdir -p $S/../strada_a
: > $S/../strada_a/lista.txt
for cm in 470p 560p 680p 820p 1n 1.2n; do
  for r in 1.69k 1.33k; do
    for d in tb_loop tb_loop_blockA tb_loop_bufferfissa; do
      /usr/bin/python3 $S/varianti.py strada_a $d cm${cm}_r${r} "alter c124 = $cm" "alter r128 = $r" >> $S/../strada_a/lista.txt
    done
  done
done
wc -l $S/../strada_a/lista.txt
