# Prompt per la sessione successiva — L52, l'architetto avversariale di nuovo, sul dossier completo

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L52**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'utente, il 2026-10-09 dopo L49b: «rigeneriamo il dossier, mettilo nel prossimo lotto abbiamo
cambiato molto, poi lo passiamo all'avversariale di nuovo, poi affrontiamo G1». Il dossier è
rigenerato e completo (L51a, L51b, L51c): `docs/preamp/dossier/index.html`. Questo lotto è
«l'avversariale di nuovo». Dopo viene **G1**, poi L45 FMEA e L50 massa e terra.

L'architetto ha visto il progetto una volta sola, in L43a (2026-09-27). Da allora sono nate le
ADR **054–066**: compensazione, PSRR, rumore 1/f, la cella del mute e il suo abbandono, il mute
coi soli relè, il selettore, il volume col bilanciamento. Sono cambiati l'alimentatore e il
firmware, e ci sono le schede di prova di L49.

## Il mandato

La sessione **non cerca difetti per conto suo**: è un controllo cieco, come L43a. Fa tre cose.

### 1. Per primo: lanciare l'architetto avversariale

All'avvio, prima di qualsiasi conversazione sul dossier:
- `Agent` con `subagent_type: "adversarial-architect"`: **un agente nuovo, mai `fork`**. Un fork
  eredita questa conversazione, e la revisione non sarebbe più cieca. In background.
- **Il prompt contiene solo** la data, i tre obiettivi dell'utente e i percorsi del prodotto (il
  dossier `docs/preamp/dossier/index.html`, `docs/preamp/PRB.md`, `REQUIREMENTS.md`,
  `decisions/`, `circuits/preamp/`, `spice/preamp/`, `firmware/preamp_timer/`, `layout/preamp/`,
  `models/`). Il suo mandato sta già nella definizione (`.claude/agents/adversarial-architect.md`),
  compresa la cecità a `NONCOMPLIANCE.md`, `STATE.md` e `reports/` fino alla fase 2. I tre
  obiettivi, con le parole dell'utente:
  - un preamplificatore che suoni bene (secondo la letteratura e la tecnica);
  - che non abbia bump fastidiosi sulle uscite ai cambi di configurazione;
  - che fallisca senza danneggiare altri elementi della catena.

  In più: se sono possibili semplificazioni, e se c'è over-engineering.
- **Niente nel prompt** di ciò che i lotti hanno già trovato. In particolare niente dei rilievi
  di L43a, dei 45 tratti ristretti di L51c, delle righe `Stato:`: entrano nella sintesi alla
  fine, non nel prompt.
- Quando torna, il suo messaggio finale è il report. Salvalo **verbatim** in
  `docs/preamp/reports/<data>-L52-architetto-avversariale.md`.

### 2. I rilievi, uno per uno con l'utente

Come in L43a:
- ogni rilievo si porta all'utente **per nome, senza sigle** (al più tra parentesi), coi gradini
  in dB SPL contro una stanza silenziosa;
- la severità la decide l'utente;
- un rilievo entra in `NONCOMPLIANCE.md` **solo se l'utente lo accetta**, con il requisito del
  PRB, l'evidenza e la severità;
- le ADR che l'architetto riaprirebbe e le semplificazioni che propone vanno all'utente una per
  una: sceglie lui;
- cambiare il PRB vuole una ADR (ADR-053).

### 3. Alla fine

- Un report degli esiti, `docs/preamp/reports/<data>-L52-esiti-architetto.md`, con la tabella
  dei rilievi, le decisioni dell'utente e la taratura contro L43a: cosa ha trovato di nuovo e
  cosa ha ripetuto, e se un rilievo era già noto (NC-0xx) o già deciso (ADR-0xx).
- **Chiedere all'utente** (proposta di «Dopo L49b», non decisa) se vuole rifare anche la sua
  lettura del dossier, come L43b, prima del gate. La risposta decide il lotto successivo: L53
  la lettura dell'utente, oppure G1.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (54 voci), `AGENTS.md` (il paragrafo sul revisore
  avversariale), `.claude/agents/adversarial-architect.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di **L51c**.
- `docs/preamp/reports/2026-09-27-L43a-esiti-architetto.md`: com'è andata la prima volta.
- Il dossier si legge in `docs/preamp/dossier/index.html`, oppure in A4 con
  `/usr/bin/python3 docs/preamp/dossier/stampa_a4.py <file fuori dal repo>.pdf`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- Il PDF del dossier non si versiona; la pagina autoconsistente (`--standalone`) va sempre fuori
  dal repo.

## NON fa parte di questo lotto

- Correggere quello che l'architetto trova: si registra, e i rimedi sono lotti successivi.
- Qualsiasi modifica al circuito, al firmware, ai deck o al dossier.
- Il gate (**G1**), la FMEA (L45), la massa e la terra (L50), il layout vero (G2).

## CHIUSURA

1. `STATE.md` con L52 **fatto** nella tabella dei lotti, e il prossimo (L53 o G1, secondo la
   risposta dell'utente).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L52`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
