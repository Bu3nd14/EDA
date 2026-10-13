#!/bin/zsh
# corri.sh <lista.txt> : ogni deck della lista con uno.sh, 8 alla volta (xargs -P 8).
# L45a. NON esegui.sh di L56: lanciato in background il suo `jobs -r` dentro $( ) conta zero e
# fa partire tutta la lista insieme (in L45a 440 ngspice su 10 core).
L=${0:A:h:h}
xargs -P 8 -n 1 /bin/zsh $L/script/uno.sh < $1
print -r -- "fine: $1"
