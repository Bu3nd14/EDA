#!/bin/zsh
# corri_diagnosi.sh [variante ...] : le corse di prepara_diagnosi.py, in parallelo, ciascuna
# nella sua cartella run/diagnosi/<variante>/. Senza argomenti, tutte. L60d1.
L=${0:A:h:h}
cd $L/run/diagnosi
v=($@)
if (( ${#v} == 0 )); then
  v=(${(f)"$(ls -d */ | sed 's|/$||' | grep -v '^deck$')"})
fi
for x in $v; do
  (
    cd $x
    t0=$SECONDS
    /opt/homebrew/bin/ngspice -b corsa.cir > corsa.log 2>&1
    print -r -- "$x rc=$? $((SECONDS-t0))s"
  ) &
done
wait
