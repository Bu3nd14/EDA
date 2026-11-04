#!/bin/zsh
# prepara_angoli.sh - L54b3b: the ranges of each temperature and dielectric hypothesis
# (campioni_mc.py --n 0 writes only intervalli.json), and the worst corners from the 25 C fit
# (angoli.sh). Hypotheses: c0g = every timing capacitor C0G; x7r = X7R on the small ones (C518, C527,
# C529, C549, C550, C551, C553), C0G on C548, C552, C528.
set -u
D=${0:A:h}
L=$D:h
M=$L/mc25
X=C518,C527,C529,C549,C550,C551,C553
for t in 0 25 60; do
    /usr/bin/python3 -I $D/campioni_mc.py --n 0 --seme 54 --temp $t --uscita $L/angoli/c0g_t$t > /dev/null
    /usr/bin/python3 -I $D/campioni_mc.py --n 0 --seme 54 --temp $t --x7r $X --uscita $L/angoli/x7r_t$t > /dev/null
    /bin/zsh $D/angoli.sh $M $L/an_mc25.csv c0g_t${t}_ $L/angoli/c0g_t$t/intervalli.json
    /bin/zsh $D/angoli.sh $M $L/an_mc25.csv x7r_t${t}_ $L/angoli/x7r_t$t/intervalli.json
done
