# Prompt per la sessione successiva — L47c2 (il mute coi soli relè: il firmware, l'alimentatore col carico nuovo, V2 e i guasti)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47c2**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L47c è stato diviso dall'utente all'inizio («Due parti»). **L47c1** (fatto, ADR-062) ha portato la
decisione, il contratto e l'hardware:
- PR-21 è firmata: «Il mute taglia: con la musica il silenzio arriva di colpo, e al rilascio la
  musica torna di colpo al livello di prima». Il clic si misura e si dichiara, senza tetto;
- S è tolto da V2; C, il residuo del fit attorno al taglio, è il clic dichiarato;
- i relè vanno subito dopo il tasto;
- le quattro NSL-32SR3 e J3 sono uscite dalla scheda audio, il pilota delle LDR e J3 da `psu.py`
  (33 parti);
- il 2e e il 2j sono riscritti coi falsi;
- E3 è 114,7 kΩ ed E5 5,496 µV senza celle;
- limitations #45.

**L47c2** chiude il lotto: il firmware, le misure dell'alimentatore col carico nuovo, V2 senza
celle, i guasti. Fino a qui restano due incoerenze **dichiarate** (STATE, L47c1):
- il firmware scrive ancora sull'SPI verso il DAC tolto;
- i deck V2 hanno ancora le celle.

L'ordine dei lotti di rimedio resta quello dell'utente: L47 → **L48** selettore d'ingresso →
**L49** placement e routing di prova → **G1** → **L45** FMEA → **L50** massa e terra.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV. Due da portare, e una proposta:
- **i pin del micro rimasti liberi** (PA1, PA2, PA3, PA4, PB4): lasciati aperti, oppure il firmware
  li configura come uscite basse o ingressi con pull-up (il consumo in standby, NC-037). Proporre;
- **la tenuta di `VRELAY`** col carico nuovo (sotto): se sale molto, chiedere se ridurre `C_VRELAY`,
  oppure tenerla e dirlo;
- **se dividere il lotto** (per esempio: firmware e alimentatore in uno; V2 e guasti nell'altro).
  Proporre, non decidere.

### 2. Il firmware (`firmware/preamp_timer/`)

- Via da `src/timer_core.{c,h}`: `LDR_I_TOP`, `LDR_I_IDLE`, `LDR_I_CAL_LO`, `T_FADE_US`,
  `T_MUTE_HOLD_US`, la legge (`timer_law_vx`, `timer_law_code`), `timer_cal_t` e
  `timer_cal_fit*`, le scritture SPI al DAC.
- La sequenza del mute **coi relè subito** (ADR-062): all'inserimento `MUTE_REQ` cade appena letto
  il tasto (antirimbalzo a parte), poi Δ in hardware (ADR-045). Accensione, spegnimento morbido e
  guasto restano come sono, senza la sfumatura.
- `spec/timer_spec.md` §4 (le sequenze) e §5 (la legge delle LDR: va tolta).
- I test sull'host (`test/`, il blocco 2k di `run_tests.sh`): via `test_legge.c` o riscritto; i 21
  falsi rivisti. Ogni falso che spariva con la legge va sostituito da uno sulle sequenze nuove, e
  il conto va detto.
- `preamp_audio.py`, il contratto di J4: rileggerlo sul firmware nuovo.

### 3. L'alimentatore col carico nuovo (`circuits/preamp/psu.py`)

- **La tenuta di `VRELAY` a rete −10 %** (NC-050): la catena di L42b (36,1 ms col carico di
  L41b1) ricorsa senza il pilota. Riscrivere il commento di `C_VRELAY` (NC-051) dalle cifre
  misurate, togliendo la nota «NOT CURRENT» che L47c1 ha messo.
- **Lo standby** (NC-037): il consumo senza U510/U511.
- `psu_blocks_draw.py` se cambia una cifra che disegna.

### 4. V2 senza celle

- **I generatori e i deck.** `docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`
  e il generatore di `tb_v2_mute_ldr.cir`, rigenerati dalla netlist senza celle. I nomi che
  mentono si cambiano, come `tb_e3_e5_ldr` → `tb_e3_e5`. **S esce dal banco**
  (`scripts/v2_metodo.py`, righe `S_ins` e `S_rel`). La sequenza dei relè è quella del firmware
  nuovo (relè subito).
- **La matrice**: la pipeline di L29c più la guardia di L47b2b1
  (`docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py`). Si misurano:
  - A e B senza segnale (≤ 100 µV);
  - il silenzio dei cambi di guadagno e di trim;
  - l'accensione;
  - **B a mute inserito**: NC-053 si chiude qui se regge;
  - **il clic del taglio con musica**: C, in picco e dB SPL a 1 m, all'inserimento e al rilascio,
    su tutte e tre le uscite, ai tre toni. È dichiarato, non un verdetto.
- **NC-049** si chiude con la matrice senza S.

### 5. I guasti e la regressione

- **La catena dei guasti di L41c** sull'alimentatore nuovo. Il ponte usava le correnti delle LED:
  togliere quel ramo.
- **I 21 deck veloci**: `docs/preamp/data/2026-10-05/L47c1/script/regressione.sh`, il «prima» è
  `L47c1/regressione/dopo`.
- **Il firmware sull'host.**

### 6. Non conformità

NC-049 e NC-053 da chiudere con l'evidenza nuova; NC-050 e NC-051 col lotto; NC-037 aggiornata.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`;
  - #33/#38/#40 il «transient op», #34 un `alter` che sopravvive a `destroy all`;
  - #35 la `tran` abortita che scrive zeri (la guardia di L47b2b1 la vede), #36 la PWL lunga;
  - #37 le Note nelle tabelle, #42 le opzioni di convergenza a 20 Hz, #44 l'offset nel banco V2;
  - **#45**: `meas min` salta l'ultimo punto. Ogni minimo o massimo di banda si prende con
    `vecmin()` / `vecmax()`.
- `docs/preamp/STATE.md`: «In breve», **L47c1**, «Dopo L47b2b1», L41b1, L41b2, L41c, L42b, L29e.
- `decisions/ADR-062*`, `045*`, `046*`, `049*`, `050*`; `firmware/preamp_timer/spec/timer_spec.md`.
- `NONCOMPLIANCE.md`: NC-037, NC-049, NC-050, NC-051, NC-053.
- `reports/2026-10-05-L47c1-mute-coi-soli-rele.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte** (#39).
- `docs/preamp/data/` è versionato per regola: le forme d'onda grosse vanno in `.gitignore` prima
  del commit. Le matrici V2 sono lunghe: 135 corse, ~2,5 h con 8 processi, e l'analisi ore.

## NON fa parte di questo lotto

- tornare a una sfumatura (fotoresistenze, JFET, relè a gradini, gradino fisso a −20 dB): l'ha
  deciso l'utente, e si riapre solo se lo chiede;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
    e L46a;
  - il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
    `tb_e3_e5.cir`, senza celle);
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima) non lo dicono, e quelle di ADR-059 e ADR-060 nominano ADR più vecchie (il
    controllo del punto 14 le rifiuta): si allineano con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L47c2 **fatto** (o il primo sotto-lotto) e il prossimo lotto nella tabella (L48, o
   il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47c2` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
