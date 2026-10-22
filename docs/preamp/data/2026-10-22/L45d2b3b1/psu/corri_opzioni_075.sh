#!/bin/zsh
# corri_opzioni_075.sh - L45d2b2b2: ADR-075's options on the netlist of before the lot, each list after
# the other (corri_lista.sh, 8 at a time), at most 20 passes (GIRI_MAX, README «Il comando che riparte»)
set -u
D=${0:A:h}
L=$D:h
export GIRI_MAX=20
/bin/zsh "$D/corri_lista.sh" "$L/lista_k501.txt" oggi
/bin/zsh "$D/corri_lista.sh" "$L/lista_comando.txt" oggi_ds --n2n7002 ds
/bin/zsh "$D/corri_lista.sh" "$L/lista_comando.txt" opz_a --n2n7002 ds --serie2 D506,D508,D505 --mos Q503=DMN6075S
/bin/zsh "$D/corri_lista.sh" "$L/lista_comando.txt" opz_b --n2n7002 ds --mos Q501=DMN6075S,Q502=DMN6075S,Q503=DMN6075S
/bin/zsh "$D/corri_lista.sh" "$L/lista_resistenze.txt" opz_r --serie2 R503,R510,R512
/bin/zsh "$D/corri_lista.sh" "$L/lista_5v.txt" opz_5v --u504doppio
# the normal sequences: the jack's release, Delta, the power-up, with and without the options together
/bin/zsh "$D/corri_lista.sh" "$L/lista_norm.txt" norm_base
/bin/zsh "$D/corri_lista.sh" "$L/lista_norm.txt" norm_opz --serie2 D506,D508,D505,R503,R510,R512 --mos Q503=DMN6075S --u504doppio
echo "fatto"
