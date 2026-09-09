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
- **Un'analisi ripetuta senza `destroy all` fa leggere a `setplot` il plot
  VECCHIO, e il numero stampato è sbagliato senza alcun errore.** Ogni
  analisi crea plot numerati progressivamente: due `noise` di fila
  producono `noise1`/`noise2` e poi `noise3`/`noise4`, quindi un
  `setplot noise2` dopo la seconda seleziona ancora la **prima**. Vale
  identico per `ac`/`tran`/`dc`, ed è insidioso perché il numero c'è, è
  plausibile, ed è quello della configurazione precedente.

  Trovato il 2026-09-09 in `spice/preamp/tb/tb_zout_psrr_noise.cir`, la
  cui riga "WORST CASE" riportava **1,676 µV** — cioè esattamente il
  valore "intrinsic" della riga sopra — invece di **5,697 µV**: un
  fattore **3,4** in meno sul rumore in uscita nel caso peggiore.

  Provato, non dedotto, su tre gambe: (1) `alter` funziona in quel deck,
  perché il `foreach` sopra dà numeri diversi per le due modalità; (2)
  `tb_noise_breakdown.cir`, che misura la **stessa** configurazione con
  `destroy all`, dà 5,696897e-06; (3) aggiungendo `destroy all` a una
  copia di scratch dello stesso deck la riga diventa 5,696896e-06, cioè
  coincide a sette cifre. Il rimedio è quindi verificato, non ipotizzato.

  **Corretto in L5** (2026-09-09): i due `destroy all` sono ora in coda al
  deck e la riga stampa 5,696896e-06. La correzione è stata misurata
  rieseguendo il deck contro una baseline presa prima della modifica: il
  diff dei due log tocca **esattamente due righe**, ed è la coppia
  `onoise_total`/`inoise_total` del caso peggiore.

- **Un `$var` dentro un nome di file `wrdata` non si chiude da solo, e il
  fallimento è SILENZIOSO.** ngspice fa entrare nel nome della variabile
  anche `.`, `-` e `_`, quindi `wrdata out_$rs.txt v(A)` cerca una
  variabile chiamata `rs.txt`, non la trova, la sostituisce con la stringa
  vuota e scrive un file chiamato **`out_`** — senza errore, senza
  warning, e con exit code 0. Le graffe **non** sono supportate: `${rs}`
  finisce nel nome letteralmente.

  Terminano il nome `"`, `+`, `%`, `:`, `!` — ma restano dentro il nome del
  file. La forma pulita è **due variabili adiacenti**, perché anche `$`
  termina il nome:

  ```
  set t = .txt
  foreach rs 1.5 430 2500
    wrdata out_$rs$t v(A)      -> out_1.5.txt, out_430.txt, ...
  end
  ```

  E `set` converte in numero ciò che sembra un numero: `set gm = 0db`
  memorizza `0`, `set mode = 1G` memorizza `1000000000`. Per tenere una
  stringa **va quotata**: `set gm = "0db"`.

  Misurato con una sonda in L5 su ngspice 47, non dedotto: la prima sonda
  ha prodotto `probe_` e `probe_0db_`, entrambi vuoti, prima che la forma
  `$rs$t` producesse i nomi giusti.

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

## 16. Il piazzamento automatico di uno schematico analogico leggibile non esiste

Ricercato e **provato**, non assunto. È una limitazione dello stato
dell'arte, non di KiCad né di questo ambiente — ed è la ragione per cui
la limitazione #5 (auto-piazzamento SKiDL inutilizzabile) non ha una
soluzione alternativa.

**Strumenti valutati, con l'esito reale:**

| Strumento | Esito |
|---|---|
| **ASG** 1.1.0 (`pip install asg`) | **Non parte.** Importa `segments_intersections` da `bentley_ottmann.planar`, funzione rimossa dall'API. Fissando versioni storiche: 7.3.0 non ce l'ha; scendendo a 3.0.0 la dipendenza transitiva `cfractions` **non compila su Python 3.13**. Strumento accademico del 2020 (WOSET), non manutenuto. In più nasce per l'output di **qflow**, cioè celle standard digitali, ed emette Xschem o EEschema legacy che KiCad 10 non legge. |
| **lcapy** 1.26 | **Non produce nulla in tempo utile.** Non legge SPICE ma un proprio dialetto: sono servite tre traduzioni separate solo per il parsing (i diodi non accettano il nome del modello, i transistor nemmeno, il suffisso `MEG` non è riconosciuto). Superato quello, il disegno è rimasto **al 100% di CPU per 4 minuti e 44 secondi su 44 componenti senza emettere un file**, ed è stato interrotto. Il suo auto-layout è pensato per circuiti da manuale, non per un amplificatore a tre stadi. |
| **netlistsvg** | Disegna da netlist JSON di **Yosys**: sintesi digitale. Non applicabile. Valutato da documentazione, non provato. |

**Perché è così, e perché non cambierà a breve.** Nel digitale il
piazzamento segue il flusso dei dati, che un algoritmo ricostruisce dalla
netlist. Uno schema analogico invece si legge grazie a **convenzioni che
codificano l'intenzione del progettista** — alimentazioni in alto e in
basso, segnale da sinistra a destra, massa verso il basso, uno specchio
di corrente disegnato *come* uno specchio perché lo si riconosca a colpo
d'occhio. Nessuna di queste informazioni è deducibile dalle connessioni.
È il motivo per cui in ogni EDA analogico si piazza a mano.

**Conseguenza operativa**: i disegni si fanno a mano, in codice, con
`schemdraw`. Il rischio che ne deriva — il disegno che diverge in
silenzio dal circuito — è **meccanizzato** da
`scripts/check_schematic.py`. Non si può piazzare in automatico, ma si
può verificare in automatico. Vedi `docs/architecture.md`.
