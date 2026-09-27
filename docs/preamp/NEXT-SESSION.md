# Prompt per la sessione successiva — L43b (la revisione dell'utente col PRB come contratto, e la sintesi con l'architetto)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L43b** e si ferma. Non iniziarne un secondo.

## Il mandato

L43 è stato diviso dall'utente il 2026-09-27. La prima metà è **fatta**: la revisione
dell'architetto avversariale, con i suoi rilievi già discussi e decisi. Report verbatim in
`reports/2026-09-27-L43a-architetto-avversariale.md`, esiti in
`reports/2026-09-27-L43a-esiti-architetto.md`, voci **NC-039…NC-046**. L43b è la **seconda
revisione umana del dossier** (la prima fu L5e), **col PRB come contratto**, e il **report di
sintesi** delle due revisioni.

**L'architetto non si rilancia.** L'utente ha già visto i suoi rilievi, quindi la sua revisione
non è cieca rispetto all'architetto; lo è ancora rispetto all'orchestratore.

La sessione **non cerca difetti per conto suo**. È un controllo cieco: se l'utente sta cercando
un difetto e l'orchestratore lo trova prima, la taratura è persa. L'orchestratore fa tre cose:
1. accompagna l'utente nella lettura: apre le pagine, risponde alle domande, riesegue una verifica
   quando l'utente la chiede;
2. registra gli esiti;
3. scrive la sintesi.

### 1. La revisione dell'utente

- L'utente legge il dossier: `docs/preamp/dossier/index.html`, oppure il PDF A4 di
  `stampa_a4.py`, scritto **fuori** dal repo. La sezione 0 è il PRB; l'appendice A è il registro
  delle ADR, l'appendice B l'indice dei requisiti. I rimandi PR-n, ADR-0xx ed E1…V5 sono
  cliccabili. **Il dossier non è stato rigenerato dopo L43a**: non contiene NC-039…NC-046, e la
  frase della sezione 3 sul trim (NC-041) è ancora quella falsa. Si legge così com'è: lo legge
  solo l'utente, niente avvisi di obsolescenza.
- **Il PRB è il contratto**. Ogni cosa che l'utente trova diventa una voce di `NONCOMPLIANCE.md`
  (da **NC-047**) con la voce del PRB e il requisito tecnico, l'evidenza e la **severità decisa
  dall'utente**. Una proposta di severità dell'orchestratore resta una proposta.
- Se l'utente trova una voce del PRB ambigua o sbagliata, cambiarla vuole una ADR (ADR-053).
- Un rilievo dell'utente che coincide con una voce di L43a si registra **in quella voce**, non
  come voce nuova: «trovato anche dall'utente, dopo aver letto l'architetto».

### 2. Alla fine: la sintesi, con chi ha trovato cosa

`docs/preamp/reports/<data>-L43b-revisione-dossier.md`:
- ogni rilievo, dell'utente e dell'architetto, con **chi l'ha trovato** (utente, architetto o
  entrambi) e se era già noto (NC-0xx) o già deciso (ADR-0xx);
- la taratura dell'architetto: cosa ha trovato che l'utente non ha visto, e viceversa, **letta
  sapendo che l'utente l'aveva già letto**;
- i tre punti «per L43» di `STATE.md`, segnati come sono andati. L'architetto non li ha trovati.
  I punti sono tre: S del mute con la cima delle LDR a 12 mA mai misurato (ADR-050); la tenuta di
  `VRELAY` scesa da 62,8 a 36,1 ms (P9 ≥ 25 regge); il commento di `C_VRELAY` in `psu.py` con le
  cifre di L41a. **Non vanno detti all'utente prima che finisca la sua lettura.**

### 3. L'ordine dei lotti dopo L43b

L'ordine deciso il 2026-09-27 era **L44 (NC-004) → G1**. L43a ha aperto tre bloccanti per G1
(NC-039, NC-040, NC-041) e due per G2 (NC-043, NC-044), e ha messo a piano **L45**, la FMEA
(NC-042, prima di G2). Alla fine di L43b si propone all'utente un ordine dei lotti di rimedio;
**sceglie lui**. La tabella dei lotti in `STATE.md` si aggiorna con la sua scelta.

## Prima di tutto

- Leggi `CLAUDE.md`, `docs/limitations.md`, e in `docs/preamp/STATE.md` «In breve» e la voce di
  diario di L43a.
- `docs/preamp/PRB.md`, i due report di L43a e le voci NC-039…NC-046 di `NONCOMPLIANCE.md`.
- `docs/preamp/reports/2026-09-09-revisione-utente-dossier.md`: com'è andata la prima revisione
  umana.

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

- correggere quello che la revisione trova, comprese NC-039…NC-046: si registra, e i rimedi sono
  lotti successivi;
- rigenerare il dossier;
- le soglie numeriche di V4, la lista dei condensatori ammessi (P6), il selettore d'ingresso;
- qualsiasi modifica al circuito, al firmware o ai deck; NC-004 (L44); la FMEA (L45).

## CHIUSURA

1. `STATE.md` con L43b **fatto** e il prossimo lotto, secondo l'ordine scelto dall'utente, nella
   tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L43b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
