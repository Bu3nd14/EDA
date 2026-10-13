#!/bin/zsh
# corri_lista.sh <lista> - L45c1: every case of <lista> (one per line) through uno_psu.sh, at
# most 8 at a time (xargs -P 8, limitations #58).
set -u
D=${0:A:h}
/usr/bin/xargs -P 8 -n 1 /bin/zsh "$D/uno_psu.sh" < "$1"
echo "fatto: $(wc -l < "$1") casi"
