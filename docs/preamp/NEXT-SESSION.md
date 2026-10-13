# Prompt per la sessione successiva — L45, la FMEA della scheda audio

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1** per decisione dell'utente in L52): nessuna analisi dei guasti
singoli della scheda audio, e il tetto di non-danno (PR-23, 112,2 dB SPL a 1 m) vale finora solo per
l'alimentatore. L'architetto di L52 (R1) l'ha messa prima del congelamento perché il rimedio
naturale — un rivelatore di continua sulle uscite dei blocchi che comandi il sink di `MUTE_CMD`, che
esiste già — **cambia la topologia**. Le sue stime sono a calcolo: un blocco al rail durante
l'ascolto porta ~13,8 V al jack, che il finale limita a ~114 dB SPL, sopra il tetto.

L56 (2026-10-12/13) ha chiuso NC-060: **nessuna voce è più bloccante per G1**, ma NC-042, NC-054,
NC-055, NC-059 (maggiori) e NC-056 (minore) vanno chiuse prima, per decisione dell'utente. Il blocco
di guadagno è quello di **ADR-067** (inseguitore davanti al VAS, transistor di aiuto sullo specchio,
collettori al rail negativo) e **ADR-068** (VAS e suo carico in SOT-223): la FMEA si fa su questo.
L45 viene prima di L57 (l'ingresso protetto per l'RCA a caldo, NC-059) e L54 (il micro e lo
standby, NC-054) perché il rivelatore e il mute che può portare servono anche lì (ordine proposto
in L53, l'utente non l'ha fissato: se vuole un altro ordine, vale il suo).

**L'utente sta leggendo il dossier in parallelo.** Se porta dei rilievi, si registrano come in
L43b e non si mescolano alle misure di questo lotto.

## Il mandato

1. **L'elenco dei guasti singoli** della scheda audio, uno per uno, dal sorgente
   (`circuits/preamp/preamp_audio.py`, `gain_block.py`): almeno i dispositivi d'uscita in corto o
   aperti (MJE15032 / 15033), il VAS e il suo carico (ora DZT5401 / DZT5551), l'inseguitore e
   l'aiuto nuovi di ADR-067, la coda, i JFET; le bobine e i contatti dei relè (guadagno, mute,
   permissivo K6, trim, selettore; saldati, aperti, rimbalzo); i condensatori d'uscita (4,7 µF) e
   C_T (10 µF) in corto o aperti; la cella RC di ADR-056; il firmware (le LDR non ci sono più,
   ADR-062: dirlo). Per ognuno: l'effetto **al jack principale e alle fisse**, in dB SPL a 1 m
   contro il tetto di non-danno (112,2 dB SPL, PR-23) e contro un tetto per le fisse ancora da
   fissare (la Stax SRM-T1 da 60 dB, NC-046).
2. **I casi che superano il tetto, simulati** (non a calcolo): il banco della scheda audio di oggi
   (gli 8 blocchi), coi guasti introdotti nel deck. Dove serve, il calore (limitations #55: SPICE
   non scalda i dispositivi; `data/2026-10-12/L56/script/caldo.py` per il blocco).
3. **All'utente**, per nome e senza sigle, coi numeri in tabella: se un rivelatore di continua sulle
   uscite dei blocchi debba comandare il sink di `MUTE_CMD`, e se serve un tetto di non-danno sulle
   fisse; sceglie lui, con **ADR**. Se la scelta cambia il circuito, il sorgente, la netlist, il
   disegno del blocco (`docs/preamp/schematic/`, `run_tests.sh` 2d), `run_tests.sh`, la regressione
   dei deck veloci (`data/2026-10-12/L56/script/regressione.sh`, prima/dopo) e i guasti
   dell'alimentatore (`data/2026-10-12/L56-alimentatore/`, il carico in `carico.txt`).
4. Report `docs/preamp/reports/<data>-L45-fmea.md`, dati in `docs/preamp/data/<data>/L45/`.

Il lotto è grande: se all'inizio sembra più di una sessione, proporre all'utente di dividerlo (come
L51 in L51a/b/c) e lasciar decidere lui.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**57** voci; la #57 è di L56: un `op` non convergente stampa
  numeri), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di **L56**.
- `NONCOMPLIANCE.md`: NC-042, NC-046, NC-059; `reports/2026-10-12-L52-architetto-avversariale.md` (R1).
- ADR-021 (P7), ADR-022, ADR-027 (il «Da riaprire se» sulla bobina di K6), ADR-033, ADR-044,
  ADR-045, ADR-051, ADR-062, ADR-067, ADR-068.
- `reports/2026-10-12-L56-specchio.md` (il blocco di oggi, i guasti dell'alimentatore col suo carico).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- I subagenti in una sessione isolata possono non poter eseguire comandi (L52): se servono
  simulazioni, falle dalla sessione principale.
- Un `op` va letto rifiutando «source stepping failed» e controllando un nodo noto (limitations #57).
- Le cifre di distorsione si danno sempre con la temperatura delle giunzioni dichiarata.

## NON fa parte di questo lotto

- L'ingresso protetto (L57), il micro e lo standby (L54), il dispositivo d'uscita (L55), i due casi
  della catena di NC-055, G1. Se un rimedio della FMEA tocca uno di questi, si dice e si lascia al
  suo lotto.

## CHIUSURA

1. `STATE.md` con L45 **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
