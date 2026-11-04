#!/bin/zsh
# catena_l71.sh - L71: catena_audio.sh of L69b (here beside it, unchanged) on one deck of nine slots
# filled by ponte/estrai_ponte_l71.py: the V2 deck with --matrice l41c, the 18 runs (nine cases, nine
# references) 2 at a time, the guards, the analysis, the events, tabella_l71.py.
#   /bin/zsh catena_l71.sh <gruppo>      (ponte/<gruppo>/ with the nine JSONs and posti.csv)
set -eu
D=${0:A:h}
L=$D:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
g=$1
PO=$L/ponte/$g
C=$L/corse/$g
POSTI=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta corto_u503)
mkdir -p $L/deck $C
$P "$R/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py" \
    --matrice l41c --ponte "$PO" --uscita "$L/deck/tb_v2_l41c_$g.cir"
$P "$L/deck/controlla_deck.py" "$L/deck/tb_v2_l41c_$g.cir"
/bin/zsh "$R/docs/preamp/data/2026-09-23/L29c/script/corri.sh" "$C" "$L/deck/tb_v2_l41c_$g.cir" '_l41c$' 2
$P "$R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py" "$C"
$P "$L/script/verifica_partenza.py" "$C" "$PO" > "$C/partenza.txt"
cat "$C/partenza.txt"
$P "$R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py" "$C"
$P "$R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py" "$C/manifest_ok.csv" \
    "$C" "$C/analisi.csv" 3
$P "$L/script/verifica_eventi.py" "$C" "$PO" $POSTI > "$C/eventi.txt"
cat "$C/eventi.txt"
$P "$L/script/tabella_l71.py" "$C/analisi.csv" "$C/fallite.txt" "$PO/posti.csv" "$L/tabella_$g.csv"
