#!/bin/zsh
# L64b: the sequences of a list (default lista_l64b.txt) on the circuit of today, <paralleli> at a
# time (default 2: the user, 2026-11-03, «non caricare troppo la CPU ... ci sono altre sessioni di
# claude running oggi»), at low priority. The results go to seq/<etichetta>/<caso> (psu/corri_an.sh).
#
#   /bin/zsh script/corri_sequenze.sh [paralleli] [lista]
set -u
L=${0:A:h:h}
P=${1:-2}
LISTA=${2:-$L/lista_l64b.txt}
/usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $L/psu/corri_lista_an.sh $LISTA $P
