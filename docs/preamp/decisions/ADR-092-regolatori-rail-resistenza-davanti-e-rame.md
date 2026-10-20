# ADR-092 — Il calore dei regolatori dei rail a regime: 4,7 Ω davanti a ciascuno, e il rame al layout

Data: 2026-10-20 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Applica la regola delle parti attive di **ADR-021** (REQUIREMENTS, sotto P7: 60 °C + P · R_thJA ≤
  125 °C) a due parti che non erano mai state lette contro di essa.
- Apre **NC-072**, che si chiude con questa resistenza nel sorgente e col rame misurato al layout
  dell'alimentatore (G2).
- Conserva la riserva di tensione che la quota di **ADR-020** suppone (≥ 1 V fra ingresso e uscita
  del regolatore) e la tenuta di P9.

## Contesto

Trovato in L45d2b2a, rispondendo a una domanda dell'utente sul calore all'avvio
(«accorcia la vita o mette a rischio rottura il regolatore?»).
- A regime U501 e U502 dissipano (RAW − 15 V) · ~0,3 A.
- **2,34 / 2,38 W a rete +10 %**: con 60 °C d'aria e i 32,5 °C/W di SBVS204G, **136 / 137 °C**,
  oltre i 125 °C.
- 114 °C alla rete nominale, 92 °C a −10 %.

## Decisione

Parole dell'utente (2026-10-20): «4,7 Ω + rame al layout».

1. **R550 e R551, 4,7 Ω**, fra il serbatoio (C501 / C502) e l'ingresso di U501 / U502.
   - Sono assiali da 2 W, alzati dalla scheda.
   - Sul lato del piedino, `RAW_PR` / `RAW_MR`, vanno anche l'abilitazione, il 10 µF d'ingresso
     (C509 / C510) e lo Schottky di protezione (D510 / D511): l'abilitazione non deve superare
     l'ingresso, e lo Schottky protegge il piedino.
2. **Il rame sotto il pad termico** dei due regolatori, al layout dell'alimentatore: **≤ 27 °C/W**
   giunzione-aria, da misurare sul prototipo.

## Perché

Dal banco della rete di L45d2b2a (regime e perdita di rete a −10 / 0 / +10 %, sul sorgente):

| | Rete −10 % | Nominale | **Rete +10 %** | Nella resistenza | Riserva a −10 % | Il jack si apre prima del rail (perdita a −10 %) |
|---|---|---|---|---|---|---|
| senza | 92 °C | 114 °C | **136–137 °C** | — | 2,88 / 2,79 V | 51 ms |
| **4,7 Ω** | 77 °C | 99 °C | **122 °C** | 0,44 / 0,46 W | 1,45 / 1,32 V | 40 ms |
| 5,6 Ω | 74 °C | 97 °C | 119 °C | 0,52 / 0,55 W | 1,18 / 1,04 V | 38 ms |

- **La resistenza da sola dà pochi gradi di margine.** Fra rete −10 % e +10 % il grezzo cambia di
  ~4,5 V e il regolatore li assorbe tutti; la resistenza (come un trasformatore più basso) toglie la
  stessa caduta in tutti e due i casi, e a −10 % la riserva non può scendere sotto 1 V. 4,7 Ω lascia
  1,3 V; 5,6 Ω arriva a 1,04 V.
- **Il margine vero lo dà il rame.** Con ≤ 27 °C/W: ~112 °C a rete +10 %.
- **La resistenza costa poco**: la tenuta dei rail alla perdita di rete scende di ~11 ms, e il jack
  si apre ancora 40 ms prima che il rail lasci i 13,5 V. La partenza morbida è uguale (ADR-091), e
  l'avvio è come senza resistenza (U501 0,45 A).
- **Le cifre sono stime.** I 32,5 °C/W sono della scheda JEDEC del costruttore, non della nostra; il
  TPS7A3301 ha lo stesso contenitore (RGW) e se ne usano le stesse cifre.

## Alternative scartate

- **Solo il rame, al layout**: niente parti nuove, ma fino al layout la regola resterebbe violata a
  rete +10 %, e serve ≤ 25 °C/W per stare a 119 °C.
- **Un pre-regolatore** (un transistor con dissipatore davanti a ciascun regolatore): il regolatore
  a ~0,7 W per qualunque rete. Più parti e un dissipatore sulla scheda dell'alimentatore.
- **Una resistenza più grande**: la riserva a rete −10 % scende sotto 1 V, fuori dalla quota di
  ADR-020.

## Da riaprire se

- La misura sul prototipo dà R_thJA > 27 °C/W, o i regolatori oltre 115 °C a rete +10 % con 60 °C
  d'aria: si torna alla scelta, col pre-regolatore.
- Il carico dei rail cresce oltre ~0,33 A per rail.
- La riserva misurata a rete −10 % scende sotto 1 V (trasformatore con meno tensione a vuoto del
  modello di ADR-048).
- L45d2b2b (i diodi della tenuta, ADR-074) trova che la resistenza cambia i guasti del lato grezzo:
  in un corto del serbatoio la tenuta si scarica nel corto attraverso R550 / R551, non direttamente.
