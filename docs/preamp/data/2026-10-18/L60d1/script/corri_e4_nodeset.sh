#!/bin/zsh
# corri_e4_nodeset.sh <fase> : tb_e4_uscite di regressione/<fase> col .nodeset di e4_nodeset.py,
# in run/e4_nodeset/<fase>/; poi la tabella confrontata con regressione/prima. L60d1.
L=${0:A:h:h}
F=$1
D=$L/run/e4_nodeset/$F
/usr/bin/python3 -I $L/script/e4_nodeset.py $L/regressione/$F/tb_e4_uscite/tb_e4_uscite_resolved.cir $D
cd $D
/opt/homebrew/bin/ngspice -b tb_e4_uscite.cir > tb_e4_uscite.log 2>&1
print -r -- "ngspice rc=$?"
diff $L/regressione/prima/tb_e4_uscite/tb_e4_uscite_tab.csv tb_e4_uscite_tab.csv
print -r -- "diff rc=$?"
