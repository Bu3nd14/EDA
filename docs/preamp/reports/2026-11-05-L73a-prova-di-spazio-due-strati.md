# L73a — la prova di spazio a due strati sul circuito di oggi

Data: 2026-11-05 · Lotto: L73a (la prima metà di L73, spezzato su richiesta dell'utente) · NC-048
(bloccante per G1), NC-080, NC-082 · Dati: `data/2026-11-05/L73/`

## In breve

- La scheda audio di oggi (653 parti, i sedici dissipatori, i condensatori della lista ammessa al pezzo più
  grande) **si piazza in 392,6 × 198,3 mm e si sbroglia a due strati quasi del tutto**: una connessione
  aperta (K3, piedino 6) e due distanze di 0,248 mm contro 0,25. Il riempimento è **0,46**, contro ~0,38 di
  L49a: **non c'è margine**, e lo sbroglio vero con la massa a stella e il piano di massa (L50, NC-044)
  chiede più area, non meno — è l'obiezione dell'utente, e i numeri la confermano.
- **Nel Pesante 3U a fondo piatto non ci sta**: mancano **18,3 mm** di profondità per l'alimentatore (oggi
  189 parti, 246,9 × 110 mm) e i toroidali davanti alla scheda audio, e i condensatori da 32 mm superano di
  3,6 mm il bordo basso dei RCA. L'alimentatore sotto la scheda audio va peggio (fino a 21 mm).
- **Un rilievo che vale anche per L49a**: i transistor del simbolo `Device:Q_NPN` / `Q_PNP` (piedini B / C /
  E) arrivano sulla scheda **senza nessuna rete** sulle impronte SOT-23 / SOT-223 (piazzole 1 / 2 / 3), senza
  errore. La scheda di L49a, chiusa «100 %, DRC 0 / 0», aveva 40 + 8 SOT-23 e 16 TO-220 scollegati. Era
  annotato solo nel README di L45d2b3b2b1 («va risolto prima di G2»). Qui è mappato per la prova dai
  datasheet (`script/pinmap.py`, 72 transistor); per G2 è una decisione del sorgente.
- **La scelta dell'utente** (2026-11-05): misurare tutte e quattro le strade — **contenitore più profondo,
  quattro strati, scheda figlia, due contenitori** — e poi decidere. È **L73b**.

## Che cosa si è fatto

1. **Le impronte della lista ammessa** (ADR-122), nella netlist di prova e non nel sorgente: ingressi
   26,5 × 11,5 mm a passo 22,5 (il 2,2 µF WIMA è 26,5 × 11 × 21: più grande dell'1 µF che il prompt
   indicava), principale 31,5 × 15 a passo 27,5, C_T e Singxer 41,5 × 19 a passo 37,5.
2. **La Stax distinta dal Singxer (NC-080)**: un'impronta a passo 22,5 con la serigrafia «STAX 1uF 5%
   ONLY» (`footprints/L73.pretty`). Il 4,7 µF ha passo 27,5 e non entra nei fori: lo scambio col Singxer
   diventa impossibile, non solo segnalato. **Proposta per G2.**
3. **Il piazzamento** (`script/audio/place.py`, copia di L49a): i gruppi di oggi; il sensore di bias è il
   DZT5551 del moltiplicatore (19,2 mm dal suo MJE15032, col dissipatore in mezzo; L49a 10,9 mm); i
   dissipatori al collettore a ≥ 10,9 mm fra loro (il più vicino è la coppia NPN / PNP di un blocco, V+
   contro V−). Con la connettività di L49a la scheda veniva 409,7 × 268,1 mm (riempimento 0,33): i
   dissipatori alti 16,5 mm mescolati alle parti piccole rendevano ogni fila alta quanto il più alto. Coi
   **più alti prima** (le parti di pari misura restano in ordine di connettività, il sensore accanto al suo
   NPN) 392,6 × 198,3 mm.
4. **Lo sbroglio** (Freerouting 2.4.1, 2 strati, ≥ 0,25 mm, fan-out spento): 6154 tracce, 419 vie, 40
   passi. DRC: 1 aperta, 2 errori di 2 µm, 52 avvisi estetici (serigrafie, la libreria `preamp` non nella
   tabella del progetto di prova).
5. **L'alimentatore** di oggi (189 parti contro 118: la logica analogica dei temporizzatori, R550 / R551,
   i quattro SB340): la scansione dà 306,8 × 100 / 246,9 × 110 / 226,9 × 120 mm. Lo sbroglio a 110 mm era
   in corsa alla chiusura: **lo rifà L73b** con le piste larghe.
6. **La pianta** (`script/assembly/floorplan.py`) a fasce d'altezza (`audio/heights.json`, ogni altezza con
   la sua fonte: il dissipatore 32,0 + 3,6 mm da `sink-w.pdf`, i WIMA da ADR-122, il resto dichiarato come
   ipotesi).

## Le strade che misura L73b

| Strada | Che cosa dà | Che cosa cambia |
|---|---|---|
| Contenitore più profondo | **Hifi2000 Slimline 3U 350**: interni 415 × 350 × 120, esterni 435 × 361 × 122 mm (Audiophonics, letto il 2026-11-05; ~135 €), dentro P8. +50 mm contro i 18,3 che mancano | il contenitore di P8 (si sceglie entro G2) |
| Quattro strati | il piano di massa in uno strato suo: dice se la scheda resta di questa misura col piano vero | la tecnologia scelta in L49a («due strati misti») |
| Scheda figlia | le quattro uscite fisse (~256 parti) sopra la principale | P4 («due circuiti stampati»): ADR |
| Due contenitori | alimentatore e toroidali a parte: la scheda audio ha ~290 mm (riempimento ~0,31), i trasformatori lontani dagli ingressi (P3) | PR-27 («un solo telaio»): il contratto firmato, ADR-053 |

Le temperature non cambiano con nessuna: dissipatori e regolatori sono gli stessi, e un contenitore più
grande o separato scalda meno.

## Non conformità

- **NC-048** resta aperta, bloccante per G1: avanzamento scritto nel registro.
- **NC-080 / NC-082** (per G2): l'impronta della Stax e quelle dei pezzi più grandi esistono come prova.
- Il rilievo dei transistor senza rete: **da registrare con la severità che decide l'utente** (proposta:
  maggiore, prima di G2), in L73b.
