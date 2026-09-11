#!/bin/zsh
# run_tests.sh - run the whole repo test suite.
#
#   1. Model validation (scripts/validate_models.py) - provenance +
#      real ngspice electrical checks on every file in models/.
#   2. Fast subset of the smoke pipeline, re-executed for real (not
#      just "files exist"):
#        a. run_drc.sh against the known-good routed smoke board
#           (must be DRC-clean).
#        b. run_simulation.sh against a real testbench netlist and
#           verify CSV/JSON output was produced with data rows.
#        c. sanity-check that the smoke pipeline's key artifacts
#           (schematic, netlist, routed board, gerbers) exist and are
#           non-empty, i.e. the full pipeline was actually run at
#           least once and left evidence behind.
#
# Nonzero exit if ANY of the above fails. Safe to re-run (idempotent):
# writes scratch output under results/run_tests/, overwriting each run.

set -u

# Resolve from this script's own location, NOT a hard-coded path: with a
# hard-coded ROOT, running the suite from an isolated working copy silently
# tests the main checkout instead of the tree you are editing - a wrong
# answer with no error, which is exactly what this repo exists to avoid.
ROOT=${0:A:h:h}
SCRIPTS="$ROOT/scripts"
SCRATCH="$ROOT/results/run_tests"
mkdir -p "$SCRATCH"

fail=0
n_pass=0
n_fail=0

report() {
    # $1 = label, $2 = rc
    if [ "$2" -eq 0 ]; then
        echo "[PASS] $1"
        n_pass=$((n_pass + 1))
    else
        echo "[FAIL] $1 (exit $2)"
        n_fail=$((n_fail + 1))
        fail=1
    fi
}

echo "== run_tests.sh: EDA repo test suite =="
echo

echo "-- 1. model validation (scripts/validate_models.py) --"
/usr/bin/python3 "$SCRIPTS/validate_models.py" > "$SCRATCH/validate_models.log" 2>&1
rc=$?
tail -5 "$SCRATCH/validate_models.log"
report "validate_models.py" $rc
echo

echo "-- 2a. DRC gate on known-good routed smoke board --"
GOOD_BOARD="$ROOT/smoke/rc_circuit_routed.kicad_pcb"
if [ -f "$GOOD_BOARD" ]; then
    /bin/zsh "$SCRIPTS/run_drc.sh" "$GOOD_BOARD" "$SCRATCH/rc_circuit_routed_drc.json" > "$SCRATCH/run_drc.log" 2>&1
    rc=$?
    tail -3 "$SCRATCH/run_drc.log"
    report "run_drc.sh on $GOOD_BOARD (expect clean)" $rc
else
    echo "   MISSING: $GOOD_BOARD - has the smoke pipeline been run?" >&2
    report "run_drc.sh on $GOOD_BOARD" 1
fi
echo

echo "-- 2b. run_simulation.sh on a real testbench netlist --"
TB="$ROOT/testbenches/01_op.cir"
if [ -f "$TB" ]; then
    /bin/zsh "$SCRIPTS/run_simulation.sh" "$TB" "$SCRATCH/sim_01_op" > "$SCRATCH/run_simulation.log" 2>&1
    rc=$?
    tail -5 "$SCRATCH/run_simulation.log"
    if [ $rc -eq 0 ] && [ -s "$SCRATCH/sim_01_op/01_op.csv" ] && [ -s "$SCRATCH/sim_01_op/01_op.json" ]; then
        rows=$(/usr/bin/python3 -c "import json;print(json.load(open('$SCRATCH/sim_01_op/01_op.json'))['rows'])" 2>/dev/null)
        echo "   produced $rows data row(s) in 01_op.csv/.json"
        [ "${rows:-0}" -gt 0 ] 2>/dev/null && rc=0 || rc=1
    else
        rc=1
    fi
    report "run_simulation.sh on $TB" $rc
else
    echo "   MISSING: $TB" >&2
    report "run_simulation.sh on $TB" 1
fi
echo

echo "-- 2c. smoke pipeline artifact sanity check --"
# Two classes of artifact, deliberately treated differently.
#
# TRACKED ones are in git, so their absence is a real failure.
#
# SCRATCH ones (gerbers, drill) are gitignored by design - fabrication output
# is generated, never committed. A fresh clone or a new working copy simply
# does not have them, so demanding their presence made the suite impossible
# to pass anywhere but the one checkout that happened to have run the smoke
# pipeline. They are SKIPPED when absent and CHECKED when present: an empty
# or truncated file is still a failure.
missing=0
for f in smoke/rc_circuit.kicad_sch smoke/rc_circuit.net \
         smoke/rc_circuit_routed.kicad_pcb smoke/rc_sim_summary.json; do
    p="$ROOT/$f"
    if [ -s "$p" ]; then
        echo "   OK: $f ($(stat -f%z "$p" 2>/dev/null || stat -c%s "$p") bytes)"
    else
        echo "   MISSING/EMPTY: $f" >&2
        missing=$((missing + 1))
    fi
done
for f in smoke/gerbers/rc_circuit_routed.drl; do
    p="$ROOT/$f"
    if [ -e "$p" ]; then
        if [ -s "$p" ]; then
            echo "   OK: $f ($(stat -f%z "$p" 2>/dev/null || stat -c%s "$p") bytes)"
        else
            echo "   EMPTY: $f" >&2
            missing=$((missing + 1))
        fi
    else
        echo "   SKIP: $f (scratch gitignorato - rigenera con: zsh smoke/run_pipeline.sh)"
    fi
done
report "smoke pipeline artifacts present" $missing
echo

echo "-- 2d. schematic drawings vs netlists (see docs/limitations.md #16) --"
# Readable analog schematics cannot be auto-placed, so drawings are laid out
# by hand and MUST be checked against the netlist they claim to describe.
# Discovers every manifest under docs/*/schematic/ - no per-project wiring.
sch_fail=0
sch_seen=0
while IFS= read -r mf; do
    [ -n "$mf" ] || continue
    sch_seen=$((sch_seen + 1))
    net=$(/usr/bin/python3 -c "
import json,sys
print(json.load(open('$mf')).get('source_netlist',''))" 2>/dev/null)
    case "$net" in
        /*) ;;                       # already absolute
        "") echo "   MANIFEST WITHOUT source_netlist: $mf" >&2
            sch_fail=$((sch_fail + 1)); continue ;;
        *)  net="$ROOT/$net" ;;
    esac
    if /usr/bin/python3 "$ROOT/scripts/check_schematic.py" "$mf" "$net"; then
        echo "   OK: $(basename "$mf")"
    else
        sch_fail=$((sch_fail + 1))
    fi
done < <(find "$ROOT/docs" -path '*/schematic/*.manifest.json' -type f 2>/dev/null | sort)
if [ "$sch_seen" -eq 0 ]; then
    echo "   (nessun disegno da controllare)"
fi
report "schematic drawings match their netlists" $sch_fail
echo

echo "-- 2e. relay safe state on de-energised coils (NC-014) --"
# A mute relay must short the outputs to ground when its coil is
# de-energised (ADR-012) and a gain relay must leave R_g floating (ADR-004).
# Until L21 the G6K-2F-Y pin map was DEDUCED instead of read, and pole 2 -
# the right channel - came out inverted: at power-on that channel was not
# muted at all, and nothing said so. The fix is one line; this is what stops
# it from coming back in silence.
#
# The netlists are named rather than discovered: the checker FAILS when it
# finds no relay, deliberately, so it cannot go blind. Adding a second
# circuit means adding a line here.
rly_fail=0
for net in circuits/preamp/preamp_audio.net; do
    p="$ROOT/$net"
    if [ ! -f "$p" ]; then
        echo "   MISSING: $net (rigenera con: env/venv/bin/python3 ${net%.net}.py)" >&2
        rly_fail=$((rly_fail + 1))
        continue
    fi
    # NOT a pipeline: the exit status of `cmd | sed` is sed's, so piping the
    # output straight into an indenter would have made this block pass no
    # matter what the checker said. Capture first, then print.
    out=$(/usr/bin/python3 "$ROOT/scripts/check_relay_safe_state.py" "$p" 2>&1)
    rc=$?
    echo "$out" | sed 's/^/   /'
    if [ $rc -ne 0 ]; then
        rly_fail=$((rly_fail + 1))
    fi
done
report "relays fail safe with de-energised coils" $rly_fail
echo

echo "== run_tests.sh SUMMARY: $n_pass passed, $n_fail failed =="
exit $fail
