#!/bin/zsh
# L73 - the audio trial board on TODAY's circuit, end to end: netlist (with the
# admitted-list footprints) -> board -> placement -> Freerouting -> import -> DRC.
# Copied from L49a (layout/preamp/audio/run.sh). Exit code is the DRC's.
#
#   /bin/zsh run.sh <out_dir> [gap_mm] [block_w_mm] [spine_gap_mm] [passes]
#
# Freerouting 2.4.1 is run with its fan-out stage OFF (L49a, limitations #50):
#   ~/Library/Application Support/freerouting/freerouting.json
#   "router": { "fanout": { "enabled": false }, "automatic_neckdown": false }
# This script refuses to run without it. The router runs at nice 10: the
# machine is a fanless MacBook Air (at most 3 heavy jobs at once).
set -e

OUT=${1:?usage: run.sh <out_dir>}
HERE=${0:A:h}
REPO=${HERE:h:h:h:h:h:h:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
JAVA=/opt/homebrew/opt/openjdk/bin/java
JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar   # not versioned: absolute (CLAUDE.md)
FR_SETTINGS="$HOME/Library/Application Support/freerouting/freerouting.json"
GAP=${2:-1.0}
BLOCK_W=${3:-85}
SPINE_GAP=${4:-3.0}
PASSES=${5:-40}

if ! /usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["router"]; sys.exit(0 if r.get("fanout",{}).get("enabled") is False else 1)' "$FR_SETTINGS"; then
    echo "REFUSED: Freerouting fan-out is not disabled in $FR_SETTINGS (see header)" >&2
    exit 2
fi

mkdir -p "$OUT"
if [[ ! -f "$OUT/audio_raw.kicad_pcb" ]]; then
    $KICAD_PY "$HERE/make_board.py" "$OUT"
fi
$KICAD_PY "$HERE/place.py" "$OUT" $GAP $BLOCK_W $SPINE_GAP
$KICAD_PY "$HERE/route.py" export "$OUT"
/usr/bin/nice -n 10 /opt/homebrew/bin/timeout 5400 $JAVA -jar "$JAR" -de "$OUT/audio.dsn" -do "$OUT/audio.ses" -mp $PASSES -l en > "$OUT/freerouting.log" 2>&1
grep -E "Auto-routing stage completed|finished with state" "$OUT/freerouting.log" | cut -c1-200
$KICAD_PY "$HERE/route.py" import "$OUT"
set +e
/bin/zsh "$REPO/scripts/run_drc.sh" "$OUT/audio_routed.kicad_pcb" "$OUT/drc_audio_routed.json"
rc=$?
/usr/bin/python3 "$HERE/drc_summary.py" "$OUT/drc_audio_routed.json"
exit $rc
