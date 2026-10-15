#!/bin/zsh
# uno.sh <deck.cir> : una corsa con run_simulation.sh in run/<gruppo>/<nome>/ (svuotata prima,
# limitations #35), e rc e durata in run/esiti.tsv. L60a, da L45d2b1/banco/script/uno.sh; la
# radice del repo e' cinque livelli sopra L60a/.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
d=$1
v=${d:h:t}
b=${d:t:r}
OUT=$L/run
rm -rf $OUT/$v/$b
mkdir -p $OUT/$v
t0=$SECONDS
/bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$v/$b > $OUT/$v/$b.stdout 2>&1
rc=$?
print -r -- "$v	$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
