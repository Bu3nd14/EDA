# Prompt per la sessione successiva — L45d2b3b2b, i rimedi del calore nel sorgente

Nome della sessione: **hi-fi preamp L45d2b3b2b** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L45d2b3b2a** (2026-10-22): lo stato dopo la parte bruciata, i rimedi
> misurati su varianti del blocco, la scelta dell'utente (ADR-099). L45d2b3b2 era stato diviso
> dall'utente in due all'inizio («Due parti»). Quindi: **L45d2b3b2b il sorgente** (questo), poi
> **L45d2b3b3 la sintesi**.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b3b2b**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, prima di G1). L'utente ha scelto (ADR-099, «Quattro rimedi», «Dissipatore scelto
ora») il rimedio dei quindici guasti del blocco che portano una parte oltre i limiti termici. Su varianti
del blocco (`data/2026-10-22/L45d2b3b2a/`, variante `rv2`) i rimedi chiudono 13 dei 15 con il blocco sano
invariato; il dissipatore chiude i due corti dei finali, **a calcolo**. Ora vanno nel circuito canonico
e si verificano lì.

## Che cosa costruire

1. **Il sorgente** (`circuits/preamp/gain_block.py`, otto istanze), ogni valore col commento che punta ad
   ADR-099; le parti nuove in fondo, come le sezioni 7–13 (limitations #22):
   - una **10 kΩ** fra il collettore dell'aiuto dello specchio (Q148) e il rail negativo (oggi il
     collettore è sul rail);
   - il **limite del VAS**: R123 da 56 Ω diventa **33 Ω** dal rail filtrato a un nodo nuovo **+ 22 Ω**
     verso l'emettitore del VAS; un **MMBT5401** con emettitore sul rail filtrato, base sul nodo fra le
     due, collettore sulla base del VAS (NVB);
   - una **1 kΩ, ≥ 0,5 W a 60 °C** (0,236 W con R107 in corto) fra il nodo dei source (SRC) e il
     collettore di Q106;
   - **R101 in due da 3,40 kΩ** in serie;
   - il **dissipatore Ohmite WA-T220-101E** su ciascun finale (MJE15032, MJE15033): l'impronta (due
     piedini in più, al potenziale del collettore), la distinta (`preamp_audio.py`). I dissipatori non
     devono toccarsi né toccare il telaio.
   La variante `rv2` di L45d2b3b2a è il riferimento testuale (`varianti/rv2/gain_block.subckt`): il blocco
   generato deve coincidere con lei a meno delle sigle.
2. **Netlist e disegni**: rigenerare (con la cartella corrente in `circuits/preamp`), confrontare le
   netlist per piedini (`nomi_reti.py` di L45d2b3b1, limitations #74), i tre disegni
   (`gain_block_draw.py`, `psu_draw.py`, `audio_draw.py` col manifesto), `run_tests.sh`.
3. **Le verifiche sul blocco del sorgente**:
   - la regressione dei 21 deck veloci, prima / dopo; V1; P7 con le parti nuove (`prepara_regressione.py`
     e `p7_confronto.py` di L45d2b3b2a);
   - il calore dei quindici e dei modi delle parti nuove (`genera.py` di L45d2b3b2a): devono ridare
     `sintesi_rv2.csv`;
   - **la Stax** dei casi oltre 100 ms (`script/genera_stax_lunghi.py` di L45d2b3b1, ADR-098: D102 / D103
     aperti erano 145,8 ms);
   - **la corrente di riposo e V4 a caldo** col metodo di L56 (il limite del VAS a caldo, e il
     moltiplicatore accoppiato in rame a un finale che ora ha un dissipatore: ADR-034, ADR-082 punto 4);
   - i «Da riaprire se» di ADR-099 e di ADR-097 (le correnti dei rail del blocco).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#22, #37, #62, #69, #74, #75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L45d2b3b2a.
- **ADR-099** (i vincoli per la seconda parte), ADR-097, ADR-098, ADR-087, ADR-067, ADR-054, ADR-034.
- `data/2026-10-22/L45d2b3b2a/README.md`: il banco, le varianti, i comandi.

## I vincoli

- **La memoria (limitations #75)**: il numero di corse in parallelo si sceglie sulla memoria, non sui
  processori (il Mac ha 24 GB). Le corse del banco del calore pesano ~50 MB; R120 in corto e ogni caso
  lento si corrono **da soli e corti** (0,6 s). Prima di lasciar girare una lista lunga: commit e push.
- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `cd … && script`, le variabili di shell nei percorsi (anche `f=$(ls …)` seguito da un comando);
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, i cicli con variabili, un heredoc, un `python3 -c` dentro un altro comando,
    gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - `sed` con un valore calcolato al momento (si scrive uno script);
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- **SKiDL scrive i suoi `.erc` / `.log` / `_sklib.py` nella cartella corrente**: i sorgenti in
  `circuits/preamp` si lanciano con la cartella corrente lì (`data/2026-10-22/L45d2b3b1/script/rigenera.sh`).
- **`analizza_calore.py` di L45d2b3b1 divide la cartella al primo «_»**: nomi di variante senza «_», o la
  sintesi di L45d2b3b2a che ricompone la posizione.
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
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a…c, L45d2b3a, L45d2b3b1, L45d2b3b2a non si
  riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso si torna all'utente coi
  numeri.

## CHIUSURA

1. `STATE.md` con L45d2b3b2b **fatto** nella tabella dei lotti, e il prossimo (L45d2b3b3).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b3b2b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
