#!/bin/zsh
# corri_lista.sh <lista> <etichetta> [opzioni di genera_tb_psu.py] - L45d2b2b1: every case of
# <lista> (one per line) through uno.sh, at most 8 at a time (xargs -P 8, limitations #58), the
# results in seq/<etichetta>/<caso>, each case's output in seq/<etichetta>/log_<caso>.txt
set -u
D=${0:A:h}
lista=$1
etich=$2
shift 2
/usr/bin/xargs -P 8 -I CASO /bin/zsh "$D/uno.sh" "$etich" CASO "$@" < "$lista"
echo "fatto: $(wc -l < "$lista") casi in seq/$etich"
