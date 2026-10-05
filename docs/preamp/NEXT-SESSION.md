# Prompt per la sessione successiva — L47c2b (il mute coi soli relè: V2 senza celle e i guasti)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47c2b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L47c2 è stato diviso dall'utente all'inizio («Due parti»). **L47c2a** (fatto, nessuna ADR) ha
portato il firmware e l'alimentatore:
- il firmware senza la legge delle LDR, la calibrazione, la sfumatura e la SPI. All'inserimento
  `MUTE_REQ` cade nello stesso istante in cui il debounce conferma il tasto, poi Δ (20 ms) e
  `PERMIT_REQ`; al rilascio le due richieste insieme, 10 ms del G6K, poi MUSICA. Sull'host 19
  falsi su 19; **sul circuito 6 sequenze su 6** (relè 21,1 ms dopo il tasto al rilascio, 21,2 ms
  dopo il pin del frontale allo spegnimento);
- i pin liberi del micro col buffer d'ingresso disattivato (scelta dell'utente);
- la tenuta di `VRELAY` 61,1 ms a rete −10 %, 4700 µF tenuti (scelta dell'utente); standby 80,5
  mW da T2; **NC-051 chiusa**, NC-050 e NC-037 aggiornate.

**L47c2b** chiude L47c: V2 senza celle e i guasti. Resta **un'incoerenza dichiarata** (STATE,
L47c1): i deck V2 (`tb_v2_casopeggiore.cir`, `tb_v2_mute_ldr.cir`) hanno ancora le celle e il
profilo v5.

L'ordine dei lotti di rimedio resta quello dell'utente: L47 → **L48** selettore d'ingresso →
**L49** placement e routing di prova → **G1** → **L45** FMEA → **L50** massa e terra.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV. Da portare:
- **se dividere il lotto** (per esempio: la matrice V2 in uno; i guasti e la regressione
  nell'altro). La matrice V2 è lunga: 135 corse, ~2,5 h con 8 processi, e l'analisi ore. Proporre,
  non decidere;
- **come presentare il clic del taglio**: è dichiarato, non un verdetto (PR-21, ADR-062). Proporre
  la forma, cioè il picco in dB SPL a 1 m, all'inserimento e al rilascio, sulle tre uscite e ai
  tre toni. Chiedere se basta il caso peggiore o serve la tabella intera.

### 2. V2 senza celle

- **I generatori e i deck.** `docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`
  e il generatore di `tb_v2_mute_ldr.cir` vanno rigenerati dalla netlist senza celle. I nomi che
  mentono si cambiano, come ha fatto L47c1 con `tb_e3_e5_ldr` → `tb_e3_e5`.
- **S esce dal banco**: in `scripts/v2_metodo.py`, le righe `S_ins` e `S_rel`.
- **La sequenza dei relè è quella del firmware di L47c2a**: `MUTE_CMD` 21 ms dopo il tasto (20 di
  debounce più il gate), `PERMIT_CMD` Δ dopo. Le cifre stanno in
  `data/2026-10-05/L47c2a/seq/analisi_seq.txt`.
- **La matrice**: la pipeline di L29c più la guardia di L47b2b1
  (`docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py`). Si misurano:
  - A e B senza segnale (≤ 100 µV);
  - il silenzio dei cambi di guadagno e di trim;
  - l'accensione;
  - **B a mute inserito**: NC-053 si chiude qui se regge;
  - **il clic del taglio con musica**: C, in picco e dB SPL a 1 m, all'inserimento e al rilascio,
    su tutte e tre le uscite, ai tre toni. È dichiarato, non un verdetto.
- **NC-049** si chiude con la matrice senza S.

### 3. I guasti e la regressione

- **La catena dei guasti di L41c** (`data/2026-09-26/L41c/README.md`, in due tempi) sull'alimentatore
  nuovo:
  - **il primo tempo** usa il generatore di L47c2a (`data/2026-10-05/L47c2a/deck/`). Ha già i casi
    di L41c (`spegnimento_l`, `perdita`, `perdita_min`, `guasto_u501`, `guasto_u503`,
    `guasto_u503_min`, `cf_nodelta`, `corto_u503`) e `corri_seq.sh` ne conosce preambolo e fine.
    `spegnimento_l` è accorciato a TE + 1,1 s, da confermare;
  - **i criteri r ed s** di L41c stanno nel suo `psu/analizza_seq.py`, non in quello di L47c2a, e
    vanno riportati;
  - **il ponte** (`L41c/ponte/estrai_ponte.py`) usava le correnti delle LED: togliere quel ramo;
  - **il banco audio** usa `--matrice l41c` del generatore V2, rigenerato senza celle.
- **I 21 deck veloci**: `docs/preamp/data/2026-10-05/L47c1/script/regressione.sh`, il «prima» è
  `L47c1/regressione/dopo`.
- **Il firmware sull'host** (il 2k di `run_tests.sh`).

### 4. Non conformità

NC-049 e NC-053 da chiudere con l'evidenza nuova; NC-050 resta aperta fino al carico congelato
(G2).

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse, #24 nodi del blocco, #29 `altermod`;
  - #33/#38/#40 il «transient op», #34 un `alter` che sopravvive a `destroy all`;
  - #35 la `tran` abortita che scrive zeri (la guardia di L47b2b1 la vede), #36 la PWL lunga;
  - #37 le Note nelle tabelle, #42 le opzioni di convergenza a 20 Hz, #44 l'offset nel banco V2;
  - **#45**: `meas min` salta l'ultimo punto. Ogni minimo o massimo di banda si prende con
    `vecmin()` / `vecmax()`.
- `docs/preamp/STATE.md`: «In breve», **L47c2a**, **L47c1**, «Dopo L47b2b1», L41c, L29c, L29d2,
  L29e, L47b2b1.
- `decisions/ADR-062*`, `045*`, `044*`, `032*`, `035*`, `036*`.
- `NONCOMPLIANCE.md`: NC-049, NC-053.
- `reports/2026-10-05-L47c2a-firmware-alimentatore.md`, `reports/2026-10-05-L47c1-mute-coi-soli-rele.md`.

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
  del commit.
- `zsh` espande un `=` a inizio parola: `echo =====` fallisce («not found»).

## NON fa parte di questo lotto

- tornare a una sfumatura (fotoresistenze, JFET, relè a gradini, gradino fisso a −20 dB): l'ha
  deciso l'utente, e si riapre solo se lo chiede;
- togliere `models/optocoupler/nsl32sr3_comportamentale.lib` da `models/`: se ne decide con
  l'utente solo se lo chiede;
- l'adattatore `firmware/preamp_timer/src/main_attiny.c` (dove l'`ISC` dei pin liberi si scriverà
  davvero): non è mai stato scritto, e non è di qui;
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` («solo l'LSK489A porta KF», «niente distorsione») è superato da L44
    e L46a;
  - il mute descritto è quello della VTL5C4, e il dossier cita `tb_e3_e5_ldr.cir` (ora
    `tb_e3_e5.cir`, senza celle);
  - il firmware descritto è quello di L41b2: la legge delle LDR, 21 falsi, sette sequenze;
  - le righe `Stato:` di ADR-038, 039, 040, 049, 050, 058, 059, 060, 061 (superate o precisate da
    ADR-062 e prima) non lo dicono, e quelle di ADR-059 e ADR-060 nominano ADR più vecchie (il
    controllo del punto 14 le rifiuta): si allineano con l'utente, toccando solo quella riga.

## CHIUSURA

1. `STATE.md` con L47c2b **fatto** (o il primo sotto-lotto) e il prossimo lotto nella tabella (L48, o
   il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47c2b` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
