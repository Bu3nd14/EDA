# Prompt per la sessione successiva — L60, il rivelatore differenziale

Nome della sessione: **hi-fi preamp L60** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60 si rivela più grande di una sessione, **dividilo con
l'utente all'inizio** (per esempio L60a la prova sul rivelatore di oggi, L60b la costruzione), come
si è fatto con L45d2b.

## Perché questo lotto, e perché adesso

L59 (2026-10-15) ha fatto rivedere il rivelatore di continua di ADR-079 ad `adversarial-architect`.
Due difetti, opposti e con la stessa causa (il rivelatore sull'uscita vede insieme il guasto e il
segnale):
- **NC-064, bloccante**: con la musica sopra la persistenza può non scattare. Il temporizzatore
  riparte a ogni avvallamento del basso; a calcolo un guasto da +1,93 V su una fissa resta ~0,88 s
  sopra il tetto. I 762 guasti di L45d2b1 erano tutti **in silenzio**.
- **NC-065, bloccante per decisione dell'utente**: sotto la banda scatta su ingressi sani.
  Un'ondulazione del disco fra 1 e 5 Hz da 0,4–1,35 V di picco sulle fisse, a qualunque volume, o una
  sorgente che si accende con 0,65 V di continua (ADR-066), spengono l'apparecchio fino al frontale.

**Le cifre del revisore sono tutte a mano**: non ha potuto eseguire comandi. La prima cosa di questo
lotto è quindi provarle.

L'utente ha deciso (2026-10-15): **«Differenziale analogico, A dopo»** → **ADR-080**. Il rivelatore
guarda la differenza fra l'ingresso e la reazione di ogni blocco, non l'uscita. E: **«Lotto proprio,
prima»**: L60 viene prima di L45d2b2.

## Che cosa fare

1. **La prova sul rivelatore di oggi** (il banco di L45d2b1, `data/2026-10-14/L45d2b1/banco/`).
   - I guasti **con la musica**: i guasti che lasciano il blocco lineare con poca continua (|VX| <
     ~3 V) nelle sette posizioni, con la musica di prova sopra. **P10 si legge per differenza**:
     d(t) = v_jack(guasto + musica) − v_jack(musica), come V2 per A (R1, punto 7, del report).
   - La musica di prova: il K11 a −10…0 dBFS con energia a 40–80 Hz, il phono a 0,5 V; più forme
     d'onda che ripassano spesso per lo zero opposto (il caso peggiore del mascheramento).
   - **Le ondulazioni**: seni e forme realistiche da 0,5 a 10 Hz. L'utente non può misurare il phono
     («No, usiamo una stima»): l'ampiezza si stima dal caso peggiore della letteratura (risonanza
     braccio-testina 4–8 Hz a Q moderato, «many times larger» della modulazione, RIAA ~+20 dB sotto i
     50 Hz senza polo IEC; fonti nel report di L59) e **si scrive come ipotesi**, col numero.
   - La continua delle sorgenti al gradino (0,5 e 0,65 V attraverso C_IN, τ 0,32 s), agli angoli.
   - Esito atteso: NC-064 e NC-065 confermate o smentite coi numeri simulati. Se una non si conferma,
     **lo si dice all'utente prima di costruire**: è il primo «Da riaprire se» di ADR-080.
2. **Il rivelatore di ADR-080**, in `circuits/preamp/dc_detector.py` (sorgente unica).
   - F1, F2: uscita del blocco A contro uscita del buffer.
   - B: ingresso contro reazione; la soglia col guadagno fino a 3,152.
   - **La soglia contro l'errore di un blocco sano** ad alta frequenza e al clip (E6): è il numero
     che oggi non c'è.
   - **I guasti che il differenziale non vede**: quelli che spostano il nodo d'ingresso stesso (la
     polarizzazione aperta, C_IN che perde o in corto), le parti dopo il blocco, i due corti della
     scelta 9. P10 per ognuno.
   - **Il blocco A**: la presa sul gate d'ingresso (320 kΩ verso massa in continua: 0,1 µA sono
     32 mV), il rumore contro E3 / E5, i fronti dei comparatori che rientrano. **La decisione su A la
     prende l'utente** coi numeri; se non regge, A resta visto attraverso F1 e F2.
   - Poi lo stesso banco del punto 1 sul rivelatore nuovo: 0 guasti fuori da P10 con e senza musica,
     nessuno scatto con le ondulazioni e con la continua delle sorgenti.
   - **NC-068**: i commenti allineati alle cifre in vigore (il 91,5 ms, il seno a 10 Hz).
   - Netlist, disegno, `run_tests.sh`, la regressione.
3. **NC-066 e NC-067**: se il lotto le tocca, si portano all'utente; altrimenti restano.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L59 e L45d2b1.
- **ADR-080** (la decisione), ADR-079 (che cosa resta), ADR-072, ADR-069, ADR-066.
- `reports/2026-10-15-L59-architetto-avversariale.md` (i rilievi e le fonti) ed
  `reports/2026-10-15-L59-esiti-architetto.md` (le decisioni e il confronto con le altre proposte).
- `NONCOMPLIANCE.md`: NC-063…068.
- `circuits/preamp/dc_detector.py`, `gain_block.py` (il nodo di reazione FB, R_f, R_g), `preamp_audio.py`.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- **Un vincolo per il layout (G2), dal rilievo R5 di L59**: le correnti del rivelatore (lo scarico
  di C_T, fino a ~20 mA per ~16 µs) non devono scorrere nella massa audio. Isola di massa propria
  riportata alla stella in un punto, e qualche centinaio di Ω in serie fra ogni comparatore e il suo
  C_T. Con le prese sul gate di A e sul nodo di reazione vale il doppio.
- Il rivelatore resta **analogico e in hardware** (PR-24): il micro non entra nella protezione.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando;
  - un comando che contiene la parola «git» anche solo in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito: in
  L52 e in L59 Bash gli è stato rifiutato.

## NON fa parte di questo lotto

- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063): il suo prompt pronto è nella storia del
  repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`), da aggiornare con ADR-080 quando si
  riprende. L45d2b3 (i guasti rifatti), L58 (la diagnosi).
- La reazione a due tempi (NC-066), se il lotto non la tocca.
