# ADR-011 — Trim di livello per ingresso

Data: 2026-09-08 · Stato: accettata

## Contesto

Le due sorgenti hanno livelli molto diversi: il FiiO K11 R2R eroga
**2,7 V**, il phono a valvole circa **0,5 V**. Sono ~15 dB di
differenza. Cambiando sorgente bisogna rifare il volume ogni volta.

## Decisione

Un **partitore resistivo selezionabile a ponticello su ciascun
ingresso**: 0 / −6 / −12 dB. Si regola una volta all'installazione.

## Perché

- Con il trim la manopola del volume resta più o meno dov'è quando si
  cambia sorgente: è una scocciatura quotidiana che sparisce.
- Sono due resistenze e un ponticello per ingresso — costo e complessità
  trascurabili.
- Passivo, prima del buffer: non aggiunge stadi attivi né rumore
  significativo.
- Le uscite fisse verso gli amplificatori per cuffia stanno **dopo** il
  trim. È voluto: anche loro hanno il proprio volume, e mantenere la
  compensazione rende coerente anche il loro punto di regolazione.

## Alternative scartate

- **Trim continuo (trimmer)**: regolazione più fine ma un componente
  meccanico in più nel percorso del segnale, e la precisione non serve —
  bastano tre passi.
- **Nessun trim**: costringe a rifare il volume a ogni cambio sorgente.

## Da riaprire se

Entra una sorgente con livello fuori dall'intervallo coperto dai tre
passi.

---

## Aggiornamento 2026-09-08 — il trim non è più solo una comodità

Il testo sopra non è stato modificato, ma la sua motivazione è
cambiata di peso.

La Fase 2 ha misurato che in modalità **+10 dB** con il K11 a fondo
scala (2,7 V, requisito E6) l'uscita richiesta sarebbe **8,54 V RMS**
contro un clipping a **9,31 V RMS**: **0,75 dB di margine**. È un
limite strutturale dei rail ±15 V, non un difetto di progetto — 2,7 ×
3,16 non ci sta comodo.

**La mitigazione è il trim di questa ADR**, con l'ingresso K11 a −6 dB.
Nata come comodità quotidiana (evitare di rifare il volume cambiando
sorgente), diventa **portante per l'headroom** nella modalità +10 dB.

Conseguenza pratica: se un giorno si userà il +10 dB, il trim
sull'ingresso ad alto livello **non è opzionale**. Va scritto sul
pannello o nella documentazione d'uso.

L'alternativa sarebbe rail a ±18 V, che contraddice E7 e richiederebbe
una ADR propria.
