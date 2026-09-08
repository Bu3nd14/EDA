# ADR-001 — Guadagno unitario, non +16,5 dB

Data: 2026-09-08 · Stato: accettata

## Contesto

Il preamplificatore sostituisce un Technics SU-9070 giudicato "poco
lively, senza dinamica". Prima di progettare serviva capire se quel
giudizio soggettivo avesse un meccanismo misurabile dietro.

Ce l'ha, ed è la struttura di guadagno dell'intera catena. Vedi
`../reports/2026-09-08-analisi-catena.md` per l'analisi completa.

## Decisione

Il preamplificatore ha **guadagno unitario (0 dB)**, non guadagno di
tensione. Il suo lavoro è attenuare bene, commutare gli ingressi e
pilotare il finale — non amplificare.

## Perché

- Il **FiiO K11 R2R** eroga **2,7 V RMS**. Il **cj Evolution 250** va a
  piena potenza (25 W) con **0,67 V**. La sorgente ha già **12 dB più**
  del necessario, prima di qualsiasi preamplificatore.
- Il Technics aggiungeva **+16,5 dB** (150 mV → 1 V). In uscita:
  2,7 × 6,67 = **18 V** per pilotare un ingresso che ne vuole 0,67.
- All'ascolto normale (~0,5 W su Klipsch Heresy da 96 dB/1W/1m) al
  finale servono **95 mV**. Attenuazione richiesta: **45,6 dB**.
- **La manopola del Technics indicava 46 dB.** Il modello della catena
  si chiude a mezzo decibel.
- Amplificare di 16,5 dB per poi buttarne via 46 significa lavorare in
  fondo alla corsa del potenziometro, dove il tracking fra i canali è
  peggiore (±2-3 dB tipici) e la risoluzione più grossolana.
- Il phono a valvole dell'utente esce a ~0,5 V, cioè **già quasi
  esattamente i 0,67 V** che il finale vuole. Guadagno unitario va bene
  per entrambe le sorgenti.

Con guadagno unitario l'attenuatore lavora intorno a **−29 dB**
all'ascolto normale, invece che a −46: a metà corsa, dove qualunque
attenuatore fa il suo mestiere onestamente.

## Alternative scartate

- **Mantenere guadagno "standard" da preamplificatore (+10…+20 dB)**:
  è esattamente il difetto che stiamo rimuovendo.
- **Guadagno negativo fisso (attenuazione)**: risolverebbe il K11 ma
  lascerebbe il phono senza margine.

## Da riaprire se

Cambia il finale (sensibilità diversa da 0,67 V) o entra in catena una
sorgente a basso livello. Per quel caso esiste già il guadagno
commutabile a +10 dB — vedi ADR-004.
