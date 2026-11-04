#!/bin/zsh
# L70: L69b's ponte.sh with the variant as a parameter - the bridge from the variant's sequences
# (seq/<v>, seq/<v>_m10, seq/<v>_p10) to the V2 deck, then the chain to the jack at the three mains
# (script/catena_audio.sh <v>_<rete>, 18 runs each, 2 at a time, low priority). As in L69b: at
# -10 / +10 % spegnimento_l, perdita, perdita_min from their own runs, the other six JSONs copied
# from <v>_nom/ so that the deck is whole (their rows are not read).
#   /bin/zsh script/ponte_l70.sh <variante>
set -eu
L=${0:A:h:h}
V=$1
P=/usr/bin/python3
NOVE=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503)
TRE=(spegnimento_l perdita perdita_min)
mkdir -p $L/ponte/${V}_nom $L/ponte/${V}_m10 $L/ponte/${V}_p10
$P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/$V $L/ponte/${V}_nom $NOVE
for r in m10 p10; do
    $P -I $L/ponte/estrai_ponte.py --passata-unica --te 3.0 $L/seq/${V}_$r $L/ponte/${V}_$r $TRE
    for c in $NOVE; do
        [ -f $L/ponte/${V}_$r/$c.json ] || cp $L/ponte/${V}_nom/$c.json $L/ponte/${V}_$r/$c.json
    done
    print -r -- "spegnimento_l, perdita, perdita_min: dalle loro corse a rete $r (seq/${V}_$r).
Gli altri sei JSON sono quelli di ponte/${V}_nom/, copiati perche' il deck sia intero: le loro righe non si leggono." > $L/ponte/${V}_$r/LEGGIMI.txt
done
for r in nom m10 p10; do
    if /usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $L/script/catena_audio.sh ${V}_$r > $L/catena_${V}_$r.out 2>&1; then
        echo "catena ${V}_$r: rc 0"
    else
        echo "catena ${V}_$r: FALLITA (vedi catena_${V}_$r.out)"
    fi
done
