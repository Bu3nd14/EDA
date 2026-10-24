# Prompt per la sessione successiva — L57, l'ingresso protetto per l'RCA a caldo

Nome della sessione: **hi-fi preamp L57** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L45d2b3b3** (2026-10-24): la sintesi della FMEA della scheda audio
> dopo i rimedi, **NC-042 chiusa** (ADR-100), R550 / R551 in corto a NC-072. Con lui è finito **L45**.
> Il prossimo nell'ordine deciso con l'utente dopo L45d2b3b2a: L57 → L54 → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L57**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con l'utente
all'inizio**.

## Perché questo lotto

**NC-059** (maggiore, prima di G1, «Remedy in circuit, major», decisione dell'utente in L53): inserendo
un cavo RCA sull'ingresso selezionato, con una sorgente in classe II (la massa a metà rete attraverso i
condensatori Y), il polo caldo tocca prima della massa e l'ingresso vede il 50 Hz a decine di volt. In
L53 (`data/2026-10-12/L53/rca/`): al volume in cima **il clip del finale,
~113,8 dB SPL**, sopra il tetto di non-danno di **112,2 dB SPL** di PR-23 (`rca/out/rca_spl.csv`,
`rca/out_gate/gate.csv`); il gate-gate dell'LSK489 del
blocco A a **−28,1 V** contro una rottura di ±30 V minima (1,9 V di margine). Con una sorgente a terra
conta la sola continua (0,65 V: 110 dB SPL in cima e il clip a +10 dB).

## Che cosa fare

1. **Il banco di L53 sul circuito di oggi**, provato prima su un suo caso noto (lo stesso deck sul
   blocco di L53 deve ridare `out/rca_spl.csv` / `out_gate/gate.csv`). Il blocco è cambiato da allora (L56,
   ADR-086/087/090/095/097/099): le copie del blocco si rifanno da quello di oggi (limitations #62).
2. **I numeri di oggi** senza rimedio: il gradino al jack principale e alle fisse in dB SPL a 1 m, col
   volume in cima e alla posizione d'ascolto, e il gate-gate / gate-source dell'LSK489 contro i limiti
   del datasheet.
3. **Le strade, coi numeri**, ciascuna con la sua cifra contro il limite della parte e contro il tetto:
   proteggere l'ingresso (un limitatore, diodi verso i rail, una resistenza in serie, coi loro effetti
   su rumore e distorsione), tenere l'uscita in mute (che cosa vede il cambio d'ingresso), un avviso.
   La catena a valle è quella generica (memoria «catena a valle generica»: l'RCA a caldo non è un
   guasto della scheda audio, ADR-081 non vale qui).
4. **La scelta è dell'utente**, con ADR; se cambia il circuito: sorgente, netlist, disegni,
   `run_tests.sh`, regressione (V1, E5, V4 dove il rimedio tocca l'ingresso).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#22**, **#62**, **#75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b3b3 e L53.
- **NC-059** in `NONCOMPLIANCE.md`; il report di L53 (`reports/2026-10-12-L53-misure-veloci.md`, la parte
  sull'RCA) e `data/2026-10-12/L53/rca/` (le ipotesi dichiarate in `genera.py`: il polo caldo 10 ms
  prima della massa, i condensatori Y 1 nF e 3,46 nF, la corrente di contatto di 0,25 mA).
- ADR-064 (il selettore: C_IN, R_SEL, R_J), ADR-066 (fino a ~0,65 V dalla sorgente), ADR-052 (i pin SS
  dell'LSK489), PR-20 / PR-23 in `PRB.md`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli su
  file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`). Comandi semplici, **percorsi assoluti**, script scritti con Write, Edit per i testi.
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga; le
  forme d'onda grandi non si committano (`run/` nel `.gitignore`).
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- Il micro e lo standby (L54), il dispositivo d'uscita (L55), la diagnosi (L58, con le 46 righe latenti
  della FMEA di L45d2b3b3, `data/2026-10-24/L45d2b3b3/fmea_dopo.csv`), il dossier (L64), la revisione
  (L65), G1.
- NC-072 (il rame al layout, ora anche con R550 / R551 in corto, ADR-100), NC-073 / NC-075 (alla scelta
  della parte), i piedini dei transistor contro le piazzole (al layout).
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso
  si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L57 **fatto** nella tabella dei lotti, e il prossimo (L54, dall'ordine deciso con
   l'utente).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L57`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
