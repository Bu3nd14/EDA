#!/bin/zsh
# L64a: la distorsione del blocco di oggi col banco di L46b (come L51c), a priorita' bassa.
# Dalla radice del repo: /bin/zsh docs/preamp/data/2026-11-02/L64a/distorsione/script/tutto.sh
S=${0:A:h}
D=${S:h}
cd ${D:h:h:h:h:h:h}
/usr/bin/python3 $S/oggi.py || exit 1
/usr/bin/python3 $S/genera.py thd,imd oggi || exit 1
nice -n 10 /bin/zsh $S/esegui.sh $D/deck/lista_thdimd.txt
/usr/bin/python3 $S/leggi_four.py oggi
