#!/bin/zsh
# L73 - the supply trial board on TODAY's psu.net, end to end: netlist -> board ->
# placement -> escapes -> Freerouting -> import -> DRC. Copied from L49b
# (layout/preamp/psu/run.sh). Exit code is the DRC's (0 clean, 5 violations).
#
#   /bin/zsh run.sh <out_dir> [height_mm] [gap_mm] [sep_mm] [logic_gap_mm] [power_mm] [wide_mm]
#
# As L49b: Freerouting 2.4.1 with its fan-out OFF (limitations #50, the user's
# global settings file), the neckdown ON for this board only (the user's
# "stretta solo al piedino", L49b). Router at nice 10 (fanless MacBook Air).
set -e

OUT=${1:?usage: run.sh <out_dir>}
HERE=${0:A:h}
REPO=${HERE:h:h:h:h:h:h:h}
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
JAVA=/opt/homebrew/opt/openjdk/bin/java
JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar   # not versioned: absolute (CLAUDE.md)
FR_SETTINGS="$HOME/Library/Application Support/freerouting/freerouting.json"
HEIGHT=${2:-100}
GAP=${3:-3.0}
SEP=${4:-8.0}
LOGIC_GAP=${5:-4.0}
POWER_MM=${6:-1.0}
WIDE_MM=${7:-$POWER_MM}

if ! /usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1]))["router"]; sys.exit(0 if r.get("fanout",{}).get("enabled") is False else 1)' "$FR_SETTINGS"; then
    echo "REFUSED: Freerouting fan-out is not disabled in $FR_SETTINGS (limitations #50)" >&2
    exit 2
fi

mkdir -p "$OUT"
$KICAD_PY "$HERE/make_board.py" "$OUT" $POWER_MM $WIDE_MM
$KICAD_PY "$HERE/place.py" "$OUT" $HEIGHT $GAP $SEP $LOGIC_GAP
$KICAD_PY "$HERE/escape.py" "$OUT"
$KICAD_PY "$HERE/route.py" export "$OUT"
FREEROUTING__ROUTER__AUTOMATIC_NECKDOWN=true /usr/bin/nice -n 10 /opt/homebrew/bin/timeout 3600 $JAVA -jar "$JAR" -de "$OUT/psu.dsn" -do "$OUT/psu.ses" -mp 40 -l en > "$OUT/freerouting.log" 2>&1
grep -E "Auto-routing stage completed|finished with state" "$OUT/freerouting.log" | cut -c1-200
$KICAD_PY "$HERE/route.py" import "$OUT"
set +e
/bin/zsh "$REPO/scripts/run_drc.sh" "$OUT/psu_routed.kicad_pcb" "$OUT/drc_psu_routed.json"
rc=$?
/usr/bin/python3 "$HERE/../audio/drc_summary.py" "$OUT/drc_psu_routed.json"
exit $rc
