# Prompt per la sessione successiva — L51b, il dossier rigenerato: l'alimentatore e il firmware

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L51b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'utente, il 2026-10-09 dopo L49b: «rigeneriamo il dossier, mettilo nel prossimo lotto abbiamo
cambiato molto, poi lo passiamo all'avversariale di nuovo, poi affrontiamo G1». All'inizio di L51
l'ha diviso: **«Tre parti»** — **L51a** la scheda audio (**fatto**, 2026-10-09), **L51b**
l'alimentatore e il firmware (questo), **L51c** le schede di prova e l'assieme di L49, «Cosa questo
dossier non dice», la provenienza e le righe `Stato:` restanti. Poi **L52** l'architetto
avversariale sul dossier nuovo, poi **G1**, poi L45 FMEA e L50 massa e terra.

Il dossier lo legge **solo l'utente** e **non si taglia**: si rigenera, senza avvisi di
obsolescenza.

## Come L51a ha lasciato il generatore (leggere prima del codice)

- `build_dossier.py` ha **`PARTI = ("audio",)`**: ogni sezione di `SECTIONS_TUTTE` dice a quale
  parte appartiene, e la pagina ha solo quelle delle parti presenti. Finché le parti non sono tutte
  e tre, il generatore **non scrive niente accanto a sé** (né `index.html`, né le figure, né il
  summary: sono ancora quelli di L42) e scrive la pagina solo con `--standalone` **fuori dal
  repo**. L51b aggiunge `"alimentatore"`; il primo `index.html` nuovo lo scrive L51c.
- Le sezioni dell'alimentatore della pagina, e le righe dell'alimentatore della tabella dei
  requisiti, sono **intatte e sotto `if psu:`**: si riscrivono da qui. Le misure
  (`measure_psu_power`, `measure_supervisor`, `measure_timer`, `measure_fw`, `measure_ldr_drive`,
  `measure_shutdown`, `measure_heat`) sono quelle di L42b, e **leggono il circuito di L41**:
  `main()` le chiama solo con la parte presente.
- I dati della scheda audio passano da **`sa()`**: niente da prima di `AUDIO_DA` (2026-10-07, il
  circuito di L48b) se non le eccezioni nominate in `AUDIO_PERMESSI`, con la loro ragione stampata
  nella pagina. Per l'alimentatore serve la stessa guardia, col suo giorno.
- Il testo cita le sezioni con `sez()`, mai il numero a mano: le sezioni nuove spostano i numeri.

## Il mandato

- **L'alimentatore di oggi è quello di L47c2a** (`psu.py` non è cambiato dopo): il firmware senza
  la legge delle LDR (19 falsi sull'host, 6 sequenze sul circuito), l'alimentatore senza il pilota
  (tenuta di `VRELAY` 61,1 ms a rete −10 %, poi **48,3 ms** col carico del selettore, L48a/psu),
  lo standby 80,5 mW da T2; i guasti e lo spegnimento al jack di **L47c2b2** (U502 spento
  0,89 mV, spegnimento morbido 15 nV). Le prime strade sono le cartelle di quei lotti, le seconde
  ricorse di oggi, come L42b fece con L41: decidere con l'utente se ricorrere tutto (in L42b una
  ricorsa ha trovato la tenuta di `VRELAY` scesa da 62,8 a 36,1 ms).
- **Via la sezione «Il pilota delle LDR»** (`sldr`, `measure_ldr_drive`, `fig_ldr_drive`): il pilota
  non c'è più (ADR-062). La sezione dello schema dell'alimentatore cita ancora ADR-050 e la cima a
  12 mA.
- **Il calore** (`sheat`, uscito da L51a): la stima di L30 (`data/2026-09-26/L30/termica/stima_telaio.py`,
  e la versione di L41a in `L41a/scelte/stima_telaio_l41a.py`) ha voci **superate**: i blocchi a
  0,993 W (prima di ADR-054: `tb_op` di oggi dà 15 V × (36,70 + 37,72) mA = 1,116 W per blocco), le
  LDR tolte, le bobine e il regolatore di `VRELAY` col selettore. Rifare la stima con le cifre di
  oggi è una misura nuova: **portarla all'utente prima**, coi numeri.
- Le righe dell'alimentatore nella tabella dei requisiti (P9 (a), P9 (b), ADR-045, NC-037), e le
  due tessere del quadro sinottico (Δ, il guasto al jack).
- I sabotaggi di L42b sono sui dati di L41: rifarli sui controlli nuovi (`L51a/script/sabotaggi.py`
  è il modello).

## All'inizio, con l'utente

Misurare prima (quanti dati sono da ricorrere, quanto durano le catene), poi chiedere per nome e
senza sigle: ricorrere o no, e il calore.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (**54 voci**; per l'alimentatore #29, #33–#36, #38, #40).
- `docs/preamp/STATE.md`: «In breve», **L51a**, **L42b** (come si è rigenerato l'alimentatore
  l'altra volta), L47c2a, L47c2b2, L48a (la parte `psu/`).
- `docs/preamp/dossier/build_dossier.py` per intero; `data/2026-10-09/L51a/README.md`.
- I report di L47c2a, L47c2b2 e L48a.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` e `run_simulation.sh` vanno lanciati da soli, senza redirect seguiti da altro);
  - `cd … && script`, **le variabili di shell nei percorsi**;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che **contiene la parola «git»** anche solo
    in un testo;
  - un heredoc Python lungo da solo: gli script si scrivono su file con Write, i testi con Edit;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file. Il venv non è nel
  worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- `docs/preamp/data/` è versionato per regola: i file grossi vanno in `.gitignore` prima del commit.
- `zsh` espande un `=` a inizio parola; un glob senza corrispondenze ferma il comando: `(N)` in coda.

## NON fa parte di questo lotto

- Le schede di prova e l'assieme di L49, «Cosa questo dossier non dice», le righe `Stato:` restanti
  (ADR-009, 027, 032, 038, 039, 040, 049, 050, 061, 062): **L51c**.
- L'architetto avversariale (**L52**) e il gate (**G1**).
- Cambiare il circuito, i deck o il firmware: il dossier li descrive com'è oggi. Un difetto trovato
  rigenerando si scrive e si porta all'utente, non si corregge da sé.
- La FMEA (L45), la massa e la terra (L50), il layout vero (G2).

## CHIUSURA

1. `STATE.md` con L51b **fatto** nella tabella dei lotti, e il prossimo (**L51c**).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L51b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
