#!/bin/zsh
# corri_rete.sh : i due deck di prepara_rete.py (base, im06) con ngspice, poi analizza.py di L51b
# su ciascuno. L60c2.
L=${0:A:h:h}
DATA=${L:h:h}
for n in base im06; do
  /opt/homebrew/bin/ngspice -b $L/run/rete/$n/tb_psu_rete.cir -o $L/run/rete/$n/tb_psu_rete.log > /dev/null 2>&1 &
done
wait
for n in base im06; do
  /usr/bin/python3 $DATA/2026-10-09/L51b/psu/analizza.py $L/run/rete/$n
done
print -r -- "fine rete"
