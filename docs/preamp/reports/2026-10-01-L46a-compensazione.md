# 2026-10-01 — L46a, la compensazione del blocco di guadagno e la distorsione verso gli acuti

**Chiude NC-039. Aggiorna NC-047 (resta a L46b) e NC-041. ADR nuove: ADR-054, ADR-055.**

**Documento datato: non si riscrive.** Dati: `../data/2026-10-01/L46a/` (README dentro).
Requisiti: PR-7, **PR-8**, V1, **V4** · ADR-019, ADR-024, ADR-031, **ADR-042** · NC-039, NC-047.

**Cifre di modello, non misure** (`CLAUDE.md`, «Nessun agente giudica come suona un circuito»):
conta il trend fra varianti sullo stesso banco, non il valore assoluto.

## 0. Le due decisioni prese all'inizio

Il prompt di L46 le chiedeva prima di tutto. Risposte dell'utente (2026-10-01):

- **Il livello musicale a cui si giudica la distorsione verso gli acuti: −20 dB**, cioè
  **0,2 V RMS all'uscita** del preamp, ~99 dB SPL a 1 m su un tono continuo (finale ×21,1,
  Heresy 96 dB/1 W/1 m). Le opzioni erano −12 dB (0,5 V, ~107 dB SPL) e i 2 V dell'architetto
  (~119 dB SPL). I 2 V restano nel banco come **prova di stress**, non come criterio.
- **Il lotto si divide**: L46a (questo) la compensazione e la distorsione; **L46b** il PSRR del
  rail + nel blocco o nell'alimentatore, ADR-020 ricalcolato, la nota su E5 ripuntata (NC-047,
  NC-052).

## 1. Il banco

Un banco solo per tutte le varianti (`script/genera.py`), che include il blocco della variante
(`inc/<variante>.inc`, scritto da `script/varianti.py` come copia di `gain_block_flat.inc` con le
righe cambiate) al posto del blocco generato:

| Famiglia | Deck | Cosa |
|---|---|---|
| V1 | `tb_loop`, `tb_loop_blockA`, `tb_loop_bufferfissa` (versionati) | criterio di ADR-024, com'è in `L40/script/sintesi_v1.py` |
| I_DSS | `tb_idss_loop` (versionato) + `L40/script/idss_istanze.py` | gruppo B di ADR-031, sulle tre istanze, per le finaliste |
| punto di lavoro | `tb_op` (versionato) | corrente di riposo, VAS, rail |
| PSRR, rumore | `tb_zout_psrr_noise`, `tb_noise_breakdown` (versionati) | PSRR+ a +10 dB (il modo peggiore), E5 |
| slew | il metodo di L12/L40 | gradino ±1,9 V; 20 kHz a 12 V di picco |
| THD | nuovo, dal banco dell'architetto (L43a) | blocco B nei tre modi; sorgente 2,5 kΩ; 47 Ω + 4,7 µF + 10 kΩ; 1 / 10 / 20 kHz; **0,2 V RMS** (criterio) e 2 V RMS (stress) |
| IMD | nuovo, stesso banco | CCIF 19 + 20 kHz, toni uguali, picco composto pari a quello del sinusoide del livello; prodotto a 1 kHz contro un tono |

**I controlli, prima di fidarsi.**
- I due deck dell'architetto, col solo include ripuntato, ridanno L43a: **0,1682 %** e
  **−59,6 dB** con 1 nF (L43a: 0,168 %, −59,6), **0,01182 %** e **−85,5 dB** con 470 pF (0,0118 %,
  −85,4).
- La variante `cm1n` (il blocco di oggi, invariato) ridà L40 al centesimo: V1 62,08 / 76,20 /
  96,66 / 67,68 / 63,21°, PSRR+ 23,0 dB a 10 kHz, slew −1,68 V/µs, continua a 20 kHz 0,572 V;
  nel gruppo B 62,19 / 67,71 / 63,23° (L40: 62,19–62,24 / 67,71–67,74 / 63,23–63,25).
- `cm470p` ridà L39 (55,55 / 54,92°).
- Il pavimento numerico della `fourier` (la sorgente ideale nella stessa corsa) sta a
  ~2·10⁻¹⁰ %, sei decadi sotto la cifra più bassa misurata.
- Ogni caso controlla che la sorgente abbia l'ampiezza chiesta (±1 %).

**Una trappola nota, ritrovata.** Nel primo deck IMD una `Note:` del gmin stepping è caduta
dentro una riga della tabella `fourier` (#37): il parser ha perso l'armonica 14 e ha spostato le
successive, e il primo caso sembrava a uscita spenta. `script/leggi_four.py` ora ricuce la riga e
rifiuta una tabella con un'armonica mancante; la ricucitura capita una volta per deck IMD e viene
stampata.

**E una nuova, sul rimedio di #33.** Coi dispositivi d'uscita ZXT l'op della `tran`, dopo l'`alter`
che cambia il modo, ripiegava sul «transient op» in 23 deck su 32, e la THD usciva al **73 %**
(lo stato sbagliato di #33). Il parser li ha rifiutati. Il rimedio di L29c,
`option gminsteps=40`, qui fa il **contrario**: fa ripiegare anche i MJE, che senza opzione non
ripiegavano mai. `option itl1=1000` (più iterazioni di Newton per l'op) toglie ogni ripiego, e
sul blocco di oggi le cifre sono quelle senza opzione alla sesta cifra (cambia solo il pavimento
numerico, sotto −250 dB). È nei deck `thd` e `imd` di tutte le varianti, rieseguiti tutti.
Da portare in `docs/limitations.md` accanto a #33: il rimedio dipende dal circuito, e si prova.

## 2. Le alternative

La radice è quella di ADR-042: la CJE di 3,06 nF dei MJE15032/33. Le strade misurate:

- **a. solo il Miller** (C124 470p–1n): la griglia di L40, ora con la distorsione;
- **b. un driver** fra il VAS e i MJE: un inseguitore complementare MMBT5551/MMBT5401 (QD1,
  QD2), RD12 330 Ω fra gli emettitori (~6,2 mA), il moltiplicatore di Vbe su 4 Vbe (R128 3,48k,
  tarato in `run/drv_r*/tb_op` per ~20,3 mA d'uscita come oggi);
- **c. il VAS a ~10,7 mA** invece di 6,8: R123 e R126 da 91 a **56 Ω** (uguali, per il clipping
  simmetrico del commento del VAS), R128 da 1,69k a **1,58k** perché la corrente d'uscita resti
  ~20,5 mA;
- **b + c** insieme (R128 3,24k);
- **d. la compensazione a due poli**: **non misurata**. Il piano la teneva per il caso in cui a,
  b e c non tenessero i 60° con distorsione bassa; c li tiene da sola.
- **e. dispositivi d'uscita più veloci**: vedi §5.

### La tabella

V1: il minimo su blocco B (0 / +3 / +10 dB), blocco A, trim e buffer delle fisse. THD e IMD: il
peggiore sui tre modi del blocco B. «Crescita»: THD a 20 kHz contro 1 kHz, al livello −20 dB.
I_rail: corrente del rail + di **un** blocco.

| Variante | V1 min | crossover | I_rail | PSRR+ 10 k / 20 k | slew giù | THD −20 dB 1 k / 20 k | crescita | h5+ | IMD −20 dB | THD 2 V 20 k | IMD 2 V |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1 nF (oggi)** | 62,08 | 430 k | 32,6 mA | 23,0 / 17,1 dB | −1,68 V/µs | 0,000044 / **0,0017 %** | 32,0 dB | −164 dB | **−96,3 dB** | **0,17 %** | −60,2 dB |
| 820 pF | 60,70 | 520 k | 32,6 | 24,7 / 18,8 | −2,02 | 0,000038 / 0,0013 | 30,8 | −171 | −99,4 | 0,075 | −66,9 |
| 680 pF | 59,26 | 622 k | 32,6 | 26,3 / 20,4 | −2,41 | 0,000033 / 0,0010 | 29,9 | −178 | −102,2 | 0,037 | −72,6 |
| 470 pF (L39) | 54,92 | 889 k | 32,6 | 29,5 / 23,5 | −3,40 | 0,000026 / 0,00068 | 28,2 | −192 | −107,4 | 0,012 | −82,0 |
| driver, 1 nF | 66,45 | 431 k | 38,8 | 23,0 / 17,1 | −1,72 | 0,000054 / 0,0029 | 34,7 | −163 | −91,2 | 0,19 | −58,5 |
| driver, 680 pF | 66,14 | 625 k | 38,8 | 26,3 / 20,4 | −2,52 | 0,000042 / 0,0015 | 31,2 | −178 | −97,9 | 0,043 | −70,8 |
| driver, 470 pF | 65,70 | 896 k | 38,8 | 29,5 / 23,6 | −3,62 | 0,000034 / 0,00089 | 28,4 | −191 | −104,3 | 0,014 | −80,5 |
| driver, 330 pF | 63,16 | 1,27 M | 38,8 | 32,6 / 26,6 | −5,11 | 0,000029 / 0,00062 | 26,7 | −190 | −110,5 | 0,0070 | −88,5 |
| driver, 220 pF | **57,10** | 1,91 M | 38,8 | 36,0 / 30,0 | −7,12 | 0,000025 / 0,00048 | 25,8 | −190 | −117,7 | 0,0049 | −96,7 |
| VAS 10,7 mA, 1 nF | 69,36 | 422 k | 36,7 | 23,0 / 17,1 | −1,85 | 0,000048 / 0,00098 | 26,2 | −171 | −108,9 | 0,072 | −67,9 |
| VAS 10,7 mA, 680 pF | 67,32 | 611 k | 36,7 | 26,3 / 20,4 | −2,68 | 0,000038 / 0,00074 | 25,7 | −185 | −114,4 | 0,016 | −81,0 |
| **VAS 10,7 mA, 470 pF** | **64,94** | 876 k | 36,7 | **29,5 / 23,5** | **−3,80** | 0,000032 / **0,00059** | 25,5 | −185 | **−119,2** | **0,0070** | **−91,3** |
| VAS 10,7 mA, 390 pF | 62,83 | 1,05 M | 36,7 | 31,1 / 25,1 | −4,51 | 0,000029 / 0,00054 | 25,3 | −185 | −121,5 | 0,0057 | −95,7 |
| VAS 10,7 mA, 330 pF | 60,30 | 1,24 M | 36,7 | 32,6 / 26,6 | −5,25 | 0,000027 / 0,00050 | 25,2 | −185 | −123,6 | 0,0051 | −99,2 |
| driver + VAS, 470 pF | 71,07 | 878 k | 42,5 | 29,5 / 23,5 | −3,97 | 0,000035 / 0,00067 | 25,6 | −184 | −115,5 | 0,0079 | −90,0 |
| **driver + VAS, 330 pF** | **69,98** | 1,25 M | 42,5 | **32,6 / 26,6** | −5,59 | 0,000030 / 0,00055 | 25,2 | −184 | **−122,3** | 0,0057 | −99,0 |
| driver + VAS, 220 pF | 64,40 | 1,87 M | 42,5 | 36,0 / 30,0 | −7,47 | 0,000027 / 0,00047 | 24,9 | −184 | −130,7 | 0,0047 | −108,9 |
| ZXT, 1 nF | 66,44 | 431 k | 32,5 | 23,0 / 17,1 | −1,71 | 0,000050 / 0,0030 | 35,4 | −162 | −91,0 | 0,20 | −58,3 |
| ZXT, 470 pF | 65,66 | 896 k | 32,5 | 29,5 / 23,6 | −3,59 | 0,000031 / 0,00089 | 29,1 | −191 | −103,9 | 0,014 | −80,1 |
| ZXT, 330 pF | 63,00 | 1,27 M | 32,5 | 32,6 / 26,6 | −5,05 | 0,000026 / 0,00061 | 27,3 | −191 | −109,9 | 0,0070 | −87,8 |
| ZXT, 220 pF | 56,95 | 1,91 M | 32,5 | 36,0 / 30,1 | −7,01 | 0,000022 / 0,00046 | 26,3 | −191 | −116,6 | 0,0047 | −95,6 |
| ZXT, 150 pF | 48,09 | 2,80 M | 32,5 | 39,3 / 33,3 | −8,39 | 0,000020 / 0,00039 | 25,9 | −191 | −122,9 | 0,0040 | −102,4 |
| ZXT + VAS, 330 pF | 70,27 | 1,25 M | 36,4 | 32,6 / 26,6 | −5,55 | 0,000028 / 0,00054 | 25,6 | −184 | −121,1 | 0,0055 | −98,0 |
| **ZXT + VAS, 220 pF** | **64,96** | 1,87 M | 36,4 | **36,0 / 30,0** | −7,40 | 0,000024 / **0,00045** | 25,4 | −184 | **−128,5** | **0,0045** | −106,9 |
| ZXT + VAS, 150 pF | 57,37 | 2,75 M | 36,4 | 39,3 / 33,3 | −8,67 | 0,000022 / 0,00040 | 25,2 | −184 | −135,6 | 0,0040 | −114,8 |

«ZXT»: i MJE15032/33 sostituiti dai Diodes ZXTN25040DZ / ZXTP25040DZ (SOT-89), R128 1,87k (1,74k
col VAS) per la stessa corrente di riposo; vedi §5.

Tutte le varianti: corrente di riposo d'uscita 20,2–20,5 mA; rumore E5 peggiore 4,27–4,32 µV
(contro 9,95), quello del blocco A 1,176–1,188 µV. Tabella completa in `sintesi.csv`.

**V1 nel gruppo B di I_DSS** (ADR-031, `idss.csv`), minimo su b_min/b_tip/b_max, blocco B /
blocco A / buffer: 1 nF 62,19 / 67,71 / 63,23°; VAS 470 pF **65,14 / 68,24 / 65,13°**; VAS 390 pF
63,29 / 64,97 / 62,85°; VAS 330 pF 61,22 / 60,91 / 60,33°; driver + VAS 330 pF **70,50 / 70,06 /
70,46°**; driver 330 pF 64,96 / 63,25 / 64,44°. In ogni variante il minimo del gruppo B sta
sopra quello del modello pubblicato (di 0,02–0,3°).

### Che cosa dicono i numeri

1. **La leva è la corrente del VAS, non il driver né i dispositivi d'uscita.** Il driver da solo,
   e allo stesso modo i ZXT da soli (le due righe sono quasi identiche: tolgono la stessa
   capacità dal nodo del VAS), comprano margine (+4° a 1 nF) ma **peggiorano** la distorsione a
   parità di Miller (0,0029–0,0030 % contro 0,0017 % a 20 kHz). Il
   VAS a 10,7 mA a parità di Miller (1 nF) dimezza la THD a 20 kHz, toglie 13 dB di IMD e compra
   7° di margine. La causa è quella di ADR-042 vista dall'altro lato: il nodo del VAS deve
   caricare la capacità dei MJE, e 6,8 mA non bastano.
2. **Il PSRR+ dipende solo dal Miller**: 470 pF dà 29,5 dB a 10 kHz in ogni topologia, 330 pF
   32,6, 220 pF 36,0. Il rail + entra nel blocco attraverso C124. È l'ingresso di L46b.
3. **Nessuna variante fa «la THD a 20 kHz dello stesso ordine di quella a 1 kHz»** (V4, prima
   clausola). La crescita minima è ~25 dB, ed è la pendenza naturale di un anello col guadagno
   che cala di 6 dB per ottava (×20 in frequenza = 26 dB). Il Miller da 1 nF ne aggiunge ~7 dB
   oltre quella. Una crescita sotto i 25 dB vorrebbe più guadagno d'anello a 20 kHz, cioè una
   compensazione di ordine superiore e un margine di fase più sottile: è proprio quello che ADR-019
   esclude. La clausola di V4 va riscritta come criterio decidibile (NC-039 lo chiede già).
4. **Lo spettro resta in ordine** in ogni variante: al livello −20 dB la h2 domina, la h3 sta
   15–50 dB sotto, e le armoniche dalla 5ª in su stanno sotto −160 dB. La clausola «armoniche
   alte» di PR-8 regge ovunque.

**In SPL, al livello deciso.** Un tono da 0,1 V RMS al preamp (ciascuno dei due del CCIF) è
~93 dB SPL a 1 m. Il prodotto a 1 kHz sta quindi a **~−3 dB SPL** col Miller da 1 nF, **~−26 dB
SPL** col VAS a 10,7 mA e 470 pF, **~−29 dB SPL** con driver + VAS a 330 pF: sotto la soglia
dell'udito (0 dB SPL) in tutti e tre i casi. Alla prova di stress (1 V RMS per tono, ~113 dB SPL):
~53 dB SPL col 1 nF di oggi, ~22 dB SPL col VAS a 470 pF, ~14 dB SPL con driver + VAS a 330 pF.
È un picco contro un livello di tono, e una stanza silenziosa sta a 25–35 dB(A).

## 3. Le tre finaliste, come l'utente le ha viste

La prima domanda proponeva le tre finaliste in tre righe; l'utente ha chiesto di vederle in
tabella prima di decidere («put the 3 options on a table before I can decide and ask me again»).
Questa è la tabella, con le soglie di ADR-055 già decise nella stessa domanda:

| | **Oggi** (1 nF) | **A. VAS più veloce, 470 pF** | **B. VAS + ZXT, 220 pF** | **C. VAS + driver, 330 pF** |
|---|---|---|---|---|
| Cosa cambia per blocco | — | 4 valori, nessuna parte nuova | 4 valori + MJE → ZXT (SOT-89) | 4 valori + 3 parti (QD1, QD2, RD12) |
| Parti nuove sugli 8 blocchi | — | nessuna | nessuna (16 sostituite) | 24 |
| V1 minimo (≥ 60°) | 62,1° | 64,9° | 65,0° | **70,0°** |
| V1 nel gruppo B di I_DSS | 62,2° | 65,1° | non misurato | **70,1°** |
| PSRR+ a 10 kHz, +10 dB | 23,0 dB | 29,5 dB (+6,5) | **36,0 dB (+13)** | 32,6 dB (+9,6) |
| THD a 20 kHz, 0,2 V (tetto 0,001 %) | 0,0017 % ✗ | 0,00059 % ✓ | **0,00045 %** ✓ | 0,00055 % ✓ |
| IMD CCIF, 0,2 V (tetto −110 dB) | −96 dB ✗ | −119 dB ✓ | **−128,5 dB** ✓ | −122 dB ✓ |
| … il prodotto a 1 kHz, a 1 m | −3 dB SPL | −26 dB SPL | **−35 dB SPL** | −29 dB SPL |
| Dalla 5ª in su (tetto −140 dB) | −164 dB ✓ | −185 dB ✓ | −184 dB ✓ | −184 dB ✓ |
| THD a 20 kHz, 2 V (tetto 0,01 %) | 0,17 % ✗ | 0,0070 % ✓ | **0,0045 %** ✓ | 0,0057 % ✓ |
| Slew in discesa | −1,68 V/µs | −3,80 V/µs | −7,40 V/µs | −5,59 V/µs |
| E5 peggiore (≤ 9,95 µV) | 4,27 µV | 4,32 µV | 4,32 µV | 4,32 µV |
| Corrente per rail, un blocco | 32,6 mA | 36,7 mA | 36,4 mA | 42,5 mA |
| Potenza in più, 8 blocchi | — | ~+1,0 W | ~+0,9 W | ~+2,4 W |
| Continua all'uscita del blocco | −15 mV | −26 mV | −26 mV | −26 mV |

I rischi, detti all'utente con la tabella:
- **A**: nessuna parte nuova; il PSRR+ recuperato è il più piccolo, il resto va a L46b.
- **B**: il PNP ZXT a 0 pezzi da Farnell e senza stato confermato altrove; il SOT-89 a ~100 °C di
  giunzione a 60 °C ambiente sul pad minimo; l'analisi termica del corto e del mute (ADR-021) da
  rifare; V_CEO 40 V contro 30 V di escursione; nessun minimo di f_T pubblicato.
- **C**: il margine più largo, ma il costo più alto in parti, potenza e corrente dei rail.

**La continua all'uscita** sale da −15 a −26 mV perché la corrente di base del VAS è più alta.
Nel blocco B la ferma il condensatore d'uscita; nel **blocco A** attraversa il trim e il volume
(NC-041, lotto L48 del selettore d'ingresso).

**La potenza in più** pesa sul bilancio termico (NC-029, chiusa in L30 con ~20 mA d'uscita) e
sulla corrente dei regolatori (ADR-048): +33 mA per rail sugli 8 blocchi con A.

**Un effetto del modello, da sapere.** Il MMBT5551 del costruttore ha la quasi-saturazione
(`QUASIMOD=1`, `RCO=170`). Col VAS a 10,7 mA il moltiplicatore di Vbe (Q127, 9,7 mA, 2,0 V fra
collettore ed emettitore) ha la giunzione base-collettore **interna** a +0,42 V (oggi −0,27 V):
lavora in quasi-saturazione nel modello. La corrente d'uscita resta quella tarata e le cifre di
distorsione lo comprendono già. Sul prototipo, se serve, il rimedio classico è un condensatore
in parallelo al moltiplicatore.

## 4. Le scelte dell'utente

Due domande, il 2026-10-01, dette per nome e con le cifre in dB SPL:
- **La compensazione: A, il VAS più veloce con 470 pF** (la raccomandata). Diventa **ADR-054**,
  che supera ADR-042 nel Miller e in R128; la corrente d'uscita ~20 mA di ADR-042 resta.
- **La clausola «dello stesso ordine» di V4: i tetti assoluti** (la raccomandata) fra «tetti
  10 dB più severi» e «nessuna soglia fino al prototipo». Diventa **ADR-055**; `REQUIREMENTS.md`,
  V4, ha la tabella.

## 5. I dispositivi d'uscita più veloci

La ricerca l'ha fatta `bom-component-manager` in background (il report sta in questo documento,
non altrove):

| Coppia | Modello del costruttore per entrambe | Esito |
|---|---|---|
| **Diodes ZXTN25040DZ / ZXTP25040DZ** (SOT-89) | sì | **importata**: f_T 194,6 / 275,5 MHz a 50 mA (190 / 270 tipici, nessun minimo), C_obo 12,18 / 18,09 pF, CJE ~190 pF contro 3,06 nF dei MJE. Disponibilità: NPN 101 pezzi da Farnell, **PNP 0**; Mouser, Digi-Key e LCSC non leggibili in automatico (dati da findchips.com, 2026-10-01) |
| onsemi KSC3503DS / KSA1381 (TO-126) | sì | scartata: l'NPN è a fine vita («Last Shipments» / «Obsolete») |
| onsemi BD139 / BD140 | sì, ma generici (CJE = CJC = 10 pF) e senza f_T nel datasheet | scartata: niente da verificare |
| MJE15034 / MJE15035 | sì | scartata: CJE ~1,6 nF, lo stesso problema |
| Toshiba 2SC4793 / 2SA1837 | no | scartata |

I modelli stanno in `models/bjt_npn/zxtn25040dz.lib` e `models/bjt_pnp/zxtp25040dz.lib`, i file
del costruttore congelati in `vendor/bjt_*/diodes_inc/ZXT*25040DZ/` (sola lettura), la provenienza
nei `.provenance.json`. Restano nel repo anche se l'utente ha scartato l'opzione B: sono
l'evidenza delle righe «ZXT» della tabella, e i deck li includono. `scripts/validate_models.py` ha
due ricette nuove (`tb_zxtn25040dz`, `tb_zxtp25040dz`, corpo `_tb_zxt`): h_FE a 10 mA e 1 A
(447,8 / 311,2 e 409,2 / 291,1, sopra i minimi), f_T a 50 mA verificato da un op, C_obo. Suite:
52 su 52, provenienza 26 su 26.

## 6. Il sorgente e la regressione

**Il sorgente.** `circuits/preamp/gain_block.py`: R123 e R126 56 Ω, R128 1,58 kΩ, C124 470 pF,
ognuno col commento che cita ADR-054 e il perché; il blocco «SIMULATED RESULTS» riscritto sulle
cifre di sotto; il vincolo di distinta delle 22 Ω d'emettitore a ≥ 0,28 W.
`circuits/preamp/preamp_audio.py`: la 47 Ω dell'uscita principale a ≥ 1,13 W, e la tenuta dei
rail ricalcolata a mano per ~298 mA per rail (≥ 14,6 ms invece di 16, contro 4 ms dei relè; non
rieseguita). Rigenerati blocco e canale: nei `.subckt`/`_flat.inc` cambiano **quattro righe** per
forma; nei `.net` cambiano 4 valori nel blocco e 32 nel canale (otto istanze), il resto del diff
sono tag, timestamp e data. ERC: 0 errori.

**La regressione**, i 21 deck veloci di L40, prima e dopo nella stessa sessione
(`regressione/`, `script/regressione.sh`; i riassunti con gli script di L40 copiati senza
modifiche in `regressione/script/`): rc 0 ovunque, nessuna riga `Error`, nessun ripiego.
`confronto_grezzo.csv`: 28 069 cifre; le 31 presenti da una parte sola sono frammenti di righe
spezzate da una Note (#37: `from`, `om`, `rom`, e due chiavi contate una volta in più; le righe
`att1k` e `zn20k` sono 24 e 135 da tutte e due le parti, coi valori identici).

| Cifra | Soglia | Prima (ADR-042) | Dopo (ADR-054) | Esito |
|---|---|---|---|---|
| **V1 blocco B 0 / +3 / +10 dB** | ≥ 60° | 62,08 / 76,20 / 96,66° | **64,94 / 73,24 / 104,97°** | regge |
| **V1 blocco A** (≤ 1 nF) / trim | ≥ 60° | 67,68 / 69,80° | **68,19 / 73,10°** | regge |
| **V1 buffer** | ≥ 60° | 63,21° | **65,12°** | regge |
| V1 gruppo B, blocco B (b_min…b_max) | ≥ 60° | 62,19–62,24° | 65,14–65,24° | regge |
| V1, celle non di verdetto (ADR-024): sonda al nodo 0 / +3 dB; blocco A col cablaggio da 4,7 nF | — | 57,99 / 73,11°; 58,12° | **48,31 / 55,83°; 44,73°** | informative, **calano molto** |
| guadagno d'anello a 10 Hz | ~81 dB | 81,19 dB | 78,81 dB | — |
| E2 +3 / +10 dB a 1 kHz | ±0,1 dB / 9,5–10,5 | 3,039 / 9,963 dB | 3,039 / 9,962 dB | regge |
| banda −3 dB a 0 / +3 / +10 dB | — | 912 / 303 / 113 kHz | 1,55 MHz / 489 / 178 kHz | — |
| a +10 dB, 20 kHz contro 1 kHz | E9 ±0,2 dB | −0,133 dB | −0,055 dB | regge meglio |
| E3 peggiore | ≥ 100 kΩ | 110,71 kΩ | 110,71 kΩ | regge |
| E4 Re(Z) max principale / fisse | < 100 Ω | 60,09 / 53,12 Ω | 60,08 / 53,12 Ω | regge |
| Zout al nodo, 1 / 20 kHz | — | 0,037 / 0,57 Ω | 0,026 / 0,27 Ω | — |
| E5 peggiore (`tb_e3_e5_ldr`) | ≤ 9,95 µV | 5,034 µV | 5,103 µV | regge |
| E5, `tb_noise_breakdown` | ≤ 9,95 µV | 1,176…4,270 µV | 1,188…4,315 µV | regge |
| PSRR+ (+10 dB) 100 Hz / 1 / 10 kHz | ADR-020 | 62,6 / 43,0 / 23,0 dB | **66,9 / 49,5 / 29,5 dB** | L46b |
| PSRR− (+10 dB) 100 Hz / 10 kHz | ADR-020 | 73,3 / 76,4 dB | 70,7 / 80,1 dB | L46b |
| V3: clip; DC al jack | recupera, niente latch | +13,23 / −13,79 V; +3,19 mV | +13,28 / −13,84 V; +3,17 mV | regge |
| V3: recupero, guadagno e continua stimati insieme | — | 1,49 µs | **0,65 µs** | regge |
| P7: MJE / Q122 / Q125 | 1,04 W / 310 / 310 mW | 0,371 / 0,091 / 0,098 W | 0,365 / 0,144 / 0,143 W | regge |
| 22 Ω d'emettitore; 47 Ω principale (corto, +10 dB, 20 kHz) | distinta | 0,241 / 0,947 W | **0,280 / 1,128 W** | vincoli alzati a ≥ 0,28 / ≥ 1,13 W |
| classe A (`tb_blockA_carichi` F2; `tb_mute_corto` caso 0) | tutte | 36/36; 104/104 | 36/36; 104/104 | regge |
| V2 relè (`tb_switch_v2`): picchi delle finestre | — | 1,526 V | 1,492 V (−2,2 %) | — |

**Il recupero di V3 va letto con attenzione.** `v3.py` di L39/L40, senza modifiche, stampa dopo
«recupero 14000 µs». Non è un recupero mancato: il criterio è |v(OUT) − G·v(SRCN)| < 5 %
dell'inviluppo (78,7 mV a +10 dB) **senza togliere la continua**, e il nodo OUT a +10 dB è in
continua con guadagno 3,15: −26 mV × 3,15 ≈ −79 mV, sopra la soglia per tutta la corsa (prima
−48 mV, sotto). `regressione/script/v3_con_continua.py` stima guadagno e continua insieme: 1,49 µs
prima, **0,65 µs** dopo. Anche i 3,03 µs di L40 erano gonfiati dalla continua.

**Le celle non di verdetto** (la sonda sul nodo del blocco, prima della 47 Ω; il blocco A con
4,7 nF di cablaggio, dove il criterio è ≤ 1 nF) perdono 10–17°. Non sono criteri di V1
(ADR-024), ma dicono che il blocco è meno tollerante a una capacità messa **direttamente** sul suo
nodo d'uscita: un dato per il layout di prova (L49), dove il cablaggio del blocco A si misura.

## 7. Cosa non è stato fatto

- **V2 del mute** (`tb_v2_mute_ldr.cir`, la cella 1 kHz / 100 kΩ di L40): non rieseguito. Le
  cifre di L40 restano quelle citate, e il prossimo lotto che tocca il mute (L47) le rifà.
- **I limiti di ADR-020**, la nota su E5 e la tabella del PSRR in `REQUIREMENTS.md`: sono di
  L46b, sul blocco di oggi.
- **La tenuta dei rail** a ~298 mA è un calcolo a mano, non una corsa del banco di L30.
- **La THD sulle uscite fisse e sul blocco A**: il banco misura il blocco B nei tre modi; il blocco
  A e i buffer sono lo stesso blocco a 0 dB con altri carichi.
- **La compensazione a due poli**: non misurata (§2).
- Solo 27 °C, come ogni deck del repo. Il dossier non è rigenerato.
