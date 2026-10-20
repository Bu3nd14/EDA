# ADR-093 — I corti del lato grezzo dei rail: uno Schottky in serie dopo ciascun regolatore, e due sul piedino

Data: 2026-10-20 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Realizza **ADR-074** (scelta 3 di `data/2026-10-14/L45d1/scelte_L45d2.pdf`): rivedere D510 / D511 e
  proteggere U502 dall'uscita sopra l'ingresso. È la forma che ADR-074 lasciava a L45d2b.
- Risponde al «Da riaprire se» di **ADR-092** che nominava questo lotto: la resistenza da 4,7 Ω ha
  cambiato i guasti del lato grezzo. La resistenza resta 4,7 Ω (scelta dell'utente).
- Conserva la tenuta di P9 (b) di **ADR-046** (la tenuta resta sul rail) e la quota di **ADR-020**
  (≥ 1 V fra ingresso e uscita del regolatore), al limite: vedi «Da riaprire se».
- Apre **NC-073** (la resistenza davanti al regolatore in un corto sul piedino).

## Contesto

Dal banco dell'alimentatore di L45d2b2b1 (`data/2026-10-20/L45d2b2b1/`), le righe di ADR-074 (C501,
C502, C509, C510, i quattro diodi di D501 in corto; l'ingresso di un regolatore a massa è il nodo di
C509 / C510) a rete −10 / 0 / +10 %, sul circuito di L45d2b2a:
- **i corti sul serbatoio** stanno meglio che in L45c1: R551 limita la scarica, il jack si apre prima
  che il rail scenda a 10,6 V, ~25–38 dB SPL a 1 m. U502 resta però a 0,52–0,55 V di uscita sopra
  l'ingresso per 61–105 ms, contro i 0,3 V del massimo assoluto (SBVS169D p. 5);
- **i corti sul piedino** (C509 / C510 in corto, o l'ingresso di un regolatore a massa al suo
  interno) sono peggiori di prima: in L45c1 si davano «uguali» al serbatoio, ma con la resistenza in
  mezzo non lo sono più. Tutta la capacità del rail torna nel corto attraverso D510 / D511:
  **68 A di picco** in un 1N5819 (25 A di picco non ripetitivo), **3,9 V** di uscita sopra l'ingresso,
  il jack che si apre col rail già a −0,7 V: **16,7 mV, ~78 dB SPL**, il colpo più forte della serie.

Un diodo fra uscita e ingresso porta tutta la scarica del rail: a decine di ampere nessuno Schottky
resta sotto 0,3 V. Più grosso (un SB340 al posto del 1N5819) porta i corti sul piedino a 1,64 V e
lascia il jack dopo il crollo del rail in 6 righe su 24.

## Decisione

Parole dell'utente (2026-10-20): «In serie, 4,7 Ω».

1. **Uno Schottky in serie fra il piedino d'uscita di ciascun regolatore e il suo rail**: D515 dopo
   U501, D516 prima di U502 (Vishay SB340, 3 A, 40 V, DO-201AD). La tenuta (C505 / C506, i
   condensatori della scheda audio), il sorvegliante e J1 restano sul rail, dopo il diodo.
2. **La retroazione resta sul piedino**, prima del diodo: SENSE di U501 su `VPLUS_REG`, il partitore
   di U502 da `VMINUS_REG`. Il regolatore vede il suo 10 µF ceramico (C511 / C512, sul piedino) come
   oggi. Un diodo dentro l'anello (~0,09 Ω contro ~3,6 mF, un polo vicino a 500 Hz) è un rischio di
   stabilità che il banco comportamentale non vede.
3. **La tensione impostata sale di ~0,3 V**, perché il rail resti a ~15 V dietro il diodo: U501
   15,3 V (i piedini ANY-OUT 0,2 e 0,1 V a massa), U502 −15,28 V (R501 da 118 a 120 kΩ).
4. **Sul piedino due SB340 in parallelo dall'uscita all'ingresso** (D510 + D513, D511 + D514) al
   posto di ciascun 1N5819: dietro il diodo in serie scaricano solo i 10 µF del piedino.
5. **R550 / R551 restano 4,7 Ω** (ADR-092).

## Perché

| | Oggi (L45d2b2a) | Solo SB340 sul piedino | **Questa** |
|---|---|---|---|
| righe di ADR-074 col jack dopo i 10,6 V (su 24) | 6 | 6 | **0** |
| uscita sopra l'ingresso di U502 (massimo 0,3 V) | 3,94 V | 1,64 V | **0,278 V** |
| tempo oltre 0,3 V | 105 ms | 77 ms | **0** |
| corrente di picco del diodo sul piedino | 68 A | 82 A | **0,21 A** |
| colpo peggiore al jack (picco filtrato, 100 kΩ) | ~78 dB SPL | (non corso) | **~32 dB SPL** (86 µV) |
| U502 / U501 a rete +10 %, 60 °C d'aria (limite 125 °C) | 122,2 / 121,7 °C | uguale | **119,7 / 118,7 °C** |
| riserva ingresso − uscita a rete −10 % (quota ≥ 1 V) | 1,32 / 1,45 V | uguale | **1,09 / 1,15 V** |
| tenuta di `VRELAY` a rete −10 % (≥ 25 ms) | 46,4 ms | 46,4 ms | **46,4 ms** |

Le cifre dell'ultima colonna sono del banco sul sorgente (`analisi_sorgente.csv`, `rete_opzioni.csv`
riga `sorgente`); la scelta era stata portata all'utente con l'opzione `serie_47_sb340` (U502 a
−15,3 V invece di −15,28: riserva 1,02 V, 119,1 °C).

- **Il rail non torna più indietro.** In ogni riga il rail resta sopra 13,2 V finché il jack non si
  apre: il sorvegliante muta entro 1 ms dall'uscita dai 13,5 V, come una perdita di rete lenta.
- **Il regolatore si scalda meno**: il diodo prende 0,095–0,098 W, e il regolatore li perde (3 °C).
- **L'accensione non cambia**: i rail alle soglie del firmware a 565 / 535 ms, i jack a 716 ms coi rail
  assestati, MUSICA a 726 ms (L45d2b2a: 707 / 717), anche a rete −10 %.
- **Scartata la resistenza a 3,3 Ω** con lo stesso diodo: riserva 1,46 V, ma il regolatore a 123,5 °C.

Le cifre dell'SB340 vengono dalla curva tipica a 25 °C di Vishay 88719, fig. 3, letta a occhio
(±0,03–0,05 V): i 21 mV di margine sull'uscita di U502 stanno dentro quella incertezza.

## Alternative scartate

- **Solo un diodo più grosso sul piedino**: non tocca i corti sul piedino, che restano fuori.
- **La stessa forma con 3,3 Ω**: più riserva, più calore.
- **La retroazione sul rail, dopo il diodo**: il rail esatto a 15 V, ma il diodo dentro l'anello.

## Da riaprire se

- La riserva misurata a rete −10 % scende sotto 1 V (sul prototipo, o con un trasformatore di meno
  tensione a vuoto del modello di ADR-048): si torna alla resistenza (3,3 Ω: 1,46 V, 123,5 °C).
- La Vf dell'SB340 letta da una curva del costruttore o misurata dà, a 0,22 A e alla temperatura più
  bassa d'esercizio, l'uscita di U502 oltre 0,3 V sopra l'ingresso.
- Una misura dell'impedenza del rail sotto ~400 Hz (il diodo aggiunge ~0,1 Ω prima che la tenuta
  prenda il sopravvento) dà una diafonia o un rumore fuori dal PRB.
