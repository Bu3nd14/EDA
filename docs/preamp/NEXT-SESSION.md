# Prompt per la sessione successiva — L45d2b2, i diodi della tenuta, il regolatore negativo, il comando e i 5 V

Nome della sessione: **hi-fi preamp L45d2b2** (la convenzione è in `CLAUDE.md`).

> Prompt scritto in L60c2 (2026-10-15) dal prompt originale di L45d2b1 (commit 22315ab1), aggiornato
> con ADR-081…086, messo da parte alla chiusura di L60d2 (2026-10-19) con le correzioni di L60d
> (ADR-087…089), e rimesso qui alla chiusura di L62 (2026-10-19) con le sue: il moltiplicatore di
> Vbe ha i quattro diodi di riserva (ADR-090), la scheda audio 554 parti, NC-062 chiusa.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45d2b2**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione. Se L45d2b2 si rivela più grande di una sessione, **dividilo
con l'utente all'inizio**.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45d2a ha deciso i rimedi
(ADR-071…078). L45d2b, la costruzione, è stato **diviso dall'utente in tre parti** («Tre parti»,
2026-10-14):
- **L45d2b1 (fatto, 2026-10-14)**: il rivelatore di continua, ADR-079. **Poi tolto**: ADR-081 (L61)
  protegge la Stax col condensatore d'uscita da 1 µF, e L60b ha tolto il rivelatore dal sorgente;
- **L45d2b2 (questo)**: i diodi della tenuta, il regolatore negativo, il comando, i 5 V, i massimi;
- **L45d2b3**: i guasti toccati rifatti nella forma di ADR-070, la sintesi rifatta, NC-042 chiusa.

**Che cosa è cambiato dal prompt originale di questo lotto** (scritto in L45d2b1, commit 22315ab1):
- **il rivelatore non c'è più** (ADR-081, L60b): niente `DC_FLT`, niente BAT54 sui gate, niente
  TLV1704 / TLV1702, niente `dc_detector.py`, niente R_POR / C_POR. J4 è di nuovo a tre pin;
- **J1 ha sette pin** (ADR-083): 1–2 `VPLUS`, 3–4 `GND`, 5–6 `VMINUS`, 7 `VRELAY`;
- **i moltiplicatori di Vbe** (Q127) sono DZT5551 in SOT-223 (ADR-082);
- **la Stax**: il condensatore d'uscita della fissa 2 è 1 µF prima del relè di mute (ADR-081,
  ADR-084), e il relè di mute della Stax **K3 è un TE Axicom IM06TS** a isolamento supplementare
  (ADR-085, L60c2): bobina 11,7 mA a 12 V invece di 9,1, polarizzata. Sul banco della rete di L51b la
  tenuta di `VRELAY_REG` ≥ 11,4 V scende da 48,3 a **46,4 ms** a rete −10 % (`RMUTECOIL` 401,2 Ω
  invece di 438,3; `data/2026-10-15/L60c2/rete/`);
- **P10 sulla Stax è 150 ms** (ADR-086), e **L60d** ha messo la ridondanza nel blocco: R150 da 4,7 kΩ
  in parallelo a R109, R112 / R151 due da 200 Ω, R144 / R152 due da 20 Ω, nelle otto istanze;
- **R153**, 4,7 kΩ sul collettore dell'inseguitore davanti al VAS (ADR-087, L60d1); da L62 la scheda
  audio è a **554 parti** (sotto). Col blocco che non satura più il VAS, P7 col corto sulla principale porta la
  47 Ω della principale a 1,28 W e le due 22 Ω d'emettitore a 0,333 W: i vincoli per la distinta sono
  **≥ 1,3 W** e **≥ 0,34 W** a 60 °C;
- **V2 si misura con la media su ogni campione**, corretta per l'attenuazione dei 20 kHz (ADR-087,
  ADR-088; `scripts/v2_metodo.py`, il metodo di prima nella colonna `picco_puntuale_V`). La matrice
  di L60d2: 0 su 250 fuori; la Stax a 20 kHz a mute inserito 82,4 µV, a 1,7 dB dal tetto;
- **i guasti sulla Stax** (L60d2): R109 aperta 0 ms, nessuno oltre 150 ms; 17 modi più lunghi di
  prima per R153, accettati sotto il tetto (ADR-089). NC-069 e NC-070 chiuse;
- **P7** (`tb_mute_corto.cir`) calcolava R123 / R126 con 91 Ω: corretto a 56 Ω in L60d2 (8,8 / 6,4 mW);
- **il moltiplicatore di Vbe ha quattro diodi di riserva** (ADR-090, L62, 2026-10-19): quattro 1N4148
  in serie fra NX e NY, in fondo a `gain_block()` (D154–D157 sul blocco del file; sulla scheda audio
  D152–D155, D253–D256, D551–D554, D651–D654 e lo stesso sull'altro canale). La scheda audio è a
  **554 parti**. Coi quattro guasti del moltiplicatore i finali stanno a 97–98 °C con 60 °C d'aria
  (erano 213–216); a blocco sano il riposo scende di 0,05 mA, V1, P7 e V4 a caldo uguali.
  **NC-062 è chiusa**: il punto 3 qui sotto legge i massimi sul blocco coi diodi, che è il blocco
  finale. I diodi conducono 94–177 µA a blocco sano (27–90 °C), non «qualche µA» come diceva ADR-090:
  se l'utente legge alla lettera il suo «Da riaprire se», quella domanda viene prima di questo lotto
  (`reports/2026-10-19-L62b-diodi-nel-sorgente.md`, «La corrente dei diodi»).

L45d2b1 ha aperto **NC-063**: la partenza morbida dei regolatori non era mai stata letta. Coi 10 µF
di oggi sul piedino NR il rail + sale in ~1,4 s e il − in **~12 s**, contro i 2 s che il firmware
concede. Questo lotto lavora sugli stessi regolatori, ed è il posto naturale per chiuderla.

## Che cosa costruire

Il punto di partenza è `docs/preamp/data/2026-10-14/L45d2a/decisioni.csv`. Ogni ADR, commit e report
cita la scelta per numero di `data/2026-10-14/L45d1/scelte_L45d2.pdf`, che non si riscrive. Le scelte
6, 8, 9 e 10 hanno già il loro rimedio da ADR-082…085 (non si riaprono qui).

1. **D510 / D511 rivisti e U502 protetto** dall'uscita sopra l'ingresso (ADR-074; scelta 3).
   - Oggi U502 arriva fino a 1,76 V sopra l'ingresso, contro un massimo di −0,3 V (SBVS169D).
   - Va verificato che i colpi al jack non crescano, e che la tenuta di P9 (b) regga ancora (i ≥ 25 ms
     di `VRELAY` e i ≥ 1500 µF effettivi). Se non regge: «Da riaprire se» di ADR-074, si torna
     all'utente coi due numeri.
2. **Il limite di corrente sul comando** (oggi ~1 A in un 2N7002 col corto di un clamp) e **il
   limitatore sulla linea a 5 V**, uno zener o un TVS con fusibile ripristinabile (ADR-075; scelta 4).
   - Il limite non deve rallentare lo stacco del jack né Δ.
3. **Le tensioni massime delle parti del blocco** col rail fino a ±20,3 V, e la dissipazione dei
   finali (ADR-078), sul blocco coi quattro diodi di ADR-090 (ai loro capi c'è lo spread, ~2 V a
   riposo e ~3 V coi guasti del moltiplicatore, quando portano la corrente del VAS, ~10 mA). Il sorvegliante della sovratensione si aggiunge **solo se** qualcosa esce dai
   limiti, e in quel caso **si torna all'utente**.
4. **NC-063, la partenza morbida.** Prima si scelgono, **con l'utente** (sono anche il filtro del
   rumore dei regolatori, ADR-020), i condensatori NR di U501 e U502:
   - SBVS204G eq. 5: t_SS = 10⁵ · C_NR · ln(4), 1,39 s con 10 µF;
   - SBVS169D eq. 1: t_SS = 1,2 ms per nF, 12 s con 10 µF.

   Poi, in quest'ordine:
   - si mette la partenza morbida nei regolatori comportamentali del banco dell'alimentatore (REGP /
     REGM). **Il banco più recente** è `data/2026-10-14/L45d2b1/psu/genera_tb_psu.py`, ma ha ancora la
     primitiva `riv` e le sonde di `DC_FLT` del rivelatore tolto: si parte da lì togliendole (e lo si
     dichiara), o dal banco di L51b (`data/2026-10-09/L51b/psu/`) col carico di oggi (con K3 IM06TS);
   - si rifà la sequenza `accensione` col firmware.

   Il rumore E5 e il PSRR (ADR-020) si rimisurano se cambia C_NR.

Ogni cambio al circuito porta con sé sorgente, netlist, disegno, `run_tests.sh` e regressione. Ogni
valore nuovo in `circuits/preamp/*.py` ha un commento che punta alla sua ADR. Uno strumento di
misura nuovo si controlla su un caso noto prima di usarlo.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md`, `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di L62, L60d, L60c2, L60c1, L60b, L60a, L61 e L45d2b1.
- `NONCOMPLIANCE.md`: **NC-063**, NC-042; NC-062 (chiusa in L62).
- ADR-074, ADR-075, ADR-078, ADR-020, ADR-046, ADR-048, ADR-070; poi ADR-081…090 per ciò che è
  cambiato (il rivelatore tolto, J1, la Stax, la ridondanza e R153, il metodo di V2, i diodi del
  moltiplicatore).
- `reports/2026-10-14-L45d2b1-rivelatore-continua.md` (la partenza morbida, NC-063) e
  `reports/2026-10-15-L60c2-stax-condensatore-e-rele.md` (la tenuta di `VRELAY` con K3 nuovo);
  `reports/2026-10-19-L60d2-guasti-stax-e-v2-media.md`, `reports/2026-10-19-L62b-diodi-nel-sorgente.md`.
- `docs/limitations.md` **#59** (un punto di lavoro si giudica anche dalla corrente dei rail), **#62**
  (i deck di guasto di L45a includono copie del blocco scritte una volta: un banco nuovo le rifà dal
  blocco di oggi, come `data/2026-10-19/L60d2/script/genera_L60d2.py`) e **#63**.
- I banchi dell'alimentatore (sopra) e i casi di L45c1 per le righe di ADR-074.
- `circuits/preamp/psu.py` (U501, U502, D510 / D511, U503, U504, Q501–Q503 coi clamp) e
  `firmware/preamp_timer/spec/timer_spec.md` (4.1).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `corri.sh`);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, gli script lunghi passati sulla riga di comando (scriverli
    su file e lanciarli);
  - un comando che nomina la storia del repository in forma che il guardiano non sa verificare: le
    versioni vecchie dei file si estraggono un file per comando, o prima di entrare nel worktree;
  - `pkill -f` col percorso relativo: il deck ha il percorso assoluto, si usa la sua coda;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- **Se lanci un agente che deve eseguire comandi**, il worktree si apre **dopo** che ha finito.
- Le domande all'utente si fanno per nome, senza sigle; le soglie in dB SPL.
- Le corse dei guasti del blocco che non finiscono in ~10 min si fermano e si rifanno fino a 0,6 s
  (`--tfine 0.6`) o col metodo gear (`--gear`), come in L45a / L45b.
- Nei deck in AC l'interruttore con isteresi di ngspice resta aperto nel punto di lavoro: un contatto
  chiuso si scrive come resistenza (L60c1).
- Piste larghe al layout: un rimedio che aggiunge parti di potenza lo ricordi.

## NON fa parte di questo lotto

- **I guasti rifatti nella forma di ADR-070** e la sintesi: sono di **L45d2b3**.
  - Con loro i 28 guasti di ADR-071, ricontati **senza** il rivelatore (ADR-081).
  - Il calore di R144 (la cella RC del blocco) contro la sua parte: 1,14 J in 0,16 s, picco 22,5 W
    (L45d2b1), una domanda per la distinta (G2) — da L60d R144 è sdoppiata (11,3 W e 0,69 J ciascuna
    col 1000 µF in corto).
  - **R153 in corto** rimette l'inseguitore senza limite: Q146 0,41 W medi e 2,0 W di picco in P7
    (blocco B, +10 dB, mute o principale in corto) contro i 0,31 W del SOT-23
    (`data/2026-10-19/L60d2/p7_r153cc.txt`).
  - Le durate di P10 sulla Stax di L60d2 (`data/2026-10-19/L60d2/p10_stax.csv`) come punto di partenza.
- **La diagnosi, L58**: il mute che non si inserisce, il degrado silenzioso dei 28 guasti del blocco,
  lo standby acceso.
- L'ingresso protetto (L57), il riesame del micro e dello standby (L54), il dispositivo d'uscita
  (L55), il tetto delle fisse (NC-046), G1. Il moltiplicatore di Vbe è fatto (L62, ADR-090). Se un rimedio tocca
  uno di questi, lo si dice e lo si lascia al suo lotto.
- La Stax (ADR-081…089, L60c2, L60d): fatta.
- Le decisioni prese in L45d2a, in L60a…L60d e in L62 non si riaprono, salvo che un «Da riaprire se» della
  loro ADR scatti. In quel caso si torna all'utente con i numeri.

## CHIUSURA

1. `STATE.md` con L45d2b2 **fatto** nella tabella dei lotti, e il prossimo (L45d2b3).
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45d2b2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
