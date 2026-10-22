# Prompt per la sessione successiva — L45d2b3b2b2, il calore sul blocco del sorgente

Nome della sessione: **hi-fi preamp L45d2b3b2b2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L45d2b3b2b1** (2026-10-22): i rimedi di ADR-099 nel sorgente, il
> dissipatore sui finali, regressione, V1 e P7. L45d2b3b2b era stato diviso dall'utente all'inizio
> («Due parti»): b1 il sorgente (fatto), **b2 il calore** (questo). Poi **L45d2b3b3 la sintesi**.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b3b2b2**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, prima di G1). ADR-099 è nel sorgente (`gain_block.py`, sezione 14) e il blocco
generato è riga per riga la variante `rv2` misurata in L45d2b3b2a, a meno delle sigle. ADR-099 chiede
però che il calore, la Stax e il riposo a caldo si rifacciano **sul blocco del sorgente**, e due cose
nuove vanno misurate per la prima volta: il riposo col finale sul dissipatore, V4 a caldo col limite
del VAS.

## Le sigle (attenzione, #22)

Sul banco di L45d2b3b2a le parti nuove erano R161 / R162 / R167 / Q168 / R169; nel sorgente sono
**R190** (10 kΩ, aiuto) / **R191** (3,40 kΩ, riferimento) / **R192** (22 Ω, VAS) / **Q193** (limite del
VAS) / **R194** (1 kΩ, coda), da **base + 90** su ogni istanza (R290…, R590…). Gli script del banco che
cercano le parti per nome vanno puntati alle sigle nuove; i confronti col banco rimappano
(`data/2026-10-22/L45d2b3b2b1/script/confronta_rv2.py` e `confronta_regressione.py` hanno la mappa).

## Che cosa fare

1. **Il calore dei quindici e dei modi delle parti nuove** sul blocco di `spice/preamp/` (`genera.py` di
   L45d2b3b2a, che oggi lo prende come variante: la «variante» è il blocco del sorgente). Deve ridare
   `sintesi_rv2.csv` di L45d2b3b2a a meno delle sigle: 13 su 15 entro, il VAS al più 123 °C (119 coi
   dispositivi a 60 °C), i corti dei finali a 149 / 160 °C nudi. I corti dei finali col dissipatore:
   `dissipatore.py` di L45d2b3b2a sulle potenze nuove (20 °C/W a 1 W dalla curva Ohmite, il datasheet
   è in `vendor/heatsink/ohmite/WA-T220-101E/`).
2. **La Stax dei casi oltre 100 ms** (`script/genera_stax_lunghi.py` di L45d2b3b1, ADR-098: D102 / D103
   aperti erano 145,8 ms). Il generatore rifiuta il blocco senza R160: estenderlo alle parti nuove.
3. **La corrente di riposo e V4 a caldo** col metodo di L56 (`data/2026-10-12/L56/script/caldo.py`): il
   limite del VAS a caldo, e il moltiplicatore accoppiato in rame al finale NPN che ora ha un
   dissipatore (ADR-034, ADR-082 punto 4): R_thJA del finale da 62,5 a ~24,5 °C/W, più freddo e più
   lento. Il «Da riaprire se» di ADR-099: se il riposo si sposta oltre quanto ADR-042 accetta, o se il
   limite cambia la distorsione a 20 kHz o l'intermodulazione oltre V4, si torna all'utente coi numeri.
4. **I «Da riaprire se» di ADR-099 e di ADR-097** (le correnti dei rail del blocco: a riposo VAS 10,715
   contro 10,713 mA sul banco; se il sorgente dà altro, la cella RC e R153 si rimisurano).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#22, #37, #62, #69, #74, #75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di L45d2b3b2b1.
- **ADR-099**, ADR-097, ADR-098, ADR-087, ADR-042, ADR-034.
- `data/2026-10-22/L45d2b3b2b1/README.md` (il sorgente, le sigle, la regressione) e
  `data/2026-10-22/L45d2b3b2a/README.md` (il banco del calore, i comandi).

## I vincoli

- **La memoria (limitations #75)**: il numero di corse in parallelo si sceglie sulla memoria, non sui
  processori (il Mac ha 24 GB). Le corse del banco del calore pesano ~50 MB; R120 in corto e ogni caso
  lento si corrono **da soli e corti** (0,6 s). Prima di lasciar girare una lista lunga: commit e push.
- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `cd … && script`, le variabili di shell nei percorsi e nei cicli (anche `for n in …; do sed -n
    ${n}p …`);
  - `xargs` sulla riga di comando (va dentro uno script);
  - `awk` con programmi, un heredoc, un `python3 -c` dentro un altro comando, gli script lunghi passati
    sulla riga di comando (scriverli su file e lanciarli);
  - `sed` con un valore calcolato al momento, e più `sed -e` con indirizzi in un solo comando (si usa
    Edit, o uno script);
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. `/usr/bin/env VAR=… comando` passa.
- **SKiDL scrive i suoi `.erc` / `.log` / `_sklib.py` nella cartella corrente**: i sorgenti in
  `circuits/preamp` si lanciano con la cartella corrente lì (`data/2026-10-22/L45d2b3b2b1/script/rigenera.sh`).
- **`analizza_calore.py` di L45d2b3b1 divide la cartella al primo «_»**: nomi di variante senza «_», o la
  sintesi di L45d2b3b2a che ricompone la posizione.
- **Non modificare uno script mentre zsh lo sta eseguendo**, e non cambiare un generatore mentre una
  lista di casi gira. I deck della Stax includono `spice/preamp/gain_block.subckt` direttamente: non
  rigenerare il blocco mentre corrono.
- **Le forme d'onda grandi non si committano**: `data/2026-10-22/L45d2b3b2b1/script/pulisci.py` è il
  modello (via i `.json`, i `.txt` e i `.csv` oltre 1 MB).
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Le domande all'utente si fanno per nome, senza sigle; i colpi al jack in dB SPL; ogni opzione con la
  sua cifra contro il limite della parte, alle tre reti.

## NON fa parte di questo lotto

- **La sintesi** (le colonne dopo il rimedio di ADR-070): è L45d2b3b3.
- **I piedini dei transistor e le piazzole** (il simbolo B / C / E contro le impronte 1 / 2 / 3, trovato
  in L45d2b3b2b1): al layout, prima di G2; se l'utente vuole aprirne una non conformità, glielo si
  chiede.
- **NC-073 / NC-075** (gli impulsi di R550 / R551 e di R144 / R152): alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072): al layout dell'alimentatore, G2.
- La tensione degli elettrolitici del blocco (C141 / C142 fino a 20,3 V): alla scelta delle parti.
- Il micro bloccato e lo standby (L54), la diagnosi (L58), l'ingresso protetto (L57), il dispositivo
  d'uscita (L55), il tetto delle fisse (NC-046), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a…c, L45d2b3a, L45d2b3b1, L45d2b3b2a non si
  riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso si torna all'utente coi
  numeri.

## CHIUSURA

1. `STATE.md` con L45d2b3b2b2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b3b3).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b3b2b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
