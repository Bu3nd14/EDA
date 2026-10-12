# Prompt per la sessione successiva — L56, lo specchio d'ingresso del blocco di guadagno

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L56**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

In L53 (2026-10-12) misurando la distorsione a caldo è venuto fuori **NC-060, bloccante per G1**:
lo specchio dello stadio d'ingresso del blocco (Q121B, LS350) ha 0,79 V fra i morsetti e il modello
del costruttore ha RC 231 Ω, che ne perde ~0,5 V a 2,16 mA. Lo specchio sta sull'orlo della
saturazione: il gradino della corrente di coda è il 2–4 % sopra il punto di lavoro già a 27 °C
uniformi. Col calore vero dei dispositivi (VAS e suo carico a ~0,14 W in SOT-23, +50–57 °C; la coda
a 64 mW, +27 °C) la THD a 20 kHz esce da V4 in 48 casi su 48 e l'intermodulazione arriva a
25–35 dB SPL a 57 °C. Con l'RC dell'LS350 a zero, 24 casi su 24 rientrano. Leggi
`reports/2026-10-12-L53-misure-veloci.md` e `NONCOMPLIANCE.md` NC-060.

Ogni cifra di distorsione del progetto dipende da questo: per questo L56 viene prima di L45, L57,
L54, L55 (ordine proposto in L53, l'utente non l'ha fissato: se vuole un altro ordine, vale il suo).

**L'utente sta leggendo il dossier in parallelo.** Se porta dei rilievi, si registrano come in
L43b e non si mescolano alle misure di questo lotto.

## Il mandato

1. **Le strade, misurate prima di chiedere.** Sul banco del blocco con ogni giunzione alla sua
   temperatura (`data/2026-10-12/L53/temp/autoriscaldamento.py`, da adattare al circuito
   modificato: le Tj vanno ricalcolate dal punto di lavoro di ogni variante) a 27 e 57 °C d'aria, e
   sul banco a 27 °C uniformi come controllo. Strade da considerare (non un elenco chiuso):
   - più tensione per lo specchio: abbassare la base del VAS rispetto al collettore di Q121B
     (resistenza d'emettitore del VAS più grande, un diodo o una resistenza in serie alla base del
     VAS, la cella RC di ADR-056 che oggi alimenta specchio e VAS);
   - meno caduta nello specchio: R119/R120 (oggi 220 / 226 Ω, R120 tarata per l'offset in ADR-056);
   - uno specchio che non chieda tensione (Wilson, cascode, specchio con base comune);
   - il VAS che scalda meno (la sua dissipazione; il rame nel layout è di G2, ma la R_thJA conta);
   - il generatore di coda accoppiato termicamente ai suoi diodi.
   Per ognuna: THD a 20 kHz e intermodulazione contro V4 (0,2 e 2 V, tre modi, sorgente 2,5 e
   5,6 kΩ), il margine sul gradino della coda (R107 ±10 %), V1, PSRR+, rumore (E5), la continua
   all'uscita, la dissipazione, il clip. Cosa cambia nel sorgente e nei controlli.
2. **All'utente**, per nome e senza sigle, coi numeri in tabella; sceglie lui. **ADR** per la scelta.
3. **Il sorgente** (`circuits/preamp/gain_block.py`, coi commenti che puntano all'ADR), la netlist
   rigenerata, `run_tests.sh`; poi la regressione dei deck veloci (come in L46a/L46b), i guasti
   dell'alimentatore se l'offset o la corrente cambiano (L46b ha insegnato che una modifica del
   blocco li tocca), e **NC-055 rifatta** sulla catena (`data/2026-10-12/L53/catena/`).
4. Report `docs/preamp/reports/<data>-L56-specchio.md`, dati in `docs/preamp/data/<data>/L56/`.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**56** voci; la #55 è di L53: SPICE non scalda i
  dispositivi; la #56 l'avviso dell'LS350), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di **L53**.
- `reports/2026-10-12-L53-misure-veloci.md`, `data/2026-10-12/L53/README.md`.
- ADR-054, ADR-055, ADR-056 (il blocco oggi), ADR-014, ADR-017, ADR-018 (l'LS350).
- `circuits/preamp/gain_block.py`, sezioni dello stadio d'ingresso e del VAS.

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
- Le cifre di distorsione si danno sempre con la temperatura delle giunzioni dichiarata.

## NON fa parte di questo lotto

- La FMEA (L45), l'ingresso protetto (L57), il micro e lo standby (L54), il dispositivo d'uscita
  (L55), G1. Se una strada per lo specchio tocca il dispositivo d'uscita, si dice e si lascia a L55.

## CHIUSURA

1. `STATE.md` con L56 **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L56`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
