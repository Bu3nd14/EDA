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

ROOT=/Users/roberto/EDA
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
missing=0
for f in smoke/rc_circuit.kicad_sch smoke/rc_circuit.net smoke/rc_circuit_routed.kicad_pcb \
         smoke/gerbers/rc_circuit_routed.drl smoke/rc_sim_summary.json; do
    p="$ROOT/$f"
    if [ -s "$p" ]; then
        echo "   OK: $f ($(stat -f%z "$p" 2>/dev/null || stat -c%s "$p") bytes)"
    else
        echo "   MISSING/EMPTY: $f" >&2
        missing=$((missing + 1))
    fi
done
report "smoke pipeline artifacts present" $missing
echo

echo "== run_tests.sh SUMMARY: $n_pass passed, $n_fail failed =="
exit $fail
