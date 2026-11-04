#!/bin/zsh
# L70: the five single-rail decks, <paralleli> at a time (default 1), at low priority; log next to each deck.
#   /bin/zsh blocco/corri.sh [paralleli]
set -u
B=${0:A:h}
P=${1:-1}
ls -d $B/A_*(/) | /usr/bin/xargs -P $P -I{} /bin/zsh -c 'cd {} && /usr/bin/nice -n 15 /opt/homebrew/bin/ngspice -b ${PWD:t}.cir -o ${PWD:t}.log > /dev/null 2>&1; echo "${PWD:t}: rc $?"'
