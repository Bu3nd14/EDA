#!/bin/zsh
# L64b: the analysis of the 58 sequences (psu/analizza_mc.py, L54b3b's columns), the standby census
# (psu/censimento.py, L58b) and the second road (script/confronta.py).
set -u
L=${0:A:h:h}
cd $L || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_l64b.csv seq/oggi/* seq/oggi_m10/* seq/oggi_p10/* || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/censimento.py censimento_psu.csv seq/oggi/* || exit 1
/usr/bin/python3 -I script/confronta.py
# L69b: the second road against L64b (the same bench on the circuit before ADR-116), cell by cell
/usr/bin/python3 -I script/confronta_l64b.py
