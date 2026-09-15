# Prompt per la sessione successiva — L13

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L13** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L34, di sola documentazione, non tocca L13.** Dalla sessione di domande
dell'utente del 2026-09-15:
- **ADR-028**: comandi sul frontale e LED a pannello cablati (F10, F11);
- **ADR-029**: ingombro del telaio, 450 × 130 × 367 mm (P8);
- **ADR-030**: il guadagno interbloccato dal mute, solo se L29 lo giustifica;
- **F3** dice ora «sbilanciate RCA»; «jack» vuol dire la presa d'uscita RCA
  (nota in `REQUIREMENTS.md`). Per E4 non cambia niente;
- **NC-032** aperta (maggiore, la chiude L35); **L29** esteso; lotti nuovi
  **L35** e **L36**.

**Prima, L33 ha chiuso NC-031**: nessun deck e nessun README chiama più
«del costruttore» l'LSK489 simulato.

1. **Cosa si simula, detto una volta per tutte.**
   - L'LSK489 è `LSK489X`, segnaposto con `KF = 0`
     (`spice/preamp/placeholder_devices.lib`);
   - l'unico modello del costruttore è l'LS352 (`models/bjt_pnp/ls350.lib`),
     senza `KF`;
   - **nessun dispositivo simulato ha rumore 1/f.**
2. **Il blocco 2h** (`scripts/check_deck_provenance.py`) confronta ciò che i
   commenti di un deck dichiarano con la `provenance()` del dossier, applicata
   ai suoi `.include`. **Se copi l'intestazione di un deck, copi anche le sue
   frasi di provenienza**, e il 2h le controlla. Non vede un modo nuovo di dire
   «vendor».
3. **I conti del mandato erano sbagliati**: 15 deck e 7 README, non 13 e 3. E
   il mandato non contava L13 e L20 fra i lotti aperti. **Verificare i numeri e
   le frasi dei mandati resta la regola**, anche questo.
4. **I dati** stanno in `data/2026-09-15/L33/`.

Voci: **15 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** Non aspetta nessuno. Gli altri sì:
- L29 una soglia dell'utente su V2, ed è stato esteso da L34;
- L36 e L35 aspettano L29;
- L30 l'alimentatore, che viene dopo L35 e L36;
- L28 un documento del costruttore o una ADR, prima di G2.

L20 (NC-013) non aspetta nessuno neppure lui, e viene dopo.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L33, L17 e L27, «Prossimo
   passo concreto» e la riga L13 della tabella dei lotti.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-008**. La sua evidenza cita i dati
   del **2026-09-09** (THAT320, C_f 22 pF, due guadagni): va riletta sulla
   topologia di oggi, non copiata.
4. **`docs/preamp/REQUIREMENTS.md`**: **E4**, parola per parola, e F3.
5. **Cosa c'è già**:
   - `spice/preamp/tb/tb_zout_psrr_noise.cir`: Zout al jack principale;
   - `spice/preamp/tb/tb_uscite_fisse.cir` e `data/2026-09-14/L17/`: E4 su
     **una** fissa (Re(Z) al jack ≤ 53,13 Ω);
   - `data/2026-09-14/L27/` e `L16/`: i dati vigenti, tre modi di guadagno e il
     trim.
6. **`docs/limitations.md`**: in particolare #24 (nodi che collidono con
   `_flat.inc`), #25 (tabelle `echo` sovrascritte da un `wrdata` omonimo), #26
   (`meas tran` con `tstart`) e #27 (nodi di contatto non terminati).

## IL LOTTO: L13 — E4 sulle tre uscite e a manopola che gira

### Cosa fare

1. **Baseline: cosa è già misurato, contato e non copiato.**
   - Per ciascuna delle tre uscite (F3), per ciascuno dei tre modi (0 / +3 /
     +10 dB) e per la posizione dell'attenuatore: esiste un dato versionato di
     Zout al jack, sulla topologia di oggi?
   - La tabella che ne esce va nel report. Se un pezzo di NC-008 è già coperto
     da L17 o da L27, lo si dice con il file.
2. **Misurare cosa manca.** La clausola «costante con la posizione del volume»
   vuole almeno tre posizioni dell'attenuatore (minimo, metà corsa, massimo)
   **sul ramo principale**; le due fisse vogliono la loro Zout nei modi in cui
   il loro blocco cambia.
   - Estendere un deck esistente o scriverne uno: decidere coi file, e scrivere
     perché.
   - **Prima di registrare un numero**, far fallire il deck: una sonda sul nodo
     sbagliato, o una posizione che non cambia niente, deve dare un numero
     diverso.
3. **Il verdetto su E4**, con la frase del requisito accanto a ogni cifra e la
   provenienza dei modelli.
   - La tensione nota **E4 contro E8 a 20 Hz** (`STATE.md`, «Due tensioni fra
     requisiti»): a 20 Hz la |Zout| è la reattanza del condensatore d'uscita. Si
     tratta come è già scritta, non si riscopre.
4. **Chiudere NC-008**, o lasciarla aperta con cosa manca, in `NONCOMPLIANCE.md`.

### I vincoli

- **Nessun valore del circuito cambia.** Se E4 non regge, è una non conformità
  nuova o un rimedio in un lotto suo, non un ritocco.
- **I dati si versionano** sotto `docs/preamp/data/<data>/L13/`, con un README
  che dichiara la provenienza dei modelli. **Il 2h controlla i commenti del
  deck**: scrivi la provenienza vera.
- **Il dossier non si rigenera.** Pubblicare E4 nel dossier è un lotto a sé.
- **Un controllo mai fatto fallire non è un controllo.**

## Cosa NON accettare

- **Una tabella di copertura copiata da NC-008** invece che rifatta sui file.
- **Una Zout misurata su un nodo interno** invece che al jack.
- **Un deck mai visto dare un numero sbagliato.**
- **Una frase di provenienza nel deck** diversa da quella dei suoi `.include`.
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.

## NON fa parte di questo lotto

- **L20** (NC-013, dipendenza da I_DSS), **L28** (NC-027), **L29** (NC-028,
  aspetta una soglia dell'utente su V2), **L30** (NC-029).
- **La sostituzione dei modelli** (Fase 4, NC-017).
- **Il selettore d'ingresso**, l'alimentatore, `VRELAY`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L33 ha trovato
  sbagliati i conti del proprio mandato.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con
    `git archive -o <file>` e `tar -xf` separato;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`), un comando con
    valori calcolati in posizione di opzione (`sed -n "$(grep …),+45p"`) o con
    **variabili di shell** vengono rifiutati nel worktree: usa percorsi
    letterali, o uno script su file;
  - `echo "===="` in zsh fallisce (`= not found`): usa `echo "---"`;
  - se il classificatore dei permessi va in timeout, il comando non è partito:
    rilancialo.
- **`testbenches/01_op.cir` ha un `wrdata` con percorso assoluto**: il 2b
  lanciato da un worktree scrive in `/Users/roberto/EDA/results/` (L31).
- **Se `/usr/bin/python3` o `git` escono 69** con «You have not agreed to the
  Xcode license agreements», serve `sudo xcodebuild -license` dall'utente in un
  terminale: è successo a metà di L32.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L13, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L13`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
