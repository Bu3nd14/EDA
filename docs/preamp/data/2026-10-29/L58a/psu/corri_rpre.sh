#!/bin/zsh
# corri_rpre.sh - L45d2b2a: the rete deck (regime and mains loss at -10 % / nominal / +10 %) with a
# resistor before each audio regulator, 0 (none) to 5.6 ohm; the soft-start of the + 4.7 uF / -
# 470 nF option, the audio board's capacitors on. Then analizza.py (the hold) on each, and
# riassunto_rpre.py (the regulators' heat) on all.
#   /bin/zsh corri_rpre.sh
D=${0:A:h}
R=$D:h/rete
for r in 0 2.2 3.3 4.7 5.6; do
    if [ "$r" = "0" ]; then
        /usr/bin/python3 -I $D/genera_tb_psu.py --uscita $R/rpre_$r --nome rete --cnr U501=4.7u,U502=470n > /dev/null
    else
        /usr/bin/python3 -I $D/genera_tb_psu.py --uscita $R/rpre_$r --nome rete --cnr U501=4.7u,U502=470n --rpre U501=$r,U502=$r > /dev/null
    fi
    /opt/homebrew/bin/ngspice -b $R/rpre_$r/tb_psu_rete.cir -o $R/rpre_$r/tb_psu_rete.log > /dev/null 2>&1 &
done
wait
for r in 0 2.2 3.3 4.7 5.6; do
    /usr/bin/python3 -I $D/analizza.py $R/rpre_$r > /dev/null
done
/usr/bin/python3 -I $D/riassunto_rpre.py $D:h/rpre.csv $R/rpre_0 $R/rpre_2.2 $R/rpre_3.3 $R/rpre_4.7 $R/rpre_5.6
print -r -- "fine rpre"
