#!/bin/zsh
# rigenera.sh - L45d2b2c: the block (gain_block.net, spice/preamp/gain_block.subckt and _flat.inc)
# and the audio board (preamp_audio.net) from the source, with the current folder in circuits/preamp
# (SKiDL writes its .erc / .log / _sklib.py there)
set -u
D=${0:A:h}
ROOT=${D:h:h:h:h:h:h}
PY=/Users/roberto/EDA/env/venv/bin/python3
cd "$ROOT/circuits/preamp" || exit 1
$PY gain_block.py > "$D:h/rigenera_gain_block.txt" 2>&1 || { echo "gain_block.py: rc $?"; exit 1; }
$PY preamp_audio.py > "$D:h/rigenera_preamp_audio.txt" 2>&1 || { echo "preamp_audio.py: rc $?"; exit 1; }
echo "rigenerati"
