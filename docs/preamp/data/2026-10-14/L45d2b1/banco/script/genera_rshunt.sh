#!/bin/zsh
# genera_rshunt.sh : Q146 in corto, dove anche gear si ferma all'istante dello scatto (0,376 s):
# gear e rshunt = 1e10. Lista: deck/lista_rshunt.txt. L45d2b1.
L=${0:A:h:h}
D=$L/deck
rm -rf $D/riv_F1_gear_rshunt $L/run/riv_F1_gear_rshunt
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --gear --rshunt Q146_ce
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F2 --gear --rshunt Q146_ce
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --ccout --gear --rshunt Q146_ce
cat $D/lista_riv_F1_gear_rshunt.txt $D/lista_riv_F2_gear_rshunt.txt $D/lista_riv_F1_cc_gear_rshunt.txt > $D/lista_rshunt.txt
print -r -- "lista_rshunt: $(wc -l < $D/lista_rshunt.txt) deck"
