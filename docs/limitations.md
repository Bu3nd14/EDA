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

## 17. Un costruttore può pubblicare **due modelli della stessa parte**, e sceglierne uno sbagliato non dà errore

Scoperto in L8 sul THAT320 (`vendor/bjt_array/that/THAT320/300_Series_Macro_01.lib`).

THAT Corporation spedisce, nello stesso file, **due modelli SPICE dello
stesso dispositivo**:

| Modello | `RB` | Etichetta del costruttore |
|---|---|---|
| `QPNP_THAT_NS` | 25 | *Noise performance optimized* |
| `QPNP_THAT_HF` | 103,345 | *High frequency performance optimized* |

Ogni altro parametro è **identico**. Non c'è niente nel nome del file, né
nell'atto di fare `.include`, che costringa a scegliere consapevolmente:
si prende quello che capita, e ngspice non ha nulla da segnalare.

**Quanto costa sbagliare**, misurato alle condizioni di prova del
datasheet (V_CB = −10 V, I_C = −1 mA, 1 kHz, 25 °C):

| Modello | rumore riferito all'ingresso a 1 kHz | contro il datasheet (0,75 nV/√Hz tip.) |
|---|---|---|
| `QPNP_THAT_NS` | **0,768 nV/√Hz** | +2,4% |
| `QPNP_THAT_HF` | **1,314 nV/√Hz** | **+75%** |

**Regola operativa**: una cifra di rumore e una di stabilità prese dallo
**stesso** modello non possono essere entrambe giuste. Quale modello è
stato usato va scritto **accanto al numero**, non lasciato al file.

**E il corollario che morde di più**: nessuno dei due porta `KF`/`AF`,
quindi **non c'è rumore 1/f**, come nei segnaposto. Provato empiricamente
e non con un `grep`: lo spettro simulato è piatto alla **nona cifra
significativa** da 100 Hz a 100 kHz. È lo stesso pavimento senza flicker
già annotato per `spice/preamp/placeholder_devices.lib`, e stavolta cade
proprio dove l'analisi dice che il rumore è dominante — lo specchio di
corrente.

## 18. Su alcuni siti di costruttori **HTTP 200 non significa che il file esista**

Scoperto in L8 su `www.onsemi.com`.

Quel sito risponde **200 con la stessa pagina HTML da 303 722 byte** per
*qualunque* percorso inesistente. Verificato su tre URL inventati diversi:
identico conteggio di byte, identico `Content-Type: text/html;charset=UTF-8`.
La prima richiesta di un datasheet in L8 è caduta esattamente lì —
`.../2N5551-D.PDF` è tornato 200 e conteneva HTML.

```sh
curl -sS -L -o /dev/null -w '%{http_code} %{content_type} %{size_download}\n' \
  https://www.onsemi.com/pub/Collateral/2N5551.LIB
# 200 text/html;charset=UTF-8 303722   <- il file NON esiste
```

**Regola operativa**: un codice di stato non è una verifica. Si controlla
il `Content-Type` **e** la dimensione, e per un PDF si apre il file
(`file`, `pdfinfo`). È la stessa regola che il repo applica già ai
modelli — «un modello SPICE è verificato se ngspice lo carica, non se il
link esiste» — spinta un passo più indietro, fino al trasporto.

Un secondo effetto, indipendente: **falsificare lo user-agent peggiora le
cose**. Con un UA Safari plausibile onsemi risponde **403** agli stessi
URL che serve senza problemi allo user-agent di default di curl.

## 19. Il prefisso **micro** non sopravvive all'estrazione dai PDF di onsemi: un limite letto meccanicamente è sbagliato di **1000×**

Scoperto in L24 leggendo il datasheet del 1N4148
(`vendor/diodes/onsemi/1N4148/1n914-d.pdf`).

`pdftotext` rende il glifo **µ** di questi documenti come la lettera
**m**. Non emette alcun avviso, esce 0, e il testo risultante è
perfettamente plausibile: `IC = 100 mA` invece di `IC = 100 µA`.

**Provato con le due letture indipendenti di ADR-013, non dedotto.** Il
render della pagina mostra «Pulse Width = 1.0 **μ**s»; l'estrazione
meccanica della stessa riga restituisce «Pulse Width = 1.0 **m**s».

```sh
/opt/homebrew/bin/pdftocairo -png -r 200 -f 2 -l 2 1n914-d.pdf pag2   # guardala
/opt/homebrew/bin/pdftotext  -layout 1n914-d.pdf - | grep 'Pulse Width'
```

**È una proprietà della toolchain documentale di onsemi, non di poppler.**
Contando il glifo estratto su documenti già nel repo:

| Documento | occorrenze di «µ» |
|---|---|
| `1n914-d.pdf` (onsemi) | **0** |
| `mje15032-d.pdf` (onsemi) | **0** |
| `2n5551t-d.pdf` (onsemi) | **0** |
| `LSK489DSRevA38.pdf` (Linear Systems) | **11** |
| `MMBT5401.pdf` / `MMBT5551.pdf` (Diodes) | 4 / 8 |

**Il dettaglio che lo rende pericoloso: il prefisso *nano* sopravvive.**
Nel 2N5551 le righe `50 nA` escono corrette e le righe in microampere no,
quindi un controllo a campione su una riga qualsiasi può concludere che
l'estrazione è a posto.

Le tre righe colpite in quel documento, già congelato in L8:

| Riga | Il PDF | `pdftotext -layout` |
|---|---|---|
| V(BR)CBO | I_C = **100 μA** | `IC = 100 mA` |
| V(BR)EBO | I_E = **10 μA** | `IE = 10 mA` |
| I_CBO @ 100 °C | 50 **μA** | `50 mA` |

Nessuna di queste è fra le cifre che L8 aveva registrato, e la riga che L8
*ha* registrato — V(BR)CEO a **I_C = 1,0 mA** — è **corretta**, verificata
sul render. Il `PROVENANCE.json` congelato non è stato riscritto.

**Regola operativa**: da un PDF onsemi, qualunque limite di corrente
sotto il milliampere va **guardato**, non estratto. È la stessa disciplina
di ADR-013 — due letture indipendenti che devono coincidere — applicata a
un caso in cui basta guardarne una.

## 20. Un costruttore può servire, sotto il nome della tua parte, il modello di **un'altra parte**

Scoperto in L24 sul 1N4148.

```sh
curl -sSL -o - https://www.onsemi.com/download/models/lib/1n4148.lib | grep SUBCKT
# .SUBCKT 1N4148WT 2 1
```

L'URL porta il nome della parte, risponde `200 application/octet-stream`,
restituisce un file **vero** di 1189 byte — e dentro c'è il **1N4148WT**,
la variante **SOD-323**, non il DO-35 che il progetto usa. Lo stesso file
è servito byte-identico anche come `1n4148wt.lib`, il che conferma che è
un alias e non un errore di battitura del server.

ngspice lo carica **senza una parola** e simula un altro dispositivo.

Il modello giusto sta in un file che porta il nome di **un'altra parte
ancora**, e lo dichiara nella propria intestazione:

```
** Product: 1N/FDLL914/A/B / 916/A/B / 4148 / 4448
** Package: DO-35 / LL-34
```

**Come si risolve, e la risposta era sul sito del costruttore**: la pagina
prodotto del 1N4148 di onsemi linka **un solo** datasheet, ed è
`1n914-d.pdf`. È onsemi stessa a schedare il 1N4148 sotto il documento
1N914.

```sh
grep -o '/download/data-sheet/pdf/[a-z0-9-]*\.pdf' <pagina-prodotto-salvata> | sort -u
```

**Regola operativa**: un modello scaricato si apre e si legge
l'intestazione **prima** di congelarlo, e il nome del dispositivo dentro
il file deve corrispondere alla parte — package compreso. È la lezione di **L7**
(`docs/preamp/reports/2026-09-09-L7-controllo-incrociato-lsk489.md`: il
nome di un file non è la sua **revisione**) spostata di un livello — qui
il nome di un file non è la sua **parte** — e fallisce nello stesso modo,
cioè in silenzio.

## 21. Su `diodes.com` il percorso di un modello SPICE è deciso **solo dall'id**: il nome del file nell'URL è ignorato

Scoperto in L22 cercando il modello del DMMT5401.

I modelli SPICE di Diodes stanno su
`https://www.diodes.com/spice/download/<id>/<PARTE>.spice.txt` (scoperta di
L24). Il segmento `<PARTE>` **non viene controllato**: si può scriverci
qualunque nome e il server restituisce comunque il file a cui punta l'id,
con `200` e una dimensione plausibile.

```sh
curl -sS -L -D - -o /dev/null \
  https://www.diodes.com/spice/download/2587/DMMT5401.spice.txt
# 200 ... content-type: text/plain; name="MMBT5401.spice.txt"
```

L'id 2587 è quello del **MMBT5401**, registrato in questo repo da L24. La
richiesta chiede `DMMT5401` e riceve `MMBT5401` — 1609 byte, un file vero,
nessun errore. Il modello del DMMT5401 sta all'id **3323**.

**Dove sta la verità**: nel `Content-Type` della risposta, che porta
`name="..."` con il nome vero, e nel `Content-Disposition` quando c'è. Non
nell'URL che hai scritto tu.

È la limitazione **#20** spostata di un passo indietro. Là il costruttore
serviva la parte sbagliata sotto un nome giusto (`1n4148.lib` conteneva
`1N4148WT`); qui è **chi richiede** a poter mettere nell'URL un nome che il
server non verifica — e il fallimento ha la stessa forma, cioè un file vero
di un'altra parte, senza un errore da nessuna parte.

**Regola operativa**: dopo ogni download da un percorso con un id, si
confronta il nome dichiarato dalla risposta con la parte cercata, **e** si
apre il file per leggerne l'intestazione (#20). Due controlli, perché
falliscono in modo diverso.

## 22. Una rinumerazione rompe i deck in silenzio, in due modi, e ngspice esce 0 in entrambi

Scoperto in L10, facendo la baseline dei deck prima di rinumerare.

**Primo modo — il nome non esiste più.** Dentro un blocco `.control`,
`alter r138 = 1e12` o `print @q133[ic]` su un dispositivo che non c'è
stampano

```
Error: no such device or model name r138
```

e l'esecuzione **prosegue ed esce 0**. `run_simulation.sh` riporta
`ngspice rc=0`. Così, dopo lo scarto di −1 di L22,
`tb_switch_v2_counterfactual.cir` ha smesso di aprire R_f: lo stato «anello
aperto» era identico allo stato chiuso (−0,0522 V invece di −13,7 V).

Rimedio meccanico: `scripts/check_deck_refs.py`, blocco **2g** di
`run_tests.sh`.

**Secondo modo — il nome esiste, ma è un altro dispositivo.** È il peggiore,
e **nessun controllo di esistenza lo vede**. Dopo L22 `tb_bias_sweep.cir`
continuava a spazzare `r130`, che era diventato l'**altro** ramo del
moltiplicatore di Vbe: I_q 5,2 mA invece di 14,7, nessun errore.

L31 ne ha trovati altri tre, in `tb_noise_vectors.cir`. La riga `wrdata` di L4
citava `onoise_q122`, `onoise_r120` e `onoise_r138` per il diodo dello specchio,
la sua degenerazione e R_f. Dopo L22 e L10 quei nomi erano il VAS, l'**altra**
degenerazione e R_g, e il 2g esteso ai vettori di rumore li passa: sono vivi. Li
ha mostrati solo la mappa per nodi dall'include di L4 a quello di oggi
(`data/2026-09-15/L31/esplorazione/mappa.txt`). Il deck non scriveva dati per
via dei quattro nomi morti accanto: senza quelli, i tre sbagliati avrebbero
scritto colonne plausibili sotto l'etichetta sbagliata.

**Regola operativa**: una rinumerazione si fa (a) ricavando la mappa dai nodi,
(b) portando **prima** ai nomi correnti ogni riferimento rimasto indietro, e
solo dopo applicando la mappa nuova — applicata alla cieca, una mappa può
trasformare un nome morto in un nome vivo sbagliato — e (c) confrontando i
numeri dei deck prima e dopo. Il controllo del punto (c) è l'unico che vede il
secondo modo.

## 23. SKiDL non sceglie il nome di una net fusa in modo riproducibile

Scoperto in L10.

Quando due net vengono unite (`b["IN"] += att_wiper`), la net risultante
prende **uno** dei due nomi, e quale dipende dall'esecuzione, non dal codice.
Due rigenerazioni consecutive di `preamp_audio.py`, senza toccare nulla:

| run | nomi diversi rispetto alla netlist di prima |
|---|---|
| 1 | `L_ATT_W→BL_IN`, `R_ATT_W→BR_IN`, `R_FIXJACK1→R_FIXOUT1` |
| 2 | `AR_OUT→R_ATT_TOP`, `R_ATT_W→BR_IN` |

I membri delle net sono identici. È una ragione in più, oltre a quella di L3b
(`date`, `tstamps`), per cui **un `.net` non si confronta con `diff`**, e un
confronto che abbina le net per **nome** fallisce o, peggio, abbina male.

**Regola operativa**: nessun controllo deve dipendere dal nome di una net che
nasce da un'unione. I nomi scelti esplicitamente e mai uniti (`GND`, `VPLUS`)
sono stabili; il 2e si appoggia solo a `GND` per questo.

## 24. Un deck che include `gain_block_flat.inc` condivide i nomi dei nodi del blocco, e una collisione non dà errore

Scoperto in L17.

`gain_block_flat.inc` mette i dispositivi del blocco **a livello superiore**,
non dentro un `.subckt`: serve, perché i deck d'anello devono poter fare
`alter r109`. Ma anche i **nodi** del blocco stanno a livello superiore —
`SRC`, `IN`, `OUT`, `FB`, `G1`, `G2`, `S1`, `NX`, `NREF`… — e un nodo del deck
con lo stesso nome **si collega** al blocco.

`tb_loop_bufferfissa.cir` alla prima esecuzione chiamava `SRC` il nodo del
generatore d'ingresso. Nel blocco `SRC` è la sorgente comune della coppia
JFET: il generatore da 0 V cortocircuitava la coda. ngspice ha risolto il
circuito senza un avviso e ha dato:

| | con la collisione | corretto |
|---|---|---|
| guadagno d'anello a 10 Hz | 22,25 dB | 72,30 dB |
| attraversamento | 76 MHz | 1,00 MHz |
| margine di fase, a vuoto | 105,85° | 69,31° |

Un margine **migliore** di quello vero, cioè il verso in cui nessuno va a
controllare. `check_deck_refs.py` non lo vede: controlla i **dispositivi**
citati, non i nodi.

**Regola operativa**: in un deck che include `_flat.inc`, i nodi propri hanno
nomi che il blocco non usa (`VSRCN`, non `SRC`), e un anello si confronta col
guadagno a bassa frequenza noto (~72 dB) prima di leggerne il margine. Coi
`.subckt` il problema non esiste: i nodi interni sono privati.

## 25. Il secondo passaggio di `run_simulation.sh` sovrascrive una tabella `echo` che ha il nome di un `wrdata`

Scoperto in L17.

Il secondo passaggio converte ogni `<nome>.txt` prodotto dall'esecuzione in
`<nome>.csv` e `<nome>.json`, **sovrascrivendo** ciò che c'è. Un deck che
scrive con `echo ... > tb_x_zout.csv` una tabella di riepilogo **e** con
`wrdata tb_x_zout.txt` la curva perde la tabella in silenzio: al suo posto c'è
la conversione della curva, con intestazione `col0,col1,…`. È successo a
`tb_uscite_fisse.cir`.

**Regola operativa**: le tabelle scritte da `echo` hanno un nome che nessun
`wrdata` dello stesso deck produce (`tb_uscite_fisse_e4.csv` accanto a
`tb_uscite_fisse_zout.txt`).

## 26. Una `meas tran` su una `tran` con `tstart` può fallire in silenzio, e la tabella `echo` esce con celle vuote

Scoperto in L12.

Un deck di slew rate faceva `tran 20n 1m 0.5m 20n` e poi
`meas tran vomax max v(out) from=0.5m to=1m`. ngspice ha stampato
«ft_polyfit @ 240034 failed» e ha lasciato le variabili **non definite**:
- `echo $&vpp_pos` dà «Error: &vpp_pos: no such variable»;
- le colonne della tabella escono vuote;
- ngspice esce **0**, e nella stessa esecuzione la `fourier` funziona.

**Il rimedio usato**: `tran` senza `tstart`, con la finestra della `meas` dentro
l'intervallo simulato. Anche `deriv()` emette gli stessi avvisi sui punti di
rottura delle sorgenti PULSE, ma lì le misure escono. La verifica è che la
tabella non abbia celle vuote e che un numero noto torni: in L12 lo slew in
salita contro I_coda/C124, entro il 3 %.

**Regola operativa**: in un deck con `meas`, contare le righe `Error:` del log e
le celle vuote della tabella. L'exit code non basta.

## 27. Un nodo del blocco lasciato su un solo terminale non dà errore, e il deck misura un altro circuito

Scoperto in L27.

L27 ha dato al blocco un secondo nodo di contatto del relè, `RG10`, che nel
blocco tocca un solo terminale (R143). Un deck scritto per un solo contatto non
lo collega a niente. **ngspice non se ne accorge**: un nodo appeso a una sola
resistenza non rende la matrice singolare, segue il nodo all'altro capo.
Misurato sui deck di `main` con l'include nuovo:
- `tb_op.cir`: rc 0, 87 valori, uno solo diverso alla sesta cifra;
- `tb_ac.cir`: la modalità «10db» chiudeva solo il vecchio contatto e ha
  stampato **+3,037 dB** invece di +9,949, sotto un nome di file che dice ancora
  10db.

La forma generale: **ogni nodo esterno che un blocco generato lascia su un solo
terminale è un contatto**, e un deck che non lo termina simula il contatto
aperto e senza la sua capacità parassita, qualunque cosa dica l'etichetta.

**Rimedio meccanico**: `scripts/check_deck_refs.py`, blocco **2g**. Ricava i nodi
pendenti dall'intestazione «External nodes» dell'include flat e dal corpo dei
`.subckt`, e rifiuta un deck che non li collega o una riga `X` col numero
sbagliato di porte. Fatto fallire sui 16 deck di `main`.

**Cosa non vedeva**, fino a L31: i nomi dei vettori di rumore
(`onoise_<dispositivo>`), che un deck costruisce da sé. Un nome morto in un
`wrdata` dà `Error: no such vector`, ferma il `wrdata` e l'esecuzione esce 0:
`tb_noise_vectors.cir` non ha scritto dati da L22 a L31 (NC-030). Da L31 il 2g
controlla ogni `onoise_<x>`/`inoise_<x>` fuori da commenti e stringhe fra
virgolette: `<x>` deve essere un vettore del circuito (`spectrum`, `total`), un
nome definito con `let`, un dispositivo, o un dispositivo più un suffisso di
sotto-sorgente che ngspice costruisce davvero. I suffissi sono letti da un deck
sonda, perché nel log i nomi sono troncati a 15 caratteri (`d102_ids` è
`d102_idsw`). Fatto cadere sul deck di allora (4 nomi morti) e su 13 casi di
sabotaggio, senza falsi allarmi sui deck di `main` e su quelli pre-L27.

**Cosa non vede ancora**: un vettore di rumore **vivo ma sbagliato**, come i tre
che L31 ha trovato (#22).

## 28. Un'impedenza misurata per iniezione con la sorgente AC ancora accesa somma il segnale, e non dà errore

Scoperto in L13.

Una Zout si misura iniettando 1 A AC nel nodo e leggendo la tensione: è
un'impedenza solo se **ogni altra sorgente AC è spenta**. La sezione Zout di
`tb_zout_psrr_noise.cir`, dal 2026-09-09 a L13, accendeva l'iniezione e
lasciava `VSRC` a 1 V AC. ngspice non se ne accorge: il circuito è lineare, le
due risposte si sommano, rc 0. Il dossier ha pubblicato quei numeri per E4.

La firma sta nei numeri, se si guardano:
- al nodo d'uscita del blocco, prima dei 47 Ω, `za1k` valeva **1,0355 /
  1,4704 / 3,2621 Ω** a 0 / +3 / +10 dB. È il guadagno del modo per 1 V, piatto
  in frequenza. Il nodo di un buffer identico, a sorgente spenta, dà 0,0386 Ω;
- al jack il segnale si nasconde: 58,76 Ω invece di 57,94, perché lì domina la
  47 Ω.

**Il gemello, dal lato opposto** (L13, sabotaggio `c0`): un controllo positivo
`vdb(nodo)` su un nodo dove il segnale è **zero esatto** non dà −∞. Dà
`Error: argument out of range for db`, la `meas` non esiste e la cella della
tabella esce vuota, con rc 0. È il #26 con un'altra causa.

**Regola operativa.**
- In una sezione d'impedenza, `alter @<sorgente>[acmag] = 0` per ogni sorgente
  AC, prima della prima `ac`, e rimetterla dopo.
- Accanto a una Zout al jack si legge anche la Zout **al nodo del blocco**: se
  scala col guadagno, dentro c'è segnale.
- Un controllo che deve dire «la manopola arriva al blocco» si fa col
  **guadagno**, a iniezione spenta. Una Zout costante da sola non lo prova,
  perché un attenuatore scollegato la darebbe identica.
