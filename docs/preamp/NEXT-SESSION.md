# Prompt per la sessione successiva — L63, lo schematico completo leggibile

Nome della sessione: **hi-fi preamp L63** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L45d2b2c (2026-10-21), su richiesta dell'utente in quella
> sessione. Dopo viene **L45d2b3**, i guasti rifatti e la sintesi: il suo prompt è già pronto in
> `data/2026-10-21/L45d2b2c/NEXT-SESSION-L45d2b3.md`, e chi chiude L63 lo copia qui.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L63**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con
l'utente all'inizio** (per esempio: L63a la scheda audio, L63b l'alimentatore).

## La richiesta dell'utente (2026-10-21, a fine L45d2b2c, parola per parola)

> «dopo questo passo voglio vedere lo schematico, due pagine, ma complete (anche fosse A3) una per la
> scheda audio e una per l´alimentatore, complete senza blocchi ripetuti, crea un lotto per generare
> un full schematic human readable, subito dopo questo step»

## Che cosa costruire

Due pagine, generate dal sorgente e leggibili da una persona:
1. **La scheda audio** (`circuits/preamp/preamp_audio.py`, 570 parti): ingressi e selettore, trim,
   volume, i blocchi di guadagno, le uscite col mute, i relè, i connettori.
2. **L'alimentatore** (`circuits/preamp/psu.py`, 133 parti): trasformatori, raddrizzatori, rail,
   VRELAY, i 5 V, il sorvegliante, il temporizzatore, il comando dei relè, i connettori.

Formato A3 se serve (anche più grande, se l'utente lo accetta), SVG e PDF.

**Da chiarire con l'utente all'inizio, per nome e senza sigle**: che cosa vuol dire «senza blocchi
ripetuti». La lettura proposta da L45d2b2c:
- il blocco di guadagno è **uno** (otto istanze identiche, ADR-006): si disegna **una volta**, completo
  in ogni parte, con una tabella delle istanze e delle loro sigle;
- i due canali sono uguali: si disegna il sinistro e si nomina il destro;
- tutto il resto **completo**, parte per parte, senza riquadri astratti.
Se l'utente intende altro (per esempio ogni istanza disegnata), cambia la dimensione del lavoro: lo si
dice coi numeri prima di cominciare.

**Come, non solo che cosa** (limitations #16, #5): il piazzamento automatico di uno schematico
analogico leggibile non esiste; SKiDL `generate_schematic()` è inutilizzabile. Lo strumento che
funziona nel repo è il disegno a mano in codice con schemdraw **più un manifesto verificato contro la
netlist nei due sensi** (`docs/preamp/schematic/gain_block_draw.py`, `scripts/check_schematic.py`, il
controllo 2d di `run_tests.sh`). Le due pagine nuove si fanno allo stesso modo, e il controllo 2d le
deve prendere da sé (cerca ogni `docs/*/schematic/*.manifest.json`). Un disegno che non corrisponde
alla netlist è un test rosso, non una nota.

Riusare: il disegno del blocco (completo, 61 dispositivi), gli schemi a blocchi della scheda e
dell'alimentatore (`preamp_blocks_draw.py`, `psu_blocks_draw.py`, con le loro asserzioni nel 2f), i
disegni del dossier (L32b, L51a–c).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#5, #16, #22, #47, #68**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L45d2b2c.
- `docs/preamp/schematic/` e `scripts/check_schematic.py`.
- Guardare le pagine con gli occhi prima di consegnarle: il controllo verifica le connessioni, non la
  leggibilità. L'anteprima PNG: `/usr/bin/env PREVIEW_PNG=<file.png> <python del venv> <script>`
  (`gain_block_draw.py` lo fa già); la miniatura di Quick Look taglia i disegni larghi.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc, un `python3 -c` dentro un altro comando,
    gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- I disegni girano col Python del venv (`/Users/roberto/EDA/env/venv/bin/python3`, schemdraw 0.23).
- Le domande all'utente si fanno per nome, senza sigle.

## NON fa parte di questo lotto

- **Nessun cambio al circuito.** Se disegnando si trova un errore nel sorgente, lo si scrive nel report
  e lo si porta all'utente; la topologia sta solo in `circuits/preamp/*.py`.
- Il layout, i gerber, G1, G2.
- I guasti rifatti (L45d2b3).

## CHIUSURA

1. `STATE.md` con L63 **fatto** nella tabella dei lotti, e il prossimo (L45d2b3).
2. Copia `data/2026-10-21/L45d2b2c/NEXT-SESSION-L45d2b3.md` in QUESTO file, aggiornando le righe che
   L63 avesse cambiato, con la riga «Nome della sessione: hi-fi preamp L45d2b3» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L63`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
