#!/bin/zsh
# corri_sonda.sh - L47c2b1: corre le corse preparate da prepara.py, una per processo, nella
# cartella della loro variante; scrive tempi.txt con rc e durata. Nessuna seconda prova: la sonda
# vuole vedere chi si ferma.
QUI=${0:A:h}
zmodload zsh/parameter
corri() {
  local d=$1 c=$2 t0=$SECONDS
  cd $d
  /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1
  local rc=$?
  if grep -q 'Transient op started' corsa_$c.log; then rc=OPT; fi
  if grep -q -i 'timestep too small\|aborted' corsa_$c.log; then rc="$rc,FERMA"; fi
  print -r -- "$c rc=$rc $((SECONDS-t0))s $(date +%H:%M:%S)" >> tempi.txt
}
for v in ${@:-t1 t1r gear}; do
  for f in $QUI/$v/corsa_*.cir; do
    c=${${f:t}#corsa_}
    c=${c%.cir}
    corri $QUI/$v $c &
  done
done
wait
echo fatto
