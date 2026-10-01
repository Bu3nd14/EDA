# ADR-056 — La cella RC su specchio e VAS, e R120 a 226 Ω

Data: 2026-10-01 · Stato: accettata

## Contesto

NC-047 (bloccante per G1), il rilievo dell'utente: «Temo che l'alimentatore non riuscirà ad essere
abbastanza silenzioso e quindi dovremo mettere mano al circuito audio per aumentare la PSRR.» Col
blocco di ADR-054 il PSRR+ a +10 dB valeva 66,9 / 49,5 / 29,5 / 23,5 dB a 100 Hz / 1 / 10 / 20 kHz,
~50 dB sotto il rail − a 10 kHz. Il rail + entra perché specchio d'ingresso e VAS stanno sul rail e
C124 porta in uscita il moto della base del VAS (per questo il PSRR+ seguiva il Miller, L46a).
L46b ha misurato le strade sullo stesso banco di L46a (report
`reports/2026-10-01-L46b-psrr-rail-positivo.md`, dati `data/2026-10-01/L46b/`).

## Decisione

**Una cella RC per blocco, 10 Ω dal rail + a un nodo `VPF` e 1000 µF da `VPF` a massa, alimenta
lo specchio d'ingresso (R119, R120) e il VAS (R123); R120, la degenerazione del lato d'uscita dello
specchio, passa da 220 a 226 Ω.** In tutte e otto le istanze; l'alimentatore resta com'è (ADR-048).
Decisioni dell'utente del 2026-10-01: la cella fra quattro strade in tabella; R120 dopo che la
ricorsa dei guasti all'alimentatore ha mostrato un margine sottile.

## Perché

**La cella.** Peggiore sui tre modi; ESR del condensatore 0,05 Ω (ipotesi dichiarata, prudente: in
alta frequenza l'attenuazione tende a R / ESR):

| | ADR-054 | **ADR-056** |
|---|---|---|
| PSRR+ a 100 Hz / 1 / 10 / 20 kHz | 66,9 / 49,5 / 29,5 / 23,5 dB | **79,0 / 79,5 / 71,7 / 66,2 dB** |
| PSRR+ a 100 kHz (fuori banda) | 10,7 dB | 52,6 dB |
| PSRR− a 50 / 100 Hz | 65,6 / 70,7 dB | **71,3 / 76,2 dB** (R120) |
| ADR-020 sul limite per eccesso dei rail | 0,51 µV, −13 dB SPL a 1 m | **0,098 µV, −27 dB SPL** |
| margine sulla quota di 1 µV | 5,9 dB | **20,2 dB** |
| di quanto può peggiorare il rail + prima di sforare | 6,3 dB | **37,5 dB** |
| clip positivo a +10 dB / margine su E6 × E2 | 13,28 V / 0,82 dB | 13,14 V / 0,73 dB |
| V1 minimo / gruppo B di I_DSS | 64,94 / 65,13° | **65,16 / 65,36°** |
| THD 20 kHz a 0,2 V / IMD CCIF / a 2 V | 0,00059 % / −119,2 dB / 0,0070 % | 0,00060 % / **−125,6 dB** / 0,0068 % |
| E5 peggiore | 5,10 µV | 5,08 µV |

- **Specchio e VAS sullo stesso nodo, non uno solo.** Filtrare solo lo specchio dà −12 dB di PSRR+,
  solo il VAS 47 dB: la differenza fra i due rail cade fra base ed emettitore del VAS.
- **Sul solo alimentatore la quota reggeva** (0,51 µV, sul limite per eccesso dai datasheet dei
  regolatori: il modello TI del TPS7A4701 non ha rumore), ma con 6 dB di tolleranza su tutto ciò
  che il datasheet non contiene: cablaggio, masse, un regolatore peggiore del tipico. La cella la
  porta a 37,5 dB.
- **10 Ω e non 22 o un moltiplicatore**: 22 Ω compra 3 dB di tolleranza per 0,12 dB di clip, il
  moltiplicatore 6 dB per 0,53 dB di clip e il doppio delle parti. Un elettrolitico generico (ESR
  0,2 Ω) dà ancora 62,7 dB a 10 kHz: il low-ESR non serve.
- **Costi**: 16 parti (otto 10 Ω, otto 1000 µF ≥ 25 V), ~2 mW per blocco; τ = 10 ms, sotto la
  rampa di ~1,4 s del TPS7A4701 (C_NR 10 µF): ~0,16 A di carica contro 1,26 A di limite.

**R120.** La ricorsa della catena di L41c ha mostrato che **ADR-054**, non la cella, aveva eroso
due guasti (L46a non l'aveva ricorsa): U502 spento 1,37 → 1,93 mV al jack (obiettivo 2 mV), il corto
della linea a 12 V dei relè 69,4 → 117 mV (ADR-051). Il meccanismo: i relè del guadagno cadono
prima del jack, e al jack arriva il salto della continua d'uscita del blocco, −26 mV × 3,15 → −26
mV. La continua è la corrente di base del VAS (83 µA) che sbilancia la coppia. R120 226 Ω la porta a
**−6,6 mV** (~3,2 mV per ohm): U502 spento **0,90 mV**, il corto **29,7 mV** (~83 dB SPL), il
controfattuale senza Δ 29,7 mV (fallisce, come deve, e ora arriva in fondo), perdita di rete ≤ 0,09
µV, spegnimento 13 nV. R119 e R120 all'1 %, stessa serie: un errore dell'1 % sul rapporto vale ~7 mV,
sotto il VGS1−VGS2 dell'LSK489 (8 mV tipici, 20 massimi) e la dispersione di β del VAS (−36…+6 mV
per hFE 60–250, stima).

## Alternative scartate

- **Solo l'alimentatore**: 6,3 dB di tolleranza sul rail +, verifica tutta sul prototipo.
- **Cella 22 Ω + 1000 µF**: 40,8 dB di tolleranza, margine di clip 0,61 dB.
- **Moltiplicatore di capacità**: 43,8 dB, margine di clip 0,29 dB, 32 parti.
- **Cella sul solo specchio o sul solo VAS**: peggio di niente (sopra).
- **Anche il riferimento del cascode sulla cella**: nessuna differenza, è già filtrato a ~1 Hz.
- **2200 µF**: +0,3 dB a 10 kHz (comanda l'ESR), condensatore più grande.
- **Il Miller più piccolo coi ZXT (opzione B di ADR-054)**: il suo «Da riaprire se» chiedeva un
  rimedio del PSRR+ che stesse nella quota; questo ci sta con 20 dB.
- **R120 229 Ω (E192)**: ~+3 mV invece di −6,6; il β del prototipo sposta comunque l'offset.

## Cosa precisa

- **ADR-020**: il rimedio sta nel blocco, l'alimentatore lineare di ADR-048 resta; i limiti per
  tono ricalcolati in `REQUIREMENTS.md`.
- **ADR-051**: la decisione resta; la cifra del corto è 29,7 mV, non 69,4.
- **ADR-054**: i valori restano; la continua d'uscita del blocco non è più −26 mV ma −6,6.

## Da riaprire se

- Sul prototipo l'offset d'uscita del blocco esce dalla finestra che L48 (NC-041) fisserà per trim e
  volume: R120 si ritocca, o si passa a un circuito che non dipenda dal β del VAS.
- Il ripple o il rumore misurato del rail negativo, che ora comanda la quota, si avvicina al limite.
- Il margine di clip su E6 × E2 diventa il vincolo stringente (oggi 0,73 dB).
- V2 del mute (L47) mostra che la cella o R120 cambiano S o A.
