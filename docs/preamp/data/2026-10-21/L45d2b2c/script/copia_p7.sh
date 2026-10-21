#!/bin/zsh
# copia_p7.sh - L45d2b2c: P7's tables of every rail (run/tb_<rail>/ and run/tb_cbe_<rail>/: the regime
# and the finals' junctions) into p7/<gruppo>_<tabella>.csv, the curated copy that stays in the
# repository (run/ is gitignored, as L62b's)
set -u
D=${0:A:h}
L=$D:h
mkdir -p "$L/p7"
for d in "$L"/run/tb_*(/); do
    g=${d:t}
    for t in regime vbe; do
        cp "$d/tb_mute_corto/tb_mute_corto_$t.csv" "$L/p7/${g}_$t.csv" || exit 1
    done
done
print -r -- "copiati in $L/p7"
