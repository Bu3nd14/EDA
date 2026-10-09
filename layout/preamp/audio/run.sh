#!/bin/zsh
# L49a - the audio trial board, end to end: netlist -> board -> placement ->
# Freerouting -> import -> DRC. Exit code is the DRC's (0 clean, 5 violations).
#
#   /bin/zsh layout/preamp/audio/run.sh <out_dir> [gap_mm] [block_w_mm] [spine_gap_mm]
#
# Freerouting 2.4.1 is run with its fan-out stage OFF. With it on, it necks
# tracks to 0.187 mm at SOIC-8 pins (below the 0.25 mm the user chose), and
# neither router.automatic_neckdown=false nor FREEROUTING__ROUTER__* env vars
# stop it. The switch lives in the user's global settings file:
#   ~/Library/Application Support/freerouting/freerouting.json
#   "router": { "fanout": { "enabled": false }, "automatic_neckdown": false }
# (set in L49a with the user's permission; the previous file is kept next to
# it as freerouting.json.bak-L49a). This script refuses to run without it.
set -e

OUT=${1:?usage: run.sh <out_dir>}
HERE=${0:A:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
JAVA=/opt/homebrew/opt/openjdk/bin/java
JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar   # not versioned: absolute (CLAUDE.md)
FR_SETTINGS="$HOME/Library/Application Support/freerouting/freerouting.json"
GAP=${2:-1.0}        # mm between courtyards inside a group
BLOCK_W=${3:-85}     # mm, packing width of one gain block
SPINE_GAP=${4:-3.0}  # mm between the relays of the spine

if ! /usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["router"]; sys.exit(0 if r.get("fanout",{}).get("enabled") is False else 1)' "$FR_SETTINGS"; then
    echo "REFUSED: Freerouting fan-out is not disabled in $FR_SETTINGS (see header)" >&2
    exit 2
fi

mkdir -p "$OUT"
$KICAD_PY "$HERE/make_board.py" "$OUT"
$KICAD_PY "$HERE/place.py" "$OUT" $GAP $BLOCK_W $SPINE_GAP
$KICAD_PY "$HERE/route.py" export "$OUT"
/opt/homebrew/bin/timeout 3600 $JAVA -jar "$JAR" -de "$OUT/audio.dsn" -do "$OUT/audio.ses" -mp 40 -l en > "$OUT/freerouting.log" 2>&1
grep -E "Auto-routing stage completed|finished with state" "$OUT/freerouting.log" | cut -c1-200
$KICAD_PY "$HERE/route.py" import "$OUT"
set +e
/bin/zsh "$HERE/../../../scripts/run_drc.sh" "$OUT/audio_routed.kicad_pcb" "$OUT/drc_audio_routed.json"
rc=$?
/usr/bin/python3 "$HERE/drc_summary.py" "$OUT/drc_audio_routed.json"
exit $rc
