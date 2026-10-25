# L57b — il limitatore d'ingresso nel sorgente

Data: 2026-10-25 · Lotto: L57b (sessione «hi-fi preamp L57b») · Dati: `data/2026-10-25/L57b/` (README)
· Decisione: **ADR-101** (le parti, scelte qui nel suo perimetro) · Non conformità: **NC-059 chiusa**.

All'inizio l'utente: **«Una sessione»**. Il lotto mette nel sorgente il limitatore scelto in L57a — per
canale 1 kΩ in serie fra il contatto del selettore e l'ingresso del blocco A e due diodi verso due
riferimenti a ±5 V comuni ai due canali —, sceglie le parti, rifà il banco di L57a sul circuito
generato e misura la regressione.

## 1. Le parti, contro i loro limiti

| Parte | Scelta | Contro i limiti (caso peggiore delle tre reti, classe II) |
|---|---|---|
| D179 / D379 | **Nexperia BAV199**, coppia in serie in SOT-23 (il comune sull'ingresso) | ≤ 1,15 mA a rete +10 % contro 140 mA (IF, doppio in uso); dispersione 3 pA tip. / 5 nA max a 75 V e 25 °C (p. 3) contro i 30 nA max a 25 V del BAV99; 1,1 pF a 5 V inversi (fig. 5) |
| U1 / U2 | **TI LM4040B-5.0** in SOT-23, a shunt (+5 V catodo sul nodo, −5 V anodo) | bias ~1,0 mA dai 10 kΩ (IRMIN 74 µA max, p. 26), +1,15 mA da un diodo che limita: ~3,3 mA coi due canali, 3,8 mA col rail a ~20 V di un regolatore in corto (L45d2b2c), contro 15 mA raccomandati; 19 mW contro 306 mW, ~6 °C sopra l'aria |
| R179 / R379 | 1 kΩ (ADR-101) | picco 5,41 mA al contatto della massa (29 mW, un impulso) contro 0,25 W |
| R4 / R5 | 10 kΩ dai rail | 10 mW, 22,5 mW col rail a 20 V |
| C1 / C2 | 100 nF ceramici | l'LM4040 è stabile con qualunque carico capacitivo (p. 1, p. 40) |

**Perché il BAV199 e non il BAV99.** La corrente di dispersione, la differenza fra i due diodi, scorre
in R_SEL ‖ R_IN (320 kΩ) e mette una continua all'ingresso del blocco A. Col BAV199 al tetto del
datasheet (5 nA a 75 V; ~12 nA a 60 °C letti sulla curva massima della fig. 4) sono ~1,6–3,7 mV, una
continua fissa che non cambia col selettore (nessun gradino, NC-040); col BAV99 (30 nA max a 25 °C e
30 µA a 150 °C, ~0,2 µA a 60 °C per interpolazione) diventerebbero decine di mV. Il BAV199 ha la
capacità solo **tipica** (2 pF a 0 V) dove il BAV99 la garantisce (1,5 pF max): il suo costo si misura
qui sotto anche col doppio della capacità. Nessuna delle due differenze cambia una promessa del
contratto, e la scelta resta nel perimetro di ADR-101 («le parti si scelgono in L57b»): non serviva una
domanda all'utente.

**I modelli.** Per l'LM4040 il modello di TI a 5,0 V (SNOM508, grado B, l'unico non cifrato a 5 V),
adattato a ngspice in `models/voltage_reference/` con la provenienza e una ricetta in
`validate_models.py` (4,992 V a 100 µA, ZR 0,46 Ω contro 0,5 tip.). Per il BAV199 **nessun modello
del costruttore**: nexperia.com risponde 403. `models/diodes/bav199_fit.lib` è una stima dichiarata —
la capacità dalla fig. 5 letta a occhio (1,85 pF a 0 V, 1,10 a 5 V), la parte statica e la dispersione
del 1N4148 (3,91 nA a 5 V, un tetto). Se il modello di Nexperia arriva, si sostituisce e si rifà
il costo. I due datasheet di Nexperia vengono da uno specchio di terzi (dichiarato nella provenienza).

## 2. Il sorgente

- `circuits/preamp/input_limiter.py`, nuovo: `references()` una volta per la scheda (U1, U2, R4, R5,
  C1, C2) e `limiter()` per canale (R179 / D179, R379 / D379), con le sigle esplicite (limitations #22)
  e ADR-101 su ogni valore. Da solo scrive `spice/preamp/input_limiter.subckt`: `INLIM`, `INREF` e
  `INREF_EQ` (§4).
- `preamp_audio.py`: i COM dei quattro relè del selettore si incontrano su `L_SELCOM` / `R_SELCOM`, il
  limitatore va da lì all'ingresso del blocco A. Scheda audio **628 parti** (618 + 10).
- Il simbolo KiCad `Diode:BAV99` ha i numeri dei piedini del BAV199 (1 = A1, 2 = K2, 3 = il comune,
  datasheet p. 1) ma chiama 1 «K» e 2 «A», contro il suo stesso disegno: si cabla per numero, e lo
  dicono il sorgente, il controllo e il kit dello schematico.
- **Il controllo dei relè (2e)** verifica il limitatore per intento: dal nodo dei COM una sola 1 kΩ
  verso l'ingresso, sull'ingresso un solo BAV199 col comune, gli estremi su due LM4040 a shunt verso
  massa col verso giusto. Sei falsi su sei (`falsi/esito.txt`: diodo rovesciato, comune sbagliato, i
  due riferimenti rovesciati, la resistenza d'altro valore, la netlist di prima).
- **I disegni**: lo schema a blocchi ha il riquadro «LIMITATORE» fra selettore e blocco A, coi valori
  letti dalla netlist e le asserzioni sulle reti; lo schematico completo ha la R179 e il D179 sotto il
  quarto ingresso e i due riferimenti sotto il blocco AL (il kit ha un `dio_pair()` per numero di
  piedino, e `zref()` accetta un valore stampato altrove). Il 2d è caduto prima del disegno, come deve,
  e passa dopo: 628 su 628.
- I quattro deck canonici che modellano l'ingresso (`tb_e3_e5`, `tb_trim`, `tb_f1_selettore`,
  `tb_loop_blockA`) includono il limitatore generato fra il contatto del selettore e AIN.
- `run_tests.sh` **15 / 0**. Il 2g (`check_deck_refs.py`) è caduto sul primo deck che includeva un
  sottocircuito con un'istanza (`XU1`) e ora la sa leggere; un deck sabotato è ancora preso.

## 3. Il banco di L57a sul circuito generato

`script/limitatore.py` **prende** le righe della protezione dal subckt generato (il corpo di `INLIM`
con `SELCOM` → `NK`, e dei riferimenti) e `prova()` le confronta con `preamp_audio.net` dispositivo per
dispositivo, valori e reti: 9 su 9. `genera.py` e `dist.py` di L57a, copiati, le usano con
`--prot S[,rif=…][,dio=…]`: nessuna riga della protezione è scritta a mano.

**Il caso noto prima**: la topologia generata coi modelli del banco di L57a (il 1N4148 come BAV199,
riferimenti ideali a 5 V) ridà `r1k_lim5` di L57a: **256 celle su 256**. (Una prima corsa ne dava 240:
le 16 diverse erano la mia colonna `vin_rail_v` misurata contro i riferimenti invece che contro i rail,
10 V esatti; riportata alla definizione di L57a.)

**Col circuito** (BAV199 stimato, i riferimenti come `INREF_EQ`), caso peggiore in classe II
(`sintesi.csv`):

| | rete −10 % | nominale | rete +10 % | limite |
|---|---|---|---|---|
| gate-gate LSK489 | 4,32 V | 4,32 V | 4,33 V | 30 V |
| gate-drain | −14,7 V | −14,7 V | −14,7 V | 60 V |
| corrente di gate | 0,164 mA | 0,164 mA | 0,164 mA | 10 mA |
| corrente nel diodo | 0,99 mA | 1,07 mA | 1,15 mA | 140 mA |
| jack, posizione d'ascolto, 0 / +10 dB | 99,8 / 109,8 dB SPL | uguale | uguale | 112,2 dB SPL |
| volume in cima | clip (113,8) | clip | clip | (la musica lo fa già, ADR-101) |
| fisse sul picco del K11 | +3,4 dB | +3,4 dB | +3,4 dB | — |
| col mute inserito: 0 / +10 dB / cima | 77,0 / 82,5 / 105,3 dB SPL | uguale | uguale | 112,2 dB SPL |

Le cifre di ADR-101. Con la capacità del diodo raddoppiata le stesse (gate-gate 4,29 V). Il blocco è
vivo in ogni corsa: la sorgente a terra a 10 mV dà 10,3 mV al jack come il caso noto (la trappola del
blocco spento di L57a). I riferimenti si muovono al più di 1,5 mV durante l'evento (4,9933 V).

## 4. Il modello di TI dell'LM4040 non trova il punto di lavoro (limitations #76)

I deck del selettore coi riferimenti del modello di TI sono caduti: `.op` senza convergenza (gmin e
source stepping), un punto di ripiego col nodo a 0,566 V invece di 4,99, il transitorio fermo a ~92 µs
sul JFET del blocco A, e **un CSV scritto lo stesso**, con celle vuote e un gradino di 608 µV dove main
dà 6,3 µV (`regressione/dopo_ti/`). Lo stesso succede al riferimento da solo, dietro i suoi 10 kΩ
(`parti/lm4040_rif_*.log`); le ricette di `validate_models.py` lo pilotano con una sorgente di
corrente e passano. Il modello ha un condensatore d'avvio da 400 nF e 10 µH in serie all'uscita.

Nei deck e nei banchi i riferimenti sono quindi `INREF_EQ`, che `input_limiter.py` genera accanto a
`INREF`: le stesse R4 / R5 / C1 / C2, ogni LM4040 come la sua cifra di datasheet, 4,992 V dietro 1,1 Ω
(la ZR massima). Nel limitatore conduce al più ~2 mA: un errore di ~2 mV su una soglia di 5,6 V.
Dichiarato nel subckt, nei deck e nella limitazione.

## 5. Il costo al segnale (V4, E5)

Banco del costo di L57a (sorgente 2,5 kΩ, la fissa col carico di V4, il punto di lavoro vivo come
nodeset), con in più **10 kHz** e la **CCIF**, che V4 chiede e L57a non misurava (`costo/costo.csv`):

| | senza protezione | caso noto (L57a) | **circuito** | capacità doppia | tetto di V4 |
|---|---|---|---|---|---|
| THD 20 kHz, 0,2 V RMS | 0,000686 % | 0,000764 % | **0,000764 %** | 0,000764 % | 0,001 % (riaprire a 0,0009) |
| h5+ a 1 / 10 / 20 kHz, 0,2 V | −148,9 / −188,6 / −200,1 | −148,9 / −188,6 / −200,4 | **−148,9 / −188,6 / −200,2 dB** | −148,9 / −188,7 / −198,8 | ≤ −140 dB |
| h2 / h3 a 20 kHz, 0,2 V | −103,3 / −157,5 | −102,3 / −158,1 | **−102,3 / −140,7 dB** | −102,3 / −134,8 | lo spettro cala in ordine |
| CCIF 19 + 20 kHz | −134,4 dB | −133,6 dB | **−133,6 dB** | −133,6 dB | ≤ −110 dB |
| THD 20 kHz, 2 V RMS | 0,00685 % | 0,00765 % | **0,00772 %** | 0,00792 % | 0,01 % |
| THD 20 kHz, 2,7 V d'ingresso (E6) | 0,00923 % | 0,0103 % | 0,0106 % | 0,0112 % | — |
| E5 stimato per eccesso | 4,577 µV | 4,922 µV | **4,922 µV** | 4,922 µV | 9,95 µV |

Il diodo vero si vede solo nella terza armonica: la capacità del BAV199 varia di più di quella del
modello del 1N4148 (M 0,25 contro 0,025). A 0,2 V h3 a 20 kHz sale da −158 a −141 dB, a 2 V da −118 a
−100 dB; la THD non cambia alla terza cifra e lo spettro resta ordinato (h2 > h3 > h5+). Il rumore
aggiunto è il termico della 1 kΩ (0,574 µV all'uscita del blocco A). Il rumore dei due LM4040 (80 µV RMS
tipici, 10 Hz–10 kHz, p. 26) non è nel banco: arriva all'ingresso attraverso ~1,1 pF di un diodo in
inversa su ~3,5 kΩ (la sorgente e la 1 kΩ), al più 2π·10 kHz·1,1 pF·3,5 kΩ ≈ 2,4·10⁻⁴, ~19 nV a
diodo; due diodi in quadratura e il guadagno peggiore (×3,152) danno ~86 nV al jack, che sommati in
quadratura ai 4,922 µV di E5 non cambiano la terza cifra.

## 6. Regressione dei deck canonici

`regressione/verdetti.csv`, prima (main) → dopo:

| | prima | dopo | limite |
|---|---|---|---|
| V1, margine di fase del blocco A (CWIRE ≤ 1 nF, ADR-024) | 68,12° | **67,81°** | ≥ 45° |
| E3, \|Zin\| minima al jack (CSEL 68 pF) | 108,2 kΩ | **105,3 kΩ** (102,5 con la capacità doppia) | ≥ 100 kΩ |
| E5, rumore massimo dei deck | 5,102 µV | **5,413 µV** | ≤ 9,90 µV |
| F1, gradino massimo al cambio d'ingresso | 139,9 µV | 139,8 µV | (ADR-064) |

Nessun ripiego in più nei log (gli avvisi di gmin stepping sono quelli di main). **E3 cambia**, contro
quello che il prompt si aspettava: non per la 1 kΩ in serie, dopo R_SEL, ma per i ~2,2 pF dei due
diodi in inversa sull'ingresso, che a 20 kHz si sommano ai 68 pF del selettore (−2,7 %). Resta sopra i
100 kΩ; col doppio della capacità tipica il margine è il 2,5 %.

## 7. I «Da riaprire se» di ADR-101

- THD a 20 kHz a 0,2 V sopra lo 0,0009 % o la regressione fuori da V4, V1, E5: **no** (0,000764 %;
  V4, V1, E5 dentro).
- E6 sopra ~3,5 V RMS: no, invariato.
- Più di 0,25 mA di corrente di contatto da una sorgente reale: non misurato (non c'è un prototipo).
- Un manuale senza l'avviso del mute: non c'è ancora un manuale.

Nessuno scatta. **NC-059 si chiude**: il rimedio è nel sorgente, la parte torna nei suoi limiti alle tre
reti, il jack sta sotto il tetto alla posizione d'ascolto, e il costo sta dentro V4 ed E5.

## 8. Fuori da questo lotto, da non perdere

- **Le righe della FMEA delle dieci parti nuove** non ci sono (la FMEA di NC-042 / ADR-100 è chiusa
  sulle parti di allora). Due modi meritano attenzione: un LM4040 **aperto** porta il suo nodo al rail
  attraverso i 10 kΩ e il limitatore sale a ~15,6 V **in silenzio** (la protezione persa senza un
  sintomo); un diodo del BAV199 **in corto** mette l'ingresso del blocco A a ±5 V di continua. Da
  portare in L58 (la diagnosi) o nella revisione; non è stato misurato.
- Il modello di Nexperia del BAV199: con quello si rifà il costo (§5).

## Limiti dichiarati

- Il BAV199 è una stima dal datasheet (capacità tipica letta a occhio, dispersione del 1N4148); i
  riferimenti nei banchi sono la cifra di datasheet, non il modello del costruttore (#76).
- Le ipotesi della sorgente sono quelle di L53 / L57a. Nessuna cifra è una misura su un prototipo.
