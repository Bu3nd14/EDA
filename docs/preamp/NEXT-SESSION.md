# Prompt per la sessione successiva — L60c2, la Stax ha il suo condensatore nel sorgente

Nome della sessione: **hi-fi preamp L60c2** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60c2**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60c2 si rivela più grande di una sessione, **dividilo con
l'utente all'inizio**: è un lotto M, una parte nuova, il circuito e le prove.

## Perché questo lotto, e perché adesso

ADR-081 (L61) protegge la Stax col condensatore d'uscita della fissa 2 a **1 µF film**. ADR-082 (L60a)
lo voleva **dopo** il relè di mute K3, perché K3 che cede (l'isolamento fra bobina e contatti) oggi
lascia 12 V per sempre sulla Stax. La prima parte di L60c, sul banco, ha mostrato che non regge
(`reports/2026-10-15-L60c1-stax-condensatore-prova.md`, `data/2026-10-15/L60c1/`).
- **Il condensatore dopo K3** porta alla Stax la continua del buffer a ogni mute: 6,0–27,3 mV, cioè
  77–90 dB SPL all'orecchio, contro i 100 µV di V2. Col bleed di oggi, inoltre, il blocco al rail
  dura 129–135 ms.
- **Due condensatori** (10 + 1 µF) tengono il mute a zero, ma K3 che cede con 1 kΩ dura 131–138 ms.
- **La geometria di oggi con 1 µF** regge tutto (118–124 ms al rail, 0,161–0,178 dB a 20 Hz), tranne
  K3 che cede.

L'utente ha scelto **«Relè rinforzato»** → **ADR-084**:
1. il condensatore da 1 µF **resta prima di K3**, nel posto del 4,7 µF di oggi: `BUFFER F2 → 47 Ω →
   1 µF → K3 → jack`, geometria iii di ADR-044 invariata;
2. **K3 diventa un relè con isolamento rinforzato fra bobina e contatti**, così il cedimento non è più un
   guasto singolo credibile;
3. K2 e K4 restano G6K.

## Che cosa fare

1. **Il relè.** Va scelto sul datasheet, e il datasheet va scaricato in `vendor/relays/` con la sua
   provenienza (`bom-component-manager` se serve). Requisiti:
   - **isolamento rinforzato fra bobina e contatti dichiarato** (il G6K ha isolamento base, 1500 V
     efficaci, `vendor/relays/omron/G6K/en-g6k.pdf`);
   - **due deviatori** (un polo per canale) e **bobina a 12 V** (`VRELAY`, ADR-048), per contatti di
     segnale (dorati o biforcati, bassa corrente);
   - si leggono, e si confrontano con ADR-044, la capacità del contatto aperto (0,1 pF misurati con
     ADR-044; il limite è ~2,4 pF, oltre si riapre), il tempo di trasferimento (1 ms), intervento e
     rilascio (≤ 3 ms in V2), la resistenza di contatto e la corrente della bobina (il bilancio di
     `VRELAY` sta nel commento di `preamp_audio.py` ~:426–450);
   - se nessun relè regge, **si torna all'utente** con i due condensatori da rifinire (ADR-084,
     «Da riaprire se»).

   La scelta, coi candidati e i numeri, si fa con l'utente per nome.
2. **Il circuito.** In `circuits/preamp/preamp_audio.py`:
   - il condensatore della fissa 2 a **1 µF** (`("STAX", "4.7u")` in `channel()` ~:265). Il commento
     di ADR-007 (~:278–285) va riscritto: «4,7 µF su tutte e due le fisse» non vale più. Va citata
     ADR-081 / ADR-084 e il nuovo E9, e lo schema in testa al file (~:14) va aggiornato;
   - **K3 come parte diversa**: oggi i tre relè di mute nascono nello stesso ciclo (~:473–478, valore
     `G6K-2F-Y MUTE{i+1}`), e la piedinatura `K_COM/K_NO/K_NC` è quella del G6K (~:520–522). Serve
     l'impronta del relè nuovo e la sua piedinatura dal datasheet;
   - controllare che cosa del 2e (`scripts/run_tests.sh`) legge il valore o il modello del relè;
   - ogni valore nuovo porta il commento con la sua ADR;
   - netlist, disegni (`preamp_blocks_draw.py`), `run_tests.sh`.
3. **Le prove sulla fissa 2, col carico della Stax** (50 kΩ, ADR-081). Il banco di
   `data/2026-10-15/L60c1/` è il punto di partenza: si riproducono prima i suoi numeri di G0.
   - **E9** sul circuito.
   - **P10** ≤ 125 ms: il blocco al rail e **i guasti di L45a che portano continua** sui blocchi A e
     F2 (L60c1 ha fatto solo i due al rail); un pin di un rail aperto è già 0.
   - **V2** sulla fissa 2 con 1 µF: il generatore di `tb_v2_casopeggiore.cir`
     (`data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py`) legge i valori dalla netlist. Il
     contatto aperto va coi valori del relè nuovo.
   - **L'inserimento a caldo** (in L60c1 era nullo).
4. **NC-042 avanza**: la scelta 6 su K3 si chiude col relè nel sorgente.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L60c1, L60b, L60a e L61.
- **ADR-084**, ADR-082, ADR-081, **ADR-044** (la geometria del mute e i suoi «Da riaprire se»),
  ADR-048 (`VRELAY` a 12 V), ADR-007, ADR-021 / ADR-023.
- `reports/2026-10-15-L60c1-stax-condensatore-prova.md` e `data/2026-10-15/L60c1/README.md`.
- `NONCOMPLIANCE.md`: NC-042, NC-046 (il tetto delle fisse).

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Nei deck in AC l'interruttore con isteresi di ngspice resta aperto nel punto di lavoro, anche col
  flag `ON`: un contatto chiuso si scrive come resistenza (L60c1).
- Le forme d'onda del banco (`run/`, ~8 GB) non si committano.

## NON fa parte di questo lotto

- L45d2b2 (i diodi, il comando, i 5 V, i massimi, NC-063): il suo prompt pronto è nella storia del
  repository (commit 22315ab1, `docs/preamp/NEXT-SESSION.md`), da aggiornare con ADR-081…084 (il
  rivelatore non c'è più, J1 ha sette pin). L45d2b3 (i guasti rifatti), L58 (la diagnosi).
- La fissa 1 e la principale: contano sulla protezione a valle (ADR-081), e K2 e K4 restano G6K.
