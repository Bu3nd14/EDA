# Prompt per la sessione successiva — L43 (la revisione dell'utente col PRB come contratto, e l'architetto avversariale in parallelo)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L43** e si ferma. Non iniziarne un secondo.

## Il mandato

L'ordine deciso dall'utente il 2026-09-27 è: **L43 → L44 (NC-004) → G1**. L43 è la **seconda
revisione umana del dossier** (la prima fu L5e), fatta **col PRB come contratto**. **In
parallelo e alla cieca** gira la prima revisione di `adversarial-architect`, l'agente creato nel
lotto precedente.

La sessione **non cerca difetti per conto suo**. È un controllo cieco: se l'utente ha già trovato
un difetto e l'orchestratore lo cerca, la taratura del revisore è persa. L'orchestratore fa tre
cose:
1. lancia l'architetto;
2. accompagna l'utente nella lettura: apre le pagine, risponde alle domande, riesegue una
   verifica quando l'utente la chiede;
3. registra gli esiti.

### 1. Per primo: lanciare l'architetto avversariale

All'avvio, prima di qualsiasi conversazione sul dossier:
- `Agent` con `subagent_type: "adversarial-architect"`: **un agente nuovo, mai `fork`**. Un fork
  eredita questa conversazione, cioè le osservazioni dell'utente, e la revisione non sarebbe più
  cieca. Va in background, perché la sua revisione corre in parallelo a quella dell'utente.
- **Il prompt contiene solo** la data, i tre obiettivi dell'utente e i percorsi del prodotto.
  Il suo mandato sta già nella definizione (`.claude/agents/adversarial-architect.md`), compresa
  la cecità a `NONCOMPLIANCE.md`, `STATE.md` e `reports/`. **Niente** di ciò che l'utente ha
  detto o dirà sul dossier, e niente dei punti «per L43» di `STATE.md` (la misura mancante di S
  a 12 mA, la tenuta di `VRELAY`, il commento di `C_VRELAY`): quelli entrano nel report di
  sintesi alla fine, non nel prompt. I tre obiettivi, con le parole dell'utente: un
  preamplificatore che suoni bene (secondo la letteratura e la tecnica), che non abbia bump
  fastidiosi sulle uscite ai cambi di configurazione, e che fallisca senza danneggiare altri
  elementi della catena. In più: se sono possibili semplificazioni e se c'è over-engineering.
- Quando torna, il suo messaggio finale è il report. Salvalo **verbatim** in
  `docs/preamp/reports/<data>-L43-architetto-avversariale.md`. **Non mostrarne i rilievi
  all'utente** finché l'utente non ha finito la sua lettura, o non lo chiede lui.

### 2. La revisione dell'utente

- L'utente legge il dossier: `docs/preamp/dossier/index.html`, oppure il PDF A4 di
  `stampa_a4.py`, scritto **fuori** dal repo. La sezione 0 è il PRB; l'appendice A è il registro
  delle ADR, l'appendice B l'indice dei requisiti. I rimandi PR-n, ADR-0xx ed E1…V5 sono
  cliccabili, anche nel PDF.
- **Il PRB è il contratto**. Ogni cosa che l'utente trova diventa una voce di `NONCOMPLIANCE.md`
  con la voce del PRB (e il requisito tecnico) a cui si riferisce, l'evidenza e la **severità
  decisa dall'utente**, come in L5e. Una proposta di severità dell'orchestratore resta una
  proposta.
- Se l'utente trova una voce del PRB ambigua o sbagliata, cambiarla vuole una ADR (ADR-053).

### 3. Alla fine: i due esiti, con chi ha trovato cosa

- Un report di sintesi, `docs/preamp/reports/<data>-L43-revisione-dossier.md`. Ogni rilievo
  porta **chi l'ha trovato**: l'utente, l'architetto o entrambi, e se era già noto (NC-0xx) o
  già deciso (ADR-0xx). Servono anche la taratura dell'architetto (cosa ha trovato che l'utente
  non ha visto, e viceversa) e i punti «per L43» di `STATE.md`, segnati come erano.
- I rilievi dell'architetto entrano in `NONCOMPLIANCE.md` **solo se l'utente li accetta**, con la
  severità decisa da lui. Le ADR che l'architetto riaprirebbe e le semplificazioni che propone
  vanno portate all'utente una per una: sceglie lui.

## Prima di tutto

- Leggi `CLAUDE.md`, `docs/limitations.md`, e in `docs/preamp/STATE.md` «In breve» e la voce di
  diario del lotto precedente.
- `docs/preamp/PRB.md`, `AGENTS.md` (il paragrafo sul revisore avversariale) e
  `.claude/agents/adversarial-architect.md`.
- `docs/preamp/reports/2026-09-09-revisione-utente-dossier.md`: come si è svolta la prima
  revisione umana.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi.
- Il PDF del dossier non si versiona (`stampa_a4.py` rifiuta un percorso dentro il repo).

## NON fa parte di questo lotto

- correggere quello che la revisione trova: si registra, e i rimedi sono lotti successivi;
- le soglie numeriche di V4, la lista dei condensatori ammessi (P6), il selettore d'ingresso;
- qualsiasi modifica al circuito, al firmware o ai deck; NC-004 (L44).

## CHIUSURA

1. `STATE.md` con L43 **fatto** e il prossimo lotto (L44, salvo che la revisione cambi l'ordine
   con l'utente) nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L43`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
