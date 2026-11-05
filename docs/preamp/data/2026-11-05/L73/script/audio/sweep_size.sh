#!/bin/zsh
# L73 - board size as a function of the packing parameters, placement only (no
# routing). Copied from L49a's sweep_size.sh, with the packing mode (L73_PACK:
# connectivity = L49a's, height = tallest first in the blocks too).
#
#   /bin/zsh sweep_size.sh <work_dir> > sweep.txt
#
# <work_dir> must hold audio_raw.kicad_pcb / .kicad_pro (make_board.py).
# One placement at a time, at nice 10 (a fanless MacBook Air).
set -e
WORK=${1:?usage: sweep_size.sh <work_dir>}
HERE=${0:A:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
for pack in connectivity height; do
  for gap in 1.0 1.2; do
    for bw in 70 80 90 100 110; do
      d="$WORK/sweep/${pack}_g${gap}_b${bw}"
      mkdir -p "$d"
      cp "$WORK/audio_raw.kicad_pcb" "$WORK/audio_raw.kicad_pro" "$d/"
      size=$(L73_PACK=$pack /usr/bin/nice -n 10 $KICAD_PY "$HERE/place.py" "$d" $gap $bw 3.0 2>/dev/null | grep board_mm | cut -c1-44)
      ov=$(/usr/bin/python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d["courtyard_overlaps"]), d["heatsinks"]["min_gap_mm"][0], {k: v["mm"] for k, v in d["thermal_pairs"].items()}.get("A_L"))' "$d/placement.json")
      echo "pack=$pack gap=$gap block_w=$bw  $size  overlaps/hs_gap/AL_pair: $ov"
    done
  done
done
