#!/bin/zsh
# L49b - the pictures of a routed trial board, for the user ("fammi poi vedere
# in qualche modo placement e routing", L49a): a 3D render from the top, and
# the copper as vector PDF plus a 200 dpi PNG of each.
#
#   /bin/zsh layout/preamp/psu/images.sh <board.kicad_pcb> <out_dir>
#
# Writes placement_3d_top.png, routing_both.*, routing_top.*, routing_bottom.*.
# Works for either board (L49a's audio pictures were made the same way).
set -e
PCB=${1:?usage: images.sh <board.kicad_pcb> <out_dir>}
OUT=${2:?usage: images.sh <board.kicad_pcb> <out_dir>}
CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli
mkdir -p "$OUT"
$CLI pcb render --side top --width 2400 --height 1600 --quality high \
    --output "$OUT/placement_3d_top.png" "$PCB"
$CLI pcb export pdf --mode-single --layers F.Cu,B.Cu,Edge.Cuts \
    --output "$OUT/routing_both.pdf" "$PCB"
$CLI pcb export pdf --mode-single --layers F.Cu,F.Silkscreen,Edge.Cuts \
    --output "$OUT/routing_top.pdf" "$PCB"
$CLI pcb export pdf --mode-single --mirror --layers B.Cu,Edge.Cuts \
    --output "$OUT/routing_bottom.pdf" "$PCB"
for n in routing_both routing_top routing_bottom; do
    /opt/homebrew/bin/pdftoppm -png -r 200 -singlefile "$OUT/$n.pdf" "$OUT/$n"
done
ls -la "$OUT"/placement_3d_top.png "$OUT"/routing_*.p*
