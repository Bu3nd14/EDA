#!/bin/zsh
# L51a: la seconda strada del mute. Le celle peggiori di ogni gruppo della matrice di L48b
# (verdetto.csv: 1 B2g, 2 B2g, 3 A_ins, 4 il clic e B2g, 5 A_ins, 6 A_ins) e i loro
# riferimenti, rifatte oggi sul deck versionato con corri.sh di L29c, 7 in parallelo; poi la
# guardia sui log (L47b2b1) e l'analisi (analizza_par.py di L29c). Il generatore del dossier
# confronta le righe di analisi.csv con quelle di L48b per le stesse celle.
LOTTO=${0:A:h:h}
ROOT=${LOTTO:h:h:h:h:h}
C=$ROOT/docs/preamp/data/2026-09-23/L29c
OUT=$LOTTO/mute/corse
RE='^(vol_g10_iii|vrif_g10_iii|gm3x10_20_iii|g3sempre_20_iii|g3mai_20_iii|tm6x0_1k_iii|t6sempre_1k_iii|t6mai_1k_iii|x1010012_dpamax_iii|rsempre_g10t12_dpamax_iii|rmai_g10t12_dpamax_iii|mev_1k_iii|g10sempre_1k_iii|g10mai_1k_iii|on_r300p_iii|g10sempre_lz_iii|g10mai_lz_iii|g10mai_20_iii|g10sempre_20_iii|rmai_g10t0_dpamax_iii|rsempre_g10t0_dpamax_iii)$'
/bin/zsh $C/script/corri.sh $OUT $ROOT/spice/preamp/tb/tb_v2_casopeggiore.cir "$RE" 7
/usr/bin/python3 $ROOT/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py $OUT
/usr/bin/python3 $C/script/analizza_par.py $OUT/manifest_sel.csv $OUT $OUT/analisi.csv 8
