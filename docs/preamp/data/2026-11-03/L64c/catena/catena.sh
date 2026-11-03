#!/bin/zsh
# L64c: i guasti che tolgono i 5 V (C536 in corto, U512 spento) dalla scheda dell'alimentatore al jack,
# con la catena di L64b (che e' quella di L54b2 / L41c): il ponte dalle sequenze di oggi (seq/oggi,
# --passata-unica --te 3.0), il deck di V2 con la matrice l41c sui soli casi di L64c (L64C_CASI), le
# corse 2 alla volta a priorita' bassa, la guardia, l'analisi, la tabella coi criteri scritti prima.
# corto_u503 (il JSON di L64b, copiato) e' il controllo: deve ridare il picco di L64b.
#   /bin/zsh catena/catena.sh
set -eu
C=${0:A:h}
L=$C:h
R=${0:A:h:h:h:h:h:h:h}
P=/usr/bin/python3
CASI=(f_c536_corto_muss f_c536_corto_musm10s f_c536_corto_musp10s f_u512_spento_muss f_u512_spento_musm10s f_u512_spento_musp10s)
$P -I $C/estrai_ponte.py --passata-unica --te 3.0 $L/seq/oggi $C/ponte $CASI
export L64C_CASI="$CASI corto_u503"
$P $C/genera_tb_v2_l64c.py --matrice l41c --ponte $C/ponte --uscita $C/tb_v2_l64c.cir
$P $C/controlla_deck.py $C/tb_v2_l64c.cir
mkdir -p $C/corse
/usr/bin/nice -n 15 /usr/bin/caffeinate -i /bin/zsh $R/docs/preamp/data/2026-09-23/L29c/script/corri.sh $C/corse $C/tb_v2_l64c.cir '_l41c$' 2
$P $R/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py $C/corse
$P $C/verifica_partenza.py $C/corse $C/ponte > $C/corse/partenza.txt
cat $C/corse/partenza.txt
$P $R/docs/preamp/data/2026-09-25/L29d2/script/solo_riuscite.py $C/corse
$P $R/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py $C/corse/manifest_ok.csv $C/corse $C/corse/analisi.csv 2
$P $C/verifica_eventi.py $C/corse $C/ponte $CASI corto_u503 > $C/corse/eventi.txt
cat $C/corse/eventi.txt
$P $C/tabella.py $C/corse/analisi.csv $C/corse/fallite.txt $C/tabella_l64c.csv
