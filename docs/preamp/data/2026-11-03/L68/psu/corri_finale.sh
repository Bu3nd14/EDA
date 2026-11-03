#!/bin/zsh
# corri_finale.sh - L45d2b2a: the bench on TODAY's psu.net (C507 4.7 uF, C508 470 nF, ADR-091;
# R550 / R551 4.7 ohm, ADR-092), no option overriding the netlist: the power-up at the nominal
# mains and at -10 %, the rete deck (regime and mains loss at -10 / 0 / +10 %); then misura_ss.py,
# termico_avvio.py, analizza.py and riassunto_rpre.py on them.
#   /bin/zsh corri_finale.sh
D=${0:A:h}
S=$D:h/seq
R=$D:h/rete
/bin/zsh $D/corri_seq.sh accensione sorgente > $S/sorgente_accensione.txt 2>&1 &
/bin/zsh $D/corri_seq.sh accensione_m10 sorgente > $S/sorgente_accensione_m10.txt 2>&1 &
/usr/bin/python3 -I $D/genera_tb_psu.py --uscita $R/rpre_sorgente --nome rete > /dev/null
/opt/homebrew/bin/ngspice -b $R/rpre_sorgente/tb_psu_rete.cir -o $R/rpre_sorgente/tb_psu_rete.log > /dev/null 2>&1 &
wait
/usr/bin/python3 -I $D/misura_ss.py $D:h/accensione_sorgente.csv $S/sorgente/accensione $S/sorgente/accensione_m10
/usr/bin/python3 -I $D/termico_avvio.py $D:h/termico_sorgente.csv $S/sorgente/accensione $S/sorgente/accensione_m10
/usr/bin/python3 -I $D/analizza.py $R/rpre_sorgente > /dev/null
/usr/bin/python3 -I $D/riassunto_rpre.py $D:h/rete_sorgente.csv $R/rpre_sorgente
print -r -- "fine finale"
