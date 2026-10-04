#!/bin/zsh
# corri_curve.sh - L47b2b1: la matrice «curve» del banco V2 (genera_tb_v2_casopeggiore.py
# --matrice curve) per le curve A, C, D, E della NSL-32SR3 (B e' nella matrice del deck
# versionato), una dopo l'altra, con corri.sh di L29c. Aspetta che la matrice principale
# (v2/sorgente) abbia finito, per non mettere 16 ngspice su 10 core.
#   /bin/zsh corri_curve.sh <npar>
QUI=${0:A:h}
ROOT=${0:A:h:h:h:h:h:h:h}
NPAR=${1:-8}
while pgrep -f 'corri.sh .*v2/sorgente' > /dev/null; do
  sleep 30
done
for c in D A C E; do
  /bin/zsh $ROOT/docs/preamp/data/2026-09-23/L29c/script/corri.sh $QUI/curve_$c$c $QUI/deck/tb_v2_curve_$c$c.cir '.*' $NPAR
done
echo "curve: fatto"
