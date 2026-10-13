#!/bin/zsh
# corri_l56.sh - L56 (from data/2026-10-09/L51b/sonda_u503/corri.sh): the variants of prepara_l56.py, in parallel, each with
# a ceiling of 300 s (perl alarm: macOS has no timeout(1)); rc and seconds in esiti_l56[_g<N>].tsv.
#   /bin/zsh corri_l56.sh        # pass 1, both cases (the first run had no "gear" and no
#                                # "trap8_rel3": they come from prepara_l56.py's second version)
#   /bin/zsh corri_l56.sh 2      # pass 2 of guasto_u503_min alone
set -u
D=${0:A:h}
NG=/opt/homebrew/bin/ngspice
G=${1:-1}
if [[ $G == 1 ]]; then
    S="" ; casi=(guasto_u503 guasto_u503_min) ; E="$D/esiti_l56.tsv"
else
    S="_g$G" ; casi=(guasto_u503_min) ; E="$D/esiti_l56_g$G.tsv"
fi
: > "$E"
for v in gear gear_rel3 gear_gmin9 trap9 trap8 trap8_rel3; do
    for c in $casi; do
        [[ -f "$D/l56_$v$S/$c.cir" ]] || continue
        (
            cd "$D/l56_$v$S" || exit 1
            t0=$SECONDS
            /usr/bin/perl -e 'alarm shift; exec @ARGV' 300 $NG -b "$c.cir" -o "$c.log" > /dev/null 2>&1
            rc=$?
            print -r -- "$v	$c	$rc	$(( SECONDS - t0 ))" >> "$E"
        ) &
    done
done
wait
sort "$E"
