# Prompt per la sessione successiva — L45d2b3, i guasti rifatti e la sintesi

Nome della sessione: **hi-fi preamp L45d2b3** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L45d2b2c (2026-10-21) e messo da parte qui: per decisione
> dell'utente prima viene **L63**, lo schematico completo. Chi chiude L63 lo copia in
> `docs/preamp/NEXT-SESSION.md`, aggiornando le righe che L63 avesse cambiato.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b3**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078); L45d2b li ha costruiti:
- L45d2b1 il rivelatore, poi uscito (ADR-079, ADR-081);
- L45d2b2a…c la partenza morbida (ADR-091, ADR-092), i diodi della tenuta (ADR-093), il comando e i
  5 V (ADR-094), i massimi del blocco (ADR-095).

Resta **L45d2b3**: i guasti rifatti nella forma di ADR-070, sul circuito di oggi, e la sintesi. Se i
numeri lo permettono NC-042 si chiude.

## Che cosa costruire

1. **Le righe di `data/2026-10-14/L45d2a/decisioni.csv`** (88) e le 9 basse delle sovratensioni,
   con le colonne dopo il rimedio di ADR-070, sul circuito di oggi.
2. **I modi delle parti nuove**:
   - ADR-093: D513–D516;
   - ADR-094: D530–D532 aperti, R552, U512, C536, le metà aperte delle resistenze sdoppiate;
   - **ADR-095: D158 / D159** aperti (si torna a 5,18 V in P7 e alle resistenze d'uscita di prima,
     L45d2b2c) e in corto (la base-emettitore di un finale in corto).
3. **R144 contro la sua parte**, **R153 in corto** (Q146 a 0,41 W in P7, `data/2026-10-19/L60d2/`),
   **le durate di P10 sulla Stax**.
4. **La sintesi** rifatta, e NC-042 chiusa se i numeri lo permettono.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Uno
strumento di misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#59, #62, #64, #67, #68, #69**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b2c, L45d2b2b2, L45d2b2b1, L45d2b2a.
- `NONCOMPLIANCE.md`: NC-042, NC-072, NC-073, NC-074.
- ADR-070, ADR-071, ADR-078, ADR-090, ADR-093, ADR-094, ADR-095.
- I banchi: del blocco di L45d2b2c (`data/2026-10-21/L45d2b2c/`, con le giunzioni dei finali in P7) e
  dell'alimentatore di L45d2b2b2 / L45d2b2c; le copie guaste del blocco rifatte dal blocco di oggi
  (limitations #62).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc, un `python3 -c` dentro un altro comando,
    gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - `sed` con un valore calcolato al momento (si scrive uno script);
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- **SKiDL scrive i suoi `.erc` / `.log` / `_sklib.py` nella cartella corrente**: i sorgenti in
  `circuits/preamp` si lanciano con la cartella corrente lì (`data/2026-10-21/L45d2b2c/script/rigenera.sh`).
- **Non modificare uno script mentre zsh lo sta eseguendo**, e non cambiare un generatore mentre una
  lista di casi gira.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL; ogni opzione con la
  sua cifra contro il limite della parte, alle tre reti.

## NON fa parte di questo lotto

- **NC-073** (l'impulso di R550 / R551) e il sovraccarico breve di R552: alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- La tensione degli elettrolitici del blocco (C141 / C142 fino a 20,3 V col rail alto): alla scelta
  delle parti.
- Il micro bloccato e lo standby (L54), la diagnosi (L58), l'ingresso protetto (L57), il dispositivo
  d'uscita (L55), il tetto delle fisse (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a…c non si riaprono, salvo che un «Da riaprire
  se» della loro ADR scatti. In quel caso si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L45d2b3 **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b3`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
