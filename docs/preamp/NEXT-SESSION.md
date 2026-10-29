# Prompt per la sessione successiva — L58, la diagnosi e la distinta dell'alimentatore

Nome della sessione: **hi-fi preamp L58** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura del lotto del dispositivo d'uscita (2026-10-29): il MJE15032 / MJE15033
> resta per scelta dell'utente (ADR-106, NC-056 chiusa); aperta NC-076, il VAS a 126 °C col finale NPN
> in corto base-emettitore, maggiore prima di G1, al lotto **L66**. L'ordine verso G1: **L58** → L66 →
> L64 → L65 → G1 (la posizione di L66 è una proposta: confermala con l'utente all'inizio).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L58**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione.

## Dove siamo

Il circuito di oggi: il blocco di guadagno con i MJE15032 / MJE15033 e il dissipatore di ADR-099, lo
specchio di ADR-067, il VAS a ~10,7 mA col Miller a 470 pF (ADR-054); l'alimentatore col temporizzatore
a comparatori (ADR-102…ADR-105: R585, D534 / D535 / D536 / D541 BAS416, R571 1,1 MΩ, i condensatori dei
ritardi C0G). Nessuna bloccante per G1; da chiudere prima di G1 per decisione dell'utente NC-055, NC-072,
NC-076 (maggiori).

## Che cosa fare

La riga di L58 nella tabella dei lotti di `STATE.md`, più quello che i lotti del temporizzatore le hanno
mandato. Tre parti; **all'inizio chiedi all'utente se dividerlo** (come L45, L54, L57):

1. **I test point** sulle due schede per la diagnosi al banco e la riparazione: i rail e `VRELAY` dai due
   lati del cablaggio, V5, `MUTE_G` / `PERMIT_G` / `PERMIT_T`, l'uscita di ogni blocco, i comandi dei
   relè, ciascuno con la massa vicina.
2. **L'autodiagnosi**: che cosa il circuito vede da sé dei guasti latenti della FMEA mandati a L58
   (ADR-071 i 28 guasti silenziosi del blocco, ADR-076 il mute che non si inserisce, ADR-078 lo standby
   acceso per guasto, ADR-100 le righe «alla diagnosi L58»). **Il micro è uscito** (ADR-102): quello che
   le ADR davano al firmware si fa in hardware (per esempio un canale di comparatore verso la ritenuta) o
   torna all'utente; ogni scelta coi numeri, se serve una voce del PRB con la sua ADR.
3. **Le parti nuove dell'alimentatore**: le righe della FMEA di R585 e dei BAS416 (aperti, in corto, la
   perdita), nella forma di ADR-070; e alla distinta la conferma del **BAS416** (perdita ≤ 5 nA a 25 °C,
   VF ≤ 0,9 V a 1 mA, ADR-104) e dei **C0G da 1 µF in 1206** (ADR-105, «Da riaprire se»), con
   `bom-component-manager`: disponibilità vera, mai un codice plausibile non controllato.

Se cambia il circuito: sorgente, netlist, disegni, `run_tests.sh`, regressione, ADR nuova.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare #78–#83), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la riga di L58.
- ADR-070, ADR-071, ADR-076, ADR-078, ADR-100, ADR-102…ADR-105; il report di L45d2a
  (`2026-10-14-L45d2a-scelte-rimedi.md`) e `data/2026-10-14/L45d1/scelte_L45d2.pdf`; il report di
  L45d2b3b3 (la FMEA dopo i rimedi, `fmea_dopo.csv`).
- NC-076 in `NONCOMPLIANCE.md`: è di L66, ma **la riga della FMEA di Q132 in corto base-emettitore è
  già corretta** in `data/2026-10-29/L55/fmea_correzione.csv` (126 °C): non usare il 115 di
  `fmea_dopo.csv`.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli
  su file); `sed` con valori calcolati o con apostrofi; un titolo di PR con l'apostrofo (il corpo su
  file, `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi. **`git add` con `":(exclude)…"` non mette
  nulla in silenzio**: i percorsi si danno uno per uno. **Copiando script da un altro lotto, guarda
  che un nome non sovrascriva una copia già fatta** (successo una volta con `sintesi.py`).
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga.
  Le forme d'onda non si committano.
- Un banco o un modello nuovo si prova prima su un caso di cui si sa la risposta. Un modello del
  costruttore con un VJ sotto ~0,2 V si prova con la `tran` alla temperatura più alta (limitations #82).
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte. **Le cifre di una domanda si
  ricontano dai CSV prima di farla.**

## NON fa parte di questo lotto

- **NC-076** (il VAS a 126 °C e i modi del blocco fuori dai quindici di ADR-099): **L66**.
- Il dispositivo d'uscita (ADR-106) non si riapre, salvo che un suo «Da riaprire se» scatti.
- Il dossier (L64), la revisione (L65), G1.

## CHIUSURA

1. `STATE.md` con L58 **fatto** nella tabella dei lotti, e il prossimo (L66, o quello che l'utente ha
   deciso); le celle di «In breve» sostituite, la voce di diario, la più vecchia delle tre in cima al
   diario di `STATE-STORIA.md` (la regola 7 di «Le regole»).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L58`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
