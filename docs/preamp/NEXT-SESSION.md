# Prompt per la sessione successiva — L45d2b3b2, il calore dei guasti del blocco

Nome della sessione: **hi-fi preamp L45d2b3b2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L45d2b3b1** (2026-10-22), le corse dei guasti singoli sul circuito
> di oggi. L45d2b3b era stato diviso dall'utente in due («Due parti»: le corse, la sintesi); coi numeri
> delle corse l'utente ha scelto un lotto in mezzo per il calore («Lotto dedicato», ADR-097 punto 4).
> Quindi: **L45d2b3b2 il calore** (questo), poi **L45d2b3b3 la sintesi**.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b3b2**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, prima di G1). In L45d2b3b1 (`data/2026-10-22/L45d2b3b1/`, `sintesi_calore.csv`,
`righe_b1.csv`) **quindici guasti del blocco di guadagno portano una parte oltre i suoi limiti** con
60 °C d'aria, coi rail ideali del banco:

| Guasto | La parte più calda |
|---|---|
| R149 in corto | l'aiuto dello specchio Q148, 5123 °C (~12,6 W in SOT-23) |
| Q121A base-emettitore in corto; Q121A aperto; R119 aperta; R107 in corto; Q106 in corto | Q148, 515–885 °C |
| Q148 in corto | lo specchio Q121, 574 °C |
| D102 / D103 aperti | Q148, 416 °C (e la Stax a 145,8 ms, ADR-098) |
| Q133 in corto; Q125 in corto | il VAS Q122, 308 / 229 °C |
| R101 in corto; R126 in corto | Q148 239 °C e i diodi del riferimento; il carico del VAS 193 °C |
| Q121B base-emettitore in corto; Q132 in corto | 149 °C (P7: 125) |

In L45a li fermava il rivelatore di continua spegnendo i rail (ADR-072, «col calore»). **ADR-081 ha
tolto il rivelatore** e rimesso all'utente le scelte 6, 8, 9 e 10, **non queste righe**: da allora non
hanno rimedio. (C145 in corto non è qui: è l'impulso della cella, NC-075.)

## Che cosa costruire

1. **Lo stato dopo**: una parte da 12 W in SOT-23 si apre in millisecondi. Per ogni guasto, che cosa
   lascia la parte bruciata (aperta, o in corto), e se il danno si ferma lì o si propaga. Simulato,
   non dedotto.
2. **I rimedi candidati**, misurati sul banco del calore di L45d2b3b1 (`script/genera_calore.py`,
   varianti del blocco come L62a): per esempio un limite di corrente per blocco sui rail, un fusibile
   ripristinabile, resistenze che limitino le correnti dei nodi critici, o altro trovato in letteratura.
   Ciascuno coi suoi effetti su V1, PSRR, rumore, P7 e la regressione dei 21 deck veloci.
3. **La scelta con l'utente**, coi numeri: per ogni opzione la temperatura delle parti contro il loro
   limite, a rete ±10 % dove conta. Poi, se cambia il circuito: sorgente (con l'ADR nei commenti),
   netlist, i tre disegni (`gain_block_draw.py`, `psu_draw.py`, `audio_draw.py` col manifesto),
   `run_tests.sh`, regressione, e i guasti toccati rifatti (calore e Stax; i casi oltre 100 ms con
   `script/genera_stax_lunghi.py`, ADR-098).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#59, #62, #64, #69, #73, #74, #75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L45d2b3b1.
- `NONCOMPLIANCE.md`: NC-042, NC-075.
- ADR-070, ADR-072, ADR-081, ADR-086, ADR-090, ADR-095, ADR-097, ADR-098.
- `data/2026-10-22/L45d2b3b1/README.md`: i banchi e i loro casi noti.

## I vincoli

- **La memoria (limitations #75)**: il numero di corse in parallelo si sceglie sulla memoria, non sui
  processori (il Mac ha 24 GB). R120 in corto e ogni caso lento si corrono **da soli e corti** (0,6 s).
  Prima di lasciar girare una lista lunga: commit e push.
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
  `circuits/preamp` si lanciano con la cartella corrente lì (`data/2026-10-22/L45d2b3b1/script/rigenera.sh`).
- **Dopo una rigenerazione** si confrontano le netlist per piedini (`script/nomi_reti.py`, limitations
  #74).
- **Non modificare uno script mentre zsh lo sta eseguendo**, e non cambiare un generatore mentre una
  lista di casi gira. I deck della Stax includono `spice/preamp/gain_block.subckt` direttamente: non
  rigenerare il blocco mentre corrono.
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL; ogni opzione con la
  sua cifra contro il limite della parte, alle tre reti.

## NON fa parte di questo lotto

- **La sintesi** (le colonne dopo il rimedio di ADR-070): è L45d2b3b3.
- **NC-073 / NC-075** (gli impulsi di R550 / R551 e di R144 / R152): alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- La tensione degli elettrolitici del blocco (C141 / C142 fino a 20,3 V): alla scelta delle parti.
- Il micro bloccato e lo standby (L54), la diagnosi (L58), l'ingresso protetto (L57), il dispositivo
  d'uscita (L55), il tetto delle fisse (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a…c, L45d2b3a, L45d2b3b1 non si riaprono,
  salvo che un «Da riaprire se» della loro ADR scatti. In quel caso si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L45d2b3b2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b3b3).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b3b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
