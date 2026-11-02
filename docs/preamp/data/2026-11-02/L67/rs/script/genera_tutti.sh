#!/bin/zsh
# L67: i deck della sorgente per tutte le varianti, e una lista unica deck/lista_tutti.txt
S=${0:A:h}
D=${S:h}/deck
P=/usr/bin/python3
$P -I $S/genera.py l56
$P -I $S/genera.py l56 57
$P -I $S/genera.py oggi
$P -I $S/genera.py oggi 57
for c in t27_rame t27_minima t57_rame t57_minima; do
  $P -I $S/genera.py caldo_$c
done
cat $D/lista_l56__u27.txt $D/lista_l56__u57.txt $D/lista_oggi__u27.txt $D/lista_oggi__u57.txt \
    $D/lista_caldo_t27_rame.txt $D/lista_caldo_t27_minima.txt \
    $D/lista_caldo_t57_rame.txt $D/lista_caldo_t57_minima.txt > $D/lista_tutti.txt
wc -l $D/lista_tutti.txt
