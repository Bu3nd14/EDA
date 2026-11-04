#!/bin/zsh
# L70: the mains holes (lista_buchi_<v>.txt) -> an_buchi_<v>.csv (analizza_mc.py), and today's raw-side
# faults (lista_corti_oggi.txt, label oggi_corti... label "oggi") -> fusibili_oggi.csv.
#   /bin/zsh script/analizza_buchi.sh <variante>...
set -u
L=${0:A:h:h}
cd $L || exit 1
for v in "$@"; do
    dirs=(seq/${v}_b*/buco200(/))
    /usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_buchi_$v.csv $dirs > /dev/null || exit 1
    echo "an_buchi_$v.csv: ${#dirs} corse"
done
