#!/bin/zsh
# prova_inerte.sh <cartella di lavoro> - L54b3b: the decks of buco20 and guasto from L54b3a's
# generator and from this one, without the new options and with the nominal --toll / --temp 25 /
# --perdita at 0 A: each diff printed (README, "Il banco").
set -u
W=$1
D=${0:A:h}
A=$D:h:h/L54b3a/psu
O=(--timer sorgente --n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore --bat54 costruttore)
for caso in buco20 guasto; do
    mkdir -p $W/a_$caso $W/b_$caso $W/t_$caso
    /usr/bin/python3 $A/genera_tb_psu.py --uscita $W/a_$caso --nome seq --caso $caso $O > /dev/null
    /usr/bin/python3 $D/genera_tb_psu.py --uscita $W/b_$caso --nome seq --caso $caso $O > /dev/null
    /usr/bin/python3 $D/genera_tb_psu.py --uscita $W/t_$caso --nome seq --caso $caso $O \
        --temp 25 --toll $D/toll_nominale.json --perdita D538:0 > /dev/null
    echo "== $caso: L54b3a contro L54b3b senza opzioni"
    /usr/bin/diff $W/a_$caso/tb_psu_seq_${caso}_g1.cir $W/b_$caso/tb_psu_seq_${caso}_g1.cir
    echo "== $caso: senza opzioni contro --toll nominale --temp 25 --perdita D538:0"
    /usr/bin/diff $W/b_$caso/tb_psu_seq_${caso}_g1.cir $W/t_$caso/tb_psu_seq_${caso}_g1.cir
done
