#!/bin/zsh
# corri_sorgente_075.sh - L45d2b2b2: the bench on the SOURCE after ADR-094 (circuits/preamp/psu.net)
#  - the source's rows (RIGHE_SORGENTE, each half of each doubled part), 2N7002 as its datasheet;
#  - the normal sequences (lista_norm.txt), to set against norm_base (the netlist before);
#  - ADR-074's rows at nominal mains, against L45d2b2b1's seq/sorgente;
#  - the rete deck (VRELAY's hold, the regulators at regime) and the timer deck (standby), on the
#    source and on the netlist before (falsi/psu_prima_di_adr094.net)
set -u
D=${0:A:h}
L=$D:h
P=$L/falsi/psu_prima_di_adr094.net
export GIRI_MAX=20
/usr/bin/python3 -I "$D/lista_sorgente.py" > "$L/lista_sorgente.txt"
/usr/bin/python3 -I "$D/lista_074.py" --nominale > "$L/lista_074_nominale.txt"
/bin/zsh "$D/corri_lista.sh" "$L/lista_sorgente.txt" sorgente --n2n7002 ds
/bin/zsh "$D/corri_lista.sh" "$L/lista_norm.txt" norm_sorgente
/bin/zsh "$D/corri_lista.sh" "$L/lista_074_nominale.txt" s074
/bin/zsh "$D/corri_rete_074.sh" sorgente
/bin/zsh "$D/corri_rete_074.sh" prima --net "$P"
for x in sorgente prima; do
    mkdir -p "$L/timer/$x"
done
/usr/bin/python3 -I "$D/genera_tb_psu.py" --uscita "$L/timer/sorgente" --nome timer
/usr/bin/python3 -I "$D/genera_tb_psu.py" --uscita "$L/timer/prima" --nome timer --net "$P"
/opt/homebrew/bin/ngspice -b "$L/timer/sorgente/tb_psu_timer_nom.cir" -o "$L/timer/sorgente/tb_psu_timer_nom.log" > /dev/null 2>&1
/opt/homebrew/bin/ngspice -b "$L/timer/prima/tb_psu_timer_nom.cir" -o "$L/timer/prima/tb_psu_timer_nom.log" > /dev/null 2>&1
echo "fatto"
