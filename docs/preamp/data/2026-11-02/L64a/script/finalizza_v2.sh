#!/bin/zsh
# L64a: la chiusura della matrice di V2 corsa oggi (run/v2), come L48b e L60d2, a priorita' bassa.
#  1. le 22 celle coi .nodeset del blocco (tempi.txt «nodeset_blocco», rc=0): il log valido
#     (corsa_<c>_nb.log) prende il posto di corsa_<c>.log; quello del «Transient op» resta come
#     corsa_<c>_opt.log;
#  2. la guardia di L47b2b1 sui log e sui .dat (esito in ../v2/guardia.txt);
#  3. il manifesto finale senza off_r10m_d20_iii (filtra_manifesto.py di L48b), l'analisi
#     (analizza_par.py di L29c, 3 processi), il verdetto e il clic (verdetto.py, tabella_clic.py
#     di L47c2b1);
#  4. la sonda di VOSB = 0 (il gruppo 6, limitations #44): vol_g10_iii e vrif_g10_iii con
#     «alter vosb dc = 0», in ../v2/sonda_vosb/, analizzate come in L48b;
#  5. i file della matrice in ../v2/ (le onde restano in run/, fuori dal repository).
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
D=$L/run/v2
V=$L/v2
C=$ROOT/docs/preamp/data/2026-09-23/L29c/script
K=$ROOT/docs/preamp/data/2026-10-05/L47c2b1/script
mkdir -p $V/sonda_vosb
cd $D
for c in $(grep " rc=0 .*nodeset_blocco" tempi.txt | awk '{print $1}'); do
  [[ -f corsa_${c}_opt.log ]] || mv corsa_$c.log corsa_${c}_opt.log
  cp corsa_${c}_nb.log corsa_$c.log
done
/usr/bin/python3 $ROOT/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py $D > $V/guardia.txt 2>&1
print -r -- "guardia: esce $?" >> $V/guardia.txt
/usr/bin/python3 $ROOT/docs/preamp/data/2026-10-07/L48b/v2/filtra_manifesto.py $D/manifest_sel.csv $D/manifest_finale.csv off_r10m_d20_iii
nice -n 10 /usr/bin/python3 $C/analizza_par.py $D/manifest_finale.csv $D $D/analisi.csv 3
/usr/bin/python3 $K/verdetto.py $D/manifest_finale.csv $D/analisi.csv $D/verdetto.csv
/usr/bin/python3 $K/tabella_clic.py $D/manifest_finale.csv $D $D/analisi.csv $D/clic.csv
for f in manifest.csv manifest_sel.csv manifest_finale.csv corse_sel.txt tempi.txt analisi.csv verdetto.csv clic.csv; do
  cp $D/$f $V/$f
done
# la sonda di VOSB = 0
S=$L/run/sonda_vosb
mkdir -p $S
for c in vol_g10_iii vrif_g10_iii; do
  sed 's/^alter vosb dc = .*$/alter vosb dc = 0/' $D/corsa_$c.cir > $S/corsa_$c.cir
  ( cd $S && nice -n 10 /opt/homebrew/bin/ngspice -b corsa_$c.cir > corsa_$c.log 2>&1 )
done
head -1 $D/manifest.csv > $S/manifest_sel.csv
grep -E "^(vol_g10_iii|vrif_g10_iii)," $D/manifest.csv >> $S/manifest_sel.csv
/usr/bin/python3 $C/analizza_par.py $S/manifest_sel.csv $S $S/analisi.csv 2
cp $S/manifest_sel.csv $S/analisi.csv $S/corsa_vol_g10_iii.log $S/corsa_vrif_g10_iii.log $V/sonda_vosb/
grep -c "alter vosb dc = 0" $S/corsa_vol_g10_iii.cir $S/corsa_vrif_g10_iii.cir >> $V/sonda_vosb/alter.txt
print -r -- "fine: $(wc -l < $V/verdetto.csv) righe di verdetto"
