#!/bin/zsh
# L68: i casi della FMEA del temporizzatore a comparatori che muovono i rele' in modo diverso dalla corsa
# sana (tabella.py, L68_CASI, coi criteri scritti prima), dalla scheda dell'alimentatore al jack, con la
# catena di L64c (che e' quella di L64b / L54b2 / L41c). corto_u503 (il JSON di L64b) e' il controllo.
# Le corse 2 alla volta a priorita' bassa (ogni corsa ~1 GB).
#   /bin/zsh catena/catena_l68.sh
set -eu
C=${0:A:h}
L=$C:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
CASI=(f_j4permit_aperto_muss f_j4mute_aperto_muss f_tp501_corto_muss f_tp502_corto_muss f_tp504_corto_muss
      f_tp505_corto_muss f_tp507_corto_muss f_tp509_corto_muss f_tp510_corto_muss f_tp514_corto_muss
      f_tp516_corto_muss f_c550_aperto_inss f_c550_aperto_guas f_c550_aperto_spls f_d539_corto_spls
      f_d539_corto_guas f_r576_corto_guas f_d540_aperto_spls f_c551_aperto_spls f_r572_corto_guas)
$P -I $C/estrai_ponte.py --passata-unica --te 3.0 $L/seq/oggi $C/ponte $CASI
export L64C_CASI="$CASI corto_u503"
$P $C/genera_tb_v2_l64c.py --matrice l41c --ponte $C/ponte --uscita $C/tb_v2_l68.cir
$P $C/controlla_deck.py $C/tb_v2_l68.cir
mkdir -p $C/corse
/usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $R/docs/preamp/data/2026-09-23/L29c/script/corri.sh $C/corse $C/tb_v2_l68.cir '_l41c$' 2
$P $R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py $C/corse
$P $C/verifica_partenza.py $C/corse $C/ponte > $C/corse/partenza.txt
cat $C/corse/partenza.txt
$P $R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py $C/corse
$P $R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py $C/corse/manifest_ok.csv $C/corse $C/corse/analisi.csv 2
$P $C/verifica_eventi.py $C/corse $C/ponte $CASI corto_u503 > $C/corse/eventi.txt
cat $C/corse/eventi.txt
$P $C/tabella.py $C/corse/analisi.csv $C/corse/fallite.txt $C/tabella_l68.csv
