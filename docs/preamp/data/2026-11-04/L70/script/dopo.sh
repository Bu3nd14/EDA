#!/bin/zsh
# L69b: what follows the sequences, never more than 3 ngspice of this lot: when the batch of
# corri_lista_an.sh is over, coda.sh (the missing runs, the standby, the bridge and the chain, 2 at a
# time) and banchi.sh (the network, the faults, the heat, 1 at a time) run together.
#   /bin/zsh script/dopo.sh
set -u
L=${0:A:h:h}
while /usr/bin/pgrep -f corri_lista_an.sh > /dev/null; do
    /bin/sleep 30
done
/bin/zsh $L/script/coda.sh > $L/coda.out 2>&1 &
/usr/bin/nice -n 15 /bin/zsh $L/script/banchi.sh > $L/banchi.out 2>&1
echo "banchi: fatto"
wait
echo "coda: fatta"
