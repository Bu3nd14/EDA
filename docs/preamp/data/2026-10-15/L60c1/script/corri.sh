#!/bin/zsh
# corri.sh <lista.txt> : ogni deck della lista con uno.sh, 8 alla volta. L60c1, da L60a.
L=${0:A:h:h}
xargs -P 8 -n 1 /bin/zsh $L/script/uno.sh < $1
print -r -- "fine: $1"
