#!/bin/zsh
# controllo_l45c1.sh - L45d2b2c: L45c1's two decks of the shorts IN-OUT, copied by
# controllo_l45c1.py, run again with today's ngspice in controllo/l45c1/<caso>/
set -u
D=${0:A:h}
/usr/bin/python3 -I "$D/controllo_l45c1.py" || exit 1
for caso in f_u501_cortoio_mus f_u502_cortoio_mus; do
    cd "$D:h/controllo/l45c1/$caso" || exit 1
    /opt/homebrew/bin/ngspice -b "tb_psu_seq_${caso}_g1.cir" -o "tb_psu_seq_${caso}_g1.log" > /dev/null 2>&1
    print -r -- "$caso: ngspice rc $?"
done
