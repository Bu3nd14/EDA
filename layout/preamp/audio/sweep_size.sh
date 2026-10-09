#!/bin/zsh
# L49a - board size as a function of the packing parameters, placement only
# (no routing). One line per combination: gap block_w spine_gap -> W x H mm.
#
#   /bin/zsh layout/preamp/audio/sweep_size.sh <work_dir>
#
# <work_dir> must hold audio_raw.kicad_pcb / .kicad_pro (make_board.py).
set -e
WORK=${1:?usage: sweep_size.sh <work_dir>}
HERE=${0:A:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
for gap in 1.0 1.2 1.5; do
  for bw in 75 80 85 88; do
    d="$WORK/g${gap}_b${bw}"
    mkdir -p "$d"
    cp "$WORK/audio_raw.kicad_pcb" "$WORK/audio_raw.kicad_pro" "$d/"
    size=$($KICAD_PY "$HERE/place.py" "$d" $gap $bw 3.0 2>/dev/null | grep board_mm | cut -c1-40)
    echo "gap=$gap block_w=$bw spine_gap=3.0  $size"
  done
done
