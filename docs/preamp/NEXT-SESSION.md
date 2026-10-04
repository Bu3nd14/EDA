# Prompt per la sessione successiva — L47c (il mute coi soli relè: PR-21 riscritta, via fotoresistenze, pilota e profilo, V2 ricorso)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47c**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

Dopo L47b2b1 (il profilo v5 delle fotoresistenze, ADR-061) l'utente ha chiesto perché il mute sia
così complicato e se accettare un salto con la musica lo semplifichi (STATE, «Dopo L47b2b1»).

- **Il silenzio dei cambi** (PR-20, ≤ 100 µV) lo fanno i **relè al jack** in geometria iii
  (ADR-044), il permissivo sfasato (ADR-045) e l'interblocco del guadagno (ADR-030, ADR-041).
  **Restano.**
- **La sfumatura** (PR-21, «il mute sfuma, non taglia», S ≤ 20 dB in 100 ms) è l'unica ragione
  delle quattro NSL-32SR3, del loro pilota in `psu.py` (~30 parti), del profilo v5 e della
  calibrazione nel firmware, della nota su E3 nella sfumatura, di NC-043, NC-049 e NC-053.

Scelta dell'utente, il 2026-10-04: **«Taglio coi soli relè»**. Il prezzo, detto all'utente prima
della scelta: la musica si interrompe di colpo all'inserimento (~70 dB invece dei 20 del Technics),
torna di colpo a piena potenza al rilascio, e un contatto che apre su un picco può fare un clic.
L47b2b2 (il pilota vero della sfumatura) è **superato**.

L'ordine dei lotti di rimedio resta quello dell'utente: L47 → **L48** selettore d'ingresso →
**L49** placement e routing di prova → **G1** → **L45** FMEA → **L50** massa e terra.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV.

- **Il testo nuovo di PR-21**, da firmare (ADR-053: il PRB cambia solo con una ADR). Proposta da
  portare: «Il mute taglia: con la musica il silenzio arriva di colpo, e al rilascio la musica
  torna di colpo al livello di prima». Chiedere se vuole altro (per esempio un limite al clic del
  taglio).
- **Cosa diventa S in V2**: tolto, o tenuto come diagnostica.
- **Il tempo fra il tasto e i relè** (oggi la sequenza aspetta la sfumatura: `T_FADE_US`,
  `T_MUTE_HOLD_US` 0,5 s dopo d = 1): senza sfumatura, i relè subito.
- **L'impronta** `library/preamp.pretty/NSL-32SR3_LED3.30`: tolta o tenuta (non serve più).
- **Se dividere il lotto** (per esempio: decisione, PRB e scheda audio in uno; alimentatore,
  firmware e V2 nell'altro). Proporre, non decidere.

### 2. La decisione

**ADR-062**: supera ADR-038 sulla sfumatura (il relè al jack resta), ADR-039 e ADR-040 sul profilo e
su S, ADR-058…ADR-061 sulla cella, la cima, il profilo e la nota su E3, ADR-049 e ADR-050 sul pilota
delle LDR (il micro, il DAC se serve ad altro, Δ e Δ₂ restano). `PRB.md` (PR-21) e `REQUIREMENTS.md`
(V2: S; la nota su E3 durante la sfumatura) con la firma dell'utente.

### 3. Il circuito e il firmware

- **`circuits/preamp/preamp_audio.py`**: via le due celle per canale e J3 (`LDR_CMD`) e il
  contratto scritto accanto; il connettore d'ingresso torna sull'ingresso del blocco A. Netlist e
  schema a blocchi (`docs/preamp/schematic/preamp_blocks_draw.py`, le asserzioni del 2f).
- **`circuits/preamp/psu.py`**: via il pilota delle LDR (MCP4822 se non serve ad altro, U511, le
  coppie appaiate, gli specchi, i sense e le letture dell'ADC) e J3; `psu_blocks_draw.py`.
  **`VRELAY`** a rete −10 % ricorsa col carico nuovo (NC-050), il commento di `C_VRELAY` riscritto
  (NC-051), il consumo in standby (NC-037).
- **I controlli**: `check_relay_safe_state.py` (2e: la verifica delle LDR del mute graduale) e
  `check_psu_harness.py` (2j: J3 e `LED_PINS`) aggiornati, coi falsi che li fanno cadere;
  `trim.py` e `gain_interlock.py` nominano J3 o le celle: rileggerli.
- **Il firmware** `firmware/preamp_timer/`: via `LDR_*`, le tabelle del profilo, la calibrazione
  (`timer_cal_*`), `T_FADE_US`; la sequenza del mute coi relè subito; `spec/timer_spec.md`
  (§ 4 e § 5); i test sull'host (blocco 2k) e i falsi riscritti.
- `models/optocoupler/nsl32sr3_comportamentale.lib` resta in `models/` (validato, con la sua
  provenienza), fuori dai banchi canonici; deciderne con l'utente solo se lo chiede.

### 4. Le misure

- **V2** (`tb_v2_casopeggiore.cir`, `tb_v2_mute_ldr.cir` e i loro generatori): senza celle, i relè
  al jack tagliano. Matrice ricorsa con la pipeline di L29c **più la guardia di L47b2b1**
  (`docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py`): A e B senza segnale (≤ 100 µV),
  il silenzio dei cambi di guadagno e trim, l'accensione, B a mute inserito (NC-053 si chiude
  qui se B regge), e **il clic del taglio con musica** (picco e dB SPL, dichiarato).
- **E3 ed E5** statici senza celle (`tb_e3_e5_ldr.cir` torna senza LDR, o un deck nuovo).
- **La catena dei guasti di L41c** sull'alimentatore nuovo; i 21 deck veloci; il firmware
  sull'host.

### 5. Non conformità

NC-043, NC-049, NC-053 da chiudere per superamento (con l'evidenza dei banchi nuovi); NC-050 e
NC-051 col lotto; NC-045 è già chiusa (L47b2b1).

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio: #22 rinumerazione,
  #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`; #33/#38/#40 il «transient op»;
  #34 un `alter` che sopravvive a `destroy all`; #35 la `tran` abortita che scrive zeri (**`corri.sh`
  non lo vede: la guardia di L47b2b1 sì**); #36 la PWL lunga; #37 le Note nelle tabelle; #41 anodo e
  catodo; #42 le opzioni di convergenza a 20 Hz; #43 E3 lungo la sequenza al connettore; **#44**
  l'offset del primo stadio nel banco V2 (corretto in `iosa()`).
- `docs/preamp/STATE.md`: «In breve», **«Dopo L47b2b1»**, L47b2b1, L41b1, L41b2, L41c, L29e, L29d2.
- `PRB.md` (PR-20, PR-21, PR-24); `decisions/ADR-030*`, `038*`, `039*`, `040*`, `041*`, `044*`,
  `045*`, `049*`, `050*`, `053*`, `058*`…`061*`.
- `NONCOMPLIANCE.md`: NC-043, NC-049, NC-050, NC-051, NC-053.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti e le pipe o i `;` attorno a comandi che
  eseguono script (anche `run_tests.sh` va lanciato da solo); `cd … && script`; le variabili di
  shell nei percorsi; `awk` con programmi, i cicli con variabili; gli heredoc; un `python3 -c`
  dentro un altro comando; un titolo di PR con l'apostrofo (il corpo va su file, `--body-file`).
  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte** (#39).
- `docs/preamp/data/` è versionato per regola: le forme d'onda grosse in `.gitignore` prima del
  commit. Le matrici V2 sono lunghe (135 corse ~2,5 h con 8 processi; l'analisi ore).

## NON fa parte di questo lotto

- tornare a una sfumatura (fotoresistenze, JFET, relè a gradini, gradino fisso a −20 dB): deciso
  dall'utente; si riapre solo se lo chiede;
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- rigenerare il dossier. Quando lo si rigenera: il §14 di `build_dossier.py` («solo l'LSK489A porta
  KF», «niente distorsione») è superato da L44 e L46a; il mute descritto è quello della VTL5C4; le
  righe `Stato:` di ADR-038, 039, 040, 050 e di quelle che L47c supera non lo dicono, e quelle di
  ADR-059 e ADR-060 nominano ADR più vecchie (il controllo del punto 14 le rifiuta): si allineano
  con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L47c **fatto** (o il primo sotto-lotto) e il prossimo lotto nella tabella (L48, o
   il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47c` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
