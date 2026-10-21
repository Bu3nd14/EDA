#!/bin/zsh
# corri_massimi.sh - L45d2b2c: the block's decks (deck/lista.txt) and P7's (deck/lista_tb.txt) through
# corri.sh / uno.sh (L62b's, copied: 8 at a time, run/<gruppo>/<nome>/, rc in run/esiti.tsv)
set -u
D=${0:A:h}
/bin/zsh "$D/corri.sh" "$D:h/deck/lista.txt"
/bin/zsh "$D/corri.sh" "$D:h/deck/lista_tb.txt"
