#!/bin/zsh
# confronta_serie.sh <prefisso> - L54b3a: a run set of L54b2's safety list (lista_finale.txt's
# lines under another label prefix, e.g. q_) analysed with L54b2's analizza_an.py in L54b2's row
# order (dirs_noto.py) and compared with L54b2's fint_ (the calibrated comparator, no remedy) by
# L54b2's confronta_noto.py. Writes ../an_<prefisso>seq.csv, ../an_<prefisso>fmea.csv and
# ../confronta_<prefisso>{seq,fmea}.txt.
set -u
D=${0:A:h}
L=$D:h
B=$L:h/L54b2
for che in seq fmea; do
    dirs=(${(z)"$(/usr/bin/python3 -I $B/dirs_noto.py $L $1 $che)"})
    /usr/bin/python3 -I $B/psu/analizza_an.py --te=3.0 $L/an_$1$che.csv $dirs > /dev/null
    /usr/bin/python3 -I $B/confronta_noto.py $B/an_fint_$che.csv $L/an_$1$che.csv > $L/confronta_$1$che.txt
    echo "$che: rc $? ($L/confronta_$1$che.txt)"
done
