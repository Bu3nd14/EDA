#!/bin/zsh
# corri_follower.sh : le corse di varianti_follower.py (follower/lista.txt), 8 in parallelo.
# p7 e sonda: ngspice nella loro cartella; deck: run_simulation.sh in follower/<v>/run/<deck>/.
# rc e durata in follower/esiti.tsv. L60d1.
zmodload zsh/parameter
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
F=$L/follower
: > $F/esiti.tsv
uno() {
  local tipo=$1 v=$2 k=$3 t0=$SECONDS rc
  case $tipo in
    p7)
      ( cd $F/$v/p7 && /opt/homebrew/bin/ngspice -b tb_mute_corto.cir > tb_mute_corto.log 2>&1 )
      rc=$? ;;
    sonda)
      ( cd $F/$v/sonda && /opt/homebrew/bin/ngspice -b corsa.cir > corsa.log 2>&1 )
      rc=$? ;;
    deck)
      /bin/zsh $ROOT/scripts/run_simulation.sh $F/$v/deck/$k.cir $F/$v/run/$k > $F/$v/$k.stdout 2>&1
      rc=$? ;;
  esac
  print -r -- "$tipo	$v	$k	$rc	$((SECONDS-t0))" >> $F/esiti.tsv
}
for riga in ${(f)"$(cat $F/lista.txt)"}; do
  while (( ${#jobstates} >= 8 )); do sleep 1; done
  uno ${=riga} &
done
wait
sort $F/esiti.tsv
