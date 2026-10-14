# Prompt per la sessione successiva — L45d2b2, i diodi della tenuta, il regolatore negativo, il comando e i 5 V

Nome della sessione: **hi-fi preamp L45d2b2** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078). L45d2b, la costruzione, è stato **diviso dall'utente in tre parti** («Tre parti»,
2026-10-14):
- **L45d2b1 (fatto, 2026-10-14)**: il rivelatore di continua, ADR-072 realizzata da **ADR-079**;
- **L45d2b2 (questo)**: i diodi della tenuta, il regolatore negativo, il comando, i 5 V, i massimi;
- **L45d2b3**: i guasti toccati rifatti nella forma di ADR-070, la sintesi rifatta, NC-042 chiusa.

L45d2b1 ha aperto **NC-063**: la partenza morbida dei regolatori non era mai stata letta. Coi 10 µF
di oggi sul piedino NR il rail + sale in ~1,4 s e il − in **~12 s**, contro i 2 s che il firmware
concede. Questo lotto lavora sugli stessi regolatori, ed è il posto naturale per chiuderla.

## Che cosa costruire

Il punto di partenza è `docs/preamp/data/2026-10-14/L45d2a/decisioni.csv`. Ogni ADR, commit e report
cita la scelta per numero di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che non si riscrive.

1. **D510 / D511 rivisti e U502 protetto** dall'uscita sopra l'ingresso (ADR-074; scelta 3).
   - Oggi U502 arriva fino a 1,76 V sopra l'ingresso, contro un massimo di −0,3 V (SBVS169D).
   - Va verificato che i colpi al jack non crescano, e che la tenuta di P9 (b) regga ancora (i ≥ 25 ms
     di `VRELAY` e i ≥ 1500 µF effettivi). Se non regge: «Da riaprire se» di ADR-074, si torna
     all'utente coi due numeri.
2. **Il limite di corrente sul comando** (oggi ~1 A in un 2N7002 col corto di un clamp) e **il
   limitatore sulla linea a 5 V**, uno zener o un TVS con fusibile ripristinabile (ADR-075; scelta 4).
   - Il limite non deve rallentare lo stacco del jack né Δ.
   - Attenzione: la linea `DC_FLT` del rivelatore (L45d2b1) tira gli stessi gate (`MUTE_G`, `VR_G`,
     `MAINS_G`) con tre BAT54; un limite sul comando non deve toglierle efficacia.
3. **Le tensioni massime delle parti del blocco** col rail fino a ±20,3 V, e la dissipazione dei
   finali (ADR-078). Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai
   limiti, e in quel caso **si torna all'utente**. Il rivelatore ora ha parti sui rail anche lui
   (TLV1704 / TLV1702: 36 V tra V+ e V−, sta fra VDP e massa; i 300k d'ingresso).
4. **NC-063, la partenza morbida.** Prima si scelgono, **con l'utente** (sono anche il filtro del
   rumore dei regolatori, ADR-020), i condensatori NR di U501 e U502:
   - SBVS204G eq. 5: t_SS = 10⁵ · C_NR · ln(4), 1,39 s con 10 µF;
   - SBVS169D eq. 1: t_SS = 1,2 ms per nF, 12 s con 10 µF.

   Poi, in quest'ordine:
   - si mette la partenza morbida nei regolatori comportamentali del banco dell'alimentatore
     (`data/2026-10-14/L45d2b1/psu/genera_tb_psu.py`, REGP / REGM);
   - si rifà la sequenza `accensione` col firmware;
   - si ridimensiona e si verifica l'inibizione del rivelatore (`circuits/preamp/dc_detector.py`,
     R_POR / C_POR) sul banco della scheda audio (`data/2026-10-14/L45d2b1/banco/script/
     genera_rivelatore.py accensione`, coi casi delle rampe vere).

   Il rumore E5 e il PSRR (ADR-020) si rimisurano se cambia C_NR.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR. Uno strumento di
misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md`, `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L45d2b1, L45d2a, L45c1, L45c2.
- `NONCOMPLIANCE.md`: **NC-063**, NC-042, NC-062.
- **ADR-079** e ADR-072; poi ADR-074, ADR-075, ADR-078, ADR-020, ADR-046, ADR-048, ADR-070.
- `reports/2026-10-14-L45d2b1-rivelatore-continua.md`, `data/2026-10-14/L45d2b1/README.md`.
- I banchi dell'alimentatore: `data/2026-10-14/L45d2b1/psu/` (la copia più recente, con la primitiva
  `riv` e le sonde di `DC_FLT`), e i casi di L45c1 per le righe di ADR-074.
- `circuits/preamp/psu.py` (U501, U502, D510 / D511, U503, U504, Q501–Q503 coi clamp) e
  `firmware/preamp_timer/spec/timer_spec.md` (4.1, 4.9).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `corri.sh`);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo in un
    testo;
  - `pkill -f` col percorso relativo: il deck ha il percorso assoluto, si usa la sua coda;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Le corse dei guasti del blocco che non finiscono in ~10 min si fermano e si rifanno fino a 0,6 s
  (`--tfine 0.6`) o col metodo gear (`--gear`), come in L45a / L45b.
- Piste larghe al layout: un rimedio che aggiunge parti di potenza lo ricordi.

## NON fa parte di questo lotto

- **I guasti rifatti nella forma di ADR-070** e la sintesi: sono di **L45d2b3**.
  - Con loro i 28 guasti di ADR-071 ricontati col rivelatore.
  - Il calore di R144 (la cella RC del blocco) contro la sua parte: 1,14 J in 0,16 s, picco 22,5 W
    (L45d2b1), una domanda per la distinta (G2).
- **La diagnosi, L58**: il mute che non si inserisce, il degrado silenzioso dei 28 guasti del blocco,
  lo standby acceso, il rivelatore cieco.
- L'ingresso protetto (L57), il riesame del micro e dello standby (L54), il dispositivo d'uscita
  (L55), il moltiplicatore di Vbe (NC-062), il tetto delle fisse (NC-046), G1. Se un rimedio tocca
  uno di questi, lo si dice e lo si lascia al suo lotto.
- Le decisioni prese in L45d2a non si riaprono, salvo che un «Da riaprire se» della loro ADR scatti.
  In quel caso si torna all'utente con i numeri.

## CHIUSURA

1. `STATE.md` con L45d2b2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b3).
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
