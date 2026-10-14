#!/bin/zsh
# uno_psu.sh <caso> - L45c1: one sequence case to its fixed point (corri_seq.sh, 10 passes at
# most), its output in ../seq/corri_<caso>.txt and its exit code in ../seq/esiti.txt. Run by
# xargs -P 8 (limitations #58: never a background loop that counts its own jobs).
set -u
D=${0:A:h}
/bin/zsh "$D/corri_seq.sh" "$1" 10 > "$D:h/seq/corri_$1.txt" 2>&1
print -r -- "$1 rc=$? $(date +%H:%M:%S)" >> "$D:h/seq/esiti.txt"
