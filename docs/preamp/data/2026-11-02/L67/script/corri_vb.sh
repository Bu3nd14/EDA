#!/bin/zsh
# L67: rigenera la catena e corre solo i deck del volume basso (_vb) dei sette blocchi
L=${0:A:h:h}
/usr/bin/python3 -I $L/catena/script/genera.py l56 oggi oggi_avv caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
grep '_vb\.cir$' $L/catena/deck/lista_l56_oggi_oggi_avv_caldo_t27_rame_caldo_t27_minima_caldo_t57_rame_caldo_t57_minima.txt > $L/catena/deck/lista_vb.txt
wc -l $L/catena/deck/lista_vb.txt
/bin/zsh $L/catena/script/esegui.sh $L/catena/deck/lista_vb.txt 9
print -r -- "corri_vb: fine"
