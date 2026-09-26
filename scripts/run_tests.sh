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

echo "-- 2e. relay safe state on de-energised coils (NC-014) and the trim interlock (NC-023) --"
# L16 (ADR-027): the same checker also proves, by reachability on the netlist,
# that no trim coil can be powered out of mute, and that all of them can in
# mute. Made to fail on seven generated variants: see
# docs/preamp/data/2026-09-14/L16/esplorazione/falsi/.
# A mute relay must short the outputs to ground when its coil is
# de-energised (ADR-012) and a gain relay must leave R_g floating (ADR-004).
# Until L21 the G6K-2F-Y pin map was DEDUCED instead of read, and pole 2 -
# the right channel - came out inverted: at power-on that channel was not
# muted at all, and nothing said so. The fix is one line; this is what stops
# it from coming back in silence.
# L29e (ADR-044): the mute relay is a changeover in geometry iii - COM on the
# cap's far side, NO on the jack, NC to ground, a bleed on both sides. "NC to
# ground" alone passed on the old shunt at the jack as well; the geometry is
# asserted by intent, and was made to fail on main's netlist and on four
# sabotaged copies: docs/preamp/data/2026-09-25/L29e/falsi/.
# L35 (ADR-045, ADR-028): the permissive K6 on its own command PERMIT_CMD,
# both commands and the mute switch on the timer harness J4, the window D,
# and the panel LEDs proved on their headers J5 / J6 / J7. Made to fail on
# main's netlist and on 14 sabotaged copies:
# docs/preamp/data/2026-09-25/L35/falsi/.
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

echo "-- 2j. the harness between the audio board and the supply board (L41a, ADR-048) --"
# J1 POWER, J2 RLY_RET, J3 LDR_CMD and J4 MUTE_TIMER exist on BOTH boards
# (preamp_audio.py, psu.py); each netlist is fine on its own and a pin on the
# wrong wire errors nowhere - J1 pins 1 and 3 swapped put -15 V on VPLUS.
# Made to fail on 8 sabotaged copies, and it caught a real one while psu.py
# was written (GND renamed by a net merge, limitations #23):
# docs/preamp/data/2026-09-26/L41a/falsi/.
hrn_fail=0
a="$ROOT/circuits/preamp/preamp_audio.net"
p="$ROOT/circuits/preamp/psu.net"
if [ ! -f "$a" ] || [ ! -f "$p" ]; then
    echo "   MISSING: preamp_audio.net or psu.net (rigenera con env/venv/bin/python3 circuits/preamp/<nome>.py)" >&2
    hrn_fail=1
else
    # Captured first, printed after: a pipe would report sed's status (2e).
    out=$(/usr/bin/python3 "$ROOT/scripts/check_psu_harness.py" "$a" "$p" 2>&1)
    rc=$?
    echo "$out" | sed 's/^/   /'
    [ $rc -ne 0 ] && hrn_fail=1
fi
report "harness between the two boards agrees pin by pin" $hrn_fail
echo

echo "-- 2f. block diagram regenerates and its assertions hold (NC-026) --"
# preamp_blocks_draw.py has no manifest - a block diagram omits devices on
# purpose - so block 2d cannot cover it. Its guarantee is that every figure it
# prints is READ from preamp_audio.net and ASSERTED. From L22 to L10 it did
# not run at all (KeyError: 'R237' after a -1 renumbering), so none of those
# assertions ran either, and nothing said so. Running it IS the check.
#
# The SVG goes to $SCRATCH, not over the versioned one (matplotlib stamps ids
# and a date). The interpreter is the SKiDL venv: it is gitignored, so a
# worktree does not have its own and falls back to the main checkout's - the
# interpreter only; the script derives every data path from its own location.
VENV_PY="$ROOT/env/venv/bin/python3"
[ -x "$VENV_PY" ] || VENV_PY="/Users/roberto/EDA/env/venv/bin/python3"
mkdir -p "$SCRATCH"
# Captured first, printed after: `cmd | sed` would report sed's status (2e).
out=$(PREAMP_BLOCKS_SVG="$SCRATCH/preamp_blocks.svg" \
      "$VENV_PY" "$ROOT/docs/preamp/schematic/preamp_blocks_draw.py" 2>&1)
rc=$?
echo "$out" | tail -12 | sed 's/^/   /'
report "block diagram assertions against preamp_audio.net" $rc
echo

echo "-- 2g. every device a testbench names exists, every block contact node is terminated --"
# ngspice does NOT fail on `alter r138` or `print @q133[ic]` when the device
# is gone: it prints "no such device" and exits 0. After L22's -1 renumbering
# tb_switch_v2_counterfactual.cir opened a resistor that no longer existed,
# and V2's counterfactual silently stopped breaking the loop. Found in L10.
# L27: it also refuses a relay-contact node of the gain block (RG, RG10) that a
# deck leaves on a single terminal - ngspice runs that too, and an unmodified
# deck's "10db" mode printed +3 dB with exit code 0.
# L31: and every per-device noise vector (onoise_<device>) a deck names - a
# dead one stops the wrdata with exit code 0, and tb_noise_vectors.cir wrote no
# data for that reason from L22 to L31 (NC-030).
decks=("${(@f)$(find "$ROOT/spice" -path '*/tb/*.cir' -type f 2>/dev/null | sort)}")
if [ ${#decks[@]} -eq 0 ] || [ -z "${decks[1]}" ]; then
    echo "   MISSING: nessun deck trovato sotto spice/*/tb/" >&2
    report "testbench device citations resolve" 1
else
    out=$(/usr/bin/python3 "$ROOT/scripts/check_deck_refs.py" "$ROOT" "${decks[@]}" 2>&1)
    rc=$?
    echo "$out"
    report "testbench device citations and block contact nodes resolve" $rc
fi
echo

echo "-- 2h. what a testbench says it simulates is what its includes simulate --"
# From L22 to L33 fifteen decks called the simulated LSK489 a vendor model
# (NC-031). It is LSK489X, a hand-written placeholder with KF=0, and no deck
# includes models/jfet/lsk489.lib. Every number was right; what a reader
# believed about the numbers was not, and nothing compared a header comment
# with the includes written under it. The criterion is the dossier's own
# provenance(), imported. Made to fail on the 15 decks of main and on
# sabotaged copies: see docs/preamp/data/2026-09-15/L33/.
if [ ${#decks[@]} -eq 0 ] || [ -z "${decks[1]}" ]; then
    echo "   MISSING: nessun deck trovato sotto spice/*/tb/" >&2
    report "testbench provenance claims match their includes" 1
else
    out=$(/usr/bin/python3 "$ROOT/scripts/check_deck_provenance.py" "$ROOT" "${decks[@]}" 2>&1)
    rc=$?
    echo "$out"
    report "testbench provenance claims match their includes" $rc
fi
echo

echo "-- 2i. no canonical deck and no generated block simulates a placeholder model --"
# L39 (NC-017): the gain block and every deck of spice/*/tb/ moved from the
# hand-written models of spice/preamp/placeholder_devices.lib to the
# manufacturer models of models/. The library stays, because the dated decks
# under docs/preamp/data/ include it; nothing else would stop a copied header
# or a retyped model name from bringing a placeholder back, and ngspice would
# simulate it without a word. Until L39 this block checked the JFET variant of
# scripts/derive_jfet_variant.py (L20), retired now that the generated block
# names LSK489A itself. Made to fail on main before L39 (49 findings) and on
# 7 sabotaged copies: see docs/preamp/data/2026-09-22/L39/sabotaggi/.
out=$(/usr/bin/python3 "$ROOT/scripts/check_no_placeholders.py" "$ROOT" 2>&1)
rc=$?
echo "$out"
report "no canonical deck or generated block simulates a placeholder" $rc
echo

echo "== run_tests.sh SUMMARY: $n_pass passed, $n_fail failed =="
exit $fail
