#!/bin/zsh
# L58b: V2 at the power-up with Q501 shorted - the chain of L58a2 (its report, «Rifare»): run the
# deck's l58_* cells and L29c's two references, the guard, the analysis, the verdict.
set -u
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
D=$ROOT/docs/preamp/data
/bin/zsh $D/2026-09-23/L29c/script/corri.sh $L/v2/run $L/v2/tb_v2_l58b.cir '^(l58_.*|g10sempre_lz_iii|g10mai_lz_iii)$' 5
/usr/bin/python3 $D/2026-10-03/L47b2b1/script/guardia_v2.py $L/v2/run
/usr/bin/python3 $D/2026-09-23/L29c/script/analizza_par.py $L/v2/run/manifest_sel.csv $L/v2/run $L/v2/analisi.csv 5
/usr/bin/python3 $D/2026-10-05/L47c2b1/script/verdetto.py $L/v2/run/manifest_sel.csv $L/v2/analisi.csv $L/v2/verdetto.csv
