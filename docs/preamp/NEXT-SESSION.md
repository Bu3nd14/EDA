# Prompt per la sessione successiva — L31

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L31** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**Il lotto precedente ha rigenerato il dossier** sui dati di L27 e L16, e ha
chiuso la metà «dossier» di NC-009.

1. **`docs/preamp/dossier/build_dossier.py` legge solo i dati vigenti.**
   - Le sorgenti sono `data/2026-09-14/L27/dopo/` e `L16/dopo/`; un percorso del
     2026-09-09 fa rifiutare il builder.
   - Le tabelle `echo` si confrontano riga per riga con le `print` o le `meas`
     del log, e una cella vuota fa rifiutare (#26).
   - La provenienza dei modelli è letta dagli `.include` dei deck.
   - Nove sabotaggi, tutti rifiutati.
2. **Le cifre che pubblica**, rieseguite dai CSV:

   | Grandezza | Valore |
   |---|---|
   | V1, minimo del prodotto | **61,63°**, buffer delle fisse |
   | V1 blocco B, 0 / +3 / +10 dB | 61,80 / 69,77 / 102,98°; agli spigoli 61,42 / 68,64° |
   | V1 blocco A col trim | 63,50° |
   | NC-009 | **M1 +6,58 dB** (+10 dB, trim −6 dB); +0,58 dB a trim 0 |
   | E3 / E5 della catena | 121,1 kΩ con 68 pF / ≤ 4,92 µV |
   | P7 | Tj massima 81,8 °C; 0 righe ascoltabili fuori classe A |

3. **Trovato, NC-031** (minore, lotto **L33**). I README dei dati di L12, L27 e
   L16 dicono «segnaposto più LS352 e LSK489 vendor», e tredici deck portano un
   commento simile (dodici quello di L22, più `tb_trim.cir`). Ma i deck istanziano `LSK489X`, segnaposto con `KF=0`, e
   **nessuno include `models/jfet/lsk489.lib`**. Nei dati di oggi l'unico
   modello del costruttore è l'LS352, e **nessun dispositivo simulato ha rumore
   1/f**.

Voci: **16 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** `tb_noise_vectors.cir` è l'unico deck
versionato che non scrive dati, ed è il lotto più piccolo fra gli aperti.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L32 e L27, «Prossimo passo
   concreto» e la riga L31 della tabella dei lotti.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-030**.
4. **`docs/limitations.md` #22 e #27**: le rinumerazioni che rompono i deck in
   silenzio, e cosa il blocco 2g non vede.
5. **`scripts/check_deck_refs.py`**, intero, e il blocco **2g** di
   `scripts/run_tests.sh`.
6. **`spice/preamp/tb/tb_noise_vectors.cir`** e il suo log in
   `docs/preamp/data/2026-09-14/L27/dopo/tb_noise_vectors/`.
7. **`spice/preamp/gain_block_flat.inc`**: i nomi vivi dei dispositivi.

## IL LOTTO: L31 — i vettori di rumore di `tb_noise_vectors.cir`

### Cosa fare

1. **Baseline.** Rieseguire il deck di `main` con `scripts/run_simulation.sh` e
   ritrovare nel log `Error: no such vector onoise_q123`, con rc 0 e nessun dato.
2. **Prima il guardiano, poi la correzione.**
   - Estendere `check_deck_refs.py` ai nomi `onoise_<dispositivo>` e
     `inoise_<dispositivo>`.
   - Farlo **fallire sul deck di oggi**, prima di toccarlo.
   - Controllare che non dia falsi allarmi sugli altri deck di `main`.
3. **Rinominare i vettori dall'include generato**, non da un elenco scritto a
   mano: VAS Q122, specchio Q121A/B, JFET JQ110A/B, e ogni altro nome che il deck
   cita.
4. **Rieseguire e versionare** sotto `docs/preamp/data/<data>/L31/`:
   - il log senza righe `Error`;
   - i dati scritti, con righe;
   - un riscontro con la ripartizione per dispositivo a 1 kHz di
     `tb_noise_breakdown.cir`.
5. **Chiudere NC-030** in `NONCOMPLIANCE.md`, con l'evidenza.

### I vincoli

- **Nessun valore del circuito cambia.** Niente `circuits/`, niente netlist o
  schematici toccati a mano.
- **Le cifre di rumore restano un pavimento senza 1/f** (NC-004, NC-031): va
  scritto accanto a ogni numero che il lotto riporta.
- **Il dossier non si rigenera**: questo deck non vi entra.
- **Un controllo mai fatto fallire non è un controllo.**

## Cosa NON accettare

- **Un rc 0 preso come prova**: si contano le righe `Error:` del log e le righe
  dei dati (#26).
- **Nomi di vettore copiati da un elenco** invece che letti dall'include.
- **Un guardiano esteso e mai visto cadere.**
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.

## NON fa parte di questo lotto

- **NC-031 (L33)**, le etichette di provenienza dell'LSK489.
- **NC-028 (L29**, aspetta una soglia dell'utente su V2), **NC-029 (L30)**,
  **NC-027 (L28)**.
- **Il selettore d'ingresso**, l'alimentatore, `VRELAY`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra.
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
    script su file.
- **Se `/usr/bin/python3` o `git` escono 69** con «You have not agreed to the
  Xcode license agreements», serve `sudo xcodebuild -license` dall'utente in un
  terminale: è successo a metà di L32.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L31, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L31`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
