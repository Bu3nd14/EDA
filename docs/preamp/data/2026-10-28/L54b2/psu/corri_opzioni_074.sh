#!/bin/zsh
# corri_opzioni_074.sh - L45d2b2b1: ADR-074's 26 fault cases (lista_074.txt) for each option, one
# option after the other (8 cases at a time each), in seq/<option>:
#   serie_47_sb340  an SB340 in series after each rail regulator's OUT, the regulator regulating its
#                   pin (+0.3 V of set point: the rail ~15 V), SB340 also as D510 / D511, R550 / R551
#                   4.7 ohm as today
#   serie_33_sb340  the same with R550 / R551 at 3.3 ohm
#   clamp_sb340     today's circuit with only D510 / D511 as SB340
# The SB340's model: the bom-component-manager's fit of Vishay 88719 fig. 3, 25 C typical (README).
D=${0:A:h}
L=$D:h/lista_074.txt
SB=8.7e-5,1.47,0.0136
/bin/zsh $D/corri_lista.sh $L serie_47_sb340 --variante uscita --senso piedino --dvset 0.3 --dserie $SB --dclamp $SB
/bin/zsh $D/corri_lista.sh $L serie_33_sb340 --variante uscita --senso piedino --dvset 0.3 --dserie $SB --dclamp $SB --valore R550=3.3,R551=3.3
/bin/zsh $D/corri_lista.sh $L clamp_sb340 --dclamp $SB
print -r -- "fine opzioni"
