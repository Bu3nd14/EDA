# Prompt per la sessione successiva — L28 (SS dell'LSK489 definito per l'LSK489)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L28** e si ferma. Non iniziarne un secondo. Se si divide, la
divisione si scrive nella tabella dei lotti di `STATE.md` prima di chiudere.

## Il mandato

**NC-027** (minore, precondizione di G2): i pin 3 e 7 dell'LSK489, «SS» nel disegno SOIC del
datasheet, non sono definiti per *questa* parte. L'unica istruzione scritta («SS: SUBSTRATE,
LEAVE THESE PINS FLOATING») è per l'LSK389.

**La fonte c'è** (ricerca dell'utente del 2026-09-22, verificata in L29b2): Bob Cordell,
*LSK489 Application Note*, Rev A2, pag. 6, «The Common Substrate», dal sito del costruttore:
- URL: `https://www.linearsystems.com/_files/ugd/4be30b_49c5a96bc52f4868a7bf2a5c17150351.pdf`;
- SHA-256: `84f21b11763404e7fd4c9d8d461a86a833b0aea9c8459fdd9babe777149f1d8f`.

Dice che SS è il substrato comune, che i diodi hanno l'anodo sui gate e il catodo sul
substrato, e che «it harmlessly floats». Nel SOIC «may» collegarsi a una tensione fissa.

1. **Congelare la nota** in `vendor/` con `scripts/freeze_vendor.sh` (e la sua provenance),
   **controllando lo SHA-256** contro quello sopra. Se non torna, ci si ferma e si dice.
2. **Un'ADR**: pin 3 e 7 flottanti come oggi. Se mai collegati, a una tensione **sopra i gate,
   MAI al negativo**. Un testo di un altro modello diceva il contrario e nominava i pin 1 e 8: è
   sbagliato.
3. **Chiudere NC-027.** Nessuna modifica al circuito: `gain_block.py` li lascia già scollegati.
   Il deck V2 rigenerato (`--matrice sorgente`) deve restare byte-identico.

## Prima di tutto

- Leggi `CLAUDE.md` e `docs/limitations.md`, soprattutto la #36, nuova in L41c.
- In `docs/preamp/STATE.md`: la voce di diario di L41c e la riga L28.
- In `docs/preamp/NONCOMPLIANCE.md`: **NC-027** per intero.
- Per il simbolo, `reports/2026-09-13-L10-simbolo-lsk489.md`: i pin SS sono `passive`, non
  `no_connect`. Se l'ADR li definisce, chiediti se il simbolo va aggiornato, e dillo.

## Lo stato che trovi

- **L41c ha chiuso NC-036** (ADR-051): il banco di L30 col circuito vero dell'alimentatore regge
  in ogni caso. Il corto della linea a 12 V dei relè (~90 dB SPL di picco a 1 m) è accettato
  sotto il tetto.
- **10 non conformità aperte, 1 bloccante**: **NC-004**, per G1, il rumore 1/f fuori dalla coppia
  d'ingresso. Nessuna non conformità blocca più il layout.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - `awk` con programmi, e i percorsi calcolati a runtime.

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- `vendor/` è di sola lettura, tranne che con `freeze_vendor.sh`.

## NON fa parte di questo lotto

- **NC-004**, **NC-011**, **NC-037**;
- il dossier;
- il layout dei PCB (G2) e `src/main_attiny.c`.

## CHIUSURA

1. `STATE.md` con L28 **fatto** e il prossimo lotto: chiedi all'utente se è NC-004 o l'avvio di
   G2.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L28`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
