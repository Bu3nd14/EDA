# Prompt per la sessione successiva — L60d, la ridondanza nel blocco di guadagno

Nome della sessione: **hi-fi preamp L60d** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L60d**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se L60d si rivela più grande di una sessione, **dividilo con
l'utente all'inizio** (per esempio: il sorgente e la regressione, poi i guasti rifatti).

## Perché questo lotto, e perché adesso

Il lotto precedente ha messo nel sorgente il condensatore da 1 µF della Stax prima del relè di mute K3
(ADR-081, ADR-084) e K3 come TE Axicom IM06TS a isolamento supplementare (ADR-085), e ha rifatto P10
col carico della Stax su ogni guasto del blocco di L45a sulle posizioni A e F2 che portava la Stax
sopra 0,87 V (107 modi; `reports/2026-10-15-L60c2-stax-condensatore-e-rele.md`,
`data/2026-10-15/L60c2/p10_stax.csv`). Il condensatore ferma i gradini (il blocco al rail 118–124 ms),
ma non un'uscita che oscilla o deriva lenta:
- **R109 aperta** (la resistenza di gate della JFET d'ingresso, lato retroazione): l'anello si apre e
  il buffer oscilla da rail a rail ogni ~80 ms, **0,4–1,2 s** sulla Stax con fronti fino a 28 V;
- **R112 aperta** (la degenerazione dello stesso lato) e la source di JQ110B aperta: 140–149 ms;
- **Q133 in corto** collettore-emettitore (il finale PNP): 127–135 ms;
- **R144 aperta** (la cella RC dello stadio d'ingresso): 130 ms solo a +5 %.

L'utente ha scelto (**ADR-086**): **«Ridondanza nel blocco»**, **«Tutti e otto i blocchi»**, **«Lotto
suo, dopo»**, e per il contratto **«Tetto a 150 ms»** (PR-30 e P10 sulla Stax da 125 a 150 ms).
**NC-069** (maggiore, prima di G1) resta aperta finché R109 aperta sta fuori dai 150 ms.

**Da chiedere all'utente all'inizio: NC-070** (maggiore *proposta*). La matrice di V2 corsa in L60c2
ha la principale fuori in 16 verdetti (la musica a mute inserito fino a 0,58 mV sul jack), dove L48b
ne aveva 0: non viene da L60c2 né dal metodo d'integrazione, e il blocco è cambiato dopo L48b solo in
L56. Questo lotto rimisura comunque il blocco: l'utente decide la severità, e se la causa si cerca qui
o in un lotto suo.

## Che cosa costruire

1. **La ridondanza in `gain_block()`** (`circuits/preamp/gain_block.py`), una topologia sola per le
   otto istanze (ADR-006):
   - **R109** con una resistenza da ~10 kΩ in parallelo: aperta R109, l'anello resta chiuso. Il
     valore si sceglie guardando il rumore (E5, il gate della JFET d'ingresso) e la stabilità (la
     resistenza di gate sta lì per l'alta frequenza);
   - **R112** sdoppiata in due resistenze in parallelo (oggi 100 Ω: due da 200 Ω), e il suo gemello
     dal lato d'ingresso **R111** solo se serve alla simmetria della coppia (lo si decide coi numeri:
     la continua d'uscita e la distorsione);
   - **R144** sdoppiata (oggi 10 Ω: due da 20 Ω); il suo calore nel corto del condensatore della cella
     (22,5 W di picco, L45d2b1) va rivisto sulle due parti.
   Ogni valore nuovo ha il commento con ADR-086.
2. **Il sottocircuito, il disegno del blocco** (`gain_block_draw.py`, il manifesto) e le netlist.
3. **La regressione del blocco**: stabilità (margine di fase, carico capacitivo), rumore (E5),
   distorsione (V4), continua d'uscita, i 21 deck veloci di `run_tests.sh` / della regressione.
4. **I guasti rifatti**:
   - i modi di L45a delle parti nuove e di quelle sdoppiate (aperta e corto di ciascuna), sulle
     posizioni A e F2, col banco di L60c2 (`data/2026-10-15/L60c2/script/genera_L60c2.py`: il gruppo
     `guasti` legge i modi da `p10_blocco.csv` di L45b, va esteso ai modi nuovi);
   - P10 sulla Stax rifatto sui modi della tabella di ADR-086: R109 aperta deve stare sotto 150 ms;
   - il resto dei modi di A e F2 non deve peggiorare.
5. **NC-069 si chiude** se R109 aperta e i modi nuovi stanno dentro 150 ms; NC-042 avanza.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L60c2, L60c1, L60b, L60a, L61.
- **ADR-086**, ADR-085, ADR-084, ADR-081, ADR-006, ADR-020 (la quota di rumore), ADR-054…056 (la
  compensazione e la cella RC), ADR-067 / ADR-068 (lo specchio, il VAS).
- `reports/2026-10-15-L60c2-stax-condensatore-e-rele.md` e `data/2026-10-15/L60c2/README.md`.
- `NONCOMPLIANCE.md`: **NC-069**, NC-042.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Nei deck in AC l'interruttore con isteresi di ngspice resta aperto nel punto di lavoro: un contatto
  chiuso si scrive come resistenza (L60c1).
- Le corse dei guasti che si fermano presto si rifanno col metodo gear (in L60c2 Q122 in corto in A,
  che a 50 µs si fermava a 6 ms, col gear finisce: 118 / 124 ms).
- `analizza_p10.py` di L45b vuole una cartella per corsa, e solo corse di guasto (le corse di V2 e di
  E9 hanno altre colonne).
- Le forme d'onda del banco (`run/`) non si committano.

## NON fa parte di questo lotto

- **L45d2b2** (i diodi della tenuta, il regolatore negativo, il comando, i 5 V, i massimi, NC-063):
  dopo questo lotto. Il suo prompt pronto, aggiornato con ADR-081…086 (il rivelatore tolto, J1 a
  sette pin, K3, la tenuta di `VRELAY`), è `data/2026-10-15/L60c2/NEXT-SESSION-L45d2b2.md`: alla
  chiusura di questo lotto va in questo file, con le correzioni di L60d.
- L45d2b3 (i guasti rifatti nella forma di ADR-070), L58 (la diagnosi).
- La finestra di livello su K3: scartata in ADR-086.
- Le decisioni di L60a…L60c2 non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti.

## CHIUSURA

1. `STATE.md` con L60d **fatto** nella tabella dei lotti, e il prossimo (L45d2b2).
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L60d`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
