# Prompt per la sessione successiva — L63b, lo schematico completo della scheda audio

Nome della sessione: **hi-fi preamp L63b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L63a (2026-10-21). L63 è stato diviso dall'utente in due («Prima
> l'alimentatore»): la pagina dell'alimentatore è fatta, questa è la scheda audio. Dopo viene
> **L45d2b3**, i guasti rifatti e la sintesi: il suo prompt è pronto in
> `data/2026-10-21/L45d2b2c/NEXT-SESSION-L45d2b3.md`, e chi chiude L63b lo copia qui.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L63b**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con
l'utente all'inizio**, coi numeri.

## La richiesta dell'utente (2026-10-21, a fine L45d2b2c, parola per parola)

> «dopo questo passo voglio vedere lo schematico, due pagine, ma complete (anche fosse A3) una per la
> scheda audio e una per l´alimentatore, complete senza blocchi ripetuti, crea un lotto per generare
> un full schematic human readable, subito dopo questo step»

## Che cosa ha già deciso l'utente (L63a, 2026-10-21)

«Senza blocchi ripetuti» vuol dire **«Blocco una volta, un canale»**:
- il blocco di guadagno è **uno** (otto istanze identiche nella topologia, ADR-006): si disegna **una
  volta**, completo in ogni parte, con una **tabella delle otto istanze**, delle loro sigle e dei valori
  che cambiano da un'istanza all'altra;
- i due canali sono uguali: si disegna il **sinistro** e si nomina il destro;
- tutto il resto **completo**, parte per parte, senza riquadri astratti.

Non si richiede: è deciso. Si chiede solo se i numeri cambiano la dimensione (per esempio se non entra
in A3).

## Che cosa costruire

Una pagina, `docs/preamp/schematic/audio_draw.py` → `audio.svg`, `audio.pdf`, `audio.manifest.json`,
disegnata da `circuits/preamp/preamp_audio.net` (570 parti):

- ingressi e selettore;
- trim e volume;
- il blocco di guadagno una volta, con la tabella delle istanze;
- i buffer delle uscite fisse e l'uscita principale col mute;
- i relè, i connettori, i comandi a pannello.

## Come, con quello che L63a ha già fatto

- **Il kit**, `docs/preamp/schematic/sheet_kit.py`. Leggerlo prima di tutto: la docstring dice che cosa
  rifiuta e perché.
  - Le parti si piazzano **per rete** (`two(ref, {rete: punto, rete: punto})`, `N(ref, rete)`).
  - Integrati, connettori, comparatori, MOSFET, bipolari, ponti, relè.
  - `finish()` rifiuta: fili fra reti, corti, fili sopra le parti, reti in pezzi senza nome, testi
    sovrapposti, parti o piedini non disegnati.
- **Il modello**: `docs/preamp/schematic/psu_draw.py`, la pagina dell'alimentatore (133 parti, A3). Da
  usare come esempio, non da estendere.
- **La difficoltà nuova è il manifesto di una pagina «ripiegata».** Il controllo di oggi
  (`check_schematic.py`, 2d) vuole **tutte** le parti della netlist nel manifesto. Una pagina che
  disegna il blocco una volta e il canale sinistro solo deve quindi **espandere** il disegno nelle sue
  istanze: il blocco disegnato più la tabella → otto blocchi; il sinistro più la corrispondenza → il
  destro. Il manifesto espanso si confronta con `preamp_audio.net` nei due sensi, come oggi. Una
  tabella sbagliata deve essere un test rosso, non una nota.
  - **Fatti già verificati**:
    - le reti interne di ogni istanza hanno il prefisso dell'istanza (`AL_NREF`, `BR_VPF`, `F1L_…`;
      `tag` in `gain_block()`, `circuits/preamp/gain_block.py`);
    - le sigle avanzano da un contatore che parte da `base` e dipende dai parametri (`switchable`,
      `r_in`), quindi **le istanze non hanno le stesse sigle relative**: la 1xx ha R142 e R145, la 5xx
      R541 e R544.
  - La tabella va **ricavata** (dalla numerazione di `gain_block()` o dai prefissi delle reti) e
    asserita, mai ricopiata a mano.
  - Le parti che esistono solo in alcune istanze (i relè del guadagno di B, l'R_IN di A) vanno nella
    tabella come tali.
- **Fuori dal kit**, deciderlo all'inizio guardando il codice: se l'espansione la fa il disegno (un
  manifesto già espanso, il controllo invariato) o il controllo (un manifesto con le istanze). La
  prima tiene `check_schematic.py` com'è.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#16, #22, #47, #68, #70**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L63a.
- `docs/preamp/reports/2026-10-21-L63a-schematico-alimentatore.md`.
- `docs/preamp/schematic/` (`sheet_kit.py`, `psu_draw.py`, `gain_block_draw.py`, `preamp_blocks_draw.py`)
  e `scripts/check_schematic.py`.
- Guardare la pagina con gli occhi prima di consegnarla, a pezzi e a 300 dpi:
  `/usr/bin/env PREVIEW_PNG=<file.png> PREVIEW_DPI=300 <python del venv> <script>`. Il controllo dei
  testi del kit vede le sovrapposizioni, non la leggibilità.
- Ogni controllo nuovo si prova prima su un caso che deve fallire (limitations #70; i sabotaggi di L63a
  in `data/2026-10-21/L63a/script/sabotaggi.py` sono il modello).

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
- La pagina dell'alimentatore (fatta in L63a), il layout, i gerber, G1, G2.
- I guasti rifatti (L45d2b3).

## CHIUSURA

1. `STATE.md` con L63b **fatto** nella tabella dei lotti, e il prossimo (L45d2b3).
2. Copia `data/2026-10-21/L45d2b2c/NEXT-SESSION-L45d2b3.md` in QUESTO file, aggiornando le righe che
   L63 avesse cambiato, con la riga «Nome della sessione: hi-fi preamp L45d2b3» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L63b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
