# 2026-10-01 — L46a, la compensazione del blocco di guadagno e la distorsione verso gli acuti

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

Tutte le varianti: corrente di riposo d'uscita 20,2–20,5 mA; rumore E5 peggiore 4,27–4,32 µV
(contro 9,95), quello del blocco A 1,176–1,188 µV. Tabella completa in `sintesi.csv`.

**V1 nel gruppo B di I_DSS** (ADR-031, `idss.csv`), minimo su b_min/b_tip/b_max, blocco B /
blocco A / buffer: 1 nF 62,19 / 67,71 / 63,23°; VAS 470 pF **65,14 / 68,24 / 65,13°**; VAS 390 pF
63,29 / 64,97 / 62,85°; VAS 330 pF 61,22 / 60,91 / 60,33°; driver + VAS 330 pF **70,50 / 70,06 /
70,46°**; driver 330 pF 64,96 / 63,25 / 64,44°. In ogni variante il minimo del gruppo B sta
sopra quello del modello pubblicato (di 0,02–0,3°).

### Che cosa dicono i numeri

1. **La leva è la corrente del VAS, non il driver.** Il driver da solo compra margine (+4° a
   1 nF) ma **peggiora** la distorsione a parità di Miller (0,0029 % contro 0,0017 % a 20 kHz). Il
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

## 3. I costi delle due finaliste

| | VAS a 10,7 mA, 470 pF | driver + VAS, 330 pF |
|---|---|---|
| Parti cambiate per blocco | 4 valori: R123, R126 91 → 56 Ω, R128 1,69k → 1,58k, C124 1n → 470p | gli stessi (R128 3,24k, C124 330p) **più 3 parti**: QD1, QD2, RD12 |
| Parti nuove sulle 8 istanze | nessuna | 24 |
| Corrente per rail, un blocco | 36,7 / 37,7 mA (+4,1 mA) | 42,5 / 43,6 mA (+9,9 mA) |
| Potenza a riposo in più, 8 blocchi | **~1,0 W** | **~2,4 W** |
| VAS / pozzo (Q122 / Q125) | 0,142 / 0,122 W contro 310 mW (P7) | idem; più i driver ~0,09 W ciascuno |
| Continua all'uscita del blocco | −26 mV (oggi −15 mV) | −26 mV |
| Margine V1 / gruppo B | 64,94 / 65,13° | 69,98 / 70,06° |

**La continua all'uscita** sale da −15 a −26 mV perché la corrente di base del VAS è più alta.
Nel blocco B la ferma il condensatore d'uscita; nel **blocco A** attraversa il trim e il volume
(NC-041, lotto L48 del selettore d'ingresso). È un dato da portare lì.

**La potenza in più** pesa sul bilancio termico (NC-029, chiusa in L30 con ~20 mA d'uscita) e
sulla corrente dei regolatori (ADR-048): +33 mA per rail sugli 8 blocchi con la prima, +79 mA con
la seconda.

**Un effetto del modello, da sapere.** Il MMBT5551 del costruttore ha la quasi-saturazione
(`QUASIMOD=1`, `RCO=170`). Col VAS a 10,7 mA il moltiplicatore di Vbe (Q127, 9,7 mA, 2,0 V fra
collettore ed emettitore) ha la giunzione base-collettore **interna** a +0,42 V (oggi −0,27 V):
lavora in quasi-saturazione nel modello. La corrente d'uscita resta quella tarata e le cifre di
distorsione lo comprendono già. Sul prototipo, se serve, il rimedio classico è un condensatore
in parallelo al moltiplicatore.

## 4. La scelta dell'utente

*(da compilare dopo la risposta)*

## 5. I dispositivi d'uscita più veloci

*(da compilare con l'esito della ricerca dei modelli del costruttore)*
