#!/bin/zsh
# corri_tutti.sh - L51b (from L47c2a): ngspice on the four decks of genera_tutti.sh, in
# parallel, each from its own folder; then the guards of L41b1 (limitations
# #33/#35) on every log.
#   /bin/zsh corri_tutti.sh
set -u
D=${0:A:h}
L=$D:h
NG=/opt/homebrew/bin/ngspice
decks=(timer/tb_psu_timer_nom timer/tb_psu_timer_min rete/tb_psu_rete guasti/tb_psu_guasti)
for x in $decks; do
    ( cd "$L/${x:h}" && $NG -b "${x:t}.cir" -o "${x:t}.log" > /dev/null 2>&1 ) &
done
wait
rc=0
for x in $decks; do
    if grep -qiE 'error|singular|no such|non-increasing|transient op|timestep too small' "$L/$x.log"; then
        echo "$x: il log ha un errore"
        grep -iE 'error|singular|no such|non-increasing|transient op|timestep too small' "$L/$x.log" | head -3
        rc=1
    else
        echo "$x: log pulito"
    fi
done
exit $rc
