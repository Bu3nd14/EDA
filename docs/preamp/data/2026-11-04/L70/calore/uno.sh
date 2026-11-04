#!/bin/zsh
# uno.sh <deck.cir> : L66's script/uno.sh for calore/ (the repo's root six levels above this folder):
# one run with run_simulation.sh in calore/run/<group>/<name>/ (emptied first, limitations #35),
# rc and duration in calore/run/esiti.tsv.
C=${0:A:h}
ROOT=${C:h:h:h:h:h:h}
d=$1
v=${d:h:t}
b=${d:t:r}
OUT=$C/run
rm -rf $OUT/$v/$b
mkdir -p $OUT/$v
t0=$SECONDS
/bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$v/$b > $OUT/$v/$b.stdout 2>&1
rc=$?
print -r -- "$v	$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
