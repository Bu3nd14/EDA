# Prompt per la sessione successiva — L45d2b2b2, il comando dei relè e i 5 V della logica

Nome della sessione: **hi-fi preamp L45d2b2b2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L45d2b2b1 (2026-10-20), dal prompt di L45d2b2b. L45d2b2b è stato
> diviso dall'utente in due («Due parti»): i diodi della tenuta e il regolatore negativo (fatto,
> ADR-093), e **questa**. Dopo viene L45d2b2c, i massimi del blocco (prompt in
> `data/2026-10-20/L45d2b2a/NEXT-SESSION-L45d2b2c.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2b2**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se L45d2b2b2 si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078); L45d2b li costruisce:
- L45d2b1 (il rivelatore, poi tolto da ADR-081);
- L45d2b2: a) la partenza morbida (fatta, ADR-091), b1) i diodi della tenuta (fatto, ADR-093),
  **b2) questa**, c) i massimi;
- L45d2b3, i guasti rifatti nella forma di ADR-070 e la sintesi.

**Che cosa è cambiato con L45d2b2b1 (2026-10-20)**:
- **ADR-093**: uno Schottky SB340 in serie dopo ciascun regolatore dei rail (D515 / D516), la
  retroazione sul piedino, U501 a 15,3 V e R501 120 kΩ, due SB340 sul piedino (D510 + D513, D511 +
  D514). `psu.py` 124 parti. Non tocca la linea dei relè, U503, U504 né il comando.
- **NC-073** aperta: R550 / R551 a 80–100 W per ~0,1 s in un corto sul piedino (alla scelta della
  parte, non qui).
- **Il banco dell'alimentatore** è `data/2026-10-20/L45d2b2b1/psu/` (README): quello di L45d2b2a coi
  casi dei rail, le sonde di corrente sugli Schottky (una sorgente da 0 V in serie, solo nei casi di
  guasto: `SONDA_D` in `genera_tb_psu.py`), `--file-carico`, `--valore REF=val`, e i runner
  `uno.sh <etichetta> <caso> [opzioni]` e `corri_lista.sh <lista> <etichetta> [opzioni]` (8 alla
  volta). La catena audio è `script/catena_074.sh <etichetta> <100k|vuoto> <casi...>` (ponte → V2
  `--matrice l41c`), controllata su L45c1. Si parte da lì.
- Il `modi.py` di quel banco ha già i casi del comando di L45c2 (`f_d506_corto_mus`,
  `f_d505_corto_mus`, `f_u504_spento_mus`, …).

## Che cosa costruire

Il punto di partenza è `docs/preamp/data/2026-10-14/L45d2a/decisioni.csv`. Ogni ADR, commit e report
cita la scelta per numero di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che non si riscrive.

1. **Il limite di corrente sul comando** (ADR-075; scelta 4).
   - Oggi un diodo di bloccaggio in corto (D505, D506, D508) o la bobina di K501 in corto mettono la
     linea dei relè a massa attraverso un 2N7002 (Q501, Q503: 115 mA continui). **Il ~1 A non è una
     misura**: è dedotto dal limite del modello di U503 (`ILIM=1`). **Prima di tutto si misura**: una
     sonda di corrente nel drain dei 2N7002 (come `SONDA_D`), e la durata (fino a che il firmware
     reagisce), poi la potenza e l'energia contro i limiti della parte (corrente di picco, SOA, Tj a
     60 °C d'aria).
   - ADR-075 lo lega anche alle **righe delle resistenze in corto** (R503 del riferimento, R510 e R512
     del rivelatore di rete): in L45c2 non hanno una corsa propria (`uguale` / `calcolo`): R503 «~0,25 A
     nel LM4040», R510 «~17 V sulla base di Q504». Vanno simulate.
   - Il limite non deve rallentare lo stacco del jack né Δ (P9 (b); «Da riaprire se» di ADR-075).
     Regole di `data/2026-10-14/L45c2/script/analizza_psu.py` / `analizza_rele.py`.
2. **Il limitatore sulla linea a 5 V** (ADR-075): uno zener o un TVS con fusibile ripristinabile,
   perché U504 in corto fra ingresso e uscita non porti 12 V all'ATtiny3216 (6 V di massimo
   assoluto). In L45c2 era solo `calcolo`: va simulato (una primitiva `corto` fra `vrelay_reg` e `v5`).
   - Il limitatore non deve cambiare il consumo in standby (P9 (a), NC-037) né la logica a regime.

**Ogni opzione portata all'utente** arriva già con la sua cifra contro il limite della parte (Tj a
60 °C d'aria, corrente, tensione), alle tre reti (gli eventi `musm10` / `musp10` del `modi.py` di
L45d2b2b1 lo fanno per i casi `mus`).

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR. Uno strumento di
misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#65** e **#66**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b2b1, L45d2b2a, L45c2, L45d2a.
- `NONCOMPLIANCE.md`: NC-042 (l'avanzamento di L45d2b2b1), NC-037, NC-073.
- ADR-075, ADR-093, ADR-045, ADR-046, ADR-048, ADR-049, ADR-070.
- `reports/2026-10-20-L45d2b2b1-diodi-tenuta.md`; `data/2026-10-20/L45d2b2b1/README.md`.
- I casi di L45c2 (`data/2026-10-14/L45c2/`: `fmea_comando.csv`, `analisi_psu.csv`,
  `analisi_rele.csv`, il report `reports/2026-10-14-L45c2-fmea-comando.md`).
- `circuits/preamp/psu.py` (`sink()`, Q501–Q503, D505–D509, K501, U503, U504, U507, R503, Q504, R510,
  R512) e `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc (anche da solo: `python3 - <<EOF` è
    rifiutato), un `python3 -c` dentro un altro comando, gli script lunghi passati sulla riga di
    comando (scriverli su file e lanciarli);
  - `sed` con un valore calcolato al momento (si scrive uno script);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare;
  - `pkill -f` col percorso relativo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- **SKiDL scrive `psu.erc` / `psu.log` / `psu_sklib.py` nella cartella corrente**: `psu.py` si lancia
  con la cartella corrente in `circuits/preamp`.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi), e non cambiare il
  generatore mentre una lista di casi gira (i giri successivi leggerebbero l'altra versione).
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito. Un
  agente di sola ricerca web, senza comandi né scritture, può girare anche a worktree aperto.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL.
- Piste larghe al layout: un rimedio che aggiunge parti di potenza lo ricordi.

## NON fa parte di questo lotto

- **I massimi del blocco** (ADR-078): sono di **L45d2b2c**.
- **I guasti rifatti nella forma di ADR-070** e la sintesi: sono di **L45d2b3** (con loro R144 contro
  la sua parte, R153 in corto, le durate di P10 sulla Stax, e i modi delle parti nuove di ADR-093:
  D513–D516).
- **NC-073** (l'impulso di R550 / R551): alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- Il micro bloccato e lo standby (L54), la diagnosi (L58), l'ingresso protetto (L57), il dispositivo
  d'uscita (L55), il tetto delle fisse (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a e L45d2b2b1 non si riaprono, salvo che un «Da
  riaprire se» della loro ADR scatti. In quel caso si torna all'utente con i numeri.

## CHIUSURA

1. `STATE.md` con L45d2b2b2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b2c).
2. Riscrivi QUESTO file per il lotto successivo (dal prompt messo da parte di L45d2b2c,
   `data/2026-10-20/L45d2b2a/NEXT-SESSION-L45d2b2c.md`), con la riga
   «Nome della sessione: hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b2b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
