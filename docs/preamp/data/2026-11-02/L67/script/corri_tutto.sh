#!/bin/zsh
# L67: genera e corre la catena (sette blocchi), il caso noto 4 e la sorgente (otto varianti), in
# quest'ordine, 9 corse in parallelo per banco.
L=${0:A:h:h}
P=/usr/bin/python3
$P -I $L/script/avvolgi.py
$P -I $L/catena/script/genera.py l56 oggi oggi_avv caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/bin/zsh $L/catena/script/esegui.sh $L/catena/deck/lista_l56_oggi_oggi_avv_caldo_t27_rame_caldo_t27_minima_caldo_t57_rame_caldo_t57_minima.txt 9
$P -I $L/noto/script/genera.py
/bin/zsh $L/noto/script/esegui.sh $L/noto/deck/lista.txt 8
/bin/zsh $L/rs/script/genera_tutti.sh
/bin/zsh $L/rs/script/esegui.sh $L/rs/deck/lista_tutti.txt 9
print -r -- "corri_tutto: fine"
