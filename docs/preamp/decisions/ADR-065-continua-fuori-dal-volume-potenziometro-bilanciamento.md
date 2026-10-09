# ADR-065 — La continua fuori dal volume: C_T 10 µF fra trim e volume, R_G 1 MΩ sul gate del blocco B, il volume a potenziometro col bilanciamento MN, i canali entro 1 dB

Data: 2026-10-07 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera ADR-009 sul solo volume**: «attenuatore a scatti» diventa un potenziometro (ALPS RK27
  10 kΩ log), con un bilanciamento davanti. ADR-009 aveva scartato l'RK27 per i ±2 dB fra i canali:
  il bilanciamento è la risposta a quell'obiezione. Niente telecomando, ingressi a relè: invariati.
- **Cambia PR-10, PR-16, PR-19 e PR-20** del PRB, firmati dall'utente il 2026-10-07 («Firmo così»),
  e con loro **E10** (precisato da ADR-053), **F4** ed **F10** (ADR-028: una manopola in più).
- **Applica ADR-007** al condensatore nuovo: polipropilene, nessun servo.
- **Precisa ADR-027**: il trim resta com'è; ora è caricato dal volume e dal bilanciamento attraverso
  C_T (8,33 kΩ invece di 10 kΩ), −6,08 / −12,00 dB, dentro ±0,1 dB.
- **Chiude NC-041** (con la misura sul circuito nuovo e il volume nel banco di V2).

## Contesto

NC-041 (rilievo R3 dell'architetto, L43a): fra l'uscita del blocco A e il blocco B non c'era nessun
condensatore. La continua del blocco A (−6,6 mV nominali da ADR-056, fino a ±30 mV con la
dispersione dei pezzi) attraversava la scala del trim e l'attenuatore, e ogni scatto del volume
lasciava un gradino al jack, mentre PR-20 non elencava il volume fra gli eventi. Il rimedio
indicato nella voce, un condensatore all'ingresso del blocco B, secondo un calcolo di L48a non
toglieva il gradino.

## Decisione

Le risposte dell'utente (2026-10-07, domande per nome e in dB SPL, coi numeri misurati prima):

1. **«Tutto in questa sessione»** (L48b non si divide).
2. **«Fra trim e volume, film 10 µF»**: C_T 10 µF in polipropilene fra il COM del trim (T1) e il
   pin alto del cablaggio del volume (C265 / C465). Dopo la domanda «non ho mai sentito parlare di
   68 µF sul segnale»: il valore lo decide l'impedenza dopo il condensatore (1,5 kΩ prima del trim,
   10 kΩ prima del volume), e Self raccomanda 47 µF su 10 kΩ per lo stesso motivo.
3. Il volume: il commutatore a scatti cortocircuitante (Elma 04, Seiden, ~140–180 €) è **«troppo
   caro, da solo costa come 1/4 della scheda audio, dobbiamo usare un buon potenziometro non a
   scatti e se la precisione tra i canali può risultare udibile a 4 m e volumi di ascolto normali,
   spostando l'immagine, dovremo introdurre un balance»**.
4. **«Sì, 1 MΩ»**: R_G 1 MΩ dal cursore (gate del blocco B) a massa, R265 / R465.
5. La soglia fra i canali: **«1 dB»** (circa 2,5° di spostamento dell'immagine con la base a ±30°).
6. **«ALPS RK27 + bilanciamento»**.
7. **«Curva MN, 0 dB al centro»**: un potenziometro doppio di bilanciamento con curva MN (Alpha
   RV16 MN 50 kΩ con lo scatto al centro), usato come partitore fra C_T e la cima del volume. Al
   centro ogni sezione lascia passare tutto, senza resistenza in serie; girandolo attenua un solo
   canale, ~1 dB ogni ~16°.

Volume e bilanciamento stanno sul pannello: sulla scheda resta il connettore a tre fili (J120 /
J320, ora `VOL_L` / `VOL_R`), cima dopo C_T, cursore, massa.

## Perché

Misure di L48b (`docs/preamp/data/2026-10-07/L48b/`), dB SPL di picco a 1 m con la catena di
NC-028 (100 µV ≈ 33 dB SPL):

- **Lo scatto del volume in cima alla corsa** (da 0 a −2 dB), +10 dB, banco dedicato:

  | Strada | nominale (−6,6 mV) | peggiore (±30 mV) |
  |---|---|---|
  | oggi | 4,30 mV · 66 dB SPL | 19,5 mV · 79 dB SPL |
  | condensatore all'ingresso del blocco B (1 µF + 1 MΩ) | 4,29 mV · 66 | 19,4 mV · 79 |
  | 47 / 68 / 100 µF prima del trim | ≤ 0,002 µV | ≤ 0,002 µV |
  | **10 µF fra trim e volume, circuito finale** | **≤ 0,05 µV** | **≤ 0,05 µV** |

  Il condensatore all'ingresso del blocco B non toglie il gradino: la continua del cursore salta e
  il salto passa il condensatore. Il calcolo di L48a è confermato dalla misura.
- **Nel banco di V2** (gruppo 6, uno scatto per guadagno, dispersione peggiore): sotto a ogni
  guadagno, 19,6 µV a +10 dB col difetto noto del banco (VOSB, limitations #44, prudente) e
  **9,2 nV** senza. La matrice intera: vedi il report di L48b.
- **Il trim** porta ancora la continua (sta prima di C_T), ma si cambia solo in mute (PR-17), e il
  suo gradino decade in C_T con τ ≈ 0,1 s. Nel banco di V2, col mute rilasciato 0,5 s dopo il
  cambio, il jack principale vede **3,6 / 5,3 µV** (0→−6 / 0→−12 dB, dispersione peggiore).
- **E9**: −0,045 dB a 20 Hz su tutta la catena col cj da 100 kΩ (−0,175 dB col finale futuro da
  10 kΩ). **E5**: peggiore 5,496 µV al centro del bilanciamento (invariato), **5,60 µV** girato di
  3 dB. **V1**: ≥ **64,42°** con 5,6 kΩ di sorgente, il caso peggiore del bilanciamento (65,16° a
  2,611 kΩ, come L46b). **E3**: 108,2 kΩ, invariato.
- **R_G 1 MΩ**: un cursore che si stacca lascia il gate su R_G invece che sospeso. Con la corrente
  di gate del datasheet dell'LSK489 (−2 pA tipica, −25 pA massima a 25 °C) il gate si ferma a
  I_G · R_G: 9,5 dB SPL tipici, 31 dB SPL massimi a 25 °C, ~50 dB SPL nella stima a caldo; senza
  R_G, 1 ms di cursore aperto dava 29 / 51 / ~69 dB SPL. Il carico sul volume è ~0,02 dB.
- **La soglia di 1 dB**: le curve di localizzazione di Sengpiel (25 ascoltatori) danno 3 dB → 25 %
  della semibase, ~2,5° per dB al centro con la base a ±30°; l'angolo minimo udibile davanti è
  ~1° (Mills, 1958), in condizioni ideali. A 4 m conta l'angolo sotto cui si vedono i diffusori:
  con una base più stretta lo spostamento per dB è minore.
- **Il potenziometro**: l'ALPS RK27 dichiara ≤ 2 dB fra i canali da 0 a −60 dB (il TKD CP-2500
  ≤ 3 dB); nessun potenziometro del commercio trovato garantisce 1 dB. Il bilanciamento lo corregge
  alla posizione d'ascolto.

## Alternative scartate

- **Il condensatore all'ingresso del blocco B** (il rimedio di NC-041): misurato, non toglie il
  gradino.
- **68 µF prima del trim**: toglie la continua anche dal trim, ma il film è grande e l'utente l'ha
  trovato improbabile; il trim si muove solo in mute.
- **Un elettrolitico bipolare prima del trim**: contro ADR-007.
- **Il commutatore a scatti cortocircuitante**: troppo caro (~140–180 €).
- **Il bilanciamento lineare in serie (RK27 doppio lineare)**: ~1,9 dB di perdita comune al centro,
  contro E1 (0 dB).
- **Il servo di continua**: escluso da ADR-007.

## Da riaprire se

- il potenziometro montato mostra al prototipo più di ~3 dB fra i canali in qualche posizione
  d'ascolto (il bilanciamento non basterebbe col suo passo);
- la pista in carbone del bilanciamento si rivela rumorosa all'ascolto;
- si vuole cambiare il trim fuori mute (porta ancora la continua);
- il finale futuro ha meno di 10 kΩ d'ingresso (E9 a 20 Hz scende verso −0,2 dB).
