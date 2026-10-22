#!/bin/zsh
# corri.sh <lista.txt> <n> : ogni deck della lista con uno.sh, n alla volta (xargs -P n).
# L45d2b3b1, da L62b. NON esegui.sh di L56 (limitations #58).
L=${0:A:h:h}
xargs -P $2 -n 1 /bin/zsh $L/script/uno.sh < $1
print -r -- "fine: $1"
