#!/bin/zsh
# L69: the analysis of the options' runs. For each label given (seq/<label>/*): psu/analizza_mc.py into
# an_<nome>.csv, the healthy ones against L64b (psu/confronta_l69.py -> confronto_<nome>.csv), the
# fault runs' heat (script/calore_ritenuta.py -> calore_<nome>.csv).
#   /bin/zsh script/analizza_l69.sh <nome> <label> [<label> ...]
set -u
L=${0:A:h:h}
cd $L || exit 1
nome=$1
shift
dirs=()
guasti=()
for e in "$@"; do
    for d in seq/$e/*(/); do
        [ -f $d/ok.txt ] || { echo "manca ok.txt: $d"; continue; }
        dirs+=$d
        case ${d:t} in f_*) guasti+=$d ;; esac
    done
done
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_$nome.csv $dirs > /dev/null || exit 1
/usr/bin/python3 -I psu/confronta_l69.py an_$nome.csv confronto_$nome.csv > confronto_$nome.txt || exit 1
: > calore_$nome.txt
for d in $guasti; do
    /usr/bin/python3 -I script/calore_ritenuta.py ${d:h} /dev/null ${d:t} | sed "s|^|${d:h:t}/|" >> calore_$nome.txt
done
cat confronto_$nome.txt calore_$nome.txt
