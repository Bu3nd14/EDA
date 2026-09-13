# L14 — le tre correzioni di testo

Data: 2026-09-13 · Lotto: **L14** (XS) · Chiude: **NC-003**, **NC-006**,
**NC-007** (tutte minori)

**Il difetto comune**: tre punti in cui il repo diceva una cosa diversa da
quella che i suoi dati misurano. **Nessun numero del circuito è stato toccato e
nessuna misura è stata rifatta.** Il dossier legge ancora `data/2026-09-09/`,
cioè la topologia col THAT320, e questo lotto corregge *come* le cifre sono
presentate.

## 1. Baseline, prima di toccare

| Controllo | Esito |
|---|---|
| `build_dossier.py` rieseguito da HEAD `0f2f3c4`, senza modifiche | `OK: tutti i controlli incrociati`, `git status --porcelain` **vuoto**: la rigenerazione è riproducibile |
| `run_tests.sh` | **8 passed, 0 failed** |
| `spice/preamp/tb/tb_op.cir` rieseguito con `run_simulation.sh` | 81 righe `print`, **81 valori su 81 identici** a `data/2026-09-10/tb_op-LS352.log`. Cambiano solo i nomi di 47 righe, per la rinumerazione di L10 (`@jq110[id]` → `@jq110a[id]`, `@q118` → `@q117`, …) |

Quindi il log che descrive la topologia di oggi è **`tb_op-LS352.log`**, e non
il `2026-09-09/tb_op.log` citato da NC-006:

| Nodo | `2026-09-09/tb_op.log` (THAT320) | `2026-09-10/tb_op-LS352.log` | rieseguito 2026-09-13 |
|---|---|---|---|
| `v(ncasc)` | 9.886765 | **9.886582** | 9.886582 |
| `v(d1n)` | 9.208879 | **9.208604** | 9.208604 |
| `v(d2n)` | — | **9.209279** | 9.209279 |

## 2. NC-006 — `circuits/preamp/gain_block.py`

Righe 314-315 e 320-321, prima e dopo:

```
-    # Cascode base reference: 8.485 V from a ~1 mA divider off V+, heavily
-    # bypassed to ground so the JFET drains sit still while the rail moves.
+    # Cascode base reference (ADR-014): 4.99k/10.0k off V+, ~1 mA, bypassed so
+    # the drains sit still. v(ncasc) = 9.887 V: data/2026-09-10/tb_op-LS352.log
-    # Cascode transistors, common base: they hold the JFET drains at a fixed
-    # 7.8 V, which is what kills the Miller multiplication of C_rss.
+    # Cascode transistors, common base: they hold the JFET drains at 9.21 V
+    # (v(d1n)/v(d2n), same log), which kills the C_rss Miller multiplication.
```

La riga 153 («First draft used 8.485 V») è storia dichiarata e **resta**.

**La prova che il codice non è cambiato** sta nell'AST, che non contiene i
commenti:

| Controllo | Esito |
|---|---|
| righe HEAD / nuovo | 648 / 648 |
| righe diverse | 314, 315, 320, 321 |
| `ast.dump(ast.parse(HEAD)) == ast.dump(ast.parse(nuovo))` | **True** |
| stesso controllo su una copia con `R("10.0k", NCASC, GND)` → `"10.1k"` | **False**: il controllo fallisce quando deve |

Il numero di righe è rimasto lo stesso, quindi i `SKiDL Line` di
`gain_block.net` e `preamp_audio.net` puntano ancora alle righe giuste. Non è
stato rigenerato niente.

## 3. NC-007 — lo scarto ADR-014

Valori dai `print` di `data/2026-09-09/tb_ac.log`, gli stessi che `check()`
pubblica:

| Modalità | sorgente | g(1 kHz) | g(20 kHz) |
|---|---|---|---|
| 0 dB | 1,5 Ω | −8.49073e-03 | −8.30256e-03 |
| 0 dB | 2500 Ω | −3.01652e-02 | −2.99335e-02 |
| +10 dB | 1,5 Ω | 9.949078 | 9.933093 |
| +10 dB | 2500 Ω | 9.927404 | 9.911556 |

Da cui, con ogni scarto calcolato come «2500 Ω meno 1,5 Ω»:

| Modalità | scarto assoluto 1 kHz | scarto assoluto 20 kHz | **20 kHz riferito a 1 kHz** |
|---|---|---|---|
| 0 dB | −0,02167 dB | −0,02163 dB | **4,35·10⁻⁵ dB** |
| +10 dB | −0,02167 dB | −0,02154 dB | **1,37·10⁻⁴ dB** |

**Ricalcolo indipendente** dai CSV (`tb_ac_{0db,10db}_{1.5,2500}.csv`, per
interpolazione in log f, senza passare dai `print`): 4,352·10⁻⁵ e 1,370·10⁻⁴,
coincidenti. A 20 Hz, dai `print`, lo scarto assoluto vale −0,02167 dB in
entrambe le modalità: è una perdita di livello a banda larga.

**Cosa pubblica ora il dossier** (`build_dossier.py`, nuova funzione `adr014()`):

- **KPI**: «Scarto ADR-014 — 1,37·10⁻⁴ dB @ 20 kHz rif. 1 kHz · peggiore delle
  2 modalità». La scelta del peggiore, e non della sola modalità 0 dB come
  prima, è di questo lotto: un KPI che non dice che caso copre è esattamente
  NC-003.
- **Sezione 5**: la claim è enunciata come *forma* della risposta. La tabella
  ha tre colonne (scarto assoluto 1 kHz, scarto assoluto 20 kHz, 20 kHz
  riferito a 1 kHz) e un paragrafo dice che le prime due sono il partitore con
  la Zin, ci sarebbero anche senza cascode e **non misurano la claim**.
- **`dossier.summary.json`**: `adr014_scarto_20kHz_dB_0db` diventa
  `adr014_scarto_20kHz_rif_1kHz_dB_peggiore` più
  `partitore_sorgente_2500ohm_20kHz_dB_0db`. Nel repo nessuno legge il file.

**La seconda copia della cifra**: `data/2026-09-09/README.md` presentava anche
lui 0,022 dB come prova di ADR-014. Ha preso una nota datata L14 sotto la
tabella, e la tabella non è stata riscritta. L'executive summary del 2026-09-11
non cita nessuna delle due cifre (cercato con grep).

## 4. NC-003 — il margine di fase

`spice/preamp/tb/tb_loop.cir`, riga 38: «BLOCK B output network + cable».
Quindi i quattro `tb_loop_*` pubblicati sono tutti del blocco B, e lo si è
letto nel deck.

- **KPI**: «Margine di fase, blocco B — 56,945 gradi · peggiore dei 4 casi
  pubblicati».
- **Sezione 6**: si apre dicendo che i dati d'anello sono tutti del blocco B e
  che il blocco A non è pubblicato (NC-002, L12), quindi il caso peggiore non è
  quello del prodotto. Nessuna cifra del blocco A entra nel dossier, perché non
  è nei dati.
- «Il caso peggiore fra questi quattro casi **del blocco B**», riga V1
  qualificata, titolo di `fig_loop.svg` con «blocco B».

## 5. Il prodotto, letto

`build_dossier.py` rieseguito: `OK: tutti i controlli incrociati CSV vs log sono
passati.` File cambiati: `build_dossier.py`, `index.html`, `fig_loop.svg` (solo
il titolo), `dossier.summary.json`. Nessun'altra figura.

Il blocco KPI di `index.html`, testo estratto:

```
Guadagno 0 dB -0,00849 dB @ 1 kHz
Guadagno +10 dB 9,9491 dB @ 1 kHz
Scarto ADR-014 1,37·10^−4 dB @ 20 kHz rif. 1 kHz · peggiore delle 2 modalità
Margine di fase, blocco B 56,945 gradi · peggiore dei 4 casi pubblicati
PSRR, peggiore 29,765 dB @ 10 kHz
Z out al jack 58,7602 Ω @ 1 kHz
```

Il diff di `index.html` tocca soltanto:
- il KPI;
- la sottosezione ADR-014 (paragrafo, tabella, paragrafo nuovo);
- l'apertura della sezione 6 (paragrafo nuovo) e la frase del caso peggiore;
- la riga V1.

**Nessun altro numero** si è mosso. Ogni `0,02…` rimasto nella pagina è o una
cella della tabella di risposta (guadagni assoluti) o uno scarto etichettato
«assoluto». Il vecchio 0,022 senza etichetta non c'è più.

Suite a lavoro finito: **8 passed, 0 failed**.

## 6. Osservazioni fuori perimetro

- `testbenches/01_op.cir:10` ha `wrdata /Users/roberto/EDA/results/01_op.csv`
  cablato. Il blocco 2b di `run_tests.sh`, eseguito da un worktree, trova quindi
  il proprio wrdata nel checkout principale. Passa lo stesso, perché il CSV
  della run viene riscritto nella directory dei risultati del worktree. È della
  stessa famiglia di `export_fab.sh`/`setup.sh`; non corretto qui.
- STATE.md, sezione storica L5: «ADR-014 regge: 0,022 dB». È storia, e resta.
- NC-005 propone la nota su E3 «in ADR-011»: le ADR non si riscrivono, ma
  ADR-001/007/008/011 portano aggiunte in coda. È il nodo di forma che L15 deve
  sciogliere, e sta scritto nel suo mandato.
