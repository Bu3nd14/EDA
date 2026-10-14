#!/bin/zsh
# genera_corte2.sh : il secondo giro delle corse lente fino a 0,6 s. Con la compensazione di ADR-079
# anche Q133 (emettitore aperto) e R135 (aperta) non finivano piu' in F1, F2, B e B col
# condensatore d'uscita in corto (oltre un'ora); a +10 dB si'. Lista: deck/lista_corte2.txt. L45d2b1.
L=${0:A:h:h}
D=$L/deck
: > $D/lista_corte2.txt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --tfine 0.6 Q133_ae R135_ap
cat $D/lista_riv_F1_corta.txt >> $D/lista_corte2.txt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F2 --tfine 0.6 Q133_ae R135_ap
cat $D/lista_riv_F2_corta.txt >> $D/lista_corte2.txt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --tfine 0.6 Q133_ae R135_ap
cat $D/lista_riv_B_corta.txt >> $D/lista_corte2.txt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --ccout --tfine 0.6 Q133_ae R135_ap
cat $D/lista_riv_B_cc_corta.txt >> $D/lista_corte2.txt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --ccout --tfine 0.6 Q133_ae R135_ap
cat $D/lista_riv_F1_cc_corta.txt >> $D/lista_corte2.txt
print -r -- "lista_corte2: $(wc -l < $D/lista_corte2.txt) deck"
