# Prompt per la sessione successiva — L53, le misure veloci prima di G1

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L53**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

In L52 (2026-10-12) l'architetto avversariale ha rivisto il dossier completo, e l'utente ha deciso
rilievo per rilievo (`reports/2026-10-12-L52-esiti-architetto.md`). Prima di **G1** vanno chiuse
NC-042 (la FMEA), NC-054 (micro e standby), NC-055, NC-056, NC-058 e NC-059. L'utente: «I will read
the dossier in parallel, please run remedies, FMEA, and all what is needed before G1 in the
meantime». L'ordine l'ho scelto io: **le misure veloci prima**, perché possono cambiare i lotti
grandi. Poi L45 FMEA → L54 micro e standby → L55 dispositivo d'uscita → G1.

**L'utente sta leggendo il dossier in parallelo.** Se porta dei rilievi durante la sessione, si
registrano come in L43b (per nome, severità sua, in `NONCOMPLIANCE.md` solo se li accetta) e non si
mescolano alle misure di questo lotto.

**Le cifre dell'architetto di L52 sono calcoli, non simulazioni**: la sua sessione non poteva
eseguire comandi. Questo lotto le misura per la prima volta; una stima che non regge si scrive così.

## Il mandato

### 1. NC-055 — la distorsione delle istanze a guadagno unitario

- **La prova che falsifica l'ipotesi** (R5 di L52): il banco
  `docs/preamp/data/2026-10-10/L51c/distorsione/deck/oggi/thd_20k.cir` (il blocco di oggi,
  rigenerato dal sorgente in L51c) a **0 dB**, con l'impedenza di sorgente a **0 / 1,5 / 2,5 /
  5,6 kΩ**, a 0,2 V e a 2 V. Se la THD segue |R_S − 1,5 kΩ| (R_F), il meccanismo d'ingresso a modo
  comune è confermato; se no, si scrive che non lo è. Anche a 1 kHz e 10 kHz, e l'IMD.
- **V4 sulla catena, su ogni uscita** («su ogni uscita» è il testo del requisito): la principale
  (A → trim → C_T → bilanciamento → volume → B → jack) col volume in cima e col bilanciamento girato
  (la sorgente peggiore di ADR-065, 5,6 kΩ), e le due fisse (A → buffer) col K11 a piena scala. Le
  cifre contro i quattro tetti di V4 (ADR-055).
- Se un tetto cade, **non si corregge**: si portano all'utente le strade di letteratura (cascode
  pilotato; R_F adattata nelle istanze unitarie), coi numeri, e sceglie lui (un rimedio è un lotto).

### 2. NC-058 — V1 e V4 a 57 °C

- La temperatura del telaio al peggio è **57,2 °C** a 3 cm (L51b). V1 sulla matrice di oggi e V4 sul
  banco del blocco a 57 °C, con la trappola di `CLAUDE.md`: **`.temp` con una lista ricade a 27 °C**;
  si usa un `.temp` singolo per corsa o `dc TEMP` in un blocco `.control`, e si verifica nel log che
  la temperatura sia quella chiesta.
- Le cifre contro le soglie (V1 ≥ 60°, i tetti di V4).

### 3. NC-059 — l'RCA inserito a caldo

- Sul selettore di ADR-064 (`tb_f1_selettore.cir` come base): il polo caldo che tocca prima della
  massa sull'ingresso selezionato, col volume in cima e al centro; il gradino al jack principale e
  alle fisse **in dB SPL di picco a 1 m** (la catena di NC-028: finale ×21,1, Heresy 96 dB/1 W/1 m,
  stanza a 25–35 dB(A)), e per le fisse la metrica delle cuffie, se esiste (NC-046).
- Il modello del contatto (la carica del cavo, la massa che arriva dopo) si dichiara come ipotesi.
- Poi all'utente: serve un rimedio, un avviso, o niente.

### 4. Alla fine

- Un report `docs/preamp/reports/<data>-L53-misure-veloci.md`, dati in `docs/preamp/data/<data>/L53/`
  con README.
- Le voci chiuse o aggiornate in `NONCOMPLIANCE.md`, **solo con la decisione dell'utente**.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (54 voci), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di **L52**.
- `docs/preamp/reports/2026-10-12-L52-esiti-architetto.md` e il report verbatim di L52 (R5 e la
  sezione sul blocco di guadagno).
- `NONCOMPLIANCE.md`: NC-055, NC-058, NC-059.
- ADR-014, ADR-055, ADR-064, ADR-065.

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
- **I subagenti in una sessione isolata possono non poter eseguire comandi** (L52: Bash rifiutato
  all'architetto). Se un lotto ha bisogno di un subagente che simula, verificarlo subito con un
  comando banale, e se non può, fare le corse dalla sessione principale.

## NON fa parte di questo lotto

- I rimedi: si misurano, si portano all'utente, si fanno in un lotto successivo.
- La FMEA (L45), il micro e lo standby (L54), il dispositivo d'uscita (L55), E3 (NC-057), G1.
- Qualsiasi modifica al circuito, al firmware o al dossier.

## CHIUSURA

1. `STATE.md` con L53 **fatto** nella tabella dei lotti, e il prossimo (L45).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L53`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
