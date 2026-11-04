#!/bin/zsh
# L64b: what follows the sequences, in one queue at low priority, never more than 2 ngspice of mine:
#   1. waits for the running batch of corri_lista_an.sh;
#   2. the standby from T2 (lista_consumo.txt, --sonda-t2, L54b2's method: psu/potenza_t2.py over
#      2.5-3.0 s) -> consumo.txt;
#   3. the bridge and the chain to the jack (script/ponte.sh).
#   /bin/zsh script/coda.sh
set -u
L=${0:A:h:h}
while /usr/bin/pgrep -f corri_lista_an.sh > /dev/null; do
    /bin/sleep 30
done
echo "le sequenze sono finite: $(/usr/bin/find $L/seq -name ok.txt | /usr/bin/wc -l) ok.txt"
# what the batch did not run (the list of the missing was rewritten while it read it): once more
/usr/bin/python3 -I $L/script/lista.py
if [ -s $L/lista_l64b_mancanti.txt ]; then
    /bin/zsh $L/script/corri_sequenze.sh 2 $L/lista_l64b_mancanti.txt
fi
/bin/zsh $L/script/corri_sequenze.sh 2 $L/lista_consumo.txt
: > $L/consumo.txt
for r in consumo consumo_m10 consumo_p10; do
    /usr/bin/python3 -I $L/psu/potenza_t2.py $L/seq/$r/accensione/tb_psu_seq_accensione_g1_out.txt 2.5 3.0 >> $L/consumo.txt
done
cat $L/consumo.txt
/bin/zsh $L/script/ponte.sh
