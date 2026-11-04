#!/bin/zsh
# L70: ponte.sh of L64b / L69b for a variant: the bridge from seq/<v>[_m10|_p10] to the V2 deck, then the
# chain to the jack (catena_v.sh) at the three mains. As ponte.sh: at -10 / +10 % spegnimento_l,
# perdita, perdita_min from their own runs, the other six JSONs copied from <v>_nom (rows not read).
#   /bin/zsh script/ponte_v.sh <variante>
set -eu
L=${0:A:h:h}
P=/usr/bin/python3
v=$1
NOVE=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503)
TRE=(spegnimento_l perdita perdita_min)
mkdir -p $L/ponte/${v}_nom $L/ponte/${v}_m10 $L/ponte/${v}_p10
$P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/$v $L/ponte/${v}_nom $NOVE
for r in m10 p10; do
    $P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/${v}_$r $L/ponte/${v}_$r $TRE
    for c in $NOVE; do
        [ -f $L/ponte/${v}_$r/$c.json ] || cp $L/ponte/${v}_nom/$c.json $L/ponte/${v}_$r/$c.json
    done
done
for r in nom m10 p10; do
    if /usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $L/script/catena_v.sh $v $r > $L/catena_${v}_$r.out 2>&1; then
        echo "catena $v $r: rc 0"
    else
        echo "catena $v $r: FALLITA (vedi catena_${v}_$r.out)"
    fi
done
