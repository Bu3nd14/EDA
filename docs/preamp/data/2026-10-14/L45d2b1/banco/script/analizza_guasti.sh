#!/bin/zsh
# analizza_guasti.sh [VARIANTE...] : P10 (L45b/script/analizza_p10.py, invariato) su ogni corsa dei
# guasti del blocco col rivelatore, una variante alla volta -> ../analisi_<variante>.csv. Senza
# argomenti tutte le run/riv_* (comprese le _corta e le _gear). L45d2b1.
L=${0:A:h:h}
DATA=${L:h:h:h}
if [ $# -gt 0 ]; then
    vv=($@)
else
    vv=($L/run/riv_*(/:t))
fi
for v in $vv; do
    /usr/bin/python3 -I $DATA/2026-10-13/L45b/script/analizza_p10.py $L/analisi_$v.csv $L/run/$v/*(/) > $L/run/analisi_$v.stdout 2>&1
    print -r -- "$v: $(tail -1 $L/run/analisi_$v.stdout)"
done
