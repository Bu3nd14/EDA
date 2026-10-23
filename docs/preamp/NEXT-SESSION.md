# Prompt per la sessione successiva — L45d2b3b3, la sintesi della FMEA della scheda audio

Nome della sessione: **hi-fi preamp L45d2b3b3** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L45d2b3b2b2** (2026-10-23): il calore, la Stax dei casi lunghi e il
> riposo a caldo sul blocco del sorgente, tutti dentro, nessun «Da riaprire se» scattato. Con lui è finito
> **L45d2b3b2** (il calore dei quindici guasti del blocco, ADR-099). Resta la sintesi.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b3b3**, e si ferma. Non iniziarne un secondo, salvo che
l'utente lo chieda esplicitamente nella sessione. Se si rivela più grande di una sessione,
**dividilo con l'utente all'inizio**.

## Perché questo lotto

**NC-042** (maggiore, prima di G1): la FMEA della scheda audio. Le corse sono fatte (L45d2b3b1 le 88 + 9
righe sul circuito di oggi, `righe_b1.csv`; L45d2b3b2 i quindici guasti del blocco oltre i limiti termici,
rimediati da ADR-099 e rimisurati sul sorgente in L45d2b3b2b2). Manca la **sintesi nella forma di
ADR-070**: per ogni riga le colonne **dopo il rimedio** (gravità, probabilità, rilevabilità o priorità,
secondo ADR-070 e le due eccezioni di ADR-071), e da lì se NC-042 si può chiudere.

## Che cosa fare

1. **Le righe**: `data/2026-10-22/L45d2b3b1/righe_b1.csv` (97: 80 entro, 15 al calore, C145 in corto
   all'impulso della cella → NC-075, K3 escluso → ADR-085). Le 15 del calore prendono il loro esito dopo il
   rimedio da `data/2026-10-23/L45d2b3b2b2/sintesi_sorg.csv` (13 entro; i due corti dei finali col
   dissipatore da `dissipatore.csv`: 99 / 95 °C, entro P7 e sotto il massimo assoluto) e, per i quattro
   guasti del VAS, da `sintesi_sorgt60.csv`.
2. **I modi delle parti nuove di ADR-099** (R190, R191, R192, Q193, R194, aperte e in corto; 11 modi), dalla
   stessa `sintesi_sorg.csv`: tutti entro. Sono righe nuove della FMEA.
3. **La Stax**: P10 per riga dove serve, da `data/2026-10-23/L45d2b3b2b2/stax_lunghi.csv` per i 121 casi
   oltre 100 ms (nessuno oltre 125 ms) e da L45d2b3b1 per gli altri.
4. **Le colonne dopo il rimedio** con le regole di ADR-070 / ADR-071 e gli strumenti di L45d1
   (`data/2026-10-14/L45d1/script/`: `motore.py`, `sintesi.py`, `tipi.py`); la sintesi rifatta sulle
   quattro tabelle di prima più queste righe.
5. **NC-042 chiusa se i numeri lo permettono**: che cosa resta aperto lo decide l'utente, coi numeri, per
   nome (le righe ancora alte, i guasti latenti che vanno a L58).

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#22**, **#37**, **#62**, **#75**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b3b2b2, L45d2b3b2a, L45d2b3b1, L45d1.
- **ADR-070**, ADR-071, ADR-069 (il criterio PR-30), ADR-081, ADR-097, ADR-098, ADR-099.
- `data/2026-10-22/L45d2b3b1/README.md` (le righe) e `data/2026-10-23/L45d2b3b2b2/README.md` (il calore
  sul sorgente, la mappa delle sigle).
- Il report di L45d2b3b2b2: la lettura della corrente di riposo a caldo (ADR-042 non ha una banda) è
  dichiarata lì; se l'utente vuole una banda, è una sua decisione.

## Le sigle (attenzione, #22)

Sul banco di L45d2b3b2a le parti nuove erano R161 / R162 / R167 / Q168 / R169; nel sorgente e nei dati di
L45d2b3b2b2 sono **R190 / R191 / R192 / Q193 / R194** (base + 90 su ogni istanza). In `calore_*.csv` le
colonne `P_r161_W` / `P_r162_W` sono una lista fissa dell'analizzatore e sul sorgente restano vuote: non
sono le parti nuove.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script (anche `run_tests.sh` da solo, senza redirezioni); `cd … && script`; le variabili di shell nei
  percorsi e nei cicli; `xargs` sulla riga di comando; `awk` con programmi, heredoc, `python3 -c` dentro un
  altro comando, script lunghi sulla riga di comando (scriverli su file); `sed` con valori calcolati; un
  titolo di PR con l'apostrofo (il corpo su file, `--body-file`). Comandi semplici, **percorsi assoluti**,
  script scritti con Write, Edit per i testi.
- Se serve rieseguire corse: la memoria (limitations #75) decide il parallelo, commit e push prima di una
  lista lunga; le forme d'onda grandi non si committano.
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB SPL;
  ogni opzione con la sua cifra contro il limite della parte, alle tre reti.

## NON fa parte di questo lotto

- **I piedini dei transistor e le piazzole** (B / C / E contro 1 / 2 / 3, trovato in L45d2b3b2b1): al
  layout, prima di G2; se l'utente vuole aprirne una non conformità, glielo si chiede.
- **NC-073 / NC-075** (gli impulsi di R550 / R551 e di R144 / R152): alla scelta della parte.
- **Il rame sotto i regolatori** (NC-072) e il comportamento dinamico del riposo col dissipatore: al
  layout e al prototipo.
- La tensione degli elettrolitici del blocco (C141 / C142 fino a 20,3 V): alla scelta delle parti.
- Il micro bloccato e lo standby (L54), la diagnosi (L58), l'ingresso protetto (L57), il dispositivo
  d'uscita (L55), il tetto delle fisse (NC-046), il dossier (L64), la revisione (L65), G1.
- Le decisioni prese in L45d2a, L60a…L60d, L62, L45d2b2a…c, L45d2b3a, L45d2b3b1, L45d2b3b2a non si
  riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso si torna all'utente coi
  numeri.

## CHIUSURA

1. `STATE.md` con L45d2b3b3 **fatto** nella tabella dei lotti, e il prossimo (dall'ordine deciso con
   l'utente dopo L45d2b3b2a).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b3b3`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
