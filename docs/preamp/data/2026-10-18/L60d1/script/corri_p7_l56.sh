#!/bin/zsh
# corri_p7_l56.sh <fase> [r153] : il deck di p7_l56.py in run/p7_l56/<fase>/. L60d1.
L=${0:A:h:h}
D=$L/run/p7_l56/$1
/usr/bin/python3 -I $L/script/p7_l56.py $1 $D $2
cd $D
t0=$SECONDS
/opt/homebrew/bin/ngspice -b tb_mute_corto.cir > tb_mute_corto.log 2>&1
print -r -- "p7_l56 $1 rc=$? $((SECONDS-t0))s"
