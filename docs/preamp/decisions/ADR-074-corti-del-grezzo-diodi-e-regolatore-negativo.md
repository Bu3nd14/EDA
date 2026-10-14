# ADR-074 — I corti sul lato non regolato dei rail: si rivedono i diodi della tenuta e si protegge il regolatore negativo

Data: 2026-10-14 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- È la **scelta 3** di `data/2026-10-14/L45d1/scelte_L45d2.pdf` (9 righe alte, 1 media, L45c1).
- La realizzazione è di **L45d2b**. Il fusibile del modulo IEC resta da dimensionare a G2.

## Contesto

Un serbatoio o un diodo del ponte in corto (C501, C502, C509, C510, D501), o l'ingresso di un
regolatore a massa al suo interno: il sorvegliante muta entro 1 ms, ma D510 / D511 scaricano la
tenuta nel corto. Così il corto del grezzo diventa un corto del rail, e il rail scende sotto 10,6 V
prima che il jack si apra. Al jack arrivano al più **9,0 mV** (~72 dB SPL a 1 m). Sul rail
negativo, però, **U502 resta con l'uscita fino a 1,76 V sopra l'ingresso**, contro i −0,3 V del suo
massimo assoluto (SBVS169D): una parte oltre i suoi limiti, gravità 5.

## Decisione

Parole dell'utente (2026-10-14): «Rivedere i diodi e il regolatore».

1. **Si rivedono D510 / D511**, in modo che un corto del grezzo non scarichi la tenuta dopo il
   regolatore.
2. **Si protegge U502** dall'uscita sopra l'ingresso, per esempio con un diodo dall'uscita
   all'ingresso, come raccomanda la nota d'applicazione del regolatore. La forma la sceglie L45d2b.

L45d2b rifà le 10 righe con le colonne dopo il rimedio. Va verificato anche che i colpi al jack non
crescano, e che i rail tengano ancora i 25 ms di P9 (b) alla perdita di rete.

## Perché

- **Una parte oltre il massimo assoluto è sicurezza, non un colpo** (gravità 5, ADR-070). Il
  colpo di 9 mV si poteva accettare, U502 fuori dai limiti no.
- **D510 / D511 sono la causa comune**: sono loro a trasformare il corto del grezzo in un corto del
  rail. Rivederli può togliere sia il colpo sia la tensione inversa.

## Alternative scartate

- **Accettarlo**: al jack andava bene, ma lasciava U502 oltre il massimo assoluto per tutta la
  durata del guasto.

## Da riaprire se

- Rivedere D510 / D511 costa la tenuta di P9 (b), cioè i ≥ 25 ms di `VRELAY` o i ≥ 1500 µF effettivi:
  si torna all'utente con i due numeri accanto.
- Il datasheet di un regolatore diverso tollera l'uscita sopra l'ingresso.
