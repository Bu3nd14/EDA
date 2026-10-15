# Prompt per la sessione successiva — L60, il rivelatore esce e la Stax ha il suo condensatore

Nome della sessione: **hi-fi preamp L60** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60 si rivela più grande di una sessione, **dividilo con
l'utente all'inizio**. Per esempio: L60a le scelte rimaste scoperte e la rimozione, L60b le prove
sulla fissa 2.

## Perché questo lotto, e perché adesso

L59 ha trovato due difetti bloccanti del rivelatore di continua sulle uscite: con la musica sopra può
non scattare (NC-064), e sotto la banda scatta su ingressi sani (NC-065). ADR-080 aveva deciso di
rifarlo differenziale.

**L61 (2026-10-15) ha cambiato il piano.** L'utente: «il nodo sono le STAX, non voglio romperle […]
Se non serve proteggerle il rilevatore cade». Dai documenti, la Stax SRM-T1 è in continua con ×1000
di guadagno e senza protezione propria, quindi va protetta. Il Singxer SA-1 ha una protezione dalla
continua dichiarata dai rivenditori. Il finale cj EV250 blocca la continua col trasformatore.
L'utente ha scelto **«Condensatore 1 µF»** e ha firmato la nuova PR-30, «Firmo così» → **ADR-081**:
- **la fissa 2 (Stax) ha il condensatore d'uscita da 1 µF** al posto di 4,7 µF: a calcolo 0,15–0,18 dB
  a 20 Hz e 111–123 ms sopra 0,87 V col carico della Stax, per il blocco al rail;
- **PR-30 e P10 valgono per la catena di oggi**: la Stax al più 125 ms col suo carico; la principale
  e la fissa 1 protette a valle; un apparecchio nuovo a valle fa rivedere il preamp;
- **il rivelatore di continua esce dal progetto**. ADR-080 è superata, e NC-064…NC-068 si chiudono
  togliendolo.

## Che cosa fare

1. **Le scelte rimaste scoperte, con l'utente, prima di togliere niente.** ADR-072 affidava al
   rivelatore, oltre al blocco al rail (scelta 1), le scelte **6, 8, 9 e 10** di
   `data/2026-10-14/L45d1/scelte_L45d2.pdf`:
   - **6**, l'isolamento bobina-contatti di un relè che cede (12 V sul segnale);
   - **8**, il filo del rail positivo aperto fra le schede (13,3 V al jack, L45c1);
   - **9**, il condensatore d'uscita in corto;
   - **10**, il calore da solo. NC-066 dice «coperto dal sorvegliante a 106 ms»: verificarlo.

   Per ciascuna, con la PR-30 nuova: che cosa arriva sulla Stax (il condensatore da 1 µF la copre?),
   e che cosa sulla principale e sulla fissa 1, che contano sulla protezione a valle. Le domande per
   nome, coi numeri; le risposte dell'utente tra virgolette nel report. Una decisione nuova se serve.
2. **Togliere il rivelatore**, da sorgente unica:
   - `circuits/preamp/dc_detector.py` e il suo uso in `preamp_audio.py`;
   - la linea `DC_FLT` su J4 pin 4, D525–D527 e R549 in `psu.py`;
   - la lettura di PA1 nel firmware e la spec 4.9, coi falsi del firmware;
   - i controlli della suite e i disegni che lo citano.

   Netlist e disegni rigenerati, `run_tests.sh`.
3. **Il condensatore da 1 µF film sulla fissa 2** (`preamp_audio.py`: oggi un solo valore per le due
   fisse, `("STAX", "4.7u")`), col commento che punta ad ADR-081 al posto della nota di ADR-007.
4. **Le prove sulla fissa 2 con 1 µF**:
   - E9 col banco, su ogni carico del contesto d'uso;
   - P10 col carico della Stax (50 kΩ), il blocco al rail e i guasti di L45a che portano continua,
     ≤ 125 ms;
   - V2: il mute e i suoi colpi, perché la geometria di ADR-044 fu misurata con 4,7 µF;
   - l'inserimento a caldo.
5. **Chiudere NC-064…NC-068** togliendo il rivelatore, e aggiornare NC-042.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L61 e L45d2b1.
- **ADR-081** (la decisione), ADR-072 (le scelte che il rivelatore copriva), ADR-079 (che cosa c'è
  da togliere), ADR-044, ADR-007.
- `reports/2026-10-15-L61-stax.md` e `data/2026-10-15/L61/script/stax_e9.py`.
- `NONCOMPLIANCE.md`: NC-042, NC-063…068.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando;
  - un comando che contiene la parola «git» anche solo in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.

## NON fa parte di questo lotto

- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063): il suo prompt pronto è nella storia del
  repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`). Va aggiornato con ADR-081 quando si
  riprende, perché parte di quel lotto presupponeva il rivelatore. L45d2b3 (i guasti rifatti), L58
  (la diagnosi).
- Verificare la protezione del Singxer aprendolo: è un «Da riaprire se» di ADR-081, non un lavoro di
  questo lotto.
