#!/bin/zsh
# genera_r120.sh : R120 in corto, in ogni posizione, fino a 0,45 s. Il simulatore ci avanza di ~2 ms
# al minuto (fino a 0,6 s servivano piu' di due ore a corsa): 0,45 s bastano per lo scatto (~72 ms
# dopo il guasto a 0,3 s) e per vedere il jack, staccato, tornare sotto il tetto. Lista:
# deck/lista_r120.txt. L45d2b1.
L=${0:A:h:h}
D=$L/deck
: > $D/lista_r120.txt
for a in "A" "F1" "F2" "B" "B --gain 10" "B --ccout" "F1 --ccout"; do
    /usr/bin/python3 -I $L/script/genera_rivelatore.py guasti ${=a} --tfine 0.45 R120_cc
done
cat $D/lista_riv_A_corta.txt $D/lista_riv_F1_corta.txt $D/lista_riv_F2_corta.txt \
    $D/lista_riv_B_corta.txt $D/lista_riv_B_g10_corta.txt $D/lista_riv_B_cc_corta.txt \
    $D/lista_riv_F1_cc_corta.txt > $D/lista_r120.txt
print -r -- "lista_r120: $(wc -l < $D/lista_r120.txt) deck"
