#!/bin/zsh
# End-to-end smoke-test pipeline runner for the RC lowpass fixture.
# Re-run the whole thing from scratch with:
#   zsh /Users/roberto/EDA/smoke/run_pipeline.sh
set -e

SKIDL_PY=/Users/roberto/EDA/env/venv/bin/python3
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
KICAD_CLI=/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli
SMOKE=/Users/roberto/EDA/smoke
FREEROUTING_JAR=/Users/roberto/EDA/scripts/tools/freerouting.jar

cd "$SMOKE"

echo "== 0. one-time bridge setup (kinet2pcb into KiCad's bundled python3.9) =="
$KICAD_PY -m pip install --user kinet2pcb   # no-op if already installed

echo "== 1-6. SKiDL: circuit def, ERC, KiCad+SPICE netlists, schematic =="
$SKIDL_PY rc_circuit.py

echo "== 2b. Verify schematic parses in real KiCad (SVG render + ERC) =="
rm -rf rc_circuit_sch.svg rc_circuit_erc.json
$KICAD_CLI sch export svg --output rc_circuit_sch.svg rc_circuit.kicad_sch
$KICAD_CLI sch erc --format json --exit-code-violations --output rc_circuit_erc.json rc_circuit.kicad_sch || true

echo "== 3. SPICE netlist via kicad-cli (SKiDL's own SPICE path fails - see report) =="
$KICAD_CLI sch export netlist --format spice --output rc_circuit_kicad_spice.cir rc_circuit.kicad_sch

echo "== 4-5. Simulate with ngspice: transient (tau check) + AC (fc check); extract CSV/JSON =="
python3 - <<'PYEOF'
with open("rc_circuit_kicad_spice.cir") as f:
    lines = [l for l in f if not l.strip().lower().startswith(".end")]
with open("rc_tran.cir", "w") as f:
    f.writelines(lines)
    f.write(".tran 100n 2m\n.control\nrun\nwrdata rc_tran_out.txt v(vin) v(out)\nquit\n.endc\n.end\n")
PYEOF
/opt/homebrew/bin/ngspice -b rc_tran.cir
/opt/homebrew/bin/ngspice -b rc_ac.cir
$SKIDL_PY extract_results.py

echo "== 7. PCB creation from KiCad netlist via kinet2pcb (bundled python3.9) =="
$KICAD_PY -c "
import kinet2pcb
kinet2pcb.kinet2pcb('rc_circuit.net', 'rc_circuit.kicad_pcb',
    fp_lib_dirs=['/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints'])
"

echo "== 9. Placement =="
$KICAD_PY place_components.py

echo "== 10. Routing: DSN export -> Freerouting -> SES import =="
$KICAD_PY route_board.py export
PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar "$FREEROUTING_JAR" \
  -de rc_circuit.dsn -do rc_circuit.ses -mp 1 -l en
$KICAD_PY route_board.py import

echo "== 12. DRC =="
$KICAD_CLI pcb drc --format json --exit-code-violations --output rc_circuit_drc.json rc_circuit_routed.kicad_pcb || true

echo "== 13-14. Gerbers + drill =="
mkdir -p gerbers
$KICAD_CLI pcb export gerbers --output gerbers/ rc_circuit_routed.kicad_pcb
$KICAD_CLI pcb export drill --output gerbers/ rc_circuit_routed.kicad_pcb

echo "DONE. See rc_sim_summary.json, rc_circuit_erc.json, rc_circuit_drc.json, gerbers/ for evidence."
