#!/bin/zsh
# L71: catena_l71.sh on the groups given (default: every line of gruppi.txt), one group after the
# other (inside, 2 runs at a time), at low priority. One log per group: catena_<gruppo>.out.
#   /bin/zsh script/catene.sh [gruppo ...]
set -u
L=${0:A:h:h}
gs=("$@")
[ ${#gs} -eq 0 ] && gs=(${(f)"$(<$L/gruppi.txt)"})
for g in $gs; do
    t0=$(date +%s)
    if /usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $L/script/catena_l71.sh $g > $L/catena_$g.out 2>&1; then
        echo "catena $g: rc 0 ($(( $(date +%s) - t0 )) s)"
    else
        echo "catena $g: FALLITA o sopra la soglia (vedi catena_$g.out) ($(( $(date +%s) - t0 )) s)"
    fi
done
