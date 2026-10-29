#!/bin/zsh
# num_t0.sh - L54b3b: every 0 C run went over corri_an.sh's 300 s cap with gear and was redone with
# trap + gmin 1e-8 (ripiego.txt). The check: two 0 C runs with gear and NO cap, against their trap
# runs - the tightest corner (the music after a 20 ms hole) and a fault (guasto, the latch).
set -u
D=${0:A:h}
L=$D:h
P=(--n2n7002 ds --tss 3.0 --comparatore tarato --ritenuta costruttore --bat54 costruttore --sonde-piu
   --temp 0 --perdita D538:5.5e-9,D535:2.9e-9,D536:2.9e-9,D541:2.9e-9,D533:0.4e-6,D534:2.9e-9,D537:0.4e-6)
for spec in buco20:dmus guasto:dperm_gu; do
    p=(${(s/:/)spec})
    O=$L/seq/numgear_c0g_t0_$p[2]/$p[1]
    rm -rf $O
    mkdir -p $O
    /usr/bin/python3 $D/genera_tb_psu.py --uscita $O --nome seq --caso $p[1] --giro 1 --angolo nom \
        --timer sorgente $P --toll $L/mc25/toll_c0g_t0_$p[2].json > /dev/null
    ( cd $O && /opt/homebrew/bin/ngspice -b tb_psu_seq_$p[1]_g1.cir -o tb_psu_seq_$p[1]_g1.log > /dev/null 2>&1 ) &
done
wait
for spec in buco20:dmus guasto:dperm_gu; do
    p=(${(s/:/)spec})
    O=$L/seq/numgear_c0g_t0_$p[2]/$p[1]
    if grep -qiE 'error|singular|timestep too small' $O/tb_psu_seq_$p[1]_g1.log; then
        echo "$spec: errore nel log"
    else
        echo "gear nessun tetto" > $O/ok.txt
        echo "$spec: fatto"
    fi
done
