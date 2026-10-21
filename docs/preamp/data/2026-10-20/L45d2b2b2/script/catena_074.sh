#!/bin/zsh
# catena_074.sh <etichetta> <100k|vuoto> <caso>... - L45d2b2b1: the audio half of ADR-074's cases,
# L45c2's chain (data/2026-10-14/L45c2/script/catena_l45c2.sh, which stays as it was) on the cases of
# seq/<etichetta>: the bridge (estrai_ponte.py) into ponte/<etichetta>, the V2 deck of the copied
# generator (deck/: --rl 100k, the load of L41c / L56 for PR-23's filtered peak; --rl 1e12, unloaded,
# for P10, ADR-069), the runs (L29c's corri.sh, 8 at a time), the guard, the retry with gear, the
# analysis of V2 (A_ins), the P10 duration, and the runs that still abort read to the end of the
# bounces (fino_all_aborto.py).
set -eu
D=${0:A:h}
L=$D:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
etich=$1
c=$2
shift 2
PO=$L/ponte/$etich
C=$L/corse/${etich}_$c
mkdir -p "$PO" "$L/corse"
$P "$L/ponte/estrai_ponte.py" "$L/seq/$etich" "$PO" "$@" > "$PO/estrai.txt"
print -l "$@" > "$PO/casi.txt"
rl=100k
[ "$c" = vuoto ] && rl=1e12
$P "$L/deck/genera_tb_v2_casopeggiore.py" --matrice l41c --ponte "$PO" --casi "$PO/casi.txt" \
    --rl $rl --uscita "$L/deck/tb_v2_${etich}_$c.cir"
$P "$L/deck/controlla_deck.py" "$L/deck/tb_v2_${etich}_$c.cir"
/bin/zsh "$R/docs/preamp/data/2026-09-23/L29c/script/corri.sh" "$C" "$L/deck/tb_v2_${etich}_$c.cir" '_l41c$' 8
$P "$R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py" "$C" || true
/bin/zsh "$D/rifai_gear.sh" "$C"
$P "$D/verifica_partenza.py" "$C" "$PO" > "$C/partenza.txt" || true
cat "$C/partenza.txt"
$P "$R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py" "$C"
$P "$R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py" "$C/manifest_ok.csv" "$C" "$C/analisi.csv" 8
$P "$D/misura_p10.py" "$C" "$C/manifest_ok.csv" "$C/p10.csv"
$P "$D/fino_all_aborto.py" "$C" "$C/aborto.csv" --ponte "$PO" --da-tempi
echo "catena fatta: $etich $c"
