#!/bin/zsh
# confronta.sh <vecchio_audio.net> <vecchio_gain_block.net> : i due confronti di ADR-123, scritti in L72/.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
/usr/bin/python3 -I $L/script/confronta_netlist.py $2 $ROOT/circuits/preamp/gain_block.net \
  R136,R138,R143 > $L/confronto_gain_block.txt
print -r -- "gain_block rc=$?"
/usr/bin/python3 -I $L/script/confronta_netlist.py $1 $ROOT/circuits/preamp/preamp_audio.net \
  R235,R237,R242,R435,R437,R442,R901,R902,R903,R911,R912,R913 > $L/confronto_preamp_audio.txt
print -r -- "preamp_audio rc=$?"
