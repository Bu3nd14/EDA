#!/bin/zsh
# corri.sh [n] : every deck of calore/lista.txt with calore/uno.sh, n at a time (default 3), at low
# priority (L66's script/corri.sh).
C=${0:A:h}
/usr/bin/nice -n 10 /usr/bin/xargs -P ${1:-3} -n 1 /bin/zsh $C/uno.sh < $C/lista.txt
print -r -- "fine: $C/lista.txt"
