# L46b — Il PSRR del rail positivo: nel blocco o nell'alimentatore

Data: 2026-10-01 · Lotto: L46b · Decisione: **ADR-056** · Chiude **NC-047** e **NC-052**;
aggiorna NC-011 e NC-041 · Dati: `data/2026-10-01/L46b/` (README dentro)

**Cifre di modello**, sui modelli del costruttore e senza dispersione fra esemplari: conta il
trend fra varianti sullo stesso banco. I numeri dell'alimentatore sono un **limite per eccesso**
dai datasheet, non una simulazione.

## 0. In breve

- **Il meccanismo**: specchio d'ingresso e VAS stanno sul rail +; la base del VAS segue il rail e
  C124 lo porta in uscita. Per questo il PSRR+ seguiva il Miller (L46a).
- **La scelta dell'utente**, fra quattro strade misurate: **una cella RC per blocco, 10 Ω + 1000 µF,
  che alimenta specchio e VAS**. PSRR+ a 10 kHz 29,5 → 71,7 dB (ESR 0,05 Ω).
- **La quota di ADR-020** su uno spettro dei rail limitato per eccesso: 0,51 µV col blocco di
  ADR-054, **0,098 µV** con quello di ADR-056 (−27 dB SPL a 1 m, 20 dB dentro la quota).
- **Una scoperta lungo la strada**: la ricorsa dei guasti all'alimentatore (la catena di L41c) ha
  mostrato che **ADR-054** aveva eroso due casi, e L46a non l'aveva ricorsa. Causa: l'offset
  d'uscita del blocco (−26 mV), che arriva al jack quando il guadagno cade prima del jack.
  L'utente ha chiesto di fermarsi e cercare il rimedio: **R120 da 220 a 226 Ω**, offset −6,6 mV,
  e i due casi tornano meglio di L41c.

## 1. All'inizio, con l'utente

La domanda del mandato, «dove sta il rimedio», è stata fatta dopo aver misurato le strade. Due
risposte dell'utente prima della scelta:
- **«Quale tra queste soluzioni ci permette di alimentare in futuro uno stadio phono MC?»** —
  Nessuna, ed è stato detto così: PR-19 del PRB esclude il phono integrato; l'alimentatore di
  ADR-048 è dimensionato sul solo stadio di linea (2×15 V 50 VA «per i rail ±15 V e nient'altro»,
  valle +2,5 V a rete −10 %, regolatori a 4,1 W a rete +10 %); le quattro strade agiscono solo
  dentro i blocchi. Se mai un phono condividesse i rail, la cella è la strada che lo rende meno
  rischioso (37,5 dB di tolleranza sul rail + invece di 6).
- **«Metti in tabella con le stesse colonne per farmi decidere, indica il margine per ogni
  soluzione»** — la tabella del §3, con due margini distinti: quanto si sta sotto la quota oggi,
  e di quanto può peggiorare il rail + prima di sforarla.

## 2. Il banco e i controlli

Il banco di L46a, copiato in `script/` (la base si ricava dalla posizione dello script). Le
varianti partono da `base/gain_block_flat_adr054.inc`, il blocco di `main` prima di L46b: il
sorgente ora contiene la cella e non deve essere la base. Famiglia nuova `clip`
(`tb_dc_headroom`, `tb_v3_overload`).

- **Il controllo `ctrl`** (nessuna modifica) ridà L46a al centesimo: PSRR+ 66,92 / 49,47 /
  29,52 / 23,54 dB, PSRR− a 100 Hz 70,71 dB, V1 64,94°, THD a 20 kHz 0,00059 %, IMD −119,2 dB.
- **La seconda strada**: la variante a condensatore ideale (`sv_r10_c1000u_esr0`) e la regressione
  rigenerata dal sorgente danno lo stesso PSRR entro **0,0004 dB** sugli 81 punti dei tre modi.
- **La catena di L41c dal sorgente** ridà la variante del banco (`l41c/var/corse_r120_226`) cifra
  per cifra su tutti i nove casi.
- Nessun log con «Transient op started» (#33, #38); 96 + 51 corse del banco con rc 0.

## 3. Le strade

### Il condensatore e l'ESR

In alta frequenza l'attenuazione della cella tende a R / ESR (1000 µF valgono 16 mΩ a 10 kHz).
Le cifre di scelta usano **0,05 Ω**, un'ipotesi dichiarata e prudente (~2–3× l'impedenza a
100 kHz di un low-ESR da 1000–2200 µF 25 V a 20 °C). Un elettrolitico generico (0,2 Ω) dà ancora
62,7 dB a 10 kHz. Il sorgente porta un condensatore ideale, come gli altri elettrolitici del
blocco: le sue cifre sopra 1 kHz sono più alte (78,5 dB a 10 kHz).

### Prima passata, PSRR (minimo sui tre modi, dB; `psrr.csv`)

| Variante | + 100 Hz | + 1 kHz | + 10 kHz | + 20 kHz | − 50 Hz | − 100 Hz |
|---|---|---|---|---|---|---|
| oggi (ADR-054) | 66,92 | 49,47 | 29,52 | 23,54 | 65,59 | 70,71 |
| specchio + VAS, 4,7 Ω + 1000 µF | 74,88 | 75,58 | 66,89 | 61,33 | 65,59 | 70,71 |
| specchio + VAS, 4,7 Ω + 2200 µF | 79,22 | 79,25 | 67,21 | 61,39 | 65,59 | 70,71 |
| **specchio + VAS, 10 Ω + 1000 µF** | 79,07 | 79,62 | **71,77** | 66,29 | 65,59 | 70,71 |
| specchio + VAS, 10 Ω + 2200 µF | 82,34 | 82,27 | 72,05 | 66,33 | 65,59 | 70,71 |
| specchio + VAS, 22 Ω + 1000 µF | 82,38 | 82,58 | 75,74 | 70,36 | 65,58 | 70,71 |
| specchio + VAS, 10 Ω + 1000 µF, ESR 0,2 Ω | 79,03 | 78,00 | 62,67 | 56,75 | 65,59 | 70,71 |
| **solo lo specchio**, 47 Ω + 470 µF | −12,32 | −12,34 | −12,31 | −12,20 | 41,23 | 46,42 |
| **solo il VAS**, 10 Ω + 1000 µF | 47,73 | 47,63 | 47,54 | 47,31 | 65,35 | 70,49 |
| anche il cascode, 10 Ω + 1000 µF | 79,09 | 79,61 | 71,77 | 66,29 | 65,59 | 70,71 |
| moltiplicatore di capacità | 85,37 | 85,53 | 81,12 | 76,09 | 65,58 | 70,70 |

- **Specchio e VAS vanno sullo stesso nodo.** Filtrarne uno solo è peggio di niente: la differenza
  fra i due rail cade fra base ed emettitore del VAS. Il solo specchio sposta anche la continua a
  +36 mV.
- Il riferimento del cascode non conta (è già filtrato a ~1 Hz).
- Con la cella, sotto 1 kHz il rail più debole diventa il negativo.

### L'alimentatore, limitato per eccesso (`script/quota_adr020.py`)

Il modello TI del TPS7A4701 (SBVM364) dichiara da sé di non avere il rumore d'uscita e il PSRR solo
fino al primo polo, e in ngspice dà un punto di lavoro sbagliato (L41a): non serve. Il limite:
- **rumore**: TPS7A4701, fig. 5-1 di SBVS204G, curva 15 V con C_NR 1 µF (il progetto ne ha 10);
  letta a occhio, integra a 15,9 µVrms contro i 12,28 stampati, quindi già dal lato alto (mai
  riscalata in giù). TPS7A3301, fig. 22 di SBVS169D, curva −5 V (37 µVrms), **×3** per i 15 V
  senza il credito del feed-forward C513;
- **ripple**: dente di sega da 0,80 Vpp (300 mA, 4700 µF −20 %, scarica su 10 ms interi),
  armoniche ∝ 1/n, più un tono a 50 Hz al 10 %;
- **PSRR dei regolatori**: + piatto a 66 dB fino a 10 kHz (il minimo della curva 15 V di fig.
  5-17, il buco verso 130 Hz; dropout 1 V, il progetto ne ha ≥ 3), 64 dB a 20 kHz; − piatto a
  50 dB.

Al nodo del blocco: rumore 13,8 µVrms sul +, 148 µVrms sul − (20 Hz–20 kHz).

### La tabella della scelta (come l'utente l'ha vista)

| | Solo l'alimentatore | **Cella 10 Ω + 1000 µF** | Cella 22 Ω + 1000 µF | Moltiplicatore |
|---|---|---|---|---|
| PSRR+ a 10 / 20 kHz | 29,5 / 23,5 dB | 71,8 / 66,3 dB | 75,7 / 70,4 dB | 81,1 / 76,1 dB |
| rail in uscita | 0,51 µV, −13 dB SPL | 0,18 µV, −22 dB SPL | 0,18 µV | 0,18 µV |
| margine sulla quota di 1 µV | 5,9 dB | 14,9 dB | 14,9 dB | 14,9 dB |
| tolleranza sul rail + | 6,3 dB | 37,5 dB | 40,8 dB | 43,8 dB |
| clip positivo / margine su E6 × E2 | 13,28 V / 0,82 dB | 13,14 V / 0,73 dB | 12,96 V / 0,61 dB | 12,49 V / 0,29 dB |
| V1 minimo | 64,94° | 64,93° | 64,92° | 64,91° |
| THD a 20 kHz, 0,2 V | 0,00059 % | 0,00060 % | 0,00060 % | 0,00061 % |
| E5 peggiore | 4,315 µV | 4,315 µV | 4,315 µV | 4,315 µV |
| parti in più (8 blocchi) | 0 | 16 | 16 | 32 |

**Scelta dell'utente: la cella 10 Ω + 1000 µF.** IMD, slew (−3,80 V/µs) e recupero di V3
(0,65 µs) invariati in tutte; la rampa di ~1,4 s del TPS7A4701 (C_NR 10 µF, eq. 5) carica le otto
celle con ~0,16 A contro 1,26 A di limite.

## 4. La ricorsa dei guasti all'alimentatore, e R120

La catena di L41c (solo il terzo tempo: la scheda audio coi ponti dell'alimentatore di L41c; il
deck rigenerato è byte-identico, il blocco entra da `gain_block.subckt`). Col blocco con la cella:

| Caso | L41c (ADR-042) | ADR-054 + cella | **+ R120 226 Ω** | Criterio |
|---|---|---|---|---|
| spegnimento morbido | 30 nV | 48 nV | **13 nV** | ≤ 100 µV |
| perdita di rete / angolo minimo | 0,12 / 0,18 µV | 0,18 / 0,26 µV | **0,08 / 0,09 µV** | ≤ 2 mV |
| U502 (rail −) spento | 1,37 mV, 56,2 dB SPL | **1,93 mV, 59,1 dB SPL** | **0,90 mV, 52,6 dB SPL** | obiettivo 2 mV |
| U501 (rail +) spento | 1,03 mV | 0,55 mV | 0,56 mV | ≤ 2 mV |
| U503 spento / angolo minimo | 75 nV | 75 nV | 75 nV | ≤ 2 mV |
| corto della linea a 12 V | 69,4 mV, ~90 dB SPL | **117 mV, ~95 dB SPL** | **29,7 mV, ~83 dB SPL** | tetto 0,87 V |
| controfattuale senza Δ | ≥ 66,5 mV (aborto) | ≥ 112 mV (aborto) | **29,7 mV, in fondo** | deve superare 2 mV |

**La causa non è la cella.** Né C (220, 470, 1000 µF) né R (4,7, 10 Ω) cambiano i due picchi;
il blocco di ADR-054 **senza** cella dà 1,926 mV e 117 mV. L'ha portato **L46a**, che non aveva
ricorso questa catena («V2 del mute non rieseguito», e la catena di L41c non era nella lista).

**Il meccanismo, previsto e poi verificato.** Nel corto della linea a 12 V e nel controfattuale i
relè del guadagno cadono prima del jack: il blocco B passa da +10 a 0 dB a jack collegato, e al
jack arriva il salto della continua d'uscita, −26 mV × (3,15 − 1) = 56 mV contro i 34 mV di
ADR-042. Rapporto 1,66; osservato 117 / 69 = 1,69. La continua è la corrente di base del VAS
(83 µA, β ≈ 129 nel modello) che entra in NHI: la metà cascodata della coppia su quel lato porta
75 µA in più (2,290 / 2,215 mA), e su ~3,1 mS di transconduttanza efficace sono ~24 mV.

**Il rimedio**: R120, la degenerazione del lato d'uscita dello specchio, più grande, così Q121B
fornisce ~83 µA in meno (220 / 0,962 ≈ 229 Ω). Spazzato sul banco:

| R120 | continua del blocco | PSRR− a 100 Hz | V1 minimo |
|---|---|---|---|
| 220 Ω | −26,1 mV | 70,7 dB | 64,93° |
| **226 Ω** | **−6,6 mV** | 76,2 dB | 65,16° |
| 232 Ω | +12,4 mV | 87,2 dB | — |
| 237 Ω | +27,8 mV | 80,5 dB | — |

Su 226 Ω il banco completo: V1 ≥ 65,16° (gruppo B 65,36°), THD a 20 kHz 0,00060 %, armoniche dalla
5ª −192 dB, **IMD −125,6 dB** (era −119,2), THD a 2 V 0,0068 %, E5 4,303 µV (4,315), slew
−3,75 V/µs, clip invariato. **Scelta dell'utente: sì**, con la domanda «dovrà essere una parte
all'1 %? mi sembra troppo sensibile alle variazioni». La risposta: un errore dell'1 % sul rapporto
R120/R119 vale ~7 mV, era così anche con 220/220, e sta sotto il VGS1−VGS2 dell'LSK489 (8 mV
tipici, 20 massimi dal datasheet) e la dispersione di β del VAS (−36…+6 mV per hFE 60–250, stima);
R119 e R120 all'1 %, stessa serie, con l'opzione di una coppia allo 0,1 %.

**Un'osservazione per dopo.** Il PSRR− sotto 1 kHz dipende dal bilanciamento della coppia, e ha
un massimo vicino a 232 Ω (87 dB a 100 Hz). Se sul prototipo comandasse il rail −, è una leva, a
prezzo dell'offset.

## 5. Il sorgente e la regressione

- `circuits/preamp/gain_block.py`: la rete `VPF`; R119, R120, R123 su `VPF`; R120 226 Ω; la cella
  in coda alla funzione, dopo R_G10 (#22: nessun designatore esistente cambia; R144 / C145 nel
  blocco da solo, R142 / C143 nel blocco A della scheda, R243 / C244 nel blocco B, R541 / C542…
  nei buffer, letti da `script/celle_netlist.py`); i commenti con ADR-056; HEADROOM e «SIMULATED
  RESULTS» aggiornati. Due commenti vecchi corretti («its own 47 Ohm degeneration»).
- Rigenerati blocco e scheda audio; il disegno `docs/preamp/schematic/gain_block_draw.py` (VPF in
  arancio, la cella nel pannello 4; corretti anche R123 56, R126 56, R128 1.58k, le correnti del
  VAS e di riposo e la nota sui modelli segnaposto, rimasti a prima di ADR-042/054: il 2d
  confronta le connessioni, non i valori).
- **La regressione** dei 21 deck (`regressione/prima` sul blocco di ADR-054, `dopo` su quello di
  ADR-056): V1 regge e sale di 0,1–0,3° sulle celle di verdetto (0,7–0,8° su quelle che non lo
  sono); classe A e P7 invariati (`p7.py`: 600 righe da entrambe le parti); E4 e trim uguali entro
  0,03 % sulle tabelle echo; PSRR+ a 100 kHz, minimo sui modi, 10,7 → 58,3 dB (sorgente,
condensatore ideale; 52,6 dB con l'ESR). Le cifre «presenti da una
  parte sola» e gli «+213 %» di `confronto_grezzo.csv` sono frammenti e indici slittati da Note
  (#37), verificati sulle tabelle echo.
- **Una cifra si muove, e non conta**: la continua al jack 13–14 ms dopo il sovraccarico di V3,
  +3,17 → +3,60 mV (la cella da 10 ms che si riassesta; la continua di regime al jack resta tolta
  dal condensatore d'uscita).
- `run_tests.sh`: **13 passed / 0 failed**.

## 6. ADR-020 ricalcolato (chiude NC-052)

`limiti_psrr.py` di L40 ridà ancora la tabella di L18 dai suoi CSV. Sul blocco di ADR-056 con ESR
0,05 Ω (`run/adr056_esr005/`): V+ massimo per tono 7,40 / 8,88 / 9,44 / 3,83 / 2,04 mV RMS a 50 /
100 Hz / 1 / 10 / 20 kHz; V− 3,66 / 6,46 / 20,7 / 10,3 / 5,40 mV; rumore bianco sul rail + ≤
23,9 µV/√Hz (era 87 nV/√Hz con ADR-042). La «Nota su E5» cita ora CSV versionati.

## 7. Cosa non è stato fatto

- **V2 del mute** (`tb_v2_mute_ldr.cir`) non rieseguito, né in L46a né qui: tocca a L47.
- Il dossier non rigenerato (fuori dal lotto).
- La dispersione dell'offset sul prototipo (β del VAS, LSK489, resistenze) non simulata: i modelli
  non hanno dispersione; stima nel §4.
- Il TPS7A4701 resta senza un modello di rumore: la quota è verificata su un limite per eccesso;
  la misura è di NC-011.

## 8. Una lezione di processo

Un lotto che cambia il blocco deve ricorrere **anche** le catene che stanno a valle, non solo i
21 deck veloci: L46a ha cambiato la continua d'uscita del blocco, e i guasti all'alimentatore di
L41c, la cui evidenza dipende da quella continua, sono rimasti con cifre scadute fino a qui. La
catena di L41c sta ora in `data/2026-10-01/L46b/l41c/` col comando per rifarla.
