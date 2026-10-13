# ADR-067 — Lo specchio d'ingresso fuori dal ginocchio: un inseguitore davanti al VAS e un transistor di aiuto sullo specchio

Data: 2026-10-12 · Stato: accettata

## Contesto

NC-060 (bloccante per G1, L53): lo specchio dello stadio d'ingresso del blocco di guadagno (Q121,
LS352, modello del costruttore LS350 con RC 231 Ω) lavorava sull'orlo della saturazione, e col
calore vero dei dispositivi la distorsione a 20 kHz usciva da V4 in 48 casi su 48. L56 ha misurato
le strade col blocco a ogni giunzione alla sua temperatura, **iterata fino a convergenza** (L53 si
fermava al primo passo e sottostimava il calore), a 27 e 57 °C d'aria e a 27 °C uniformi (report
`reports/2026-10-12-L56-specchio.md`, dati `data/2026-10-12/L56/`).

Il meccanismo, misurato e non supposto: l'RC del modello tiene in conduzione la giunzione
base-collettore interna di **entrambe** le metà dello specchio. Il lato a diodo (collettore e base
uniti) lo è di Ic·RC ≈ +0,51 V sempre; il lato d'uscita di +0,42 V, fissato dalla Vbe del VAS. A
27 °C le due quasi-saturazioni si compensavano (intermodulazione −125,6 dB); il calore alza la coda
(Q106 più caldo dei diodi che lo polarizzano: 4,51 → 4,84 mA) e rompe l'equilibrio.

## Decisione

**Un inseguitore di emettitore PNP (MMBT5401) fra l'uscita dello specchio e la base del VAS, e un
transistor di aiuto PNP (MMBT5401) che pilota le basi dello specchio dal collettore del lato a
diodo; R120 torna a 220 Ω.** In ogni istanza del blocco. Decisione dell'utente del 2026-10-12:
«Inseguitore + aiuto» fra quattro strade in tabella.

Nel sorgente: Q146 (inseguitore, base su NHI, emettitore su NVB, la base del VAS) con R147 1,2 kΩ da
VPF; Q148 (aiuto, base su NMIRC, il collettore del lato a diodo e del cascode Q118, emettitore sulle
basi dello specchio) con R149 10 kΩ da VPF. **I collettori dei due al rail negativo**, non a massa:
la corrente dell'inseguitore porta la corrente di base del VAS, cioè segnale, e non deve tornare
nella massa di segnale (scelta mia, misurata: distorsione identica, reiezione del rail negativo a
100 Hz / 1 kHz 95,4 / 95,0 dB contro 99,7 / 104,9 a massa e 76,2 / 86,3 prima di L56). Le parti
nuove stanno in coda alla funzione (limitations #22): nessun designatore esistente cambia numero.

## Perché

Le due metà dello specchio, giunzione base-collettore interna (positiva = in conduzione):

| | Q121A (lato a diodo) | Q121B (lato d'uscita) |
|---|---|---|
| prima, 27 °C uniformi | +0,51 V | +0,42 V |
| **dopo**, 27 °C uniformi | **−0,04 V** | **−0,18 V** |
| dopo, aria 57 °C | +0,05 V | −0,02…−0,03 V |

Col blocco a ogni giunzione alla sua temperatura (VAS 86–122 °C nel SOT-23, coda 55–85 °C), 3 modi
× sorgente 2,5 / 5,6 kΩ × 0,2 / 2 V a 20 kHz, e l'intermodulazione CCIF a 0,2 V (tetto −110 dB;
~99 dB SPL a 1 m, quindi il prodotto in dB SPL è 99 meno il margine):

| Strada | fuori da V4 (aria 27 / 57 °C) | margine peggiore | intermodulazione a 57 °C | gradino della coda |
|---|---|---|---|---|
| oggi | 12 / 12 su 12 | −39 dB | −61 dB (≈ 38 dB SPL) | già oltre (−4,6 %) |
| **inseguitore + aiuto** | **0 / 0** | **+2,7 dB** | **−131,8 dB** (sotto −30 dB SPL) | **oltre +24 %** |
| solo inseguitore | 4 / 4 su 12 | −3,8 dB | −97 dB (≈ 2 dB SPL) | oltre +24 % |
| R123 100 Ω, o un diodo in serie alla base del VAS | 4 / 6 su 12 | −4,7 dB | −96,5 dB | oltre +24 % |
| specchio a 100 Ω | 10 / 12 su 12 | −9,3 dB | −91 dB | oltre +24 % |
| coda più bassa (R107 150 Ω) | 0 / 10–12 su 12 | −15,5 dB | −88 dB | +4 % |
| diodi della coda accoppiati a Q106 (limite) | 9–12 / 12 su 12 | −31 dB | −70 dB | — |
| solo aiuto | 12 / 12 su 12 | −38,6 dB | −63 dB | già oltre |

- **Perché tutte e due le metà.** Dare tensione al solo lato d'uscita toglie il gradino ma lascia
  un secondo ordine di −105 dB a +10 dB, che **resta dell'RC** (con RC = 0: −134,5 dB), non è
  l'effetto Early (VAF 1000 V: uguale) né il bilanciamento (R120 205–240 Ω: 0,2 dB/Ω, nessun
  minimo), e non cala con più polarizzazione inversa (inseguitore + R123 100 Ω, due diodi,
  R123 150 Ω: tutti −105 dB). Viene dal lato a diodo, rimasto in conduzione da solo.
- **Le cifre a 27 °C uniformi, sul banco di L46b**, il blocco generato: THD a 20 kHz a 0,2 V
  0,00045 % (prima 0,00060), a 2 V 0,0045 % (0,0068), intermodulazione −138,5 / −138,3 /
  −132,1 dB (−130,8 / −130,7 / −125,6); margine di fase V1 65,16 / 73,29 / 105,11° a 0 / +3 /
  +10 dB, blocco A 68,38°, trim 73,36°, buffer 65,31° (prima 65,16 / 73,56 / 105,08 / 68,50 /
  73,32 / 65,37); reiezione del rail positivo a +10 dB 85,0 / 85,5 / 84,3 dB a 1 / 10 / 20 kHz
  (79,7 / 78,5 / 75,8); rumore E5 peggiore 5,10 µV (5,50); continua all'uscita −2,9 mV (−6,6);
  slew −5,9 V/µs (−3,75); impedenza al nodo del blocco a 1 kHz 0,041 Ω (0,082).
- **R120 a 220**: i 6 Ω in più di ADR-056 compensavano la corrente di base del VAS (~83 µA) che
  entrava in NHI. Ora entra nell'inseguitore: con 226 Ω il blocco starebbe a +17,0 mV.
- **Il valore delle due resistenze**: 1,2 kΩ e 2,2 kΩ per l'inseguitore, 4,7 / 10 / 22 kΩ per
  l'aiuto danno le stesse cifre alla terza cifra; 1,2 kΩ (~1,1 mA) per avere corrente di riserva
  sulla base del VAS, 10 kΩ (~0,13 mA) per l'aiuto.
- **Costi**: per blocco due MMBT5401 in SOT-23 (33 mW e 4 mW) e due resistenze; +1,27 mA per rail,
  +38 mW; ×8 istanze: 16 transistor, 16 resistenze, +10 mA per rail sull'alimentatore. Clip in
  continua a +10 dB 55 mV più basso (~0,04 dB del margine di 0,73 dB su E6 × E2).

## Alternative scartate

- **Solo l'inseguitore, una R123 più grande, un diodo in serie alla base del VAS**: tolgono il
  gradino ma restano fuori da V4 a caldo (sopra).
- **Lo specchio meno degenerato (R119/R120 150 o 100 Ω)**: peggio, e il rumore sale (L22).
- **La coda più bassa**: dentro a 27 °C d'aria, fuori a 57 °C.
- **L'accoppiamento termico della coda ai suoi diodi**: anche come limite perfetto non basta da solo.
- **Wilson o cascode sullo specchio**: chiedono più tensione allo specchio, non meno; non provati
  perché la tabella non li giustificava.
- **Collettori di inseguitore e aiuto a massa**: la corrente di base del VAS nella massa di segnale.

## Cosa precisa

- **ADR-056**: la cella RC resta; R120 torna da 226 a 220 Ω, perché la causa dei 6 Ω è sparita.
- **ADR-054**: VAS a ~10,7 mA e Miller 470 pF restano.
- **ADR-018**: l'LS352 resta. Il ginocchio è dell'RC del suo modello; sul prototipo la cifra vera.

## Da riaprire se

- Sul prototipo lo specchio misurato (Vce di saturazione dell'LS352 a 2,2 mA) è molto più duro del
  modello: l'aiuto resta utile ma va riletto il suo costo.
- La misura della distorsione sul prototipo a caldo non segue il modello (il gradino della coda,
  la seconda armonica a 20 kHz): si torna a questa tabella.
- L55 (il dispositivo d'uscita) cambia lo stadio d'uscita o il VAS: margine di fase e corto vanno
  rifatti su questo blocco.
