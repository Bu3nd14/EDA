# Prompt per la sessione successiva — L33

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L33** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**Il lotto precedente ha chiuso NC-030**: `tb_noise_vectors.cir` scrive di nuovo
dati.

1. **Il blocco 2g vede i vettori di rumore.** `scripts/check_deck_refs.py`
   controlla ogni `onoise_<x>`/`inoise_<x>` fuori da commenti e virgolette.
   - I suffissi di sotto-sorgente sono letti da un deck sonda.
   - È stato fatto cadere sul deck di allora (4 nomi morti) e su 13 sabotaggi,
     senza falsi allarmi sui deck di `main` e su quelli pre-L27.
2. **I vettori sono rinominati con una mappa per nodi**, dall'include di L4 a
   quello di oggi, e non da un elenco.
   - **Tre nomi vivi erano già sbagliati**: `onoise_q122`, `r120` e `r138`
     indicavano oggi il VAS, l'altra degenerazione e R_g.
   - Il suggerimento del mandato, «VAS Q122», era sbagliato: la lista di L4 non
     conteneva il VAS.
3. **Una premessa del mandato non era vera**: `tb_noise_breakdown.cir` non stampa
   la ripartizione per dispositivo a 1 kHz. **Verificare i numeri e le frasi dei
   mandati resta la regola.**
4. **I dati** stanno in `data/2026-09-15/L31/`. Il README di quel lotto dichiara
   già la provenienza corretta dell'LSK489: segnaposto `LSK489X`, `KF = 0`.

Voci: **15 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** È il più piccolo fra gli aperti. Gli altri
aspettano qualcosa:
- L29 una soglia dell'utente su V2;
- L30 l'alimentatore;
- L28 va fatto prima di G2.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L31 e L32, «Prossimo passo
   concreto» e la riga L33 della tabella dei lotti.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-031**, e le frasi di **NC-004** e
   **NC-013** sull'LSK489.
4. **ADR-013**: la regola di provenienza per l'LSK489. Le ADR non si riscrivono.
5. **Cosa si simula davvero**:
   - `circuits/preamp/gain_block.py` (istanza `LSK489X`);
   - `spice/preamp/placeholder_devices.lib` (il segnaposto);
   - `models/jfet/lsk489.lib` (il modello del costruttore, `LSK489A`, che nessun
     deck include).
6. **Cosa si dichiara**:
   - il commento di L22 nei deck di `spice/preamp/tb/`;
   - `tb_trim.cir`;
   - i README di `data/2026-09-14/L12/`, `L27/` e `L16/`.
7. **`docs/preamp/dossier/build_dossier.py`**: da L32 ricava la provenienza dagli
   `.include`. È il codice da riusare se serve un guardiano, non da riscrivere.

## IL LOTTO: L33 — le etichette di provenienza dell'LSK489

### Cosa fare

1. **Baseline, contata e non copiata.**
   - Ritrovare con una ricerca ogni frase che chiama «vendor» o «reale»
     l'LSK489 simulato, e contarle.
   - NC-031 dice **tredici deck** (dodici col commento di L22, più
     `tb_trim.cir`) e **tre README**. Se il conto è diverso, vale il conto.
2. **Decidere se serve un guardiano** che confronti la provenienza dichiarata da
   un deck con quella dei suoi `.include`. È il punto 3 di NC-031.
   - La decisione e il ragionamento vanno nel report.
   - **Se il guardiano si fa**, va fatto cadere sullo stato di oggi prima di
     correggere le frasi, e non deve dare falsi allarmi sui deck già giusti.
3. **Correggere i commenti dei deck.** Solo righe di commento.
   - Va **provato** che il diff tocca solo righe `*`: con uno script, non a
     occhio.
   - Va provato che il guardiano del 2g e `run_tests.sh` restano verdi.
4. **I README datati si precisano con una nota** che ne lascia intatto il testo,
   perché sono output di un'esecuzione datata.
5. **Chiudere NC-031** in `NONCOMPLIANCE.md`, con l'evidenza. Se la frase di
   NC-004 «nel repo solo l'LSK489 ha rumore 1/f» va precisata, si precisa lì,
   senza toccare le ADR.

### I vincoli

- **Nessun valore del circuito cambia**, e nessun modello si sostituisce: la
  sostituzione vera è la Fase 4 (NC-017).
- **Nessun numero si riesegue per cambiare**: si correggono frasi. Se una frase
  corretta rende falso un numero pubblicato, lo si segnala, non lo si aggiusta.
- **Il dossier non si rigenera.** Da L32 legge la provenienza dagli `.include`;
  se questo non è vero, è una scoperta da registrare.
- **Un controllo mai fatto fallire non è un controllo.**

## Cosa NON accettare

- **Un conto di deck copiato da NC-031** invece che rifatto.
- **Un commento corretto a mano senza la prova** che il diff tocca solo commenti.
- **Un README datato riscritto** invece che annotato.
- **Un guardiano esteso e mai visto cadere.**
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.

## NON fa parte di questo lotto

- **La sostituzione del modello dell'LSK489** nel circuito (Fase 4, NC-017), e
  il modello d'angolo di **NC-013**.
- **NC-027 (L28)**, **NC-028 (L29**, aspetta una soglia dell'utente su V2),
  **NC-029 (L30)**.
- **Il selettore d'ingresso**, l'alimentatore, `VRELAY`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L31 ha trovato
  sbagliate due frasi del proprio mandato.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con `git show`
    su un file;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`) o un comando
    con valori calcolati in posizione di opzione viene rifiutato: scrivi uno
    script su file;
  - in un worktree anche un comando con **variabili di shell** e `git archive`
    in **pipe** verso `tar` vengono rifiutati. Usa percorsi letterali e
    `git archive -o <file>`, poi `tar -xf` separato (L31);
  - se il classificatore dei permessi va in timeout, il comando non è partito:
    rilancialo.
- **Se `/usr/bin/python3` o `git` escono 69** con «You have not agreed to the
  Xcode license agreements», serve `sudo xcodebuild -license` dall'utente in un
  terminale: è successo a metà di L32.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L33, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L33`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
