#!/bin/zsh
# corri.sh <lista.txt> : ogni deck della lista con uno.sh, 3 alla volta. L60d2, da L60c2; 3 alla volta: la matrice di V2 ne tiene 7 sui 10 processori.
L=${0:A:h:h}
xargs -P 3 -n 1 /bin/zsh $L/script/uno.sh < $1
print -r -- "fine: $1"
