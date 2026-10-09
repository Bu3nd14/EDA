#!/bin/zsh
# L49b - the supply trial board, end to end: netlist -> board -> placement ->
# Freerouting -> import -> DRC. Exit code is the DRC's (0 clean, 5 violations).
#
#   /bin/zsh layout/preamp/psu/run.sh <out_dir> [height_mm] [gap_mm] [sep_mm] [logic_gap_mm] [power_mm]
#
# As layout/preamp/audio/run.sh: Freerouting 2.4.1 runs with its fan-out stage
# OFF (limitations #50; the user's global settings file, set in L49a with the
# user's permission). This script refuses to run without it.
set -e

OUT=${1:?usage: run.sh <out_dir>}
HERE=${0:A:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
JAVA=/opt/homebrew/opt/openjdk/bin/java
JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar   # not versioned: absolute (CLAUDE.md)
FR_SETTINGS="$HOME/Library/Application Support/freerouting/freerouting.json"
HEIGHT=${2:-100}   # mm, target board depth
GAP=${3:-1.5}      # mm between courtyards inside a group
SEP=${4:-8.0}      # mm, courtyard to courtyard, mains column to the rest
LOGIC_GAP=${5:-$GAP}   # mm between courtyards in the logic block
POWER_MM=${6:-1.0}     # mm, the rails' track width (make_board.py)

if ! /usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["router"]; sys.exit(0 if r.get("fanout",{}).get("enabled") is False else 1)' "$FR_SETTINGS"; then
    echo "REFUSED: Freerouting fan-out is not disabled in $FR_SETTINGS (limitations #50)" >&2
    exit 2
fi

mkdir -p "$OUT"
$KICAD_PY "$HERE/make_board.py" "$OUT" $POWER_MM
$KICAD_PY "$HERE/place.py" "$OUT" $HEIGHT $GAP $SEP $LOGIC_GAP
$KICAD_PY "$HERE/escape.py" "$OUT"
$KICAD_PY "$HERE/route.py" export "$OUT"
# Neckdown ON for this board only (the user's choice in L49b: rails wide,
# narrowed only where a pin is too small for them); the global file keeps it
# off for the audio board. The variable works, unlike for the fan-out of
# limitations #50 (measure.py lists every necked segment). At the regulators'
# 0.65 mm pins the neckdown alone left 2-8 connections open in a different
# place on every run: escape.py draws those escapes and gives the rails an
# anchor via instead. Without the neckdown the SOT-23 / SOIC pins on the 1.0 mm
# return and 12 V nets left 33-34 open (L49b, iterations 14-15).
FREEROUTING__ROUTER__AUTOMATIC_NECKDOWN=true /opt/homebrew/bin/timeout 3600 $JAVA -jar "$JAR" -de "$OUT/psu.dsn" -do "$OUT/psu.ses" -mp 40 -l en > "$OUT/freerouting.log" 2>&1
grep -E "Auto-routing stage completed|finished with state" "$OUT/freerouting.log" | cut -c1-200
$KICAD_PY "$HERE/route.py" import "$OUT"
set +e
/bin/zsh "$HERE/../../../scripts/run_drc.sh" "$OUT/psu_routed.kicad_pcb" "$OUT/drc_psu_routed.json"
rc=$?
/usr/bin/python3 "$HERE/../audio/drc_summary.py" "$OUT/drc_psu_routed.json"
exit $rc
