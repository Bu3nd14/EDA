#!/bin/zsh
# L68: i passi di catena_l68.sh dopo la guardia, quando la guardia rifiuta una corsa (f_tp501_corto_muss:
# il rail + a massa, «timestep too small» 4 ms dopo il corto nella scheda audio). La corsa rifiutata
# resta in corse/fallite.txt (solo_riuscite.py) e la tabella la conta come mancante.
#   /bin/zsh catena/catena_l68_resto.sh
set -eu
C=${0:A:h}
L=$C:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
CASI=(f_j4permit_aperto_muss f_j4mute_aperto_muss f_tp501_corto_muss f_tp502_corto_muss f_tp504_corto_muss
      f_tp505_corto_muss f_tp507_corto_muss f_tp509_corto_muss f_tp510_corto_muss f_tp514_corto_muss
      f_tp516_corto_muss f_c550_aperto_inss f_c550_aperto_guas f_c550_aperto_spls f_d539_corto_spls
      f_d539_corto_guas f_r576_corto_guas f_d540_aperto_spls f_c551_aperto_spls f_r572_corto_guas)
export L64C_CASI="$CASI corto_u503"
$P $C/verifica_partenza.py $C/corse $C/ponte > $C/corse/partenza.txt || true
cat $C/corse/partenza.txt
$P $R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py $C/corse
$P $R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py $C/corse/manifest_ok.csv $C/corse $C/corse/analisi.csv 2
$P $C/verifica_eventi.py $C/corse $C/ponte $CASI corto_u503 > $C/corse/eventi.txt || true
cat $C/corse/eventi.txt
$P $C/tabella.py $C/corse/analisi.csv $C/corse/fallite.txt $C/tabella_l68.csv
