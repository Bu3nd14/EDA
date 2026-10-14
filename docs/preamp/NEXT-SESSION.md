# Prompt per la sessione successiva — L59, la revisione avversariale del rivelatore di continua

Nome della sessione: **hi-fi preamp L59** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L59**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

L45d2b1 (2026-10-14) ha costruito il rivelatore di continua sulle uscite dei blocchi (ADR-072,
realizzato da **ADR-079**). Sul banco nessun guasto del blocco resta fuori da P10, e la musica di
prova sopra i 16 Hz non lo fa scattare.

**L'utente non è certo che il rivelatore sia giusto** (2026-10-14, dopo la chiusura di L45d2b1):
«non sono certo che il rilevatore di continua sia OK, un segnale sotto i 16Hz é un input assolutamente
plausibile, modifica il piano per far rivedere il rilevatore di continua all'avversariale come
prossima cosa».

Quindi, **prima di L45d2b2**, l'architetto avversariale rivede il rivelatore. L45d2b2 aspetta: il
suo prompt pronto è nella storia del repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`), e
gli esiti di questa revisione possono cambiarlo.

## Che cosa fare

1. **Lanciare `adversarial-architect`** come agente nuovo (mai un fork di questo contesto),
   **alla cieca** rispetto ad altre revisioni. Il soggetto è **il prodotto**, il rivelatore come
   circuito e come decisione, non la toolchain né il banco come strumenti.
   - La consegna è neutra, sull'intero rivelatore. **Non gli si indica il punto dei 16 Hz**: è
     scritto nei limiti dichiarati di ADR-079 e del report, e il controllo è se il revisore lo
     solleva e quanto pesa gli dà.
   - Il dubbio dell'utente si scrive nel report degli esiti, **comunque vada**, e si risponde
     comunque.
   - Che cosa gli si chiede di contestare:
     - **il principio**: la persistenza fuori da una finestra invece di un filtro;
     - la soglia e il tempo, contro P10 e contro **la musica che il preamp deve far passare**,
       comprese le sorgenti e le ipotesi su cosa sia «musica»;
     - l'alimentazione da VPLUS o VRELAY, e lo spostamento a VDP / 2 con la 634k verso VMINUS;
     - la linea su J4 e i tre gate in hardware, la ritenuta nel firmware, l'inibizione
       all'accensione;
     - le alternative scartate di ADR-079, e se ce ne sono di migliori;
     - le semplificazioni possibili, o l'eccesso di progetto.
   - **Il confronto con la letteratura, cercando online** (richiesta dell'utente, 2026-10-14:
     «aggiungi per favore il task di rivedere e confrontare con letteratura e cercando online
     (sempre a carico dell'avversariale)»). Il revisore **cerca e cita le fonti**, col link e con
     ciò che dicono, e confronta il rivelatore di oggi con:
     - come si rivela la continua nei finali e nei preamplificatori: i protettori di continua dei
       finali, i servo, i rivelatori a finestra e a integrazione, i circuiti dei costruttori e delle
       note applicative, i progetti pubblicati (Self, Cordell, le riviste, i forum tecnici seri);
     - quanta energia sotto i 20 Hz porta davvero la musica e le sorgenti: le canne d'organo da
       16 Hz e sotto, gli effetti dei film, i sintetizzatori, le ondulazioni e l'eccentricità del
       disco, i filtri subsonici degli stadi phono;
     - le soglie e i tempi che usano gli altri (quanta continua, per quanto), e i criteri di danno
       per gli altoparlanti.

     Ogni rilievo che nasce dal confronto porta la fonte. Ciò che non si trova si dice, non si
     suppone.
   - Che cosa deve leggere:
     - `docs/preamp/PRB.md` (il contratto, PR-22…PR-30), `REQUIREMENTS.md` (P10, E9, E6), ADR-069,
       ADR-072, ADR-079;
     - `circuits/preamp/dc_detector.py`;
     - `reports/2026-10-14-L45d2b1-rivelatore-continua.md`, `data/2026-10-14/L45d2b1/` (README,
       `scelte/dimensiona.py`, `banco/guasti.md`, `banco/piccole.csv`, `studio/`), NC-063.
   - Il prodotto è un **report datato** di rilievi in `docs/preamp/reports/`
     (`2026-…-L59-architetto-avversariale.md`). Ogni rilievo ha il requisito, l'evidenza e la
     severità proposta, come in L43a e L52.
2. **Gli esiti con l'utente** (`2026-…-L59-esiti-architetto.md`, come in L43a e L52).
   - Ogni rilievo si presenta per nome, **senza sigle**, coi numeri.
   - L'utente decide che cosa diventa non conformità e con quale severità, e che cosa si rifà.
   - **Se cambia una decisione** (ADR-072 o ADR-079: per esempio come trattare i segnali sotto i
     16 Hz, o un rivelatore diverso), si scrive una ADR nuova, che **non riscrive** le vecchie.
3. **Il piano dopo.**
   - Se il rivelatore va rifatto, il lavoro diventa un lotto proprio, prima o dentro L45d2b2:
     lo decide l'utente.
   - Se tocca il PRB (i segnali sotto i 16 Hz sono un requisito che oggi non c'è: E9 parte da
     20 Hz), serve la sua ADR.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md` (il ruolo di `adversarial-architect`), `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L45d2b1.
- `NONCOMPLIANCE.md`: NC-042, NC-063.
- I report di L43a e L52 (`reports/2026-09-27-L43a-*`, `reports/2026-10-12-L52-*`): come si è fatta
  la revisione avversariale le altre volte, e come se ne sono presentati gli esiti all'utente.
- Le memorie: il controllo cieco (non cercare tu il difetto che il revisore deve trovare; dichiara
  che cosa hai già guardato), la revisione del prodotto e non dell'ambiente, le domande senza sigle.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Nessun cambio al circuito in questo lotto, salvo che l'utente lo chieda nella sessione.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando;
  - un comando che contiene la parola «git» anche solo in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.

## NON fa parte di questo lotto

- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063), L45d2b3 (i guasti rifatti), L58 (la
  diagnosi). Se un rilievo li tocca, lo si dice e lo si lascia al suo lotto.

## CHIUSURA

1. `STATE.md` con L59 **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo (di norma L45d2b2: si riparte dal testo del commit
   22315ab1, aggiornato con gli esiti), con la riga «Nome della sessione: hi-fi preamp <lotto nuovo>»
   subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L59`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
