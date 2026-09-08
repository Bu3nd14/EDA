# Limitations

These are documented as found — none of them are softened, and none of them
should be reproduced as "planned fixes" unless the orchestrator explicitly
asks for a roadmap section (this file has none).

## 1. Two-interpreter split

SKiDL runs on the project venv, Python 3.13
(`/Users/roberto/EDA/env/venv/bin/python3`). `pcbnew` and `kinet2pcb` run
**only** on KiCad's bundled Python 3.9
(`/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9`).
Any script touching both must bridge explicitly with absolute interpreter
paths. A naive `venv/bin/python -c "import pcbnew"` fails with
`ModuleNotFoundError`.

## 2. SKiDL's native SPICE path does not work with KiCad-library parts

`generate_netlist(tool="spice")` errors with "Part has no SPICE model"
because parts created via `Part("Device", "R")` lack the `.pyspice`
attribute that only `skidl.pyspice`-namespace parts carry. You cannot drive
both the KiCad-schematic path and SKiDL's SPICE path from one shared set of
`Part` objects. **Workaround used**: export the schematic, then run
`kicad-cli sch export netlist --format spice` on it.

## 3. SKiDL drops `Sim.Type`/`Sim.Device` when caching symbols

When SKiDL caches library symbols into the generated `.kicad_sch`, it drops
the `Sim.Type` and `Sim.Device` fields, keeping only `Sim.Params`. This
silently produces an **invalid SPICE source line** — not an error, a wrong
answer. The caller must manually set `Sim.Type` and `Sim.Device` in addition
to `Sim.Params` on any `Simulation_SPICE` part. This is flagged strongly
because it fails silently rather than raising.

## 4. SKiDL-generated schematics do not pass real KiCad ERC

Confirmed on the smoke-test fixture
(`smoke/rc_circuit_erc.json`): one `error`-severity
`power_pin_not_driven` violation on the GND power-input pin (SKiDL's
internal `Net.drive = POWER` does not insert an actual KiCad power
symbol/PWR_FLAG into the schematic), plus 3 `warning`-severity
`lib_symbol_mismatch` violations (SKiDL's symbol caching is lossy — R, C,
and VPULSE symbols all reported as not matching their library copies).

## 5. SKiDL's schematic auto-placement is visually unusable

Components overlap/are crammed together. The generated schematic is
machine-valid (KiCad parses and plots it — confirmed via
`kicad-cli sch export svg`) but not human-presentable as-is.

## 6. SKiDL requires version-numbered env vars

SKiDL 2.3.0's default tool constant is `KICAD10`, so it needs
`KICAD10_SYMBOL_DIR` / `KICAD10_FOOTPRINT_DIR` set (not `KICAD9_*`).
Setting the wrong version produces a confusing
`FileNotFoundError: Can't open file: Device.` with no indication the env
var name is the actual problem.

## 7. SKiDL treats a missing footprint as a hard error even for simulation-only symbols

A pure-stimulus source (e.g. the `Simulation_SPICE` `VPULSE` part in the
smoke fixture) needed a placeholder footprint assigned just to pass netlist
generation, even though it will never be physically placed as designed.

## 8. `item.GetLayerName()` in pcbnew is unreliable

Observed returning `"F.Cu"` for a zone genuinely on `"B.Cu"`. Use
`board.GetLayerName(item.GetLayer())` or `item.IsOnLayer()` instead.

## 9. `ImportSpecctraSES` gives no error message on failure

It returns only `True`/`False`. A malformed `.ses` file (e.g. wrong
coordinate unit scale) fails silently with no diagnostic.

## 10. ngspice batch-mode gotchas

- No native `.step` directive — use a `.control` block with a `foreach` +
  `alterparam` loop instead.
- `.temp` with a multi-value list **silently falls back to 27°C**, emitting
  only a warning. Use `dc TEMP start stop step` inside `.control` for a real
  temperature sweep.
- `.lib <file>` fails for plain model files with no `.lib`/`.endl` section
  markers — use `.include` instead.
- `C` and `L` do not accept a positional model name the way `R` does. `R`
  supports `Rxxx n1 n2 <value> <model>`; `C`/`L` require
  `Cxxx n1 n2 <model> C=<value>` / `Lxxx n1 n2 <model> inductance=<value>`
  (verified against ngspice 47's own `devhelp capacitor` / `devhelp
  inductor` output).
- The **first line** of any `.cir` file is always treated as a
  title/comment, regardless of content.

## 11. Model-validation coverage is uneven

`scripts/validate_models.py`'s R/C/L/transformer/opamp checks are exact
analytic cross-checks (closed-form theory vs. simulated result). The
BJT/MOSFET/JFET checks are **order-of-magnitude sanity checks only** — this
is weaker evidence and is called out explicitly rather than presented as
equivalent rigor.

## 12. GUI-only KiCad features are untested

Interactive-router and other GUI-only KiCad features were **not** tested in
this environment and must not be claimed as scriptable. Everything
documented as "working" in `README.md` was exercised via CLI or the
`pcbnew` Python API, non-interactively.

## 13. Le stringhe di valore KiCad non sono SPICE-safe, e il fallimento è silenzioso

Scoperto durante la Fase 2 del preamplificatore.

`"1M"` in una libreria KiCad significa **1 megaohm**. La stessa stringa
passata a ngspice significa **1 milliohm** — in SPICE il suffisso `M` è
"milli" e "mega" si scrive `MEG`. Sei ordini di grandezza, senza alcun
errore da nessuna delle due parti.

Un esportatore che passi il valore verbatim dal `Part` SKiDL alla
netlist SPICE propaga l'errore in silenzio. Nel caso osservato la
resistenza d'ingresso da 1 MΩ è diventata 1 mΩ, e **il difetto è rimasto
invisibile a lungo**: `.op`, sweep in continua e guadagno d'anello
pilotano tutti l'ingresso da una sorgente a bassa impedenza, quindi non
se ne accorgono. È emerso solo al primo `.ac` con una impedenza di
sorgente realistica, che è tornato 63 dB più basso del previsto.

**Qualunque ponte SKiDL/KiCad → SPICE deve tradurre i suffissi, non
copiarli.** `circuits/preamp/spice_export.py` contiene una funzione
`spice_value()` che lo fa, con questa storia nel commento.

Il pericolo non è il singolo suffisso `M`: è che nessuno dei due
strumenti considera la stringa malformata, quindi non esiste un
messaggio d'errore da cercare.

## 14. `Net()` in SKiDL crea una rete nuova a ogni chiamata

`Net("VPLUS")` chiamata due volte non restituisce la stessa rete: ne
crea una seconda e **rinomina silenziosamente il duplicato**. Una
funzione che istanzia un sottocircuito e crea le proprie reti di
alimentazione al suo interno produce quindi un'alimentazione flottante
diversa per ogni istanza.

Rimedio: passare le reti condivise **come parametri** alla funzione del
sottocircuito, invece di crearle dentro. Vedi
`circuits/preamp/gain_block.py`.

## 15. SKiDL lascia detriti nella directory di lavoro

Ogni esecuzione scrive `<script>.erc`, `<script>.log` e
`<script>_sklib.py` nella cwd. Sono rigenerabili e vanno ignorati da
git — il `.gitignore` non li copriva (stessa lacuna già annotata in
`CLAUDE.md` per `skidl_REPL.*`), ora sì.
