#!/bin/zsh
# corri_finale_074.sh - L45d2b2b1: the bench on the source after ADR-093, with no option that
# replaces the netlist: ADR-074's 26 fault cases (seq/sorgente), the rete deck (rete/sorgente) and
# the power-up at nominal and -10 % mains (seq/acc_sorgente). They must give back the option chosen
# (serie_47_sb340x2: SB340 in series, two SB340 on each pin, 4.7 ohm, +0.3 V).
D=${0:A:h}
/bin/zsh $D/corri_lista.sh $D:h/lista_074.txt sorgente
/bin/zsh $D/uno.sh acc_sorgente accensione
/bin/zsh $D/uno.sh acc_sorgente accensione_m10
/bin/zsh $D/corri_rete_074.sh sorgente
print -r -- "fine finale"
