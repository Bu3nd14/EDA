# ADR-108 — C548 / C552 in film di polipropilene, C553 in 2220, C518 in 1206

Data: 2026-10-29 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Scatta il «Da riaprire se» di ADR-105** («Un C0G da 1 µF in 1206 non si trova (L58)») e **supera
  ADR-105 in una parte sola**: «ogni condensatore dei ritardi è C0G» vale ancora per tutti tranne C548 /
  C552, che sono film di polipropilene. I valori di ADR-102 / ADR-105 non cambiano.
- **Conferma ADR-104** sul BAS416 alla distinta (perdita ≤ 5 nA a 25 °C; VF a 1 mA 0,9 V, sul limite,
  da leggere sul PDF del costruttore).

## Contesto

La ricerca alla distinta di L58a (`data/2026-10-29/L58a/distinta/README.md`, 2026-10-29, codici letti su
DigiKey e LCSC) non ha trovato un C0G da 1 µF in nessun formato a montaggio superficiale (1206, 1210,
1812, 2220); il più grande C0G verificato è 330 nF in 2220. Nemmeno un C0G da 330 nF sotto il 2220, né
uno da 100 nF in 0805.

## Decisione

L'utente, 2026-10-29, sulla domanda coi numeri (la musica 537,1 ms dopo un buco di 20 ms nell'angolo
peggiore dei 69 di L54b3b, contro 500 ms):

1. **C548 e C552, 1 µF ±5 %: film di polipropilene a foro passante** («Film polipropilene foro»),
   TDK B32672L2105J003, passo 15 mm, 18 × 11 × 18,5 mm, impronta
   `Capacitor_THT:C_Rect_L18.0mm_W11.0mm_P15.00mm_FKS3_FKP3`.
2. **C553, 330 nF: C0G in 2220** (KEMET C2220C334J5GACTU); **C518, 100 nF: C0G in 1206** (era 0805)
   («Sì, solo il formato»).

## Perché

Il valore resta: gli angoli di L54b3b restano validi senza rimisure. Il polipropilene ha la tolleranza
del C0G (±5 %) e una deriva tipica di ~−200 ppm/°C (non letta sul datasheet: meno dell'1 % fra 0 e
60 °C, e a 0 °C, dove sta l'angolo peggiore, allunga il ritardo); la perdita è ≥ 10 GΩ. Costa 0,91 $.

## Alternative scartate

- Film PPS a montaggio superficiale (KEMET SMC12.7105J50B31TR24): stessi valori, 14–22 $ l'uno.
- 330 nF C0G con le resistenze ×3 (R571 3,3 MΩ, R580 8,2 MΩ): nodi da 8 MΩ, tre volte più sensibili
  alle perdite dei diodi (il guasto di L54b3b), e niente misurato.

## Da riaprire se

- La deriva del film scelto, letta sul suo datasheet, supera l'1 % fra 0 e 60 °C.
- Il layout di G2 non accoglie due film da 18 × 11 mm vicino al temporizzatore.
