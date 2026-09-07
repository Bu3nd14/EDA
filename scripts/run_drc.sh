#!/bin/zsh
# run_drc.sh - design rule check via kicad-cli, JSON output.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/run_drc.sh <board.kicad_pcb> [outjson]
#
# Exit code: propagates kicad-cli's own exit code (0 = no
# error/warning violations, 5 = violations found, per kicad-cli's
# --exit-code-violations flag). Idempotent: overwrites outjson.

set -u

KICAD_CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli

if [ $# -lt 1 ]; then
    echo "Usage: $0 <board.kicad_pcb> [outjson]" >&2
    exit 2
fi

BOARD="$1"
if [ ! -f "$BOARD" ]; then
    echo "ERROR: board not found: $BOARD" >&2
    exit 2
fi

OUTJSON="${2:-$(dirname "$BOARD")/$(basename "$BOARD" .kicad_pcb)_drc.json}"

echo "== run_drc.sh: $BOARD -> $OUTJSON =="
"$KICAD_CLI" pcb drc --format json --exit-code-violations --output "$OUTJSON" "$BOARD"
rc=$?

if [ -f "$OUTJSON" ]; then
    n=$(/usr/bin/python3 -c "
import json
d = json.load(open('$OUTJSON'))
print(len(d.get('violations', [])))
" 2>/dev/null)
    echo "   violations reported in JSON: ${n:-unknown}"
else
    echo "   WARNING: expected output JSON not found: $OUTJSON" >&2
fi

echo "== run_drc.sh done (kicad-cli exit=$rc) =="
exit $rc
