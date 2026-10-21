# Prompt per la sessione successiva — L45d2b2c, i massimi del blocco

Nome della sessione: **hi-fi preamp L45d2b2c** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L45d2b2b2 (2026-10-21), da quello messo da parte in
> `data/2026-10-20/L45d2b2a/NEXT-SESSION-L45d2b2c.md`. Dopo viene L45d2b3, i guasti rifatti e la
> sintesi.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2c**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078); L45d2b li costruisce:
- L45d2b2: a) la partenza morbida (fatta, ADR-091), b1) i diodi della tenuta (fatto, ADR-093),
  b2) il comando e i 5 V (fatto, ADR-094), **c) questa**;
- L45d2b3, i guasti rifatti nella forma di ADR-070 e la sintesi.

**Che cosa è cambiato con L45d2b2b2 (2026-10-21)**. Riguarda l'alimentatore e non il blocco:
- **ADR-094**: due 1N4148 in serie per ogni diodo di bloccaggio (D530–D532), R552 47 Ω davanti a
  Q503, R503 / R510 / R512 sdoppiate (R553–R555), U504 + U512 in serie per i 5 V. `psu.py` 133 parti.
- Il banco dell'alimentatore di `data/2026-10-20/L45d2b2b2/psu/` (README):
  - una sonda di corrente sui pin (`SONDE_I`, `--sonde`) e la corrente del corto, `i(vfc)`;
  - `GIRI_MAX`;
  - il 2N7002 tarato sul datasheet, `--n2n7002 ds`; quello di default satura ~4 volte (limitations #67).
- Trovato: il firmware rifà l'accensione dopo un falso «buco di rete» (§ 4.5), e ogni guasto del
  comando si ripete; è di L58.

## Che cosa costruire

1. **Le tensioni massime delle parti del blocco** col rail fino a ±20,3 V, e la dissipazione dei
   finali (ADR-078; la scelta di `data/2026-10-14/L45d1/scelte_L45d2.pdf`).
   - Si lavora sul blocco coi quattro diodi di ADR-090. Ai loro capi c'è lo spread: ~2 V a riposo, e
     ~3 V coi guasti del moltiplicatore, quando portano la corrente del VAS (~10 mA).
   - Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai limiti, e in quel
     caso **si torna all'utente**.
   - ±20,3 V è il rail col regolatore in corto fra ingresso e uscita, e va riletto col percorso di
     oggi:
     - il grezzo passa da R550 / R551 (ADR-092: ~1,4 V in meno a regime);
     - il rail sta dietro lo Schottky in serie (ADR-093: ~0,3 V in meno);
     - il regolatore è impostato a 15,3 V.
2. **Ogni opzione portata all'utente** arriva già con la sua cifra contro il limite della parte (Tj a
   60 °C d'aria, tensione, corrente), alle tre reti.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR. Uno strumento di
misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#59, #62, #63, #65, #66, #67, #68**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b2b2, L45d2b2b1, L45d2b2a.
- `NONCOMPLIANCE.md`: NC-042, NC-072.
- ADR-078, ADR-090, ADR-092, ADR-093, ADR-094.
- Il banco del blocco di L62b (`data/2026-10-19/L62b/`) e i deck di guasto rifatti dal blocco di
  oggi (limitations #62).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc, un `python3 -c` dentro un altro comando,
    gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - `sed` con un valore calcolato al momento (si scrive uno script);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare;
  - `pkill -f` col percorso relativo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- **SKiDL scrive i suoi `.erc` / `.log` / `_sklib.py` nella cartella corrente**: i sorgenti in
  `circuits/preamp` si lanciano con la cartella corrente lì.
- **Non modificare uno script mentre zsh lo sta eseguendo**, e non cambiare un generatore mentre una
  lista di casi gira. Se succede, si prova che i deck sono rimasti uguali (L45d2b2b2 l'ha fatto).
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito. Un
  agente di sola ricerca web, senza comandi né scritture, può girare anche a worktree aperto.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL.
- Piste larghe al layout: un rimedio che aggiunge parti di potenza lo ricordi.

## NON fa parte di questo lotto

- **I guasti rifatti nella forma di ADR-070** e la sintesi: sono di **L45d2b3**. Ci vanno anche:
  - R144 contro la sua parte, R153 in corto, le durate di P10 sulla Stax;
  - i modi delle parti nuove di ADR-093 (D513–D516) e di ADR-094 (D530–D532 aperti, R552, U512, C536,
    le metà aperte delle resistenze sdoppiate).
- **NC-073** (l'impulso di R550 / R551) e il sovraccarico breve di R552: alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- Il micro bloccato e lo standby (L54), la diagnosi (L58: anche il firmware che riparte dopo un falso
  buco di rete), l'ingresso protetto (L57), il dispositivo d'uscita (L55), il tetto delle fisse
  (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a, L45d2b2b1 e L45d2b2b2 non si riaprono,
  salvo che un «Da riaprire se» della loro ADR scatti. In quel caso si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L45d2b2c **fatto** nella tabella dei lotti, e il prossimo (L45d2b3).
2. Riscrivi QUESTO file per il lotto successivo (L45d2b3), con la riga «Nome della sessione: hi-fi
   preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b2c`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
