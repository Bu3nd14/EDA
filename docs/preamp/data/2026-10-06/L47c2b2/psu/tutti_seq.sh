#!/bin/zsh
# tutti_seq.sh - the sequence cases of L41b2, in parallel, each to its fixed
# point (corri_seq.sh), then the analysis (analizza_seq.py). L47c2a: six, the
# inversione is gone with the fade (ADR-062).
# L47c2b2: copied from L47c2a's deck/; the nine cases of L41c (the supply's faults).
#   /bin/zsh tutti_seq.sh
set -u
D=${0:A:h}
SEQ=$D:h/seq
mkdir -p "$SEQ"
casi=(spegnimento_l perdita perdita_min guasto guasto_u501 guasto_u503 guasto_u503_min cf_nodelta
      corto_u503)
# the ponte binary once, before the parallel runs (each run rebuilds it otherwise)
/bin/zsh "$D/corri_seq.sh" --solo-compila || exit 1
for c in $casi; do
    /bin/zsh "$D/corri_seq.sh" $c 10 > "$SEQ/corri_$c.txt" 2>&1 &
done
wait
rc=0
for c in $casi; do
    echo "---- $c"
    tail -3 "$SEQ/corri_$c.txt"
    grep -q "punto fisso" "$SEQ/corri_$c.txt" || rc=1
done
/usr/bin/python3 "$D/analizza_seq.py" "$SEQ" $casi > "$SEQ/analisi_seq.txt" 2>&1 || rc=1
cat "$SEQ/analisi_seq.txt"
exit $rc
