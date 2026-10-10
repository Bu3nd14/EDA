# Prompt per la sessione successiva — L51c, il dossier rigenerato: le schede di prova e la chiusura

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L51c**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'utente, il 2026-10-09 dopo L49b: «rigeneriamo il dossier, mettilo nel prossimo lotto abbiamo
cambiato molto, poi lo passiamo all'avversariale di nuovo, poi affrontiamo G1». All'inizio di L51
l'ha diviso in **«Tre parti»**:
- **L51a**, la scheda audio: **fatto**, 2026-10-09;
- **L51b**, l'alimentatore e il firmware: **fatto**, 2026-10-09/10;
- **L51c**, questo: le schede di prova e l'assieme di L49, «Cosa questo dossier non dice», la
  provenienza, le righe `Stato:` restanti, il primo `index.html` nuovo.

Dopo: **L52** l'architetto avversariale sul dossier nuovo, poi **G1**, poi L45 FMEA e L50 massa e
terra.

Il dossier lo legge **solo l'utente** e **non si taglia**: si rigenera, senza avvisi di
obsolescenza.

## Come la seconda parte ha lasciato il generatore (leggere prima del codice)

- **`PARTI = ("audio", "alimentatore")`.** Questo lotto aggiunge `"schede"`. Con tutte e tre le
  parti il generatore **scrive accanto a sé** `index.html`, le figure, gli schemi copiati e il
  summary: è il primo `index.html` da L42, e sostituisce quello.
- **La sezione `s14`, «Cosa questo dossier non dice», non gira com'è.** Sta sotto
  `if "schede" in PARTI:` e usa tre nomi che non esistono più: `all_kf0`, `kf_parts`,
  `mu["cima_deck"]`. Parla ancora di S del mute con la cima a 12 mA (ADR-050), e ha punti
  sull'alimentatore da rileggere contro le sezioni di oggi. Va riscritta, non riaccesa.
- **Le guardie del giorno**:
  - `sa()` per la scheda audio (`AUDIO_DA`, `AUDIO_PERMESSI` con la ragione stampata);
  - `ps()` per l'alimentatore (`PSU_DA = "2026-10-09"`, senza eccezioni);
  - per le schede di prova serve la stessa guardia, col giorno di L49.
- Il testo cita le sezioni con `sez()`, mai il numero a mano.
- **I sabotaggi**: L51a 27 su 27, L51b 30 su 30 (`data/2026-10-09/L51b/script/sabotaggi.py`).
  Rieseguirli tutti a fine lotto, insieme a quelli nuovi.

## Il mandato

- **Le schede di prova di L49** (L49a la scheda audio, L49b l'alimentatore, i toroidali e
  l'assieme nel Pesante 3U): le immagini, il DRC, i vincoli scritti, NC-048 chiusa. Le cartelle
  sono quelle dei due lotti. Decidere con l'utente quanto mostrarne e se rieseguire il DRC oggi.
- **«Cosa questo dossier non dice»**, riscritta sul progetto di oggi:
  - la distorsione di L46a e L46b, da verificare sul blocco di oggi;
  - i modelli comportamentali dell'alimentatore;
  - il ferro dei trasformatori nella stima del calore (un'ipotesi, L51b);
  - i falsi sul circuito (nessuno dopo L41b2);
  - `main_attiny.c`, che non è scritto.
- **La provenienza**.
- **Le righe `Stato:` restanti**, una per una con l'utente: ADR-009, 027, 032, 038, 039, 040,
  049, 050, 061, 062.
- **La stampa A4**: `stampa_a4.py` sulla pagina completa.

## Trovato in L51b, per l'utente (non correggere da sé)

In `circuits/preamp/psu.py`:
- il commento di `C_VRELAY` cita 61,1 ms (L47c2a); col selettore e i rail di oggi la tenuta è
  48,3 ms;
- quello di `C_RAW` cita la valle del grezzo di L41a, 18,1 V; oggi è 17,9 V.

Il dossier lo dice nella sezione della potenza. Chiedere all'utente se correggerli, e dove: è un
cambio del sorgente, fuori dal dossier.

## All'inizio, con l'utente

Misurare prima (quanto pesano le schede di L49 nella pagina, cosa resta vero di `s14`), poi
chiedere per nome e senza sigle.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md` (**54 voci**).
- `docs/preamp/STATE.md`: «In breve», **L51b**, **L51a**, L49a, L49b.
- `docs/preamp/dossier/build_dossier.py` per intero.
- `data/2026-10-09/L51b/README.md` e `data/2026-10-09/L51a/README.md`.
- I report di L49a, L49b, L51a, L51b.

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
- `sed -i ''` di macOS non conosce `\b`; un nome locale nel generatore può coprire un modulo
  (`sp` è `svgplot`) o una funzione (`num`): due errori di L51b.
- `docs/preamp/data/` è versionato per regola: i file grossi vanno in `.gitignore` prima del commit.
- `zsh` espande un `=` a inizio parola; un glob senza corrispondenze ferma il comando: `(N)` in coda.

## NON fa parte di questo lotto

- L'architetto avversariale (**L52**) e il gate (**G1**).
- Cambiare il circuito, i deck o il firmware: il dossier li descrive com'è oggi. Un difetto trovato
  rigenerando si scrive e si porta all'utente, non si corregge da sé.
- La FMEA (L45), la massa e la terra (L50), il layout vero (G2).

## CHIUSURA

1. `STATE.md` con L51c **fatto** nella tabella dei lotti, e il prossimo (**L52**).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L51c`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
