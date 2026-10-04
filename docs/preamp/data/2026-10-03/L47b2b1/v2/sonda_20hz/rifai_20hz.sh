#!/bin/zsh
# rifai_20hz.sh - L47b2b1: le sei corse a 20 Hz delle matrici «curve» C ed E rifatte con
# option trtol=1 (aggiungi_trtol.py), tutte, perche' il banco resti uno (#38); e, per la prova,
# cev_20 della curva D con la stessa opzione, in questa cartella, contro quella buona.
QUI=${0:A:h}
V2=${QUI:h}
corse=(cmai_20 csempre_20 cinv25_20 cinv75_20 cev_20 ch2_20)
for d in curve_CC curve_EE; do
  for c in $corse; do
    /usr/bin/python3 $QUI/aggiungi_trtol.py $V2/$d/corsa_$c.cir
  done
done
# la prova su un evento: D, cev_20, con trtol=1, nella sonda
/usr/bin/python3 $QUI/varianti.py $V2/curve_DD/corsa_cev_20.cir
uno() {
  local d=$1 c=$2 t0=$SECONDS
  cd $V2/$d
  rm -f $c.dat ${c}_stati.dat
  /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1
  print -r -- "$c rc=$? $((SECONDS-t0))s $(date +%H:%M:%S) trtol1" >> tempi.txt
}
for d in curve_CC curve_EE; do
  for c in $corse; do
    uno $d $c &
  done
done
( cd $QUI && /opt/homebrew/bin/ngspice -b curve_DD_corsa_cev_20__trtol1.cir > curve_DD_corsa_cev_20__trtol1.log 2>&1 ) &
wait
echo "rifai_20hz: fatto"
