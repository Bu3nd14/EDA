#!/bin/zsh
# catena_audio.sh - L54b2: the audio half of the chain to the jack (L41c's bridge, L51b's and L56's
# catena_audio.sh) on the sequences of the source with the comparator timer, one mains level per
# call. The bridge's JSONs are already in ponte/<rete>/ (ponte/estrai_ponte.py --passata-unica);
# then the V2 deck with --matrice l41c, the 18 runs (nine cases, nine references), the guards, the
# analysis, the events, the table. At -10 / +10 % only spegnimento_l, perdita, perdita_min come from
# their own runs: the other six JSONs are the nominal ones, copied so that the deck is whole, and
# their rows are not read.
#   /bin/zsh catena_audio.sh <rete>        (nom | m10 | p10)
set -eu
D=${0:A:h}
L=$D:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
r=$1
PO=$L/ponte/$r
C=$L/corse/$r
mkdir -p $L/deck $C
$P "$R/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py" \
    --matrice l41c --ponte "$PO" --uscita "$L/deck/tb_v2_l41c_$r.cir"
$P "$L/deck/controlla_deck.py" "$L/deck/tb_v2_l41c_$r.cir"
/bin/zsh "$R/docs/preamp/data/2026-09-23/L29c/script/corri.sh" "$C" "$L/deck/tb_v2_l41c_$r.cir" '_l41c$' 9
$P "$R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py" "$C"
$P "$L/script/verifica_partenza.py" "$C" "$PO" > "$C/partenza.txt"
cat "$C/partenza.txt"
$P "$R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py" "$C"
$P "$R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py" "$C/manifest_ok.csv" \
    "$C" "$C/analisi.csv" 8
$P "$L/script/verifica_eventi.py" "$C" "$PO" spegnimento_l perdita perdita_min guasto_u503 \
    guasto_u503_min guasto guasto_u501 cf_nodelta corto_u503 > "$C/eventi.txt"
cat "$C/eventi.txt"
$P "$L/script/tabella.py" "$C/analisi.csv" "$C/fallite.txt" "$L/tabella_$r.csv"
cat "$L/tabella_$r.csv"
