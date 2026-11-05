#!/bin/zsh
# uno.sh <deck.cir> : una corsa con run_simulation.sh, a nice 10, in stax/run/<nome>/ (svuotata
# prima), rc e durata in stax/run/esiti.tsv. L72, da L45d2b3b2b2/script/uno.sh.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
d=$1
b=${d:t:r}
OUT=$L/stax/run
rm -rf $OUT/$b
mkdir -p $OUT
t0=$SECONDS
nice -n 10 /bin/zsh $ROOT/scripts/run_simulation.sh $d $OUT/$b > $OUT/$b.stdout 2>&1
rc=$?
print -r -- "$b	$rc	$((SECONDS-t0))" >> $OUT/esiti.tsv
