#!/bin/zsh
# uno.sh <etichetta> <caso> [opzioni] - L45d2b2b1: one case through corri_seq.sh, its output in
# seq/<etichetta>/log_<caso>.txt (corri_seq.sh empties seq/<etichetta>/<caso>/ first)
set -u
D=${0:A:h}
etich=$1
caso=$2
shift 2
mkdir -p "$D:h/seq/$etich"
/bin/zsh "$D/corri_seq.sh" "$caso" "$etich" "$@" > "$D:h/seq/$etich/log_$caso.txt" 2>&1
rc=$?
echo "$caso: rc $rc"
exit 0
