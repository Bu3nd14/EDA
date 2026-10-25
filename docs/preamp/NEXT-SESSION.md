# Prompt per la sessione successiva — L54, il micro, lo standby e lo spegnimento morbido, riesaminati

Nome della sessione: **hi-fi preamp L54** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di **L57b** (2026-10-25): il limitatore d'ingresso nel sorgente, NC-059
> chiusa. L'ordine deciso con l'utente dopo L45d2b3b2a: L57 (fatto) → **L54** → L55 → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L54**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione. Se si rivela più grande di una sessione, **dividilo con l'utente
all'inizio** (è probabile: un confronto fra due architetture del temporizzatore, poi la scelta, poi
l'eventuale sorgente).

## Perché questo lotto

**NC-054** (maggiore, prima di G1; decisione dell'utente in L52: «Accept, major, before G1» per il
micro, «Accept, with the micro» per lo standby). ADR-048 scelse il temporizzatore col micro per due
ragioni — il convertitore esponenziale delle fotoresistenze su sei decadi, tolto da ADR-062, e i «molti
stati» —; nessuna ADR l'ha riesaminato dopo ADR-062. L'ordine di sicurezza è già in hardware (il Δ RC
col comparatore, il sorvegliante sul gate del sink, i pull-down, ADR-049). Lo standby (con **NC-037**:
≤ 0,5 W alla presa, la perdita a vuoto di T2 ≤ 0,40 W) e lo spegnimento morbido comprano l'interruttore
frontale a bassa tensione e lo standby, non il silenzio: la perdita di rete dà già 39,2 nV al jack
contro 33,9 nV dello spegnimento morbido (dossier §24).

## Che cosa fare

1. **Il confronto coi numeri** (NC-054, «Cosa serve per chiuderla»): il progetto di oggi contro un
   temporizzatore tutto analogico coi comparatori che ci sono già, **con e senza lo standby**
   (interruttore di rete diretto). Gli stati da coprire; PR-24 per costruzione; PR-20 e PR-23 sui casi
   di L41c; il calore (~1 W); NC-037. Ogni opzione con le sue cifre contro i limiti, alle tre reti dove
   la rete conta.
2. **La scelta all'utente**, per nome e coi numeri; poi una ADR.
3. Se la scelta cambia il circuito, il sorgente (`circuits/preamp/psu.py`, il firmware se resta), i
   disegni, `run_tests.sh` — oppure un lotto dopo, deciso con l'utente all'inizio.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare **#67**, **#73–#76**), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L57b e L57a.
- **NC-054** e **NC-037** in `NONCOMPLIANCE.md`; ADR-046, ADR-048, ADR-049, ADR-062, ADR-094; il report
  dell'architetto `reports/2026-10-12-L52-architetto-avversariale.md` (R3, R4); i casi di L41c.

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli su
  file); `sed` con valori calcolati; un titolo di PR con l'apostrofo (il corpo su file,
  `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi.
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga;
  le forme d'onda grandi non si committano. Un deck che cambia si confronta coi numeri di prima, non
  col suo codice d'uscita (#76).
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte, alle tre reti dove la rete conta.

## NON fa parte di questo lotto

- Il dispositivo d'uscita (L55), la diagnosi (L58), il dossier (L64), la revisione (L65), G1.
- Le righe della FMEA delle dieci parti del limitatore (L57b, §8 del report): vanno in L58 o nella
  revisione, non qui.
- Le decisioni prese non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti. In quel caso
  si torna all'utente coi numeri.

## CHIUSURA

1. `STATE.md` con L54 **fatto** nella tabella dei lotti (o le sue parti), e il prossimo (L55,
   dall'ordine deciso con l'utente).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L54`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
