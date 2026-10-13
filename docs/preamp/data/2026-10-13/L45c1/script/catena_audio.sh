#!/bin/zsh
# catena_audio.sh - L51b: the audio half of the supply's faults, L47c2b2's chain (its README,
# «Come si rifà») on this lot's sequences: the bridge (the rails and the contacts at the G6K's
# worst corner), the V2 deck with --matrice l41c, the 18 runs (nine cases, nine references),
# the guards, the analysis, the events, the table. The same file is in L51b/ and in
# L51b-prima/; the lot is the folder above this script.
#   /bin/zsh catena_audio.sh
set -eu
D=${0:A:h}
L=$D:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
casi=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta
      corto_u503)
$P "$L/ponte/estrai_ponte.py" "$L/seq" "$L/ponte" $casi > "$L/ponte/estrai.txt"
cat "$L/ponte/estrai.txt"
$P "$R/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py" \
    --matrice l41c --ponte "$L/ponte" --uscita "$L/deck/tb_v2_l41c.cir"
$P "$L/deck/controlla_deck.py" "$L/deck/tb_v2_l41c.cir"
/bin/zsh "$R/docs/preamp/data/2026-09-23/L29c/script/corri.sh" "$L/corse" "$L/deck/tb_v2_l41c.cir" '_l41c$' 9
$P "$R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py" "$L/corse"
$P "$L/script/verifica_partenza.py" "$L/corse" "$L/ponte" > "$L/corse/partenza.txt"
cat "$L/corse/partenza.txt"
$P "$R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py" "$L/corse"
$P "$R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py" "$L/corse/manifest_ok.csv" \
    "$L/corse" "$L/corse/analisi.csv" 8
# the order of L47c2b2's corse/eventi.txt
$P "$L/script/verifica_eventi.py" "$L/corse" "$L/ponte" spegnimento_l perdita perdita_min guasto_u503 \
    guasto_u503_min guasto guasto_u501 cf_nodelta corto_u503 > "$L/corse/eventi.txt"
cat "$L/corse/eventi.txt"
$P "$L/script/tabella.py" "$L/corse/analisi.csv" "$L/corse/fallite.txt" "$L/tabella.csv"
cat "$L/tabella.csv"
