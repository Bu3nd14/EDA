#!/bin/zsh
# run_erc.sh - electrical rule check via kicad-cli, JSON output.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/run_erc.sh <schematic.kicad_sch> [outjson]
#
# Exit code: propagates kicad-cli's own exit code (0 = no
# error/warning violations, 5 = violations found, per kicad-cli's
# --exit-code-violations flag). Idempotent: overwrites outjson.

set -u

KICAD_CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli

if [ $# -lt 1 ]; then
    echo "Usage: $0 <schematic.kicad_sch> [outjson]" >&2
    exit 2
fi

SCH="$1"
if [ ! -f "$SCH" ]; then
    echo "ERROR: schematic not found: $SCH" >&2
    exit 2
fi

OUTJSON="${2:-$(dirname "$SCH")/$(basename "$SCH" .kicad_sch)_erc.json}"

echo "== run_erc.sh: $SCH -> $OUTJSON =="
"$KICAD_CLI" sch erc --format json --exit-code-violations --output "$OUTJSON" "$SCH"
rc=$?

if [ -f "$OUTJSON" ]; then
    n=$(/usr/bin/python3 -c "
import json
d = json.load(open('$OUTJSON'))
n = sum(len(s.get('violations', [])) for s in d.get('sheets', []))
print(n)
" 2>/dev/null)
    echo "   violations reported in JSON: ${n:-unknown}"
else
    echo "   WARNING: expected output JSON not found: $OUTJSON" >&2
fi

echo "== run_erc.sh done (kicad-cli exit=$rc) =="
exit $rc
