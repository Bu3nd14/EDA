#!/bin/zsh
# corri.sh - L51b: the probe's variants (prepara.py), in parallel, each with a ceiling
# of 300 s (perl alarm: macOS has no timeout(1)); rc and seconds in esiti.tsv.
#   /bin/zsh corri.sh
set -u
D=${0:A:h}
NG=/opt/homebrew/bin/ngspice
: > "$D/esiti.tsv"
for v in com_e_05 gear_05 reltol gmin8 gear; do
    for c in guasto_u503 guasto_u503_min; do
        (
            cd "$D/$v" || exit 1
            t0=$SECONDS
            /usr/bin/perl -e 'alarm shift; exec @ARGV' 300 $NG -b "$c.cir" -o "$c.log" > /dev/null 2>&1
            rc=$?
            print -r -- "$v	$c	$rc	$(( SECONDS - t0 ))" >> "$D/esiti.tsv"
        ) &
    done
done
wait
sort "$D/esiti.tsv"
