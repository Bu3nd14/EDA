# Prompt per la sessione successiva — L45d, il riporto delle tabelle e la decisione sui guasti

Nome della sessione: **hi-fi preamp L45d** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45a il blocco di guadagno,
L45b i controlli, L45c1 i rail audio, **L45c2 la linea dei relè e il comando (fatto, 2026-10-14)**.
L'analisi è completa; **L45d** è l'ultima parte, e la voce si chiude con lei.

L45d fa due cose, in quest'ordine (ADR-070, scelta dell'utente: «retrofit in L45d»):
1. **il riporto**: le tabelle di L45a, L45b e L45c1 nella forma di ADR-070 — gravità, probabilità,
   rilevabilità, priorità, rimedi candidati — **dai dati già misurati**, senza corse nuove salvo che
   una colonna non lo chieda;
2. **la decisione**: con le quattro tabelle davanti, le scelte dell'utente sui rimedi, ognuna con la
   sua ADR.

**È un lotto grande. All'inizio chiedi all'utente se dividerlo** (per esempio il riporto in L45d1, la
decisione in L45d2), per nome e senza sigle, come in L45c.

## Il riporto

Il modello è L45c2 (`data/2026-10-14/L45c2/`, README):
- `script/classi_l45c2.py`: i tassi per tipo di parte (con la fonte), la ripartizione dei modi, la
  rilevabilità e la gravità minima per riga, i rimedi; `script/tabella_l45c2.py`: le colonne e la
  matrice della priorità di ADR-070; `tassi/fonti.md`: le fonti.
- **Le fonti dei tassi** (scelta dell'utente, 2026-10-14, «Stima dichiarata»): per gli integrati il
  valore di SN 29500-2 dai documenti di sicurezza funzionale del costruttore; per le passive e
  discrete un ordine di grandezza dichiarato come stima; i modi da MIL-HDBK-338B (Tabella 7.8-1,
  `L45c2/tassi/`). **Se l'utente ha nel frattempo SN 29500 o FMD-2016, si usano quelle**, anche per
  rifare le classi di L45c2.
- Per L45a, L45b, L45c1 servono le parti del blocco e dei controlli che L45c2 non ha (i transistor
  del blocco, i JFET, i relè di segnale G6K, i condensatori a film, i LED, i commutatori): stessa
  regola, fonte riga per riga.
- I dati già misurati: `data/2026-10-13/L45a/`, `L45b/`, `L45c1/` (README di ognuno). **Le forme
  d'onda sono gitignorate**: quelle di L45c1 sono state cancellate col suo worktree, e quelle di
  L45a e L45b probabilmente anche (da controllare). Si lavora sui CSV versionati.
  Se una colonna richiede una forma d'onda, si rifà quella corsa e lo si dice.
- Dati in `docs/preamp/data/<data>/L45d/`, una tabella per lotto più una sintesi unica, ordinata per
  priorità.

## La decisione

Le scelte da portare all'utente, **per nome e senza sigle**, coi numeri delle quattro tabelle:
- **un rivelatore di continua sulle uscite dei blocchi** che apra il mute (L45a: il blocco al rail,
  14,9 V, oggi 0,56–3,1 s sopra il tetto; P10 lo vuole entro 100 ms, ADR-069);
- **il filo del rail + fra le due schede** (L45c1: 13,3 V al jack, nessun mute);
- **il mute che non si inserisce**: Q501 in corto (L45c1) e Q501 con gate e drain in corto (L45c2,
  0,27 V alla perdita di rete, il jack a 685 ms), il NO di mute saldato (L45b, L45c1);
- **il ritardo Δ perso** (L45c2, 45 modi, 6,44 mV): accettarlo come il corto della linea a 12 V
  (ADR-051) o un permesso indipendente da VRELAY e da `MUTE_G`; e i due latenti **a ogni mute**
  (D520 in corto, R524 aperta);
- **i sovraccarichi del comando** (L45c2: i clamp D506 / D508 in corto, D505 o la bobina di K501 in
  corto) e **la sovratensione su V5** (U504 in corto ingresso-uscita);
- **la clausola di 1 ms** di P9 (b) quando a mutare è il firmware (L45c2, i sorveglianti ciechi);
- **le sovratensioni dei rail** che nessuno vede (L45c1, fino a ±20,3 V) e la presa centrale aperta;
- l'isolamento bobina–contatti che cede (L45b), lo standby con VRELAY o il toroidale accesi (L45c2);
- **il tetto delle fisse** (con NC-046).
Se una scelta cambia il circuito: sorgente, netlist, disegno, `run_tests.sh`, regressione, e i
guasti toccati rifatti.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di **L45c2**, «Dopo L45c1», L45c1, L45b, L45a.
- `NONCOMPLIANCE.md`: NC-042, NC-046, NC-062.
- I quattro report di L45 (`reports/2026-10-13-L45a…`, `L45b…`, `L45c1…`,
  `reports/2026-10-14-L45c2-fmea-comando.md`) e le loro tabelle.
- ADR-045, ADR-046, ADR-051, ADR-062, ADR-069, **ADR-070**.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `psu/corri_lista.sh`);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Uno strumento di misura nuovo si controlla su un caso noto prima di usarlo.

## NON fa parte di questo lotto

- L'ingresso protetto (L57), il riesame del micro e dello standby (L54: `MUTE_REQ` bloccata alta,
  Q502 in corto all'accensione, D522), il dispositivo d'uscita (L55), il moltiplicatore di Vbe
  (NC-062), G1. Se una scelta tocca uno di questi, si dice e si lascia al suo lotto.

## CHIUSURA

1. `STATE.md` con L45d (o le sue parti) **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh <lotto>`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
