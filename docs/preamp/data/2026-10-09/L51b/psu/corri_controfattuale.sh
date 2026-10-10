#!/bin/zsh
# corri_controfattuale.sh - L47c2a: the load's counterfactual (--carico l41a,
# with gear), regenerated, run and analysed.
set -u
D=${0:A:h}
L=$D:h
G=$D/genera_tb_psu.py
/usr/bin/python3 "$G" --uscita "$L/carico_l41a/rete" --nome rete --carico l41a || exit 1
/usr/bin/python3 "$G" --uscita "$L/carico_l41a/guasti" --nome guasti --carico l41a || exit 1
for x in rete guasti; do
    ( cd "$L/carico_l41a/$x" && /opt/homebrew/bin/ngspice -b "tb_psu_${x}_carico_l41a.cir" \
          -o "tb_psu_${x}_carico_l41a.log" > /dev/null 2>&1 ) &
done
wait
for x in rete guasti; do
    /usr/bin/python3 "$D/analizza.py" "$L/carico_l41a/$x"
    echo "== carico_l41a/$x"
    cat "$L/carico_l41a/$x/analisi.csv"
done
