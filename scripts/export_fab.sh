#!/bin/zsh
# export_fab.sh - export gerbers + drill files into fabrication/.
#
# Hard rule enforced here: NEVER export fabrication outputs from a
# board that fails DRC. This script always runs a fresh DRC pass
# first (via run_drc.sh) and refuses to export (nonzero exit, no
# files written) if any DRC violation is found. There is no flag to
# bypass this.
#
# Usage:
#   /bin/zsh /Users/roberto/EDA/scripts/export_fab.sh <board.kicad_pcb> [outdir]
#
# Output (idempotent - directory is cleared and re-populated each
# successful run): [outdir]/*.gbr, *.drl, gerber job file, plus
# [outdir]/drc.json (the passing DRC report used as the export gate).
#
# Exit codes:
#   0  - DRC clean, gerbers + drill exported
#   2  - usage error
#   5  - DRC found violations -> export REFUSED (matches kicad-cli's
#        own --exit-code-violations convention)
#   1  - export step itself failed after a clean DRC (unexpected)

set -u

KICAD_CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli
SCRIPT_DIR=/Users/roberto/EDA/scripts
ROOT=/Users/roberto/EDA

if [ $# -lt 1 ]; then
    echo "Usage: $0 <board.kicad_pcb> [outdir]" >&2
    exit 2
fi

BOARD="$1"
if [ ! -f "$BOARD" ]; then
    echo "ERROR: board not found: $BOARD" >&2
    exit 2
fi

BASENAME=$(basename "$BOARD" .kicad_pcb)
OUTDIR="${2:-$ROOT/fabrication/$BASENAME}"

echo "== export_fab.sh: DRC gate for $BOARD =="
DRC_JSON="/tmp/export_fab_${BASENAME}_drc.json"
/bin/zsh "$SCRIPT_DIR/run_drc.sh" "$BOARD" "$DRC_JSON"
drc_rc=$?

if [ $drc_rc -ne 0 ]; then
    echo "REFUSED: DRC failed (kicad-cli exit=$drc_rc) - fabrication export blocked." >&2
    echo "         Fix the violations in $DRC_JSON and re-run before exporting." >&2
    exit 5
fi

echo "   DRC clean (exit 0). Proceeding with fabrication export."

mkdir -p "$OUTDIR"
# clear stale gerber/drill outputs from a previous run for this board
# (idempotent: re-running always reflects the current board state).
# nullglob so an empty/fresh OUTDIR doesn't trip zsh's NOMATCH error.
setopt local_options nullglob
rm -f "$OUTDIR"/*.gbr "$OUTDIR"/*.gbrjob "$OUTDIR"/*.drl 2>/dev/null

cp "$DRC_JSON" "$OUTDIR/drc.json"

echo "== export_fab.sh: exporting gerbers -> $OUTDIR =="
"$KICAD_CLI" pcb export gerbers --output "$OUTDIR/" "$BOARD"
gerb_rc=$?

echo "== export_fab.sh: exporting drill -> $OUTDIR =="
"$KICAD_CLI" pcb export drill --output "$OUTDIR/" "$BOARD"
drill_rc=$?

if [ $gerb_rc -ne 0 ] || [ $drill_rc -ne 0 ]; then
    echo "ERROR: export step failed (gerbers rc=$gerb_rc, drill rc=$drill_rc)" >&2
    exit 1
fi

n_files=$(ls -1 "$OUTDIR" | wc -l | tr -d ' ')
echo "== export_fab.sh done: $n_files file(s) in $OUTDIR =="
exit 0
