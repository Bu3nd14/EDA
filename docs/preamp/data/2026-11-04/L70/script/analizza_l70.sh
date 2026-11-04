#!/bin/zsh
# L70: the analysis of the variants' sequences (psu/analizza_mc.py, L54b3b's columns, as L69b's
# an_l64b.csv) -> an_l70.csv, and the fuses on the raw side's shorts (script/fusibili.py).
#   /bin/zsh script/analizza_l70.sh
set -u
setopt nullglob
L=${0:A:h:h}
cd $L || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_l70.csv \
    seq/s2/* seq/s2_m10/* seq/s2_p10/* seq/s1/* seq/s1_m10/* seq/s1_p10/* \
    seq/s1s2/* seq/s1s2_m10/* seq/s1s2_p10/* seq/guasti_oggi/* seq/guasti_s1/* || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I script/fusibili.py
