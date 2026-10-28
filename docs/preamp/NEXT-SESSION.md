# Prompt per la sessione successiva — L55, il dispositivo d'uscita del blocco

Nome della sessione: **hi-fi preamp L55** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura del temporizzatore (2026-10-28): fatte le tolleranze e la temperatura,
> il temporizzatore è chiuso (ADR-102…ADR-105). L'ordine deciso con l'utente verso G1:
> **L55** → L58 → L64 → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L55**, e si ferma. Non iniziarne un secondo, salvo che l'utente lo
chieda esplicitamente nella sessione.

## Dove siamo

Il blocco di guadagno (`circuits/preamp/gain_block.py`, otto istanze in `preamp_audio.py`) ha come
dispositivi d'uscita i MJE15032 / MJE15033 (onsemi), col dissipatore di ADR-099 e i diodi
base-emettitore di ADR-095. Lo specchio d'ingresso è quello di L56 (ADR-067), il VAS a ~10,7 mA col
Miller a 470 pF (ADR-054), il VAS e il suo carico in SOT-223 (ADR-068). Il temporizzatore
dell'alimentatore è chiuso: ADR-105 l'ha provato sotto le tolleranze e a 0 / 60 °C.

## Che cosa fare

**NC-056** (minore, la valutazione **prima di G1** per decisione dell'utente in L52), parola per parola
dal registro:

> **Evidenza.** Il MJE15032/33 è un 8 A / 250 V con h_FE e f_T specificati a 0,5 A (datasheet onsemi
> p. 2), qui a ~20 mA; la CJE di 3,06 nF del modello è la causa isolata della caduta di V1 (ADR-042) e
> della crescita verso gli acuti di NC-039. La dissipazione peggiore, 0,36 W, sta in un dispositivo da
> driver (per esempio il 2SA1837 Toshiba, C_ob ~30 pF). ADR-054 ha valutato i ZXT, non un driver di
> taglia intermedia. Oggi i numeri reggono.
>
> **Cosa serve per chiuderla.** Prima di G1: un dispositivo d'uscita di taglia driver con modello del
> costruttore, provato sul banco del blocco (V1, V4, PSRR, slew, calore) contro il MJE, con T7 e T8;
> poi la decisione dell'utente.

In pratica:

1. **Il candidato** (o due): un driver di taglia intermedia, complementare, col **modello SPICE del
   costruttore** portato in `models/` con la provenienza e la sua ricetta in `validate_models.py`
   (`bom-component-manager`); disponibilità verificata, mai un codice plausibile non controllato.
   T7 (ADR-017) e T8 vanno rispettati.
2. **Il banco del blocco** col MJE e col candidato, stessi criteri scritti **prima** delle corse: V1
   (margine di fase, anche col carico capacitivo), V4 (la distorsione ai tetti assoluti di ADR-055,
   anche a caldo, come L56), PSRR (la quota di ADR-020 / ADR-056), lo slew, il calore (P7, coi guasti
   della FMEA che toccano i finali: i due corti dei finali col dissipatore a 99 / 95 °C, ADR-099), la
   compensazione (se il Miller o Cf cambiano, si dice coi numeri).
3. **All'utente** le opzioni coi numeri contro ogni limite (MJE com'è, il candidato con o senza
   ritocco della compensazione), prima di toccare il sorgente. Se cambia il circuito: sorgente,
   netlist, disegno del blocco (`run_tests.sh` 2d), regressione, la FMEA dei finali rifatta sul pezzo
   nuovo, ADR nuova; NC-056 si chiude con la decisione.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (in particolare le voci sui modelli del costruttore e sul calore
  del blocco), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve».
- **NC-056** in `NONCOMPLIANCE.md`; **ADR-017, ADR-042, ADR-054, ADR-055, ADR-067, ADR-068, ADR-095,
  ADR-099**; i report di L46a (`2026-10-01-L46a-compensazione.md`) e di L56
  (`2026-10-12-L56-specchio.md`), e quello di L45d2b3b2b2 (il calore del blocco).

## I vincoli

- Nel worktree vengono rifiutati: i comandi composti, le pipe o i `;` attorno a comandi che eseguono
  script; `cd … && script`; le variabili di shell nei percorsi e nei cicli; `xargs` sulla riga di
  comando; `awk` con programmi, heredoc, `python3 -c`, script lunghi sulla riga di comando (scriverli
  su file); `sed` con valori calcolati o con apostrofi; un titolo di PR con l'apostrofo (il corpo su
  file, `--body-file`); un `git` con `-C` dentro un comando composto. Comandi semplici, **percorsi
  assoluti**, script scritti con Write, Edit per i testi. **`git add` con `":(exclude)…"` non mette
  nulla in silenzio** (visto nel lotto del temporizzatore): i percorsi si danno uno per uno.
- Le corse: la memoria (limitations #75) decide il parallelo; commit e push prima di una lista lunga.
  Le forme d'onda non si committano.
- Un banco o un modello nuovo si prova prima su un caso di cui si sa la risposta.
- Le domande all'utente si fanno per nome, senza sigle (al più fra parentesi); i colpi al jack in dB
  SPL; ogni opzione con la sua cifra contro il limite della parte. **Le cifre di una domanda si
  ricontano dai CSV prima di farla.**

## NON fa parte di questo lotto

- La diagnosi e le righe della FMEA delle parti nuove dell'alimentatore (R585, i BAS416), la conferma
  del BAS416 e dei C0G da 1 µF in 1206 alla distinta: **L58**.
- Il dossier (L64), la revisione (L65), G1.
- Il temporizzatore (ADR-102…ADR-105) non si riapre, salvo che un suo «Da riaprire se» scatti.

## CHIUSURA

1. `STATE.md` con L55 **fatto** nella tabella dei lotti, e il prossimo (L58); le celle di «In breve»
   sostituite, la voce di diario, la più vecchia delle tre in cima al diario di `STATE-STORIA.md` (la
   regola 7 di «Le regole»).
2. Riscrivi `docs/preamp/NEXT-SESSION.md` per il lotto successivo, con la riga «Nome della sessione:
   hi-fi preamp <lotto>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L55`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
