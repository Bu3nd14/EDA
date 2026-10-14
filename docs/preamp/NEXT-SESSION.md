# Prompt per la sessione successiva — L45d2b, la costruzione dei rimedi dei guasti

Nome della sessione: **hi-fi preamp L45d2b** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. Le analisi L45a–L45c2 sono
fatte, L45d1 le ha riportate alla forma di ADR-070 e le ha messe in una sintesi. **L45d2a (fatto,
2026-10-14)** ha preso tutte le decisioni sui rimedi, con l'utente: otto ADR, **ADR-071…078**, senza
toccare il circuito. L45d2 era stato diviso dall'utente all'inizio («Prima decidere, poi
costruire»). **L45d2b** costruisce i rimedi scelti, rifà i guasti toccati, e chiude NC-042.

## Che cosa costruire

Il punto di partenza è `docs/preamp/data/2026-10-14/L45d2a/decisioni.csv`: ogni riga alta e media
della sintesi ha lì la sua decisione, l'ADR e la destinazione. **Le 88 righe con `dove = L45d2b`**
sono il lavoro di questo lotto, più le 9 righe basse delle sovratensioni. Ogni ADR, commit e report
cita la scelta per numero di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che non si riscrive.

1. **Il rivelatore di continua sulle uscite dei blocchi, in hardware** (ADR-072; le scelte 1, 6, 8,
   9 e 10). Quando un'uscita ha continua:
   - apre il mute;
   - toglie la linea dei relè (`VRELAY`) alla scheda audio, così nessuna bobina resta a 12 V;
   - spegne i rail audio.

   I vincoli scritti in ADR-072:
   - **la musica non deve farlo scattare** (col volume al massimo supera 0,87 V);
   - la soglia e la costante di tempo si scelgono contro i 100 ms di P10;
   - **i rail non si spengono di colpo**: la scarica della tenuta (≥ 1500 µF effettivi per rail) va
     misurata, e il calore del secondo guasto si giudica su quel tempo contro PR-22 / P7;
   - dopo lo scatto l'apparecchio resta spento fino a un comando dal frontale. Un candidato è la
     strada che esiste già: dopo un guasto con la rete presente, il temporizzatore stacca il
     toroidale.

   Col rivelatore vanno verificati sul banco il filo del rail + aperto fra le schede e il
   condensatore d'uscita in corto seguito da un guasto del blocco.
2. **D510 / D511 rivisti e U502 protetto** dall'uscita sopra l'ingresso (ADR-074; scelta 3). Oggi
   U502 arriva fino a 1,76 V sopra l'ingresso, contro un massimo di −0,3 V. Va verificato che i
   colpi al jack non crescano e che la tenuta di P9 (b) regga ancora.
3. **Il limite di corrente sul comando** (oggi ~1 A in un 2N7002 col corto di un clamp) e **il
   limitatore sulla linea a 5 V**, uno zener o un TVS con fusibile ripristinabile (ADR-075; scelta
   4). Il limite non deve rallentare lo stacco del jack né Δ.
4. **Le tensioni massime delle parti del blocco**, e la dissipazione dei finali col rail fino a
   ±20,3 V (ADR-078). Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai
   limiti, e in quel caso **si torna all'utente**.
5. **I guasti toccati rifatti**, con le colonne dopo il rimedio (gravità, probabilità, priorità;
   ADR-070). Vanno ricontati anche i 28 guasti del blocco di ADR-071: il rivelatore potrebbe
   vederne qualcuno. **P10 misurato** su ogni guasto del blocco. Poi la sintesi rifatta (README di
   `data/2026-10-14/L45d1/`, «Rifare») e NC-042 chiusa, se i numeri lo permettono.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR.

**È un lotto grande: all'inizio chiedi all'utente se dividerlo**, per nome e senza sigle. Per
esempio: prima il rivelatore da solo, poi i diodi del grezzo, il comando e i 5 V, poi i guasti
rifatti.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2a, L45d1, L45c2, L45c1, L45b, L45a.
- `NONCOMPLIANCE.md`: NC-042, NC-046, NC-062.
- **ADR-071…078**; poi ADR-045, ADR-046, ADR-051, ADR-069, ADR-070.
- `reports/2026-10-14-L45d2a-scelte-rimedi.md` e `data/2026-10-14/L45d2a/decisioni.md`.
- I banchi dei guasti: `data/2026-10-13/L45a/script/genera_canale.py` (il blocco, P10), e i banchi
  di L45b, L45c1 e L45c2 per le righe che li toccano.
- `circuits/preamp/psu.py` (U505, Q505, D510 / D511, U502, U504) e la scheda audio.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `psu/corri_lista.sh`);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Uno strumento di misura nuovo si controlla su un caso noto prima di usarlo.
- Piste larghe al layout: non è di questo lotto, ma un rimedio che aggiunge parti di potenza lo
  ricordi.

## NON fa parte di questo lotto

- **La diagnosi, L58**. Le vanno:
  - il mute che non si inserisce (ADR-076);
  - il degrado silenzioso dei 28 guasti del blocco (ADR-071);
  - lo standby acceso per guasto (ADR-078);
  - il rivelatore cieco (ADR-072).
- L'ingresso protetto (L57), il riesame del micro e dello standby (L54), il dispositivo d'uscita
  (L55), il moltiplicatore di Vbe (NC-062), il tetto delle fisse (NC-046), G1. Se un rimedio tocca
  uno di questi, lo si dice e lo si lascia al suo lotto.
- Le decisioni prese in L45d2a non si riaprono, salvo che un «Da riaprire se» della loro ADR
  scatti. In quel caso si torna all'utente con i numeri.

## CHIUSURA

1. `STATE.md` con L45d2b (o le sue parti) **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh <lotto>`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
