#!/bin/zsh
# coda.sh: dopo le corse veloci, la dispersione (punto 3) e le curve della LDR (punto 6), una
# matrice alla volta, 7 ngspice insieme (le tre a 20 kHz tengono gli altri tre core).
ROOT=${0:A:h:h:h:h:h:h:h}
L=$ROOT/docs/preamp/data/2026-09-23/L29c
while pgrep -f 'corri.sh .*matrice/veloci' > /dev/null; do
  sleep 30
done
echo "veloci finite: $(date +%H:%M:%S)"
/bin/zsh $L/script/corri.sh $L/matrice/disp $ROOT/spice/preamp/tb/tb_v2_casopeggiore.cir '_d[np](a|min|max)(max|m20)$' 7
echo "dispersione finita: $(date +%H:%M:%S)"
for c in AA AD DA DD; do
  /bin/zsh $L/script/corri.sh $L/curve/$c $L/curve/tb_v2_curve_$c.cir '.' 7
  echo "curve $c finite: $(date +%H:%M:%S)"
done
