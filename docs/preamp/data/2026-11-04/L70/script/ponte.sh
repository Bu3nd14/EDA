#!/bin/zsh
# L64b: the bridge from today's sequences to the V2 deck (L54b2's ponte/estrai_ponte.py, --passata-unica
# --te 3.0), then the chain to the jack at the three mains (script/catena_audio.sh, 18 runs each, 2 at
# a time, low priority). As in L54b2: at -10 / +10 % spegnimento_l, perdita, perdita_min from their own
# runs, the other six JSONs copied from nom/ so that the deck is whole (their rows are not read).
#   /bin/zsh script/ponte.sh
set -eu
L=${0:A:h:h}
P=/usr/bin/python3
NOVE=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503)
TRE=(spegnimento_l perdita perdita_min)
mkdir -p $L/ponte/nom $L/ponte/m10 $L/ponte/p10
$P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/oggi $L/ponte/nom $NOVE
for r in m10 p10; do
    $P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/oggi_$r $L/ponte/$r $TRE
    for c in $NOVE; do
        [ -f $L/ponte/$r/$c.json ] || cp $L/ponte/nom/$c.json $L/ponte/$r/$c.json
    done
    print -r -- "spegnimento_l, perdita, perdita_min: dalle loro corse a rete $r (seq/oggi_$r).
Gli altri sei JSON sono quelli di ponte/nom/, copiati perche' il deck sia intero: le loro righe non si leggono." > $L/ponte/$r/LEGGIMI.txt
done
for r in nom m10 p10; do
    if /usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $L/script/catena_audio.sh $r > $L/catena_$r.out 2>&1; then
        echo "catena $r: rc 0"
    else
        echo "catena $r: FALLITA (vedi catena_$r.out)"
    fi
done
