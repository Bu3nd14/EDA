#!/bin/zsh
# L64b: the benches of the network and of the faults (genera_tb_psu.py --nome rete | guasti) on the
# supply of today, and the bench of the heat from the network's deck. One at a time, at low priority
# (the user, 2026-11-03: other sessions are running).
#
#   /bin/zsh script/banchi.sh [rete] [guasti] [calore]     # none = all three
set -u
L=${0:A:h:h}
OPZ=(--timer sorgente --tss 3.0 --n2n7002 ds --comparatore tarato --ritenuta costruttore --bat54 costruttore)
cosa=("$@")
[ ${#cosa} -eq 0 ] && cosa=(rete guasti calore)
for n in $cosa; do
    if [ $n = calore ]; then
        /usr/bin/python3 -I $L/termica/genera_calore.py || exit 1
        cd $L/termica || exit 1
        /usr/bin/nice -n 15 /usr/bin/caffeinate -i /opt/homebrew/bin/ngspice -b tb_calore.cir -o tb_calore.log > /dev/null 2>&1
        echo "calore: ngspice rc $?"
        continue
    fi
    mkdir -p $L/$n
    /usr/bin/python3 -I $L/psu/genera_tb_psu.py --nome $n --uscita $L/$n $OPZ || exit 1
    cd $L/$n || exit 1
    /usr/bin/nice -n 15 /usr/bin/caffeinate -i /opt/homebrew/bin/ngspice -b tb_psu_$n.cir -o tb_psu_$n.log > /dev/null 2>&1
    echo "$n: ngspice rc $?"
done
