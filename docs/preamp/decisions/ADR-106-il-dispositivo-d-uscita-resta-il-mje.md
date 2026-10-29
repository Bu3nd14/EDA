# ADR-106 — Il dispositivo d'uscita del blocco resta il MJE15032 / MJE15033

Data: 2026-10-29 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Conferma ADR-016 / ADR-017** (i finali MJE15032 / MJE15033 col modello del costruttore), **ADR-054**
  (il VAS a ~10,7 mA, il Miller a 470 pF) e **ADR-099** (il dissipatore Ohmite WA-T220-101E): nessun
  valore del sorgente cambia.
- **Chiude NC-056** (L52, rilievo R6 dell'architetto avversariale): il driver di taglia intermedia che
  ADR-054 non aveva valutato è stato provato sul banco del blocco, e l'utente ha deciso.
- **Non scatta il «Da riaprire se» di ADR-054** sulla f_T dei MJE (si misura sul prototipo).

## Contesto

L55 (`data/2026-10-29/L55/`, README; report `reports/2026-10-29-L55-dispositivo-uscita.md`). Il MJE
è un 8 A / 250 V a ~20 mA, con la CJE del modello a 3,06 nF. Il candidato è l'unico che regge T7 e T8 fra
quelli vagliati (`modelli/README.md`): **onsemi MJE243G / MJE253G**, TO-225, modelli serviti da onsemi
(`models/bjt_npn/mje243.lib`, `models/bjt_pnp/mje253.lib`, ricetta in `validate_models.py`, 89 / 89),
«Active». A 20 mA la Cpi di piccolo segnale scende da 8,1 / 7,8 nF a 1,7 / 2,2 nF, la f_T sale da 12 a
61–88 MHz. Criteri scritti prima delle corse (`CRITERI.md`); ogni banco col suo caso noto sul MJE di oggi.

Il modello del MJE253 ha **VJC = 0,033 V**: con la scala SPICE della temperatura va sotto zero a ~35 °C e
la `tran` non parte (limitations #82). Le cifre a caldo del candidato sono state prese con le capacità di
giunzione ferme a 27 °C (`TLEVC`), metodo provato sul MJE: cifre identiche col congelamento e senza.

## Decisione

Parole dell'utente (2026-10-29), alla domanda coi numeri: **«MJE as it is»**. Il MJE15032 / MJE15033
resta, col Miller a 470 pF e il WA-T220-101E. I modelli del candidato restano in `models/` con la loro
ricetta, come quelli dei ZXT di ADR-054.

## Perché

Le tre opzioni, ricontate dai CSV (`script/tabella_opzioni.py`); a caldo = aria 57 °C, il peggiore fra il
dissipatore e il moltiplicatore accoppiato; i finali con 60 °C d'aria. **Tutte e tre stanno dentro ogni
limite.**

| | **MJE (scelto)** | candidato, 470 pF | candidato, 330 pF |
|---|---|---|---|
| margine di fase peggiore (≥ 60°) | 64,92° | 69,83° | 67,69° |
| THD 20 kHz a 0,2 V a caldo (≤ 0,001 %) | 0,000726 % | 0,000719 % | 0,000604 % |
| margine peggiore della distorsione | 2,7 dB | 2,8 dB | 4,2 dB |
| THD 20 kHz a 2 V a caldo (≤ 0,01 %) | 0,00735 % | 0,00729 % | 0,00613 % |
| intermodulazione a caldo (≤ −110 dB) | −131,7 dB | −132,2 dB | −137,0 dB |
| rifiuto del rail + a 1 / 10 / 20 kHz | 85,0 / 85,5 / 84,3 dB | 85,3 / 85,3 / 84,5 dB | 88,3 / 88,2 / 87,3 dB |
| slew in discesa | −5,92 V/µs | −6,16 V/µs | −8,23 V/µs |
| finali nei due corti (≤ 125 °C, max 150) | 99 / 95 °C | 113 / 106 °C | 113 / 106 °C |
| finali a riposo / in P7 | 67 / 70 °C | 69 / 73 °C | 69 / 73 °C |
| dissipatore che serve per 125 °C | ≤ 35,9 °C/W (20 di catalogo) | ≤ 28,4 °C/W (TV4: 21, **dal distributore**) | come a sinistra |

Il candidato col Miller di oggi compra solo margine d'anello; col Miller a 330 pF compra 1,5 dB di
distorsione e 5 dB d'intermodulazione, a cifre già 2,7 dB e 21,7 dB dentro i tetti. Il prezzo: un
contenitore nuovo e sedici dissipatori Boyd TV4 la cui curva del costruttore non si è trovata, i finali
nei corti 14 °C più caldi, R128 e C124 da cambiare, la FMEA dei finali da rifare, e un modello del PNP che
non vale sopra ~35 °C proprio dove il telaio lavora. NC-056 era minore: «oggi i numeri reggono», e lo
confermano.

## Alternative scartate

- **Il candidato col Miller a 330 pF**: sopra; il guadagno di distorsione c'è, su cifre già dentro.
- **Il candidato col Miller di oggi**: la distorsione del MJE, i costi del candidato.
- **Il candidato col Miller a 220 pF**: margine di fase del blocco A 59,54°, sotto i 60°.
- **Le altre coppie vagliate** (`modelli/README.md`): Toshiba TTC004B / TTA004B, TTC015B, TTA008B «Not
  Recommended for New Design» (T8); MJE182 / MJE172 col modello a Vbe 0,92 V a 20 mA; MJD243 senza il
  PNP; MJE340 / MJE350 con capacità a cifre tonde e senza f_T nel datasheet; D44H11 / D45H11 e MJD44H11 /
  MJD45H11 con capacità come il MJE; ZXTN / ZXTP19060CG col PNP senza scorte e 42 °C/W.

## Da riaprire se

- Sul prototipo il margine di fase o la distorsione a 20 kHz a caldo escono dai limiti col MJE: il
  candidato col Miller a 330 pF è il primo da provare (le varianti stanno in `data/2026-10-29/L55/`).
- Il MJE15032 / MJE15033 esce di produzione o il WA-T220-101E non si trova (ADR-099).
- onsemi pubblica un modello del MJE253 con VJC fisica: le cifre a caldo del candidato si rifanno senza
  il congelamento.
