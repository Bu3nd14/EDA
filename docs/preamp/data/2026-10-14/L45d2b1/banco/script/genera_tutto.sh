#!/bin/zsh
# genera_tutto.sh : tutti i deck del banco del rivelatore e la lista unica deck/lista_tutto.txt -
# le corse piccole, poi i guasti, poi le corse lente fino a 0,6 s (in fondo, perche' occupano un
# posto per decine di minuti). L45d2b1.
#
# Le lente sono i modi che nel primo giro non finivano in 10 min (come i tr_corta_* di L45a):
# R120 in corto in ogni posizione, Q133 col emettitore aperto e R135 aperta nel blocco A.
L=${0:A:h:h}
D=$L/deck
for c in prova musica rail accensione; do
    /usr/bin/python3 -I $L/script/genera_rivelatore.py $c
done
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti A
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F2
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --gain 10
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --ccout
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --ccout
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti A --tfine 0.6 Q133_ae R120_cc R135_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --tfine 0.6 R120_cc
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F2 --tfine 0.6 R120_cc
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --tfine 0.6 R120_cc
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --gain 10 --tfine 0.6 R120_cc
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --ccout --tfine 0.6 R120_cc
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --ccout --tfine 0.6 R120_cc
cat $D/lista_prova.txt $D/lista_musica.txt $D/lista_rail.txt $D/lista_accensione.txt > $D/lista_tutto.txt
cat $D/lista_riv_A.txt $D/lista_riv_F1.txt $D/lista_riv_F2.txt $D/lista_riv_B.txt \
    $D/lista_riv_B_g10.txt $D/lista_riv_B_cc.txt $D/lista_riv_F1_cc.txt \
    | grep -v -e '/R120_cc.cir$' -e 'riv_A/Q133_ae.cir$' -e 'riv_A/R135_ap.cir$' >> $D/lista_tutto.txt
cat $D/lista_riv_*_corta.txt >> $D/lista_tutto.txt
print -r -- "lista_tutto: $(wc -l < $D/lista_tutto.txt) deck"
