#!/bin/zsh
# corri_p7_r153cc.sh [valore] : il deck di p7_r153cc.py in run/p7_r153cc/. L60d2, da corri_p7_l56.sh di L60d1.
L=${0:A:h:h}
D=$L/run/p7_r153cc${1:+_$1}
/usr/bin/python3 -I $L/script/p7_r153cc.py $1
cd $D
t0=$SECONDS
/opt/homebrew/bin/ngspice -b tb_mute_corto.cir > tb_mute_corto.log 2>&1
print -r -- "p7_r153cc rc=$? $((SECONDS-t0))s"
