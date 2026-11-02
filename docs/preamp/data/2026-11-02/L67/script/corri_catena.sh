#!/bin/zsh
# L67: la catena intera coi nodeset (sette blocchi, griglia di L56 e volume basso), da zero
L=${0:A:h:h}
rm -rf $L/catena/run $L/catena/deck
/usr/bin/python3 -I $L/catena/script/genera.py l56 oggi oggi_avv caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/bin/zsh $L/catena/script/esegui.sh $L/catena/deck/lista_l56_oggi_oggi_avv_caldo_t27_rame_caldo_t27_minima_caldo_t57_rame_caldo_t57_minima.txt 9
print -r -- "corri_catena: fine"
