#!/bin/zsh
# L68: la durata di una corsa di sequenza sul banco di oggi, per contare le ore prima della lista.
# Corre <caso> con la BASE di lista_l58a.py sotto l'etichetta «base», e stampa i secondi.
#   /bin/zsh script/cronometro.sh <caso>
set -u
L=${0:A:h:h}
t0=$(/bin/date +%s)
/usr/bin/nice -n 10 /bin/zsh $L/psu/corri_an.sh $1 base sorgente --n2n7002 ds --tss 3.0 \
    --comparatore tarato --ritenuta costruttore --bat54 costruttore --sonde-piu
t1=$(/bin/date +%s)
echo "$1: $((t1 - t0)) s"
