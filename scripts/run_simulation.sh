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
# ROOT is derived from this script's own location, never hard-coded: run
# from a worktree, a hard-coded ROOT silently read and wrote the *other*
# tree. Same defect, same fix, as run_tests.sh.
ROOT=${0:A:h:h}

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
# Absolute, because this script cd's into $OUTDIR before running ngspice:
# a relative outdir argument would leave $LOG/$CSV/$JSON pointing nowhere.
OUTDIR=$(cd "$OUTDIR" && pwd)

LOG="$OUTDIR/${BASENAME}.log"
WRDATA="$OUTDIR/${BASENAME}_wrdata.txt"
CSV="$OUTDIR/${BASENAME}.csv"
JSON="$OUTDIR/${BASENAME}.json"

# Work on an absolute copy of the netlist so relative wrdata paths in
# the deck's .control block (if any) land in $OUTDIR, not $PWD.
NETLIST_ABS=$(cd "$(dirname "$NETLIST")" && pwd)/$(basename "$NETLIST")

echo "== run_simulation.sh: $NETLIST_ABS -> $OUTDIR =="

# @REPO@ placeholder: a deck writes `.include @REPO@/spice/...` and this
# script resolves it against the checkout the script is itself part of.
# That is what keeps a deck portable across worktrees and clones.
#
# Why a placeholder and not a plain relative path: ngspice resolves a
# relative `.include` against the CURRENT WORKING DIRECTORY, not against
# the directory of the deck that contains it - and this script cd's to
# $OUTDIR (below) so that bare `wrdata <name>` lands there. Verified,
# not assumed: two files both named ../real.lib, one reachable from the
# deck's directory (1k) and one from the cwd (9k); ngspice -b read the
# cwd one.
#
# A missing include is loud - ngspice exits 1 with "Could not find
# include file" - so an unresolved @REPO@ fails safe. The dangerous case
# is a same-named stray file reachable from $OUTDIR, which is what the
# warning below exists for.
SRC_DECK="$NETLIST_ABS"
if grep -q '@REPO@' "$NETLIST_ABS"; then
    SRC_DECK="$OUTDIR/${BASENAME}_resolved.cir"
    sed "s|@REPO@|$ROOT|g" "$NETLIST_ABS" > "$SRC_DECK"
    echo "   deck uses @REPO@; resolved against $ROOT -> $SRC_DECK"
fi

# A relative .include resolves against $OUTDIR, so it either fails loudly
# or - worse - picks up a same-named stray file. Say so out loud.
if grep -E '^[[:space:]]*\.include[[:space:]]+[^/@[:space:]]' "$SRC_DECK" > /dev/null 2>&1; then
    echo "   WARNING: deck has a relative .include; ngspice resolves it against" >&2
    echo "            the working directory ($OUTDIR), not the deck's directory." >&2
    echo "            Use @REPO@/<path-from-repo-root> instead." >&2
fi

# Does the deck already have its own .control/wrdata? If not, wrap it
# with a minimal .op + wrdata-all-vectors block so this script always
# produces machine-readable output, at minimum an operating point.
if grep -qi '^\s*\.control' "$SRC_DECK"; then
    RUN_DECK="$SRC_DECK"
    echo "   deck has its own .control block; running as-is"
else
    RUN_DECK="$OUTDIR/${BASENAME}_autowrap.cir"
    { grep -vi '^\s*\.end\s*$' "$SRC_DECK"
      echo ".control"
      echo "op"
      echo "wrdata $WRDATA all"
      echo "quit"
      echo ".endc"
      echo ".end"
    } > "$RUN_DECK"
    echo "   deck had no .control block; wrapped with .op + wrdata -> $RUN_DECK"
fi

# One converter, used by both the primary path and the second pass below.
# Same logic as before it was a function - only the call sites changed.
convert_wrdata() {
    local src="$1" out_csv="$2" out_json="$3"
    /usr/bin/python3 - "$src" "$out_csv" "$out_json" "$NETLIST_ABS" "$rc" <<'PYEOF'
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
}

# Marker, dropped before ngspice runs: the second pass converts only the
# files THIS run produced, never .txt debris an earlier run left in
# $OUTDIR. Timestamps and not a before/after file list, because a re-run
# overwrites its own output and a list-based check would then skip it.
# Verified, not assumed: mtimes are nanosecond on APFS and `find -newer`
# separated two files created 126 us apart.
MARKER="$OUTDIR/.run_marker"
: > "$MARKER"

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
    convert_wrdata "$SRC_WRDATA" "$CSV" "$JSON"
else
    echo "   WARNING: no wrdata output found/produced; writing rc-only JSON" >&2
    /usr/bin/python3 -c "
import json
json.dump({'netlist': '$NETLIST_ABS', 'returncode': $rc, 'rows': 0, 'columns': [], 'data': [], 'warning': 'no wrdata output found'}, open('$JSON', 'w'), indent=2)
"
fi

# Second pass: every OTHER wrdata file this run produced, written as
# <stem>.csv / <stem>.json. The primary above only ever converts ONE file,
# because the fallback does `grep ... | head -1` - so a deck with two
# wrdata lines (tb_dc_headroom.cir) silently lost the second one.
#
# Why this looks at produced FILES and not at the deck text: a wrdata name
# written inside a `foreach` is parameterised, so the deck holds the
# UNEXPANDED name and no grep can recover the real one. tb_ac.cir will
# write 8 curves out of one loop (L5).
extra=0
for f in $(find "$OUTDIR" -maxdepth 1 -type f -name '*.txt' -newer "$MARKER" 2>/dev/null | sort); do
    [ -s "$f" ] || continue
    # skip the primary, whichever path form it was found under
    if [ -n "$SRC_WRDATA" ] && [ "${f:t}" = "${SRC_WRDATA:t}" ]; then
        continue
    fi
    stem="${f:t:r}"
    echo "   additional wrdata output: $f"
    convert_wrdata "$f" "$OUTDIR/${stem}.csv" "$OUTDIR/${stem}.json"
    extra=$((extra + 1))
done
if [ "$extra" -gt 0 ]; then
    echo "   second pass converted $extra additional wrdata file(s)"
fi

rm -f "$MARKER"

echo "== run_simulation.sh done (ngspice rc=$rc) =="
exit $rc
