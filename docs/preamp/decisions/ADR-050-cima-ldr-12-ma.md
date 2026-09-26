# ADR-050 — La cima della tabella delle LDR a 12 mA, a ogni temperatura

Data: 2026-09-26 · Stato: accettata

## Contesto

NC-038 (L41b1): il LED della VTL5C4 regge 40 mA a 25 °C, declassati di 0,9 mA/°C sopra 30 °C
(`vendor/optocoupler/excelitas/VTL5C3_VTL5C4`, valori massimi assoluti). Il profilo v4 di
ADR-039 chiede 20 mA per un tempo indefinito in due punti: alla serie in ascolto (d = 0) e alla
derivazione in mute (d = 1).

| Temperatura | Massimo del LED |
|---|---|
| 45 °C | 26,5 mA |
| 52,2 °C | 20 mA |
| 58 °C (il telaio chiuso di ADR-048) | 14,8 mA |
| 60 °C (il limite di ADR-021) | 13 mA |

Il circuito non cambia: la cima è una riga della tabella del firmware.

## Decisione

**Dell'utente**, il 2026-09-26, fra quattro strade portate coi numeri:

1. **la cima della tabella è 12 mA a ogni temperatura, su tutte e due le stringhe**: la serie a
   d = 0 e la derivazione a d = 1.
   - Il resto del profilo v4 non cambia: 0,2 mA a d = 0,1, 4,5 µA a d = 0,45, 0,19 µA a d = 0,75,
     10 nA di riposo.
   - La derivazione resta log-lineare da 10 nA (d = 0,5) alla cima. Il suo punto a d = 0,75
     diventa √(10 nA · 12 mA) = 10,95 µA invece di 14,1 µA.

**Di progetto** (L41b2, non dell'utente):

2. **la calibrazione legge a 12 mA e a 2 mA**. Nella domanda all'utente il secondo punto era
   scritto «1,2 mA». Resta 2 mA (ADR-049) perché sui 10 Ω sono 20 mV, 37 passi dell'ADC col
   riferimento di 0,55 V, invece di 12 mV e 22 passi.
3. **Il fit della calibrazione usa come ascissa la corrente letta**, non quella voluta. La
   caduta ohmica avviene alla corrente che scorre. Con l'ascissa di L41b1 (quella voluta), una
   pianta esattamente lineare lasciava −0,38 dB alla cima (`test_sequenze`). Il banco di L41b1
   dava −0,92 dB anche per questo.
4. **Il firmware legge lo zero di ogni pin di corrente** mentre la sua stringa sta a 10 nA
   (0,1 µV sui 10 Ω), e lo sottrae.
   - Così si tolgono l'offset dell'ADC e la perdita del pin attraverso i 47 kΩ. Da soli costavano
     fino a ±0,95 dB, e −2,06 dB con 50 nA di perdita.
   - Il sensore di temperatura (±3 °C tipici) resta: da solo vale ±0,83 dB al ginocchio del buio.

## Perché

**Il margine.** A 60 °C il LED regge 13 mA: 12 mA lascia l'8 %. Sotto ~52 °C il margine è quello
di prima o più.

**Cosa costa** (modello comportamentale della VTL5C4 dal datasheet, con estrapolazione
dichiarata):
- **in ascolto**: la cella in serie passa da 88 a 113,5 Ω (curva B), o da 118 a 163,7 Ω (curva D,
  la più resistiva), contro 1 MΩ. La perdita resta −0,001 dB;
- **il mute a LDR**, nell'istante in cui d arriva a 1: ~−106 dB invece di −108 dB sulla curva B,
  2,2 dB meno profondo; 2,9 dB sulla curva D. Dopo 0,5 s il relè mette il jack a massa, e la
  profondità diventa quella del relè, che non cambia;
- **E5**: 5,049 µV contro 9,90 µV, cioè +0,053 µV sulla catena senza LDR (a 20 mA erano
  +0,039 µV) (`data/2026-09-26/L41b2/e3_e5/`);
- **E3**: |Zin| minima 110,7 kΩ contro ≥ 100 kΩ (a 20 mA era 111,6 kΩ).

**La tabella sul banco in continua** (`data/2026-09-26/L41b2/ldr/`, il pilota di `psu.py`,
calibrato come fa il firmware):
- da 15 a 60 °C, ogni punto entro **+0,28 dB**, la cima entro **±0,02 dB**;
- coi LED al massimo (2,0 V) e V5 a 4,90 V, entro +0,26 dB.

Con la cima a 20 mA e l'ascissa voluta, L41b1 dava −0,92 dB.

## Alternative scartate

- **Una cima che scende con la temperatura** (20 mA fino a ~45 °C, poi fino a ~12 mA a 60 °C,
  letta col sensore del micro): tiene i 118 Ω a telaio freddo. Ma il sensore sta sul chip del
  micro e non sulla cella (±3 °C), e la tabella diventa funzione della temperatura.
- **Un limite di temperatura del telaio a ~50 °C**: contraddice ADR-048 (58 °C col vano chiuso) e
  vuole un riprogetto termico.
- **Un altro pezzo**: riapre L29 (simbolo, modello, profilo).
- **Il secondo punto a 1,2 mA**: 12 mV sul pin, 22 passi dell'ADC. Scartato qui per il punto 2.

## Da riaprire se

- Il prototipo misura il LED più caldo del telaio: il declassamento vale per la temperatura
  ambiente della cella, e 12 mA su ~1,6 V sono ~19 mW per LED.
- Il mute a LDR serve più profondo nei 0,5 s prima del relè: si ridiscute la cima della sola
  derivazione.
- La misura sul prototipo contraddice la curva R(I) del modello a 12 mA.

**Chiude NC-038.** Precisa ADR-039 (il punto 3, la cima del profilo v4) e ADR-049 (il punto 6, la
calibrazione: la cima, l'ascissa del fit, lo zero dell'ADC).
