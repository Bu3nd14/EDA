#!/bin/zsh
# corri_p7.sh - L45d2b2c: P7's decks at the four rails (deck/lista_tb.txt) and at the three mains
# levels (deck/lista_tb_reti.txt), through corri.sh / uno.sh
set -u
D=${0:A:h}
/bin/zsh "$D/corri.sh" "$D:h/deck/lista_tb.txt"
/bin/zsh "$D/corri.sh" "$D:h/deck/lista_tb_reti.txt"
