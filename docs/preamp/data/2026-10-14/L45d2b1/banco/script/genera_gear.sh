#!/bin/zsh
# genera_gear.sh : le corse che trap ferma con «Timestep too small» (analizza_p10.py: CORSA CORTA),
# rifatte col metodo gear come i vuoto_tr_gear_* di L45b. Lista: deck/lista_gear.txt. L45d2b1.
L=${0:A:h:h}
D=$L/deck
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti A --gear R131_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --gear Q146_ce R131_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F2 --gear Q146_ce R131_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --gear R131_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti B --ccout --gear JQ110A_ds R131_ap R138_ap
/usr/bin/python3 -I $L/script/genera_rivelatore.py guasti F1 --ccout --gear Q146_ce R131_ap
cat $D/lista_riv_A_gear.txt $D/lista_riv_F1_gear.txt $D/lista_riv_F2_gear.txt $D/lista_riv_B_gear.txt \
    $D/lista_riv_B_cc_gear.txt $D/lista_riv_F1_cc_gear.txt > $D/lista_gear.txt
print -r -- "lista_gear: $(wc -l < $D/lista_gear.txt) deck"
