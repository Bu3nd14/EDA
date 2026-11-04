#!/bin/zsh
# L69: the runs on the new source (ADR-116): psu/analizza_mc.py on seq/oggi and seq/sano -> an_sorgente.csv,
# then psu/confronta_sorgente.py (against L64b's healthy runs and against the same case in L68).
set -u
L=${0:A:h:h}
cd $L || exit 1
/usr/bin/nice -n 15 /usr/bin/python3 -I psu/analizza_mc.py --te=3.0 an_sorgente.csv seq/oggi/* seq/sano/* > /dev/null || exit 1
/usr/bin/python3 -I psu/confronta_sorgente.py an_sorgente.csv confronto_sorgente.csv > confronto_sorgente.txt || exit 1
echo "an_sorgente.csv: $(($(wc -l < an_sorgente.csv) - 1)) corse"
