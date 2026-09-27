# Prompt per la sessione successiva — L42d (il PRB e le ADR nel dossier, e l'architetto avversariale)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L42d** e si ferma. Non iniziarne un secondo.

## Il mandato

Due cose, entrambe decise dall'utente il 2026-09-27, prima della sua revisione del dossier (L43).
L'ordine è: **L42d → L43** (la revisione dell'utente e quella dell'architetto, in parallelo)
**→ L44 (NC-004) → G1**.

**1. Il contratto dentro il dossier.** L'utente: «molto difficile leggere un dossier senza un
file di requisiti e ADR». Il dossier (`docs/preamp/dossier/build_dossier.py`) porta:
- **il PRB** (`docs/preamp/PRB.md`, le 29 voci firmate, ADR-053), in testa o in appendice (lo
  proponi all'utente);
- **un registro delle ADR**: numero, titolo, data, stato (accettata, superata da…) e la decisione
  in una o due righe. **Non il testo intero**: sarebbero 120–150 pagine (ADR-053, alternative
  scartate). Il testo resta in `decisions/`;
- i rimandi del testo (**PR-n, ADR-0xx, E1…P9, V1…V5**) che diventano link alle voci, anche nel
  PDF di `stampa_a4.py`.

Tutto **generato dai file**, nessuna copia a mano (è la regola del builder). Un controllo nuovo,
da far fallire come gli altri: ogni requisito e ogni ADR che il PRB nomina esistono davvero, e
ogni ADR del registro ha uno stato. È anche la prima verifica che il contratto sia univoco.

**2. L'architetto avversariale.** L'utente: «nel team dovremmo avere un architetto avversariale,
se non c'é lo creiamo, gli passiamo i requisiti, il dossier e il target di un preamplificatore
che suoni bene (basandosi sulla letteratura e sulla tecnica), che non abbia bump fastidiosi sulle
uscite ai cambi di configurazione e che fallisca senza danneggiare altri elementi della catena e
gli facciamo fare una review in parallelo a me».
- `design-reviewer` esiste, ma verifica che il progetto faccia **quello che dichiara**, e non ha
  il web. L'utente chiede chi contesti se ciò che dichiara sia **giusto**. `AGENTS.md` dice, dal
  2026-09-09, che un revisore nuovo non serve: la frase va superata, dichiarandolo.
- Crea `.claude/agents/adversarial-architect.md`: **sola lettura** (Read, Grep, Glob, Bash) più
  **WebSearch e WebFetch**. Il mandato:
  - i tre obiettivi dell'utente, contro il **PRB** come contratto e contro la letteratura;
  - può contestare anche le ADR, dicendo quali riaprirebbe e perché;
  - i gradini in dB SPL di picco a 1 m;
  - il soggetto è il prodotto, non la toolchain;
  - forma i suoi rilievi **prima** di leggere `NONCOMPLIANCE.md` e il diario di `STATE.md`, poi
    segna quali sono già noti;
  - consegna un report datato in `docs/preamp/reports/`, con requisito, evidenza e severità
    proposta per ogni rilievo.
- Aggiorna `AGENTS.md` (il roster e il paragrafo sul «revisore avversariale»).
- **Non lanciarlo in questa sessione**: le definizioni degli agenti si caricano all'avvio di una
  sessione, e la sua revisione va in parallelo a quella dell'utente (L43). Riscrivi il prompt di
  L43 perché la sessione di L43 lo lanci come **agente nuovo, mai come fork**, senza passargli
  niente delle osservazioni dell'utente, e alla fine scriva entrambi gli esiti con chi ha
  trovato cosa.

**Proponi all'utente come impaginare il PRB e il registro, e il testo del mandato dell'agente,
prima di scrivere codice.**

## Prima di tutto

- Leggi `CLAUDE.md`, `docs/limitations.md`, e in `docs/preamp/STATE.md` «In breve» e le voci di
  diario di L42b e L42c.
- `docs/preamp/PRB.md` e `decisions/ADR-053-product-requirements-book.md`.
- `docs/preamp/decisions/README.md`: l'indice delle ADR ha già titolo e stato di ciascuna.
- `docs/preamp/dossier/build_dossier.py`: la docstring e come L42b ha aggiunto le sezioni;
  `docs/preamp/data/2026-09-27/L42b/script/sabotaggi.py` per i sabotaggi.
- `.claude/agents/design-reviewer.md` e `AGENTS.md` (G0).

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- Il PDF del dossier non si versiona (`stampa_a4.py` rifiuta un percorso dentro il repo).

## NON fa parte di questo lotto

- la revisione dell'utente e quella dell'architetto (L43);
- le soglie numeriche di V4, la lista dei condensatori ammessi (P6), il selettore d'ingresso;
- qualsiasi modifica al circuito, al firmware o ai deck; NC-004 (L44).

## CHIUSURA

1. `STATE.md` con L42d **fatto** e il prossimo lotto (L43) nella tabella.
2. Riscrivi QUESTO file per L43: la revisione dell'utente col PRB come contratto, e l'architetto
   avversariale lanciato in parallelo, alla cieca (vedi sopra).
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L42d`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
