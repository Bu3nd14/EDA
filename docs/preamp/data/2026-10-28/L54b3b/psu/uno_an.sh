#!/bin/zsh
# uno_an.sh <caso> <etichetta> <timer> [opzioni] - L54a: one line of corri_lista_an.sh
set -u
D=${0:A:h}
mkdir -p "$D:h/seq"
/bin/zsh "$D/corri_an.sh" "$@" > "$D:h/seq/log_an_$2_$1.txt" 2>&1
echo "$2 $1: rc $?"
exit 0
