#!/bin/zsh
# L70: fusibili.py on the raw-side faults (f_*) and the events of a label family -> fusibili_<label>.csv
#   /bin/zsh script/analizza_fus.sh <etichetta> [f|tutti]
set -u
L=${0:A:h:h}
cd $L || exit 1
e=$1
dirs=()
for d in seq/$e seq/${e}_m10 seq/${e}_p10; do
    [ -d $d ] || continue
    if [ "${2:-tutti}" = "f" ]; then dirs+=($d/f_*(/N)); else dirs+=($d/*(/N)); fi
done
/usr/bin/nice -n 15 /usr/bin/python3 -I script/fusibili.py fusibili_$e.csv $dirs
