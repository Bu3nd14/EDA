#!/bin/zsh
# L64a: le corse della seconda strada. seconda.sh
#  - il deck tb_mute_corto di L66 (regressione/deck_lim365) ricorso in L64a/l66_mute/;
#  - il selettore e le due copie col bilanciamento col blocco della variante lim365 di L66
#    (genera_seconda.py) in L64a/seconda/<deck>/.
# rc e durata in L64a/seconda/esiti.tsv.
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
rm -rf $LOTTO/l66_mute $LOTTO/seconda
mkdir -p $LOTTO/seconda
/usr/bin/python3 -I $LOTTO/script/genera_seconda.py || exit 1
: > $LOTTO/seconda/esiti.tsv
uno() {
  local deck=$1 dir=$2 b=${1:t:r} t0=$SECONDS
  /bin/zsh $ROOT/scripts/run_simulation.sh $deck $dir > $dir.stdout 2>&1
  print -r -- "$b	$?	$((SECONDS-t0))" >> $LOTTO/seconda/esiti.tsv
}
uno $ROOT/docs/preamp/data/2026-11-02/L66/regressione/deck_lim365/tb_mute_corto.cir $LOTTO/l66_mute &
for b in tb_f1_selettore tb_e5_bilanciamento tb_loop_bilanciamento; do
  uno $LOTTO/seconda/deck/$b.cir $LOTTO/seconda/$b &
done
wait
sort $LOTTO/seconda/esiti.tsv
