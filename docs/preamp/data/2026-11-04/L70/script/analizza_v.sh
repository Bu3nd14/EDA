#!/bin/zsh
# L70: analizza_mc.py (L54b3b's columns) on the runs of one label family, then the comparison with
# L69b's events (confronta_eventi.py) when the family is a variant of the 117-list.
#   /bin/zsh script/analizza_v.sh <prefisso> [confronta]
# <prefisso>: seq/<prefisso>, seq/<prefisso>_m10, seq/<prefisso>_p10 when they exist -> an_<prefisso>.csv
set -u
L=${0:A:h:h}
cd $L || exit 1
p=$1
dirs=()
for d in seq/$p seq/${p}_m10 seq/${p}_p10; do
    [ -d $d ] && dirs+=($d/*(/))
done
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_$p.csv $dirs > /dev/null || exit 1
echo "an_$p.csv: ${#dirs} casi"
if [ "${2:-}" = "confronta" ]; then
    /usr/bin/python3 -I script/confronta_eventi.py an_$p.csv $p > confronto_$p.txt
    cat confronto_$p.txt
fi
