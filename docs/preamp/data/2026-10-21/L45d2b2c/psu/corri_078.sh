#!/bin/zsh
# corri_078.sh - L45d2b2c: ADR-078's rows (modi.py, RIGHE_078 + BASE_078) on the source's netlist
# (circuits/preamp/psu.net), at the three mains levels, with the 2N7002 as its datasheet (limitations
# #67) and up to 20 passes (L45d2b2b2's); the results in seq/oggi, the list in lista_078.txt
set -u
D=${0:A:h}
L=$D:h
export GIRI_MAX=20
/bin/zsh "$D/corri_seq.sh" --solo-compila || exit 1
/usr/bin/python3 -I "$D/lista_078.py" > "$L/lista_078.txt"
/bin/zsh "$D/corri_lista.sh" "$L/lista_078.txt" oggi --n2n7002 ds
echo "fatto"
