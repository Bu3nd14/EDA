# EDA — Analog EDA + PCB Automation Environment

A scripted, non-interactive toolchain for taking an analog circuit from
code-first topology definition through SPICE simulation, KiCad schematic
generation, PCB layout, autorouting, DRC/ERC, and fabrication export —
on macOS / Apple Silicon.

This README documents only what has been verified by actually running
commands in this environment. See `docs/limitations.md` for the full
limitations list and `docs/smoke-test.md` for the end-to-end pipeline
evidence.

## Installed tools

| Tool | Version | Path | Notes |
|---|---|---|---|
| ngspice | 47 | `/opt/homebrew/bin/ngspice` | Native arm64 (`file` → "Mach-O 64-bit executable arm64", non-fat). Installed via `brew install ngspice`. |
| KiCad | 10.0.6 | App: `/Users/roberto/Applications/KiCad.app`; CLI: `/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli` | Universal binary (x86_64 + arm64), runs natively on Apple Silicon. Installed from the official CERN-hosted dmg into `~/Applications`, **without sudo**. |
| Python (project) | 3.13.15 | `/opt/homebrew/bin/python3.13` | Native arm64. Project venv at `/Users/roberto/EDA/env/venv`. |
| SKiDL | 2.3.0 | installed in `env/venv` | Code-first circuit definition layer. |
| Python (KiCad bundled) | 3.9.13 | `/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9` | The **only** interpreter where `import pcbnew` works. `pcbnew` is not pip-installable. |
| kinet2pcb | (per bundled install) | installed into the bundled python3.9 via `--user pip install` | Not installed in the venv. |
| Freerouting | 2.4.1 | `/Users/roberto/EDA/scripts/tools/freerouting.jar` | External autorouter. Needs a JRE (`brew install openjdk`). |

## Installation procedure (as actually done)

1. **ngspice**: `brew install ngspice`.
2. **KiCad 10.0.6**: download the official dmg from kicad.org and install into
   `~/Applications` **without sudo**.
   - **Pitfall (verified failure)**: the Homebrew cask (`brew install --cask kicad`)
     FAILS during install because its bundled `demos` artifact needs sudo to
     write to `/Library/Application Support/kicad`. Use the no-sudo dmg route
     instead — do not retry the brew cask expecting a different result.
3. **Python / venv**: `python3.13 -m venv /Users/roberto/EDA/env/venv`, then
   `pip install skidl` (→ SKiDL 2.3.0) inside that venv.
4. **kinet2pcb**: installed into KiCad's *bundled* python3.9, not the venv:
   ```
   /Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 -m pip install --user kinet2pcb
   ```
5. **Freerouting**: `freerouting.jar` placed at `scripts/tools/freerouting.jar`.
   Requires a JRE: `brew install openjdk`, then invoke with
   `PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar scripts/tools/freerouting.jar ...`.

## Architecture: selected stack and rejected alternatives

**Selected**: KiCad 10 + ngspice, with SKiDL as the code-first circuit
definition layer and Freerouting as an external autorouter.

| Alternative | Rejected because |
|---|---|
| LibrePCB | No SPICE export at all — structurally incompatible with a simulate-then-layout workflow. SKiDL also has no LibrePCB output path. |
| Qucs-S | No headless/CLI mode found. Usable only as an optional human-facing GUI visualization layer, not automation. |
| gEDA/gaf | Effectively dead (~1-2 commits/year, last stable release 2020). |
| Xyce | Kept only as a possible alternate SPICE backend. ngspice is the reference engine KiCad targets and has a faster release cadence. |

## Source-of-truth strategy

A hybrid model with a hard boundary:

- **Circuit topology** (parts, values, connections) is canonical in
  **Python/SKiDL**, intended to live under `circuits/*.py` (version-controlled,
  no GUI state). `TODO: unverified` — a `circuits/` directory does not yet
  exist in this repo; the only SKiDL topology definition currently present is
  the smoke-test fixture at `smoke/rc_circuit.py`.
- **Physical layout** (placement, routing, stackup) is canonical in the
  **`.kicad_pcb`** file, because layout cannot be expressed in SKiDL.
- The netlist is a **one-way sync contract**: code → KiCad. Never hand-edit
  the generated schematic/netlist and expect it to survive regeneration.
  Never treat the `.kicad_pcb` as a topology source.
- **Correction to the naive "SKiDL → SPICE" assumption**: the SPICE netlist
  used for simulation is derived from the *generated schematic* via
  `kicad-cli sch export netlist --format spice`, **not** from SKiDL's native
  SPICE generator. SKiDL's native SPICE path does not work with
  KiCad-library parts — see Limitations #2.

## Project structure

```
EDA/
  models/         curated, canonical SPICE models (.include-able), each with a
                  <file>.provenance.json sidecar. See models/README.md,
                  models/PROVENANCE_CONVENTION.md.
  vendor/         read-only vendor originals (mode 0444, sha256 + PROVENANCE.json
                  per part). Never hand-edited. See vendor/README.md.
  scripts/        automation entry points (setup, validation, simulation, ERC/DRC,
                  fab export) and support tools (freerouting.jar). Owned/maintained
                  separately — see "Scripts" below.
  testbenches/    standalone ngspice .cir testbenches (01_op .. 08_vendor_model)
                  used to exercise/validate analysis types and the model library.
  smoke/          scratch: the trivial RC-lowpass smoke-test fixture and its
                  full pipeline output (schematic, netlists, sim results, PCB,
                  routing, DRC/ERC reports, gerbers).
  pcb/            scratch: PCB-automation-engineer's capability tests
                  (board creation, DSN/SES routing round-trip, DRC, fab export).
  results/        scratch: simulation outputs (raw + normalized CSV/JSON) and
                  model-validation testbenches/results.
  docs/           this documentation set (architecture, limitations, smoke-test
                  report).
  env/venv/       project Python 3.13 virtualenv (SKiDL).
  .claude/agents/ subagent role definitions (see AGENTS.md).
```

`circuits/` (canonical topology home per the source-of-truth strategy) does
not exist yet — `TODO: unverified`, flagged rather than assumed.

`smoke/` and `results/` are scratch, not canonical; `models/`, `vendor/` are
canonical (see AGENTS.md operating rules).

## Simulation workflow

All ngspice runs are non-interactive (`ngspice -b`). Verified analysis types,
with existing testbenches under `testbenches/`:

| Testbench | Analysis |
|---|---|
| `01_op.cir` | `.op` |
| `02_dc.cir` | `.dc` sweep |
| `03_ac.cir` | `.ac` |
| `04_tran.cir` | `.tran` |
| `05_noise.cir` | `.noise` |
| `06_paramsweep.cir` | parameter sweep (via `.control`/`alterparam`, not native `.step` — see Limitations #10) |
| `07_temp.cir` | temperature sweep |
| `08_vendor_model.cir` | vendor-model `.include` |

Run directly, e.g.:
```
/opt/homebrew/bin/ngspice -b /Users/roberto/EDA/testbenches/04_tran.cir
```
Results are written via `wrdata`/`.print`/`.write` and normalized to
CSV/JSON with `scripts/normalize_wrdata.py` (present under `results/*.normalized.{csv,json}`).

**Accuracy**: verified against closed-form theory (RC -3dB point, RC time
constant, thermal noise floor) to well under 1% error. Example from the
smoke-test RC fixture (R=1k, C=100n): theoretical fc = 1591.55 Hz, simulated
fc = 1587.62 Hz, error 0.25%.

**Model library**: `models/` contains curated device models (resistor,
capacitor, inductor, diode, BJT NPN/PNP, MOSFET N/P, JFET, opamp macro-model,
generic transformer subckt), each validated by
`scripts/validate_models.py` against a real ngspice testbench (24/24 checks
passing at last verification). The R/C/L/transformer/opamp checks are exact
analytic cross-checks; the BJT/MOSFET/JFET checks are order-of-magnitude
sanity checks only, not exact — see Limitations #11. The validator was
proven to catch both a bad model parameter and a tampered vendor file
(exit 1 in both cases).

Vendor model provenance: `vendor/` holds read-only (mode 0444) originals with
sha256 + `PROVENANCE.json`; `models/` holds curated/derived copies, each with
a `.provenance.json` sidecar recording origin and any changes. See
`models/PROVENANCE_CONVENTION.md`.

## PCB workflow

Verified capabilities, driven through the `pcbnew` Python API (bundled
python3.9) and `kicad-cli`:

- Board creation; footprint load/place from KiCad standard libraries;
  footprint inspection; move/rotate with verified persistence; geometry/
  courtyard queries; net enumeration and assignment; track and via creation;
  copper zone creation with real fill; save/reload round-trip fidelity.
- **ERC**: `kicad-cli sch erc --format json --exit-code-violations` — real
  JSON output, correct exit codes.
- **DRC**: `kicad-cli pcb drc --format json --exit-code-violations` — real
  JSON, exit 5 on violations / 0 when clean. Verified semantically correct:
  flagged genuine unconnected items before routing, clean after.
- **Fabrication export**: `kicad-cli pcb export gerbers` and
  `kicad-cli pcb export drill` — verified by inspecting file contents (valid
  RS-274X and Excellon data), not just exit codes.
- **Routing**: KiCad itself has **no built-in autorouter**. Routing is done
  via an external round-trip:
  `pcbnew.ExportSpecctraDSN` → Freerouting CLI → `pcbnew.ImportSpecctraSES` →
  DRC clean (0 violations), verified end-to-end. Note `kicad-cli` does **not**
  offer DSN export — only the `pcbnew` Python API does.

Example Freerouting invocation (from `smoke/run_pipeline.sh`):
```
PATH="/opt/homebrew/opt/openjdk/bin:$PATH" java -jar /Users/roberto/EDA/scripts/tools/freerouting.jar \
  -de rc_circuit.dsn -do rc_circuit.ses -mp 1 -l en
```

GUI-only KiCad features (e.g. the interactive router) were **not** tested and
must not be assumed scriptable (Limitations #12).

## API/automation workflow: the two-interpreter bridge

SKiDL runs on the project venv, **Python 3.13**
(`/Users/roberto/EDA/env/venv/bin/python3`). `pcbnew` and `kinet2pcb` run
**only** on KiCad's bundled **Python 3.9**
(`/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9`).
Any script that touches both must bridge explicitly with absolute
interpreter paths — invoking each stage with its own interpreter, e.g. from
`smoke/run_pipeline.sh`:

```sh
SKIDL_PY=/Users/roberto/EDA/env/venv/bin/python3
KICAD_PY=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
```

`venv/bin/python -c "import pcbnew"` **fails** with `ModuleNotFoundError` —
this is not a configuration bug, it is the expected split. Never assume one
interpreter can do both halves of the pipeline.

## Scripts

Scripts live under `scripts/` (owned/maintained by a separate workflow —
see `AGENTS.md`). Confirmed present at time of writing:
`scripts/validate_models.py`, `scripts/freeze_vendor.sh`,
`scripts/normalize_wrdata.py`, `scripts/pcbnew_test.py`,
`scripts/specctra_roundtrip_test.py`, `scripts/tools/freerouting.jar`.

The following entry points are documented interface (purpose/invocation as
specified) — they were being written/verified concurrently with this
documentation, so their internals are not described here beyond intent:

| Script | Purpose |
|---|---|
| `scripts/setup.sh` | One-shot environment setup. |
| `scripts/verify_env.sh` | Verify installed tool versions/paths match what's documented. |
| `scripts/run_simulation.sh <netlist.cir> [outdir]` | Run an ngspice batch simulation and extract results. |
| `scripts/run_tests.sh` | Run the project's test/validation suite. |
| `scripts/validate_models.py` | Validate every model in `models/` against a real ngspice testbench; also checks provenance (`--check-provenance`). |
| `scripts/run_erc.sh <sch> [outjson]` | Run `kicad-cli sch erc` and emit JSON. |
| `scripts/run_drc.sh <pcb> [outjson]` | Run `kicad-cli pcb drc` and emit JSON. |
| `scripts/export_fab.sh <pcb> [outdir]` | Export gerbers/drill; **refuses to export if DRC fails.** |

`TODO: unverified` — confirm the final invocation syntax/flags of the above
against the actual script contents once they land; this table reflects the
interface as specified to this documentation task, not a read of the scripts
themselves (except `validate_models.py`, which already exists and is
described above from `models/README.md`).

## Limitations

Full detail in `docs/limitations.md`. Summary (none of these are soft-pedaled):

1. Two-interpreter split (SKiDL venv 3.13 vs KiCad bundled 3.9) — must bridge with absolute paths.
2. SKiDL's native SPICE path does not work with KiCad-library parts; the schematic→`kicad-cli sch export netlist --format spice` path is used instead.
3. SKiDL drops `Sim.Type`/`Sim.Device` when caching symbols into the generated `.kicad_sch` — silent invalid SPICE line unless set manually.
4. SKiDL-generated schematics fail real KiCad ERC (`power_pin_not_driven` on GND + 3 `lib_symbol_mismatch` warnings).
5. SKiDL's schematic auto-placement is visually unusable (machine-valid, not human-presentable).
6. SKiDL needs version-numbered env vars (`KICAD10_SYMBOL_DIR`/`KICAD10_FOOTPRINT_DIR` for SKiDL 2.3.0); wrong version → confusing `FileNotFoundError`.
7. SKiDL treats a missing footprint as a hard error even for simulation-only symbols.
8. `item.GetLayerName()` in pcbnew is unreliable — use `board.GetLayerName(item.GetLayer())` or `IsOnLayer()`.
9. `ImportSpecctraSES` gives no error message on failure — only True/False.
10. ngspice gotchas: no native `.step` (use `.control`/`alterparam`); multi-value `.temp` silently falls back to 27°C with only a warning (use `dc TEMP start stop step` inside `.control`); `.lib <file>` fails for plain model files (use `.include`); `C`/`L` need `C=`/`inductance=`, not a positional value; the first line of any `.cir` is always a title/comment.
11. BJT/MOSFET/JFET model checks in `validate_models.py` are order-of-magnitude sanity checks, not exact analytic cross-checks like R/C/L/transformer/opamp.
12. GUI-only KiCad features (e.g. interactive router) were not tested and must not be claimed as scriptable.

## Smoke test results

Trivial RC low-pass fixture (R=1k, C=100n), driven through the full pipeline
by `smoke/run_pipeline.sh`. **11 stages PASSED, 3 PARTIAL, 0 FAILED.**

| Stage | Verdict |
|---|---|
| Circuit definition | PASSED |
| Simulation | PASSED |
| Result extraction | PASSED |
| KiCad netlist generation | PASSED |
| PCB creation | PASSED |
| Footprint assignment | PASSED |
| Placement | PASSED |
| Routing | PASSED |
| DRC | PASSED |
| Gerber export | PASSED |
| Drill export | PASSED |
| Schematic generation | PARTIAL |
| SPICE netlist generation | PARTIAL |
| ERC | PARTIAL |

See `docs/smoke-test.md` for per-stage evidence (exact JSON/CSV values).

## Reproducing the tests

```sh
# Model library validation (24/24 checks)
/usr/bin/python3 /Users/roberto/EDA/scripts/validate_models.py

# Individual SPICE testbenches
/opt/homebrew/bin/ngspice -b /Users/roberto/EDA/testbenches/01_op.cir
/opt/homebrew/bin/ngspice -b /Users/roberto/EDA/testbenches/04_tran.cir
# ... etc. for 02..08

# Full smoke-test pipeline (schematic -> sim -> PCB -> routing -> DRC -> gerbers)
zsh /Users/roberto/EDA/smoke/run_pipeline.sh

# Vendor freeze re-enforcement (idempotent)
/Users/roberto/EDA/scripts/freeze_vendor.sh
```

## Further reading

- `docs/architecture.md` — architecture decision detail (selected stack,
  rejected alternatives, source-of-truth contract).
- `docs/limitations.md` — full limitations list with detail.
- `docs/smoke-test.md` — per-stage smoke-test evidence.
- `AGENTS.md` — subagent roster and delegation/operating rules.
- `models/README.md`, `models/PROVENANCE_CONVENTION.md`, `vendor/README.md` —
  model library and provenance conventions (owned by the scaffolding agent,
  read here for reference).
