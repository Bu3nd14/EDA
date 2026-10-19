#!/bin/zsh
# corri_gear_v2.sh : le due corse di gear_v2.py in run/v2_gear/, insieme. L60d2, da corri_gear.sh di L60c2.
L=${0:A:h:h}
cd $L/run/v2_gear
for c in off_r10m_d20_iii g10sempre_lz_iii; do
  ( t0=$SECONDS; /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1; print -r -- "$c rc=$? $((SECONDS-t0))s" >> tempi.txt ) &
done
wait
print -r -- "fine gear"
