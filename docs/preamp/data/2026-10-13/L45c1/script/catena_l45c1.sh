#!/bin/zsh
# catena_l45c1.sh - L45c1: the audio half of the rails' faults. L56's chain (catena_audio.sh,
# next to this) on this lot's cases: the bridge of every case (estrai_ponte.py), the welded NO
# (ponte/saldati.py), the V2 deck twice from the copied generator (deck/: --rl 100k, the load of
# L41c / L56 for PR-23's method; --rl 1e12, unloaded, for P10, ADR-069), the runs (L29c's
# corri.sh, 8 at a time), the guards, the analysis of V2 (A_ins) and the P10 duration.
#   /bin/zsh catena_l45c1.sh [100k|vuoto]...      default both
set -eu
D=${0:A:h}
L=$D:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
carichi=("$@")
(( $#carichi )) || carichi=(100k vuoto)
$P "$L/psu/lista.py" | grep '^f_' > "$L/ponte/casi_f.txt"
basi=(spegnimento_l perdita guasto guasto_u501)
$P "$L/ponte/estrai_ponte.py" "$L/seq" "$L/ponte" $basi $(cat "$L/ponte/casi_f.txt") > "$L/ponte/estrai.txt"
$P "$L/ponte/saldati.py" "$L/ponte" > "$L/ponte/saldati.txt"
cat "$L/ponte/saldati.txt"
print -l $basi > "$L/ponte/casi.txt"
cat "$L/ponte/casi_f.txt" >> "$L/ponte/casi.txt"
$P -c "import sys; sys.path.insert(0, '$L/psu'); import modi; print('\n'.join(x[0] for x in modi.SALDATI))" >> "$L/ponte/casi.txt"
for c in $carichi; do
    rl=100k
    [ "$c" = vuoto ] && rl=1e12
    $P "$L/deck/genera_tb_v2_casopeggiore.py" --matrice l41c --ponte "$L/ponte" --casi "$L/ponte/casi.txt" \
        --rl $rl --uscita "$L/deck/tb_v2_$c.cir"
    $P "$L/deck/controlla_deck.py" "$L/deck/tb_v2_$c.cir"
    /bin/zsh "$R/docs/preamp/data/2026-09-23/L29c/script/corri.sh" "$L/corse_$c" "$L/deck/tb_v2_$c.cir" '_l41c$' 8
    # the guard's exit is the count of refused runs: they are listed, retried with gear
    # (rifai_gear.sh), and the ones that still abort are read up to the abort (fino_all_aborto.py)
    $P "$R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py" "$L/corse_$c" || true
    /bin/zsh "$L/script/rifai_gear.sh" "$L/corse_$c"
    $P "$L/script/verifica_partenza.py" "$L/corse_$c" "$L/ponte" > "$L/corse_$c/partenza.txt" || true
    cat "$L/corse_$c/partenza.txt"
    $P "$R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py" "$L/corse_$c"
    $P "$R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py" "$L/corse_$c/manifest_ok.csv" \
        "$L/corse_$c" "$L/corse_$c/analisi.csv" 8
    $P "$L/script/misura_p10.py" "$L/corse_$c" "$L/corse_$c/manifest_ok.csv" "$L/corse_$c/p10.csv"
    $P "$L/script/fino_all_aborto.py" "$L/corse_$c" "$L/corse_$c/aborto.csv" --da-tempi
done
echo "catena fatta: $carichi"
