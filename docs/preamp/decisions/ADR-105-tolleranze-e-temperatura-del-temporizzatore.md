# ADR-105 — Le tolleranze e la temperatura del temporizzatore: D534 a bassa perdita, R571 1,1 MΩ, i condensatori dei ritardi C0G

Data: 2026-10-28 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Completa ADR-102** al punto 2 (il temporizzatore) e **ADR-104**: D534 (dal rivelatore di rete al
  nodo d'innesco della ritenuta) non è più un BAT54 ma un BAS416 a bassa perdita, come D535 / D536 /
  D541; R571 da 1 MΩ a 1,1 MΩ; il dielettrico dei condensatori dei ritardi, finora non dichiarato, è
  C0G per tutti.
- **Scatta il secondo «Da riaprire se» di ADR-104** («la perdita dei diodi rimasti BAT54 sposta un tempo
  oltre i suoi limiti»): la perdita di D534 a 60 °C fa scattare la ritenuta. Il primo («le tolleranze o i
  60 °C portano la musica dopo un buco di 20 ms sotto i 500 ms») scatta a 0 °C ed è chiuso da R571.
- **Non scatta il «Da riaprire se» di ADR-103**: la base di Q513 all'accensione a freddo col frontale
  acceso resta ≤ 0,31 V in ogni angolo, a 0 / 25 / 60 °C, col comparatore vivo da 2,2 V.

## Contesto

L54b3b, la seconda parte della robustezza al banco (`data/2026-10-28/L54b3b/`, README; report
`reports/2026-10-28-L54b3b-tolleranze-temperatura.md`): un Monte Carlo di 100 campioni su sette casi
(R ±1 %, condensatori, VREF, lo scostamento di ognuno dei diciotto canali di comparatore, la loro
corrente d'ingresso), la regressione lineare dei margini, gli angoli peggiori costruiti da essa e corsi
a 0 / 25 / 60 °C alle tre reti, con la perdita massima del datasheet dei diodi alla temperatura. Tre
prove sono fallite contro i criteri scritti prima delle corse:

1. **A 60 °C l'accensione a freddo col frontale acceso fa scattare la ritenuta**, anche coi valori
   nominali: D534, in inversa da AT_MD (100 kΩ verso V5) verso AT_F (33 kΩ al ritorno), alla perdita
   massima del BAT54 a 60 °C (~19 µA, DS11005 × 9,5) porta la base di Q513 a 0,88 V. Senza la perdita
   massima (il solo modello del costruttore, ~7 µA) la base è a 0,37 V; con la stessa perdita a 25 °C a
   0,54 V senza scatto (la VBE più alta).
2. **A 0 °C la musica dopo un buco di 20 ms** nell'angolo peggiore delle tolleranze torna a 491 ms
   (≥ 500 ms); a 25 °C 517 ms.
3. **In X7R** C548 (1 µF, AT_PGT) porterebbe la musica dopo il buco sotto i 400 ms; C551 e C529 K501 a
   43 ms dopo il permissivo a 0 °C (≥ 50 ms, ADR-046).

## Decisione

Parole dell'utente (2026-10-28), alle tre domande coi numeri:

1. **«Solo D534 a bassa perdita»**: D534 diventa un BAS416 (sul banco il modello BAV199 di Diodes Inc.,
   dichiarato come in ADR-104). D533 e D537 restano BAT54.
2. **«R571 a 1,1 MΩ»**.
3. **«Tutti C0G»**: C518, C527, C528, C529, C548, C549, C550, C551, C552, C553, in 1206.

## Perché

**La ritenuta a 60 °C** (`an_diag.csv`, `an_rimedio_prova*.csv`; l'accensione a freddo col frontale
acceso, la base di Q513, lo scatto a ~0,45 V):

| | 60 °C, nominale | 60 °C, angolo peggiore, comparatore da 2,2 V | la musica dopo un buco di 20 ms, 60 °C |
|---|---|---|---|
| com'era (D534 BAT54) | **0,88 V, scatta** | scatta | (la ritenuta è già scattata) |
| **D534 BAS416 (scelto)** | **0,27 V** | **0,31 V** | 574,5 ms nominale |
| D533, D534, D537 BAS416 | 0,27 V | 0,31 V | **461 ms** nominale, 369 ms nell'angolo a 0 °C |

D533 in BAS416 lascia AT_PG più alto con la rete mancante (la VF ~0,75 V), AT_PGT riparte da più in
alto e il ritardo si accorcia. La perdita di D533 va in AT_PG e quella di D537 in AT_MRQ, nodi che un
comparatore tiene bassi quando conta; quella di D534 va nel nodo d'innesco.

**La musica dopo un buco di 20 ms** (l'angolo peggiore, `an_v_angoli.csv`):

| | 0 °C | 25 °C | 60 °C | la musica dopo l'accensione dal frontale (25 °C) |
|---|---|---|---|---|
| R571 1 MΩ | **491 ms** | 517 ms | 528 ms | 1150 ms |
| **R571 1,1 MΩ (scelto)** | **537 ms** | 567 ms | 579 ms | 1209 ms |

**I dielettrici** (l'angolo peggiore, prima del cambio; «X7R» = sui piccoli, C0G su C548, C552, C528):

| | K501 dopo il permissivo (≥ 50 ms) | il permissivo dopo il mute (≥ 16,9 ms) | la musica dopo il buco, 0 °C |
|---|---|---|---|
| **tutti C0G (scelto)** | 63,8–69,2 ms | 34,4–36,0 ms | 491 ms (537 con R571 1,1 MΩ) |
| X7R sui piccoli | **42,9–48,3 ms** | 28,6–30,2 ms | 477 ms |

**Sul sorgente nuovo** (`an_v_*.csv`): i 69 angoli peggiori a 0 / 25 / 60 °C passano tutti (il minimo di
ogni margine: la musica dopo il buco 537,1 ms, il permissivo 31,4 ms, K501 63,8 ms, l'armamento 723 ms
dopo l'alimentazione buona, la base 0,311 V; il timeout scatta con un rail morto fino a 2515 ms). La
lista della sicurezza (31 casi) a 25 °C ha i verdetti e gli istanti di sicurezza di L54b3a (la sola
musica +54–60 ms, R571); a 0 e 60 °C gli stessi verdetti. I gruppi di hFE A / C come il B.

## Alternative scartate

- **I tre BAT54 a bassa perdita**: la musica dopo il buco a 461 ms a 60 °C.
- **Lasciare D534 com'è**: la ritenuta scatta a ogni accensione a freddo col frontale acceso in una
  stanza a 60 °C con un pezzo alla perdita massima.
- **Lasciare R571 a 1 MΩ**: 491 ms nell'angolo peggiore a 0 °C.
- **X7R sui condensatori piccoli**: K501 43 ms dopo il permissivo.

## Da riaprire se

- Il BAS416 non si trova alla distinta (L58): un diodo con perdita ≤ 5 nA a 25 °C e VF ≤ 0,9 V a 1 mA,
  come ADR-104.
- Un C0G da 1 µF in 1206 non si trova (L58): il nodo più largo (C548 / C552) a 10 µF / 110 kΩ / 270 kΩ
  non è misurato.
- Il prototipo mostra un'accensione a freddo che scatta: le perdite superficiali della scheda su AT_F e
  AT_MD (il layout, al prototipo).
- Il filtro dei rimbalzi su AT_MRQ: con la perdita massima di D537 a 60 °C la musica dopo il rilascio del
  tasto viene a 7,7 ms invece di 18,1; se un rimbalzo vero dura più di ~7 ms, D537 a bassa perdita.
