#!/bin/zsh
# corri_varianti.sh - L47c2a: ngspice on varianti/c*/ (varianti.py), then analizza.py.
set -u
D=${0:A:h}
L=$D:h
for c in 3300u 2200u; do
    ( cd "$L/varianti/c$c" && /opt/homebrew/bin/ngspice -b "tb_psu_rete_c$c.cir" -o "tb_psu_rete_c$c.log" > /dev/null 2>&1 ) &
done
wait
for c in 3300u 2200u; do
    /usr/bin/python3 "$D/analizza.py" "$L/varianti/c$c"
    echo "== C520 = $c"
    cat "$L/varianti/c$c/analisi.csv"
done
