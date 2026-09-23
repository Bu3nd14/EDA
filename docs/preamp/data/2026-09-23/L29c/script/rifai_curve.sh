#!/bin/zsh
# rifai_curve.sh: rifa' le corse mancanti di AA e DA (i riferimenti 'sempre', seconda prova senza
# nodeset) e ne rifa' analisi e verdetto; poi DD, se l'analisi di analizza_curve.sh non c'e'.
L=${0:A:h:h}
for c in ${@:-AA DA}; do
  rm -f $L/curve/$c/analisi.csv $L/curve/$c/verdetto.csv
  /bin/zsh $L/script/corri.sh $L/curve/$c $L/curve/tb_v2_curve_$c.cir '.' 3
  /usr/bin/python3 $L/script/analizza_par.py $L/curve/$c/manifest_sel.csv $L/curve/$c $L/curve/$c/analisi.csv 3
  /usr/bin/python3 $L/script/verdetto.py $L/curve/$c/manifest_sel.csv $L/curve/$c/analisi.csv $L/curve/$c/verdetto.csv
done
