#!/bin/zsh
# L71: psu/analizza_mc.py (an_l71.csv) and script/stato_finale.py (stato_l71.csv) on every run of
# seq/l71*/ that has its ok.txt (the references l71rif* included).
#   /bin/zsh script/analizza_l71.sh
set -eu
L=${0:A:h:h}
P=/usr/bin/python3
dirs=(${(f)"$(/usr/bin/find $L/seq -mindepth 3 -maxdepth 3 -name ok.txt -path '*/seq/l71*' | /usr/bin/sort | /usr/bin/sed 's#/ok.txt$##')"})
echo "corse con ok.txt: ${#dirs}"
$P -I $L/psu/analizza_mc.py --te=3.0 $L/an_l71.csv $dirs > /dev/null
$P -I $L/script/stato_finale.py $L/stato_l71.csv $dirs > /dev/null
echo "scritti an_l71.csv e stato_l71.csv"
