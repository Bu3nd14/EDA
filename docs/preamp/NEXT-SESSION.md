# Prompt per la sessione successiva — L62a, il moltiplicatore di Vbe: i guasti e la scelta del rimedio

Nome della sessione: **hi-fi preamp L62a** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L62a**, la prima parte di L62, e si ferma. Non iniziarne un
secondo, salvo che l'utente lo chieda esplicitamente nella sessione. L62 è diviso in due parti per
decisione dell'utente (2026-10-19, dopo L60d2): **L62a** i guasti rifatti, i rimedi provati sul
banco e la scelta; **L62b** il rimedio nel sorgente e la sua verifica. **Il circuito non cambia in
L62a.**

## Perché questo lotto, e perché adesso

**NC-062** è l'unica non conformità **bloccante per G1** senza un lotto (aperta dopo L45a,
2026-10-13, dall'utente: «apri la non conformità del moltiplicatore di Vbe come bloccante»). Quattro
guasti singoli del moltiplicatore di Vbe non si sentono al jack (meno di 0,5 mV), la scheda resta
sotto 1 A e il sorvegliante non interviene, ma i finali e le 22 Ω d'emettitore vanno oltre i limiti:

| Guasto (L45a, `data/2026-10-13/L45a/analisi_B.csv`, 27 °C) | Ogni finale | Ogni 22 Ω | Corrente del blocco |
|---|---|---|---|
| Q127 emettitore aperto (`Q127_ae`) | 2,48 W, 182 °C | 3,28 W | ~0,40 A (38 mA a riposo) |
| Q127 in corto base-emettitore (`Q127_be`) | 2,45 W, 181 °C | 1,72 W | ~0,29 A |
| R129 in corto (`R129_cc`) | 2,45 W, 181 °C | 1,72 W | ~0,29 A |
| R128 aperta (`R128_ap`) | 1,23 W, 104 °C | 7,54 W | ~0,59 A |

Con 60 °C d'aria, come vuole P7 (ADR-021, Tj ≤ 125 °C, MJE in TO-220 senza dissipatore 62,5 °C/W), i
finali arrivano a ~215 °C. **Viene prima di L45d2b2** (decisione dell'utente dopo L60d2) perché il
rimedio cambia probabilmente il blocco: L45d2b2 legge i massimi e la dissipazione dei finali col
rail a ±20,3 V (ADR-078), L45d2b3 rifà i guasti del blocco nella forma di ADR-070, e conviene che il
blocco si fermi una volta sola, prima di loro.

## Che cosa costruire

1. **I quattro modi rifatti sul blocco di oggi.** Da L45a il blocco è cambiato: R150–R153 (ADR-086,
   ADR-087), il moltiplicatore Q127 in **DZT5551 / SOT-223** (ADR-082, L60b; il modello resta quello
   dell'MMBT5551, stesso die), la ridondanza su R112 e R144. Il banco è quello di L45a
   (`data/2026-10-13/L45a/script/genera_canale.py`, `analizza_tr.py`), **con le copie guaste del blocco
   rifatte dal blocco di oggi** (limitations #62: `copia_guasta()` e `reindirizza()` di
   `data/2026-10-19/L60d2/script/genera_L60d2.py`). Le quattro posizioni del canale (A, F1, F2, B; B
   anche a +10 dB). Le Tj a 27 e a 60 °C d'aria, il calore di ogni parte del blocco contro la sua
   (anche Q127 in SOT-223 e le resistenze del moltiplicatore), la corrente dei rail (limitations
   #59). Se i numeri sono cambiati rispetto a L45a, lo si dice prima di tutto.
2. **I rimedi sul banco**, almeno due o tre, ciascuno coi quattro modi e col blocco sano (il riposo
   dei finali, il margine di V1 dai deck d'anello, la distorsione di V4 a caldo se il rimedio tocca
   la polarizzazione). Candidati da valutare, non decisi:
   - la ridondanza nel moltiplicatore, come ADR-086 per R109 (parti sdoppiate o in parallelo, perché un
     guasto singolo lasci la polarizzazione dentro un limite);
   - un limite alla corrente di riposo dei finali indipendente dal moltiplicatore (per esempio sulle
     22 Ω d'emettitore);
   - uno stato sicuro e riconoscibile: il guasto porta il blocco in una condizione che il
     sorvegliante o il mute vedono;
   - accettare il calore con un dissipatore sui finali: va contro i vincoli meccanici di oggi, va
     detto con i numeri.
   La letteratura sulle protezioni dei moltiplicatori di Vbe negli stadi in classe AB va cercata (con
   un agente, se serve; il worktree si apre **dopo** che ha finito).
3. **La scelta con l'utente**, coi numeri del banco: per nome, senza sigle, temperature in °C, i
   gradini in dB SPL. La sua ADR. Nessuna modifica al sorgente: è di L62b.

## Prima di tutto

- `CLAUDE.md`, `AGENTS.md`, `docs/limitations.md` (in particolare **#57**, **#59**, **#61**, **#62**).
- `docs/preamp/STATE.md`: «In breve», le voci di L60d2, L60d1 e «Dopo L45a».
- `NONCOMPLIANCE.md`: **NC-062**, NC-042.
- ADR-021 (P7), ADR-068, ADR-070, ADR-082 (Q127 in SOT-223), ADR-086, ADR-087, ADR-089.
- `reports/2026-10-13-L45a-fmea-blocco.md` («Il calore»), `data/2026-10-13/L45a/README.md`;
  `reports/2026-10-19-L60d2-guasti-stax-e-v2-media.md`.
- `circuits/preamp/gain_block.py`: il moltiplicatore (Q127, R128, R129) e lo stadio d'uscita.

## I vincoli

- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB e dB SPL.
- Nel worktree vengono rifiutati:
  - i comandi composti, `cd … && script`, le variabili di shell nei percorsi, `xargs` sulla riga di
    comando, gli script lunghi passati sulla riga di comando (scriverli su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono prima di entrare nel worktree, o un file per comando;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Le corse dei guasti che si fermano presto si rifanno col metodo gear; se non basta, con `reltol`
  meno stretta (L60d2).
- Un punto di lavoro si giudica anche dalla corrente dei rail (limitations #59).
- Le forme d'onda del banco (`run/`) non si committano.

## NON fa parte di questo lotto

- **Il rimedio nel sorgente** e la sua verifica (regressione del blocco, i quattro modi, P7, V2 se il
  blocco cambia dove conta): **L62b**.
- **L45d2b2**: dopo L62. Il suo prompt pronto è `data/2026-10-19/dopo-L60d2/NEXT-SESSION-L45d2b2.md`.
- L45d2b3 (con R153 in corto, Q146 a 0,41 W), L58.
- Le decisioni di ADR-086…089 non si riaprono, salvo che scatti un loro «Da riaprire se».

## CHIUSURA

1. `STATE.md` con L62a **fatto** nella tabella dei lotti, e il prossimo (L62b).
2. Riscrivi QUESTO file per L62b, con la riga «Nome della sessione: hi-fi preamp L62b» subito sotto
   il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L62a` (quello del worktree).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
