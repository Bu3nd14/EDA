# CLAUDE.md — orientamento rapido per questo repo

Ambiente EDA analogico + automazione PCB su macOS/Apple Silicon: dalla
definizione della topologia in codice fino a gerber+drill, tutto non
interattivo. Roadmap del progetto hi-fi: **preamplificatore → stadio
phono → finale di potenza** (un DAC è possibile ma non deciso).

`circuits/` è la fonte di verità della topologia ed è **ancora vuota**:
il preamp sarà il primo circuito canonico del repo.

## Progetto in corso: preamplificatore

**Se stai riprendendo il lavoro sul preamp, leggi prima
`docs/preamp/STATE.md`.** Dice dove siamo, cosa è aperto e qual è il
prossimo passo.

La documentazione di progetto sta in `docs/preamp/`, organizzata per
ciclo di vita e non per fase:

| Percorso | Tipo | Regola |
|---|---|---|
| `docs/preamp/STATE.md` | vivo | Il punto di ripresa. Sempre vero al presente |
| `docs/preamp/REQUIREMENTS.md` | vivo | Requisiti congelati; ogni modifica sostanziale vuole una ADR |
| `docs/preamp/decisions/ADR-*.md` | **immutabile** | Mai riscritte. Una decisione superata si supera con una ADR nuova |
| `docs/preamp/reports/` | datato | Output di un'esecuzione: misure, giri BOM, verdetti dei gate |

**Regola operativa: ogni sessione che tocca il progetto preamp aggiorna
`docs/preamp/STATE.md` prima di chiudere, e lo committa insieme al
lavoro.** È il meccanismo che rende sicuro interrompere una sessione a
metà — se STATE.md è disallineato, il progetto non è ripartibile.

**E prima ancora: `git push`.** È l'azione che salva davvero. Un commit
non pushato dentro un worktree sotto `.claude/worktrees/` sparisce
insieme al worktree, ed è già successo una volta. Verificalo, non
assumerlo:

```sh
git log --oneline origin/<branch>..HEAD    # deve essere vuoto
```

**E dopo il push, il merge.** Un push rende il lavoro **durevole**; non
lo rende **raggiungibile**. Sono due cose diverse e per un po' ne è stata
soddisfatta una sola. Alla chiusura di L3 il lavoro era pushato,
committato e in PR — e il checkout che l'utente apre, `/Users/roberto/EDA`,
conteneva ancora il prompt di ripresa del lotto **precedente**: il passo
successivo documentato gli consegnava il file sbagliato, e niente lo
segnalava.

Quindi **un lotto non è chiuso quando la sua PR è aperta. È chiuso quando
`main` contiene il lavoro e il checkout dell'utente nomina il lotto
successivo.** L'ordine è:

**push → stato → merge e riallineo → tutto il resto.**

Non si fa a mano, si fa con lo script che rifiuta:

```sh
/bin/zsh /Users/roberto/EDA/scripts/chunk_close.sh <lotto>
```

Verifica il tree pulito, il push, che il ramo abbia aggiornato `STATE.md`,
che la tabella dei lotti segni il lotto come **fatto**, che
`NEXT-SESSION.md` **non nomini più il lotto appena finito**, e che
`run_tests.sh` passi. Poi merghia la PR, fa `pull --ff-only` sul checkout
principale, e **rilegge da lì** per provare il riallineo invece di
dichiararlo. Non ha flag di bypass, come `export_fab.sh`.

**Mergiare la propria PR è autorizzato dall'utente** (deciso il
2026-09-09) e vale per ogni lotto: sempre `gh pr merge --squash
--delete-branch`, mai un `git merge` locale su `main`, mai `--force`. La
PR resta comunque — non è cerimonia, è la traccia: URL stabile, un commit
per lotto su `main`, e un corpo che il gate potrà citare.

**Tracciabilità**: ogni valore non ovvio in `circuits/preamp/*.py` porta
un commento che punta alla ADR che l'ha prodotto. È il collegamento
dall'artefatto al ragionamento, e costa un commento.

Questo file non ripete la documentazione: è l'indice di orientamento più
ciò che è stato scoperto e non è ancora finito negli altri documenti.

## Ordine di lettura

1. **`README.md`** — toolchain installata, procedura di installazione
   reale, workflow di simulazione e PCB, capacità effettivamente
   verificate.
2. **`AGENTS.md`** — roster degli agenti, gate G1/G2/G3, e le 10 regole
   operative che valgono per tutto il lavoro nel repo.
3. **`docs/limitations.md`** — **da leggere prima di scrivere qualsiasi
   codice.** È il file più load-bearing del repo: 18 limitazioni
   documentate, molte delle quali falliscono in silenzio.

## Percorsi assoluti

È il punto in cui si perde più tempo. Nessuno di questi va scritto a
memoria o dedotto dal `PATH`.

| Cosa | Percorso |
|---|---|
| ngspice 47 | `/opt/homebrew/bin/ngspice` |
| kicad-cli 10.0.6 | `/Users/roberto/Applications/KiCad.app/Contents/MacOS/kicad-cli` |
| Python SKiDL (venv 3.13) | `/Users/roberto/EDA/env/venv/bin/python3` |
| Python `pcbnew` (KiCad 3.9) | `/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9` |
| Simboli KiCad | `/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/symbols` |
| Footprint KiCad | `/Users/roberto/Applications/KiCad.app/Contents/SharedSupport/footprints` |
| Freerouting | `/Users/roberto/EDA/scripts/tools/freerouting.jar` |
| java (per Freerouting) | `/opt/homebrew/opt/openjdk/bin/java` |
| pdftotext (poppler 26.09.0) | `/opt/homebrew/bin/pdftotext` |

**I due interpreti non sono intercambiabili.** SKiDL gira solo sul venv
3.13; `pcbnew` e `kinet2pcb` girano solo sul Python 3.9 interno a KiCad.
Nessuno dei due copre entrambe le metà della pipeline: qualsiasi script
che le tocchi entrambe deve fare il bridge con percorsi assoluti
espliciti (vedi `smoke/run_pipeline.sh`).

## Comandi

```sh
# Sanità dell'ambiente. Esce con il NUMERO di check falliti (non 0/1).
/bin/zsh /Users/roberto/EDA/scripts/verify_env.sh

# Suite completa: validate_models + DRC sulla board smoke nota buona
# + una run_simulation reale + verifica presenza artefatti smoke.
/bin/zsh /Users/roberto/EDA/scripts/run_tests.sh

# Libreria modelli: 38/38 check, ngspice reale + re-hash della provenance.
/usr/bin/python3 /Users/roberto/EDA/scripts/validate_models.py
/usr/bin/python3 /Users/roberto/EDA/scripts/validate_models.py --check-provenance

# Simulazione singola -> .log/.csv/.json
/bin/zsh /Users/roberto/EDA/scripts/run_simulation.sh <netlist.cir> [outdir]

# ERC / DRC. Propagano l'exit code di kicad-cli: 0 pulito, 5 violazioni.
/bin/zsh /Users/roberto/EDA/scripts/run_erc.sh <schematic.kicad_sch> [outjson]
/bin/zsh /Users/roberto/EDA/scripts/run_drc.sh <board.kicad_pcb> [outjson]

# Export fabbricazione. Esegue una DRC FRESCA e RIFIUTA su qualsiasi
# violazione (exit 5, nessun file scritto). Non esiste flag di bypass.
/bin/zsh /Users/roberto/EDA/scripts/export_fab.sh <board.kicad_pcb> [outdir]

# Pipeline end-to-end completa (fixture RC).
zsh /Users/roberto/EDA/smoke/run_pipeline.sh

# Normalizzazione dell'output wrdata di ngspice (colonna x ripetuta).
python3 /Users/roberto/EDA/scripts/normalize_wrdata.py <in.csv> <xname> <yname>...
```

Nota: `validate_models.py` e gli helper JSON dentro gli script shell
usano `/usr/bin/python3` (Python di sistema), non il venv — è
deliberato, servono solo della stdlib.

## Stato reale del repo (2026-09-08)

| Directory | Stato |
|---|---|
| `circuits/`, `schematics/`, `spice/`, `tests/` | **vuote** (solo `.gitkeep`) — scaffolding mai popolato |
| `models/`, `vendor/`, `testbenches/`, `scripts/`, `docs/` | popolate |
| `smoke/`, `pcb/`, `results/`, `fabrication/` | **scratch**, non canoniche |

Non c'è CI, non c'è pytest (la "suite" è `run_tests.sh`), non c'è
`.claude/settings.json`, non ci sono hook.

## Le trappole che falliscono in silenzio

L'elenco completo è in `docs/limitations.md`. Queste sono in evidenza qui
perché non danno errore — danno una risposta sbagliata:

1. **SKiDL perde `Sim.Type` e `Sim.Device`** quando mette in cache i
   simboli nello `.kicad_sch`. Il risultato è una riga SPICE non valida,
   senza alcun errore. Vanno impostati a mano su ogni parte
   `Simulation_SPICE` — il pattern è in `smoke/rc_circuit.py`.
2. **`.temp` con lista di valori ricade silenziosamente a 27 °C**,
   emettendo solo un warning. Per uno sweep vero serve
   `dc TEMP start stop step` dentro un blocco `.control`.
3. **`C` e `L` non accettano il valore posizionale** che `R` accetta:
   servono `C=<valore>` e `inductance=<valore>`.

Più due promemoria che fanno perdere tempo: usare `.include` e mai `.lib`
per i file di modello semplici, e ricordare che **la prima riga di ogni
`.cir` è sempre trattata come titolo**, qualunque cosa contenga.

## Da dove partire per scrivere codice

`smoke/rc_circuit.py` è l'unico sorgente SKiDL esistente ed è il template
di riferimento. Mostra tutto quello che serve sapere:

- il preambolo che imposta `KICAD{6..10}_SYMBOL_DIR` / `_FOOTPRINT_DIR`
  (SKiDL 2.3.0 ha come costante di default `KICAD10`; la variabile
  sbagliata produce un `FileNotFoundError` che non lascia intuire la
  causa reale);
- il workaround `Sim.Type` / `Sim.Device`;
- il footprint obbligatorio anche su parti di sola simulazione;
- `generate_netlist(file_=..., tool="kicad10")`.

È scratch: va usato come modello, non esteso sul posto. La topologia
canonica va in `circuits/*.py`.

Il percorso SPICE che funziona è: `generate_schematic()` →
`kicad-cli sch export netlist --format spice` → ngspice. Il percorso
SPICE nativo di SKiDL (`generate_netlist(tool="spice")`) **non funziona**
con le parti della libreria KiCad.

## Scoperte non ancora presenti nella documentazione

Ognuna con il comando che la verifica, così restano falsificabili.

**`Sim.Library` e `Sim.Name` sono supportati da eeschema.**

```sh
strings /Users/roberto/Applications/KiCad.app/Contents/PlugIns/_eeschema.kiface \
  | grep -E '^Sim\.[A-Za-z]+$' | sort -u
```

È la strada per usare subcircuiti SPICE **vendor reali** e quindi
l'unico modo di ottenere numeri di distorsione credibili. **Non ancora
collaudata end-to-end**: resta da verificare se SKiDL porta questi campi
fino allo `.kicad_sch` o se li perde come fa con `Sim.Type`/`Sim.Device`.

**Nel repo non esiste nessun modello SPICE vendor reale.** Tutti gli 11
file in `models/` sono fixture usa-e-getta; il macro-modello op-amp
dichiara nella propria intestazione di non avere clipping del segnale,
né slew rate, né assorbimento dalle alimentazioni. **Qualunque cifra di
THD ricavata da questa libreria è priva di significato**, e sia
`measurement-analyst` sia `design-reviewer` hanno il mandato esplicito
di segnalarlo.

**I simboli degli op-amp audio ci sono già** in
`Amplifier_Operational.kicad_sym`: OPA1612AxD, OPA1656ID, OPA1642,
OPA1602/1604, OPA134, LM4562, NE5532, OPA1662/1664, OPA1692. La libreria
`Simulation_SPICE` include anche un simbolo `Potentiometer` (utile per il
controllo di volume) oltre a VSIN/VDC/VPULSE/OPAMP e ai modelli
NPN/PNP/NMOS/PMOS/NJFET/PJFET.

**`InSpice 1.7.0.6` è installato nel venv e non è documentato da nessuna
parte** (`env/venv/bin/python3 -m pip list | grep -i inspice`). È un
percorso Python→ngspice alternativo mai esplorato. Registrato come fatto,
non come raccomandazione.

**Deriva documentale nel README** — da non scambiare per un bug da
inseguire:

- Il README dice che `kinet2pcb` non è installato nel venv, ma
  `kinet2pcb 1.1.4` **è** nel venv. Lì è inutile (manca `pcbnew`), quindi
  il workflow documentato resta corretto: è la frase a essere obsoleta.
- Il `TODO: unverified` sulla tabella degli script è superato: tutti e 8
  gli script corrispondono all'interfaccia documentata.

**`skidl_REPL.erc` e `skidl_REPL.log` nella root** sono detriti innocui:
è ciò che SKiDL scrive quando gira **senza** il preambolo delle variabili
d'ambiente (SKiDL nomina i propri file di log secondo lo script
chiamante, e ripiega su `skidl_REPL` quando non ce n'è uno). Il `.gitignore`
non li copre.

## Gate e regole

Dettaglio in `AGENTS.md`. In sintesi: `design-reviewer` interviene solo a
tre gate — **G1** congelamento topologia, **G2** pre-layout, **G3**
pre-fabbricazione.

**Il gate non è attaccato alla PR: è attaccato ai risultati dei test**
(deciso il 2026-09-09). Un diff è l'artefatto sbagliato su cui giudicare
un progetto analogico — le righe modificate di `gain_block.py` non dicono
niente sul margine di fase. Il gate gira quindi **offline, dopo il
merge**, su `main`, sul dossier e sui dati misurati, e `design-reviewer`
riesegue le verifiche da sé invece di fidarsi dei resoconti.

Il suo prodotto non è un veto su un merge: è un **report datato** in
`docs/preamp/reports/` che apre delle **non conformità**, ognuna con il
requisito a cui si riferisce, l'evidenza, la severità e lo stato. Il
registro vivo è `docs/preamp/NONCOMPLIANCE.md`.

**Il BLOCK non è sparito, si è spostato**: una non conformità di severità
**bloccante** non impedisce un merge, impedisce l'**avanzamento di fase**
— niente layout, niente fabbricazione. Su un progetto collegato alla rete
elettrica, l'assenza di un'analisi di sicurezza resta una non conformità
bloccante automatica a G3.

Le regole che vengono violate più facilmente: la topologia sta solo in
`circuits/*.py` (mai modificare a mano schematici o netlist generati); i
file in `vendor/` sono di sola lettura; ERC e DRC precedono sempre
l'export di fabbricazione; nessuna capacità va dichiarata funzionante
senza averla eseguita davvero.

**Nessun agente giudica come *suona* un circuito.** La simulazione copre
in modo credibile stabilità, rumore, risposta, PSRR e impedenze; non
copre l'ascolto, e le cifre di distorsione da macro-modelli generici non
sono un sostituto della misura su un prototipo reale.
