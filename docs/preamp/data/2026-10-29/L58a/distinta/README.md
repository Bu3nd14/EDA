# L58a — la distinta delle parti nuove del temporizzatore (2026-10-29)

Le conferme alla distinta che ADR-104 e ADR-105 mandavano a L58: il **BAS416** (perdita ≤ 5 nA a 25 °C,
VF ≤ 0,9 V a 1 mA) e i **condensatori dei ritardi in C0G**. Cercate da `bom-component-manager` il
2026-10-29, solo sul web: **ogni codice qui sotto è stato letto su una pagina scaricata** (DigiKey con
la ricerca del codice esatto, LCSC); dove la fonte è solo il riassunto di un motore di ricerca o di un
aggregatore, lo dice la colonna. Prezzi in dollari, a quella data; le scorte si muovono.

**L'esito che cambia il circuito**: un C0G da 1 µF **non esiste in nessun formato a montaggio
superficiale** trovato (1206, 1210, 1812, 2220: nessun codice; il più grande C0G verificato è 330 nF in
2220), né un C0G da 330 nF sotto il 2220, né uno da 100 nF in 0805. È il «Da riaprire se» di ADR-105.
**La scelta dell'utente** (L58a, 2026-10-29): C548 / C552 in **film di polipropilene a foro passante**,
C553 in **C0G 2220**, C518 in **C0G 1206**; nessun valore cambia (ADR-108).

## Il diodo

| Parte | Rif. | Codice | Contro il requisito | Stato (fonte, data) | Scorte / prezzo | Esito |
|---|---|---|---|---|---|---|
| BAS416, SOD-323 | D534, D535, D536, D541 | **Nexperia BAS416,115** (bobina da 3 k). Non il BAS416F,135: altro contenitore, segnato fuori produzione | V_R 75 V (il nodo sta sotto 5 V); I_R a 75 V, 25 °C: tip. ~3 pA, **max 5 nA**; a 150 °C tip. 3 nA, **max 80 nA**; **VF a 1 mA max 0,9 V a 25 °C**: esattamente sul limite, e «max» letto solo su riassunti del datasheet (Nexperia risponde 403) | In produzione (nexperia.com, dal riassunto: la pagina risponde 403), AEC-Q101, 2026-10-29 | **LCSC C89953: 14 080 pz**, 0,047 $ a 100 (pagina letta); DigiKey: listato, 0,28 $, scorta non letta; Farnell 8734399RL: 9 669 pz solo dal riassunto (pagina scaduta) | **OK** sulla perdita; VF sul limite, da leggere sul PDF del costruttore |

Al banco il BAS416 è il modello BAV199 di Diodes Inc. (ADR-104): IS 59 pA, BV 85 V.

## I condensatori dei ritardi

| Rif. | Valore | Formato | Codice | V / toll. | Scorte / prezzo (DigiKey salvo detto, 2026-10-29) | Esito |
|---|---|---|---|---|---|---|
| **C548, C552** | 1 µF | **film PP, foro passante, passo 15 mm**, 18 × 11 × 18,5 mm (`C_Rect_L18.0mm_W11.0mm_P15.00mm_FKS3_FKP3`) | **TDK B32672L2105J003** | 250 V, ±5 % | 1 342 pz; 0,91 $ a 1, 0,283 $ a 5,1 k; Active; −55…+125 °C | **SCELTO** (ADR-108) |
| C548, C552 (alternative) | 1 µF | film PP, passo 15 mm (17,5 × 7,0) / passo 7,5 mm (17,5 × 7,8) | Panasonic ECW-FE2W105J; ECW-FD2W105JB | 450 V, ±5 % | 6 622 pz, 0,96 $; ECW-FD: scorta ambigua (707 nell'elenco, 0 sulla pagina del codice; ECW-FD2W105J4 313) | alternative; la seconda chiede un'altra impronta |
| C548, C552 (scartato) | 1 µF | film PPS SMD, 12,7 × 11,5 mm | KEMET SMC12.7105J50B31TR24 | 50 V, ±5 % | 465 pz, 14–22 $ | scartato dall'utente: costo e ingombro |
| C553 | 330 nF | **C0G 2220** (`C_2220_5750Metric`) | **KEMET C2220C334J5GACTU** | 50 V, ±5 % | 4 739 pz; 6,75 $ a 1, 3,25 $ a 3 k; Active | **SCELTO** (ADR-108) |
| C518 | 100 nF | **C0G 1206** (era 0805) | **Murata GRM3195C1H104JA05D**; TDK CGA5L2C0G1H104J160AA | 50 V, ±5 % | 124 295 pz; 128 924 pz | **SCELTO** (ADR-108) |
| C528, C529, C549, C551 | 100 nF | C0G 1206 | come C518 | 50 V, ±5 % | come sopra | OK |
| C550 | 10 nF | C0G 1206 | **KEMET C1206C103J5GACTU** (il Murata GRM3195C1H103JA01D esiste ma è «Not For New Designs») | 50 V, ±5 % | 3 343 pz; 1,60 $ a 1, 0,56 $ a 2,5 k; Active | OK |
| C527 | 22 nF | C0G 0805 | **KEMET C0805C223J5GACTU** | 50 V, ±5 % | 5 611 pz; 0,98 $ a 1; Active | OK |

**Il film al posto della ceramica**: le corse di L54b3b (69 angoli) hanno preso i condensatori dei ritardi
a ±5 % senza deriva termica, la C0G. Il polipropilene ha la stessa tolleranza; la sua deriva tipica è
~−200 ppm/°C (un valore della famiglia di dielettrici, **non letto sul datasheet del TDK**, che non lo
dà nel testo raggiunto): tra 0 e 60 °C meno dell'1 %. L'angolo peggiore della musica dopo un buco di
20 ms è 537,1 ms a 0 °C (`../2026-10-28/L54b3b/an_v_angoli.csv`), dove il PP ha la capacità **più
alta** di quella a 25 °C, quindi il ritardo più lungo; a 60 °C (−0,7 %) l'angolo era 579 ms. La
perdita del film: ≥ 10 GΩ (Panasonic, IR ≥ 10 000 MΩ·µF), trascurabile contro i nodi da 1–2,7 MΩ.

## Non verificato (detto per nome)

- La riga del datasheet Nexperia con VF a 1 mA, e se 0,9 V è un massimo: letta solo su riassunti.
- Le scorte del BAS416 da Mouser, TME, Farnell (Farnell solo dal riassunto).
- La deriva termica della capacità di ogni film, compreso il TDK scelto.
- Un C0G da 1 µF di Murata, TDK o Samsung in 1210 / 1812 / 2220 provato codice per codice: le ricerche
  per valore erano troncate; nessuna riga a 1 µF in quelle lette.
