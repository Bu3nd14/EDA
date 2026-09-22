# Prompt per la sessione successiva — L39 (Fase 4: i modelli del costruttore nel progetto)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L39** e si ferma. Non iniziarne un
secondo.

## Perché adesso

**Decisione dell'utente del 2026-09-22: la Fase 4 prima di L29c.** Il caso peggiore di V2
(L29c) dipende dai modelli: l'offset del blocco B (−14,2 mV coi modelli del costruttore
contro −16,6 coi segnaposto, ADR-030), la dispersione, e il fondo di distorsione della
catena, che sulla principale vale 0,65–0,96 mV di C2 coi segnaposto. Misurarlo coi
segnaposto vorrebbe dire rifarlo. Scoprire tardi un problema dei modelli veri, peggio,
vorrebbe dire rifare molti lotti o toccare la topologia: i MJE sono gli stadi d'uscita.

## Da dove si parte

- **Da L25 tutti e sette i dispositivi attivi hanno il modello del costruttore in
  `models/`**, con la provenienza e le ricette di `validate_models.py` (48/48). Di
  **NC-017** resta la sola sostituzione nel progetto.
- **I segnaposto** stanno in `spice/preamp/placeholder_devices.lib`: `LSK489X`,
  `NSS2N5551`, `PSS2N5401`, `PTHAT320`, `NMJE15032`, `PMJE15033`, `D1N4148`, tutti con
  KF = 0. Li includono **25 deck**. Il modello dell'LS352 è già del costruttore
  (`models/bjt_pnp/ls350.lib`).
- **I nomi da mappare** (`models/`): `LSK489A` (lsk489.lib), `MMBT5551`, `MMBT5401`,
  `Qmje15032`, `Qmje15033`, e in `1n4148.lib` un modello chiamato **`D1N914`**.
  Quest'ultimo va capito prima di usarlo: vedi limitations #17 e #20, dove il costruttore
  serve un modello sotto il nome di un'altra parte.
- **I nomi si scrivono nel sorgente**: `circuits/preamp/gain_block.py` passa il nome del
  modello a `spice_export.py` (`Q(...)`, `sx.spice_dev(...)`), e da lì si generano
  `spice/preamp/gain_block.subckt` e `gain_block_flat.inc`. Il sorgente istanzia ancora
  «2N5551 / 2N5401»: **ADR-017** ha cambiato costruttore e package (MMBT). La topologia
  sta solo nel sorgente (AGENTS.md): il blocco generato non si edita a mano.
- **Il JFET è del gruppo B** (ADR-031), mentre il modello del costruttore è l'LSK489A.
  La variante è già derivata da `scripts/derive_jfet_variant.py`
  (`spice/preamp/derived/gain_block_flat_lsk489a.inc`, L20, blocco 2i). Leggi come L20
  sposta `Vto` e come lo verifica (limitations #29).

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**, in particolare #17, #20, #22, #24, #27,
   #29, #30 e #31.
2. **`docs/preamp/STATE.md`**: le voci L25, L20, L24 e L29b2 del diario, e le righe L39,
   L29c e L36.
3. **ADR-013, ADR-016, ADR-017, ADR-018, ADR-031**; poi ADR-019 (V1), ADR-020 (E5),
   ADR-023 (classe A), ADR-030 (offset), ADR-040 (S).
4. **`docs/preamp/NONCOMPLIANCE.md`**: NC-017, NC-004, NC-013, NC-020, NC-024, NC-025,
   NC-031.
5. I report di L25 e di L20.

## IL LAVORO, in ordine

1. **La mappa segnaposto → costruttore**, per ogni dispositivo. Con la provenienza, e con
   ciò che il modello del costruttore **non** ha: 1/f, dispersione, deviazioni già
   registrate dal proprio datasheet (NC-013, NC-020, NC-024, NC-025).
2. **La sostituzione nel sorgente** (`gain_block.py`, `spice_export.py` se serve), poi il
   blocco rigenerato, e il derivato rigenerato (2i). Un commento con l'ADR su ogni scelta
   non ovvia.
3. **I deck.** Ogni deck che include i segnaposto passa ai modelli del costruttore. Si
   aggiornano le intestazioni: il blocco 2h confronta ciò che un deck **dice** di simulare
   con ciò che include.
4. **La regressione, cifra per cifra, prima e dopo**, in una tabella:
   - punto di lavoro e classe A in ogni blocco (ADR-023);
   - V1, margine di fase ≥ 60° ovunque (ADR-019);
   - E2–E5 (E5 resta un pavimento senza 1/f: dirlo);
   - V3, P7;
   - l'offset del blocco B (ADR-030);
   - A, B e S di V2 su una cella di `tb_v2_mute_ldr.cir` a 1 kHz, col fondo di
     distorsione di C2 accanto.

   **Ogni cifra che cambia oltre la sua soglia apre o aggiorna una NC.** Se una richiede
   una modifica di topologia, **fermati e dillo all'utente** prima di toccarla.
5. **L'esito**: NC-017 si chiude se la sostituzione è completa e la regressione regge;
   NC-004 si aggiorna. Report datato.

**Se non entra in una sessione, dividi**: prima la sostituzione e la regressione di
punto di lavoro, V1 ed E5; poi il resto. Scrivilo in `STATE.md`.

## I vincoli

- **`set numdgt=15`** in ogni deck che scrive forme d'onda da sottrarre (#30).
- **Tempi**: le corse di V2 a 20 kHz con TMAX 0,5 µs valgono ore. Qui non servono: la
  regressione di V2 è a 1 kHz.
- **Nessun cambio di topologia senza l'utente.**
- I file in `vendor/` non si toccano; i modelli in `models/` si cambiano solo col loro
  processo (provenienza, `validate_models.py`).
- Gli script zsh si lanciano da soli. `git` e i comandi con variabili di shell composte
  vengono rifiutati nel worktree: comandi semplici e separati, script su file. Scipy non
  c'è; numpy c'è nel venv 3.13. `pkill -f` sul nome di uno script zsh prende anche i
  suoi subshell; `pgrep` con `\|` non vuol dire «oppure».

## NON fa parte di questo lotto

- **L29c** (il caso peggiore di V2: viene subito dopo), L36, L35, L28 (i pin SS: la
  ricerca la fa l'utente), L30, il dossier.

## CHIUSURA

1. `STATE.md` con L39 **fatto** e L29c come prossimo.
2. Riscrivi QUESTO file per L29c, partendo dalla bozza
   `docs/preamp/data/2026-09-22/L29b2/bozza_prompt_L29c.md` aggiornata ai modelli del
   costruttore.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L39`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
