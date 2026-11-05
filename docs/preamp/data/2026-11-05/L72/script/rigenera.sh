#!/bin/zsh
# rigenera.sh : i netlist dal sorgente dopo ADR-123 (il campo Tolerance), come L66
# (rigenera_*.txt). Gira dalla cartella del sorgente, col venv 3.13.
L=${0:A:h:h}
ROOT=${L:h:h:h:h:h}
cd $ROOT/circuits/preamp || exit 1
$ROOT/../../../env/venv/bin/python3 gain_block.py > $L/rigenera_gain_block.txt 2>&1
print -r -- "gain_block rc=$?"
$ROOT/../../../env/venv/bin/python3 preamp_audio.py > $L/rigenera_preamp_audio.txt 2>&1
print -r -- "preamp_audio rc=$?"
