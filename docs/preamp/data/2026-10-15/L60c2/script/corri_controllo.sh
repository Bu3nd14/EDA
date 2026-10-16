#!/bin/zsh
# corri_controllo.sh : la corsa di controllo_principale.py, nella sua cartella. L60c2.
L=${0:A:h:h}
cd $L/run/controllo_principale
t0=$SECONDS
/opt/homebrew/bin/ngspice -b corsa_g10sempre_1k_iii.cir > corsa_g10sempre_1k_iii.log 2>&1
print -r -- "controllo rc=$? $((SECONDS-t0))s"
