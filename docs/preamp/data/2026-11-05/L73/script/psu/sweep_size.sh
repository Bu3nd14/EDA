#!/bin/zsh
# L73 - the supply board's size against its target depth, placement only.
#   /bin/zsh sweep_size.sh <work_dir>      (<work_dir> holds psu_raw.kicad_pcb / .kicad_pro)
set -e
WORK=${1:?usage: sweep_size.sh <work_dir>}
HERE=${0:A:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
for h in 100 110 120 130 140 160; do
  for lg in 3.0 4.0; do
    d="$WORK/sweep/h${h}_lg${lg}"
    mkdir -p "$d"
    cp "$WORK/psu_raw.kicad_pcb" "$WORK/psu_raw.kicad_pro" "$d/"
    size=$(/usr/bin/nice -n 10 $KICAD_PY "$HERE/place.py" "$d" $h 3.0 8.0 $lg 2>/dev/null | grep board_mm | cut -c1-36)
    echo "height=$h logic_gap=$lg  $size"
  done
done
