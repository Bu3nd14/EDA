#!/bin/zsh
# run_simulation.sh - run an ngspice batch simulation and extract
# results to CSV/JSON.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/run_simulation.sh <netlist.cir> [outdir]
#
# <netlist.cir> must be a self-contained ngspice deck (control block
# with `run` + `wrdata` is recommended; if it has no .control block,
# this script appends a minimal `.op` batch wrapper so bare netlists
# still produce output).
#
# Outputs (idempotent - overwritten each run), written to [outdir]
# (default: results/<netlist-basename>/):
#   <name>.log            - full ngspice stdout/stderr
#   <name>_wrdata.txt      - raw wrdata table, if the deck wrote one
#   <name>.csv             - same data, comma-separated, with a header
#   <name>.json            - {"netlist":..., "returncode":..., "rows": N,
#                             "columns": [...], "data": [[...], ...]}
#
# Exit code: propagates ngspice's own exit code.

set -u

NGSPICE=/opt/homebrew/bin/ngspice
ROOT=/Users/roberto/EDA

if [ $# -lt 1 ]; then
    echo "Usage: $0 <netlist.cir> [outdir]" >&2
    exit 2
fi

NETLIST="$1"
if [ ! -f "$NETLIST" ]; then
    echo "ERROR: netlist not found: $NETLIST" >&2
    exit 2
fi

BASENAME=$(basename "$NETLIST" .cir)
OUTDIR="${2:-$ROOT/results/$BASENAME}"
mkdir -p "$OUTDIR"

LOG="$OUTDIR/${BASENAME}.log"
WRDATA="$OUTDIR/${BASENAME}_wrdata.txt"
CSV="$OUTDIR/${BASENAME}.csv"
JSON="$OUTDIR/${BASENAME}.json"

# Work on an absolute copy of the netlist so relative wrdata paths in
# the deck's .control block (if any) land in $OUTDIR, not $PWD.
NETLIST_ABS=$(cd "$(dirname "$NETLIST")" && pwd)/$(basename "$NETLIST")

echo "== run_simulation.sh: $NETLIST_ABS -> $OUTDIR =="

# Does the deck already have its own .control/wrdata? If not, wrap it
# with a minimal .op + wrdata-all-vectors block so this script always
# produces machine-readable output, at minimum an operating point.
if grep -qi '^\s*\.control' "$NETLIST_ABS"; then
    RUN_DECK="$NETLIST_ABS"
    echo "   deck has its own .control block; running as-is"
else
    RUN_DECK="$OUTDIR/${BASENAME}_autowrap.cir"
    { grep -vi '^\s*\.end\s*$' "$NETLIST_ABS"
      echo ".control"
      echo "op"
      echo "wrdata $WRDATA all"
      echo "quit"
      echo ".endc"
      echo ".end"
    } > "$RUN_DECK"
    echo "   deck had no .control block; wrapped with .op + wrdata -> $RUN_DECK"
fi

cd "$OUTDIR"
"$NGSPICE" -b "$RUN_DECK" > "$LOG" 2>&1
rc=$?
echo "   ngspice exit code: $rc (log: $LOG, $(wc -l < "$LOG" | tr -d ' ') lines)"

# Convert whatever wrdata file was produced (deck's own path, or ours)
# into CSV + JSON. Prefer an explicit wrdata target if the deck names
# one under $OUTDIR; else fall back to $WRDATA.
SRC_WRDATA=""
if [ -f "$WRDATA" ] && [ -s "$WRDATA" ]; then
    SRC_WRDATA="$WRDATA"
else
    # look for any *_out.txt / *wrdata* the deck's own .control may have written
    cand=$(grep -io 'wrdata[[:space:]]\+[^[:space:]]\+' "$RUN_DECK" 2>/dev/null | awk '{print $2}' | head -1)
    if [ -n "$cand" ] && [ -f "$cand" ]; then
        SRC_WRDATA="$cand"
    elif [ -n "$cand" ] && [ -f "$OUTDIR/$cand" ]; then
        SRC_WRDATA="$OUTDIR/$cand"
    fi
fi

if [ -n "$SRC_WRDATA" ] && [ -s "$SRC_WRDATA" ]; then
    echo "   found wrdata output: $SRC_WRDATA"
    /usr/bin/python3 - "$SRC_WRDATA" "$CSV" "$JSON" "$NETLIST_ABS" "$rc" <<'PYEOF'
import sys, csv, json

wrdata_path, csv_path, json_path, netlist, rc = sys.argv[1:6]
rows = []
with open(wrdata_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        vals = [float(v) for v in line.replace(",", " ").split()]
        rows.append(vals)

ncols = max((len(r) for r in rows), default=0)
header = [f"col{i}" for i in range(ncols)]

with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for r in rows:
        w.writerow(r)

with open(json_path, "w") as f:
    json.dump({
        "netlist": netlist,
        "returncode": int(rc),
        "rows": len(rows),
        "columns": header,
        "data": rows,
    }, f, indent=2)

print(f"   wrote {csv_path} ({len(rows)} rows)")
print(f"   wrote {json_path}")
PYEOF
else
    echo "   WARNING: no wrdata output found/produced; writing rc-only JSON" >&2
    /usr/bin/python3 -c "
import json
json.dump({'netlist': '$NETLIST_ABS', 'returncode': $rc, 'rows': 0, 'columns': [], 'data': [], 'warning': 'no wrdata output found'}, open('$JSON', 'w'), indent=2)
"
fi

echo "== run_simulation.sh done (ngspice rc=$rc) =="
exit $rc
