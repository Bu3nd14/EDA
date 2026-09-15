# Prompt per la sessione successiva — L37

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L37** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L20 ha chiuso NC-013.** Il blocco di guadagno è stato misurato col modello del
costruttore dell'LSK489, dal modello com'è (I_DSS 2,59 mA) a tutta la finestra
del **gruppo B** (15 mA).
- **Decisione dell'utente**: il JFET è del gruppo B, «Solo B, il gruppo del
  sorgente». È **ADR-031**, con la tolleranza 8,0–15,0 mA e il suo criterio;
  in `REQUIREMENTS.md` stanno la riga T4 e la «Nota su T4».
- **I numeri**: punto di lavoro, E5 e V1 non dipendono da I_DSS. Il margine di
  saturazione a modo comune scende a 2,4 V a 15 mA. E5 ≤ 4,308 µV; V1 del blocco
  B a 0 dB ≥ 62,51°.
- **Il segnaposto `LSK489X`**, che ogni altro deck istanzia ancora, ha I_DSS
  4,842 mA: un JFET quasi tipico del gruppo A.
- **Un blocco nuovo della suite, il 2i**: `spice/preamp/derived/` contiene il
  blocco con `LSK489A`, derivato da `scripts/derive_jfet_variant.py`, e il 2i
  rifiuta un derivato stantio. **Se L37 rigenera il blocco generato, il 2i cade
  finché il derivato non si rigenera.**
- **`build_dossier.py` è stato toccato**: una voce `"LSK489A": "LSK489"` in
  `PART`. Il dossier non è stato rigenerato, e l'output del 2h sui 18 deck è
  identico prima e dopo.

**Due lezioni di L20 che valgono anche qui.**
1. **Un controllo può trovare un errore nel commento, non nel circuito.** Il
   confronto con `tb_op` è caduto su due nodi soli: il commento del deck stimava
   4 pV uno spostamento che è 4,2 nV. Quando un controllo cade, si legge
   **dove** cade prima di allargare la tolleranza.
2. **Un `echo "$&x"` dopo `destroy all` scrive celle vuote con rc 0** (#26), e un
   `altermod` su un nome sbagliato non cambia niente con rc 0 (#29). Si contano
   le righe `Error` e le celle vuote, sempre.

Voci: **14 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Dopo L20 l'utente ha risposto alle domande aperte** (voce di diario «Dopo
L20» in `STATE.md`): soglia di V2 ≤ 100 µV, LED gemelli tenuti, ponte di rame
per NC-019, manuale d'uso per NC-009, Singxer chiuso. **Non sono ancora
requisiti**: li scrive **L38**. L37 non ne è toccato.

**Perché questo lotto viene adesso.** Non aspetta nessuno. Gli altri sì:
- L28 aspetta una sessione interattiva con l'utente sui pin SS;
- L29 aspetta L38, che scrive la soglia di V2 data dall'utente;
- L36 e L35 aspettano L29;
- L30 aspetta l'alimentatore, che viene dopo L35 e L36.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L20, L13 e L32, «Prossimo
   passo concreto» e la riga L37 della tabella dei lotti.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-033** per intero, poi la chiusura di
   NC-008.
4. **`docs/preamp/reports/2026-09-15-L13-e4-tre-uscite.md`** e il report di L32,
   `reports/2026-09-15-L32-dossier.md`: come il builder confronta le tabelle col
   log, e che cosa L13 ha misurato.
5. **`docs/preamp/REQUIREMENTS.md`**: **E4**, **E8** e la nota su «jack».
6. **Cosa c'è già**:
   - `docs/preamp/dossier/build_dossier.py`, in particolare `measure_zout()` e i
     controlli che rifiutano i percorsi del 2026-09-09;
   - i dati di L13: `data/2026-09-15/L13/dopo/tb_e4_uscite/` e
     `dopo/tb_zout_psrr_noise/`, col loro README e `esplorazione/script/e4.py`;
   - il dossier generato, `docs/preamp/dossier/index.html`, con le quattro righe
     sbagliate che NC-033 elenca.
7. **`docs/limitations.md`**: #25 (tabelle `echo` sovrascritte), #26 (celle
   vuote) e #28 (sorgenti AC dimenticate).

## IL LOTTO: L37 — E4 nel dossier

### Cosa fare

1. **Baseline, verificata e non ricordata.** Rigenera il dossier dal `main` di
   oggi in una cartella di scratch.
   - Controlla che le quattro cifre di NC-033 ci siano davvero, alle righe
     indicate: KPI 58,76 Ω; tabella 59,1132 / 60,5851 Ω e 1,0355 Ω «al nodo
     OUT»; nota E4/E8; riepilogo «≤ 60,5851 Ω».
2. **Il builder legge E4 dai dati di L13.**
   - `tb_e4_uscite` per le tre uscite e la costanza con trim × attenuatore.
   - `tb_zout_psrr_noise` corretto per le curve.
   - **Rifiuta** la Zout di `data/2026-09-14/L27/`, come oggi rifiuta i percorsi
     del 2026-09-09.
3. **KPI, tabella, nota E4/E8 e riepilogo rigenerati**, con le fisse e la
   costanza col volume pubblicate. Le tabelle nuove si confrontano col log come
   le altre (L32).
4. **Un controllo fatto fallire**: il builder rifiuta una Zout al nodo che scala
   col guadagno del modo (la firma di #28).
5. **Una nota in coda a `data/2026-09-09/README.md`**, che non ne riscrive il
   testo.
6. **Chiudere NC-033**, o lasciarla aperta con cosa manca.

### I vincoli

- **Nessun valore del circuito e nessun deck cambia.** L37 impagina dati che
  esistono.
- **Il dossier si rigenera** (è il lotto), ma le sezioni che non riguardano E4
  devono restare identiche: provalo con un confronto, non a occhio.
- **Un controllo mai fatto fallire non è un controllo**, e un controllo fatto
  fallire per la ragione sbagliata nemmeno.

## Cosa NON accettare

- **Una cifra di E4 presa dal log di L27.**
- **Una tolleranza allargata** per far passare un confronto, invece di capire
  dove cade.
- **Un report datato riscritto**: G0, L14, L27 e la bozza di Fase 2 restano
  com'erano.
- **Il dossier pubblicato come Artifact** senza che l'utente l'abbia chiesto.

## NON fa parte di questo lotto

- **Pubblicare nel dossier i dati di L20** (I_DSS, gruppo B, `LSK489A`).
- **L28** (NC-027), **L29** (NC-028, aspetta una soglia dell'utente su V2),
  **L30** (NC-029), **L35**, **L36**.
- **La sostituzione dei modelli nel circuito** (Fase 4, NC-017).
- **La verifica T8 dell'LSK489B**: è in «Domande aperte» di `STATE.md`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L33, L13 e L20
  hanno trovato sbagliate cose che il lotto precedente aveva scritto.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con
    `git show HEAD:<file> > <copia>` o `git archive -o <file>` e `tar -xf`
    separato;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`), un comando con
    valori calcolati in posizione di opzione (`sed -n "$(grep …),+45p"`) o con
    **variabili di shell** vengono rifiutati nel worktree: usa percorsi
    letterali, o uno script su file;
  - in zsh un argomento `--include=*.md` non quotato viene espanso come glob e
    il comando fallisce («no matches found»): quotalo;
  - `echo "===="` in zsh fallisce (`= not found`): usa `echo "---"`;
  - `sort -t, -k6 -g` non ordina in modo affidabile una colonna di un CSV:
    calcola i minimi con uno script;
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
   ancora L37, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L37`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
