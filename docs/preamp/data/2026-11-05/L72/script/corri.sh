#!/bin/zsh
# corri.sh : i deck di stax/lista.txt, 3 alla volta (MacBook Air senza ventole).
L=${0:A:h:h}
xargs -P 3 -n 1 /bin/zsh $L/script/uno.sh < $L/stax/lista.txt
print -r -- "fine"
