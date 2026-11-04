#!/bin/zsh
# corri_opzioni_075b.sh - L45d2b2b2, the second round (README «Le opzioni, secondo giro»):
#  - opz_a2: option A with 47 ohm in Q503's drain instead of the DMN6075S (the strong MOSFET dumped
#    C523 into a shorted coil, 14.7 A);
#  - opz_5v: rerun after the fix of the doubled parts' nodes (the first run shorted past both
#    regulators: a probe had renamed U504's output pin);
#  - norm_a2: the normal sequences with A2, the resistors and the two regulators together.
set -u
D=${0:A:h}
L=$D:h
export GIRI_MAX=20
/bin/zsh "$D/corri_lista.sh" "$L/lista_comando.txt" opz_a2 --n2n7002 ds --serie2 D506,D508,D505 --rk 47
/bin/zsh "$D/corri_lista.sh" "$L/lista_5v.txt" opz_5v --u504doppio
/bin/zsh "$D/corri_lista.sh" "$L/lista_norm.txt" norm_a2 --serie2 D506,D508,D505,R503,R510,R512 --rk 47 --u504doppio
echo "fatto"
