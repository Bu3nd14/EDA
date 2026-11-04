#!/bin/zsh
# L69b: the analysis of the benches (psu/analizza.py <banco> 3.0: the event at 3 s) and the chassis
# estimate, as in L64b's README
set -u
L=${0:A:h:h}
/usr/bin/python3 -I $L/psu/analizza.py $L/rete 3.0 || exit 1
/usr/bin/python3 -I $L/psu/analizza.py $L/guasti 3.0 || exit 1
cd $L/termica || exit 1
/usr/bin/python3 -I $L/termica/stima_telaio_l64b.py > $L/termica/stima_telaio_l64b.txt || exit 1
echo "banchi e telaio: fatto"
