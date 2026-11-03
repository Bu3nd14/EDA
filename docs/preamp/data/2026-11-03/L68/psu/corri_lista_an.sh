#!/bin/zsh
# corri_lista_an.sh <lista> <paralleli> - L54a: each line of <lista> is
#   <caso> <etichetta> <timer> [opzioni di genera_tb_psu.py...]
# run through corri_an.sh, <paralleli> at a time (limitations #75: chosen on the memory - each
# sequence run is ~0.3-0.5 GB). One log per line in seq/log_an_<etichetta>_<caso>.txt.
set -u
D=${0:A:h}
/usr/bin/xargs -P "$2" -L 1 /bin/zsh "$D/uno_an.sh" < "$1"
echo "fatto: $(wc -l < "$1") righe"
