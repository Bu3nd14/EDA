#!/bin/zsh
# rifai_20hz_e.sh - L47b2b1: le sei corse a 20 Hz della curva E rifatte con trtol=1 E rshunt=1e12
# (aggiungi_rshunt.py), tutte; e D cev_20 con le stesse due opzioni, nella sonda, per il
# confronto con quella senza (#38).
QUI=${0:A:h}
V2=${QUI:h}
corse=(cmai_20 csempre_20 cinv25_20 cinv75_20 cev_20 ch2_20)
for c in $corse; do
  /usr/bin/python3 $QUI/aggiungi_rshunt.py $V2/curve_EE/corsa_$c.cir
done
/usr/bin/python3 $QUI/aggiungi_trtol.py $QUI/rele2/curve_EE_corsa_cev_20__rshunt.cir > /dev/null
cp $V2/curve_DD/corsa_cev_20.cir $QUI/d_cev_20_ts.cir
/usr/bin/python3 $QUI/aggiungi_trtol.py $QUI/d_cev_20_ts.cir
/usr/bin/python3 $QUI/aggiungi_rshunt.py $QUI/d_cev_20_ts.cir
sed -i '' -e 's/^wrdata cev_20/wrdata d_ts_cev_20/' $QUI/d_cev_20_ts.cir
uno() {
  local c=$1 t0=$SECONDS
  cd $V2/curve_EE
  rm -f $c.dat ${c}_stati.dat
  /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1
  print -r -- "$c rc=$? $((SECONDS-t0))s $(date +%H:%M:%S) trtol1_rshunt" >> tempi.txt
}
for c in $corse; do
  uno $c &
done
( cd $QUI && /opt/homebrew/bin/ngspice -b d_cev_20_ts.cir > d_cev_20_ts.log 2>&1 ) &
wait
echo "rifai_20hz_e: fatto"
