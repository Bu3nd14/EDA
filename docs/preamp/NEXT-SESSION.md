# Prompt per la sessione successiva — L60b, il rivelatore esce

Nome della sessione: **hi-fi preamp L60b** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60b**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60b si rivela più grande di una sessione, **dividilo con
l'utente all'inizio**.

## Perché questo lotto, e perché adesso

ADR-081 (L61) ha tolto il rivelatore di continua dal progetto: la Stax è protetta dal condensatore
d'uscita da 1 µF, la principale e la fissa 1 dalla protezione a valle. L60 è stato diviso
dall'utente all'inizio in tre parti («Tre parti»):
- **L60a (fatto)**: le scelte 6, 8, 9 e 10 che il rivelatore copriva → **ADR-082**;
- **L60b (questo)**: togliere il rivelatore, più le due modifiche piccole di ADR-082;
- **L60c**: il condensatore da 1 µF della Stax dopo il relè di mute, e le sue prove.

## Che cosa fare

1. **Togliere il rivelatore, da sorgente unica.** La mappa (da L60a; le righe sono indicative,
   rileggerle prima di toccare):
   - `circuits/preamp/dc_detector.py`: eliminarlo, e `spice/preamp/dc_detector.subckt` che genera
     (nessun deck fuori da `docs/preamp/data/` lo include);
   - `circuits/preamp/preamp_audio.py`: l'import (~:85), la lista `fouts` (~:266, :321, il `return`
     a :410 e i due spacchettamenti a :508 e :619 cambiano insieme), il commento e la rete `DC_FLT`
     su J4 pin 4 (~:597–621) e l'istanza del rivelatore. **Da decidere**: J4 resta a quattro pin col
     4 libero, o torna a tre (cambia `check_psu_harness.py` e `psu.py` insieme);
   - `circuits/preamp/psu.py`: i commenti ~:607–608 e ~:642–660, R548, C535, D525–D527, R549,
     `DC_FLT_IN` e PA1 (pin 17) ~:662–671, l'intestazione di J4 ~:676, il conteggio degli avvisi
     ERC ~:686–687 (23 → 24 con PA1 di nuovo libero: verificarlo, non assumerlo);
   - il firmware `firmware/preamp_timer/`: `src/timer_core.h` (T_DC_PERSIST_US, il commento di PA1,
     `dc_flt_in`, `t_dc`), `src/timer_core.c` (PA1 nella tabella dei liberi ~:29, la logica
     ~:215–236), `spec/timer_spec.md` (§ 4.9 ~:178–193 e le righe ~:5–20, 46, 66, 70, 210, 222–223;
     le righe ~:142, 148 parlano del rivelatore di **rete**, da non toccare), i test (`mondo.h`,
     `mondo.c`, `ponte.c` con la colonna opzionale `v(dc_flt_in)`, `test_sequenze.c` ~:370–435,
     `run_host_tests.sh` coi falsi 31–34: 23 → 19);
   - `scripts/check_psu_harness.py` (~:13, :49–50), `scripts/run_tests.sh` (~:337, il conteggio dei
     falsi a :342 e :352);
   - i disegni: `docs/preamp/schematic/preamp_blocks_draw.py` (gli asserti ~:251–256, :690–707, la
     didascalia, la riga ~:735) e `psu_blocks_draw.py` (~:143–148, :404–405; la :183 è il rivelatore
     di rete);
   - ordine di rigenerazione: `preamp_audio.py` → `psu.py` → i due `*_blocks_draw.py` →
     `run_tests.sh`.
2. **Due pin e due fili per ciascun rail fra le schede** (ADR-082 punto 2): J1, oggi VPLUS, GND,
   VMINUS su tre pin. Lato audio e lato alimentatore, il controllo del cablaggio, i disegni. Quanti
   pin per la massa lo si chiede all'utente se non è ovvio.
3. **Q127 in SOT-223** (ADR-082 punto 4): `circuits/preamp/gain_block.py`, il moltiplicatore di Vbe
   (~:590), da `MMBT5551` a `DZT5551` con l'impronta SOT-223 come ADR-068 (il modello SPICE resta
   MMBT5551, stesso die); aggiornare il commento sull'accoppiamento termico col finale (ADR-034:
   la linguetta è il collettore, NX, non il rail). Il blocco rigenerato e la regressione dei deck
   veloci se la suite la tocca.
4. **Chiudere NC-064…NC-068** togliendo il rivelatore; NC-042 avanza.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L60a e L61.
- **ADR-082** e **ADR-081** (le decisioni), ADR-079 (che cosa c'è da togliere), ADR-068 (il modello
  per il cambio di package), ADR-034.
- `reports/2026-10-15-L60a-scelte-scoperte.md`.
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

- **L60c**: il condensatore da 1 µF della Stax dopo K3, la geometria del mute su quell'uscita, E9,
  P10 col carico della Stax, V2, l'inserimento a caldo; il relè rinforzato solo se quelle prove non
  passano. Il valore di `CFIX2` (`("STAX", "4.7u")` in `preamp_audio.py`) non si tocca qui.
- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063): il suo prompt pronto è nella storia del
  repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`), da aggiornare con ADR-081 e ADR-082.
  L45d2b3 (i guasti rifatti), L58 (la diagnosi).
