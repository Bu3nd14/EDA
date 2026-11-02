# ADR-111 — Il limitatore del VAS a 36,5 + 18,7 Ω: il VAS sotto P7 col finale NPN in corto base-emettitore

Data: 2026-11-02 · Stato: accettata

**Rapporti con le decisioni precedenti.**

- **Chiude NC-076** (L55, maggiore, prima di G1): il VAS a 126 °C col finale NPN in corto base-emettitore.
- **Modifica ADR-099**, il punto «un limite di corrente del VAS»: la degenerazione resta di 55 Ω in tutto
  (ADR-054), ma la presa si sposta. R123 passa da 33 a **36,5 Ω**, R192 da 22 a **18,7 Ω** (serie E96),
  in tutte e otto le istanze di `gain_block()`. Il transistor del limitatore (Q193) non cambia.
- **Non cambia ADR-068**: il VAS resta in SOT-223 sulla piazzola minima (125 °C/W). La strada del rame è
  stata scartata (sotto).
- **Non cambia ADR-095**: D158 in corto è lo stesso guasto di Q132 in corto base-emettitore, e il rimedio
  copre anche lui.
- **Il PRB non cambia**: P7 si applica, P10 resta dentro.

## Contesto

L66 (`data/2026-11-02/L66/`, README), sul banco del calore di L45d2b3b2b2 caricato per percorso e provato
sul suo caso noto: 20 righe di L58b e 5 di L55, 775 celle, 0 diverse.

- **Il meccanismo, misurato** (`meccanismo.csv`). Con la base-emettitore di Q132 in corto il VAS deve
  pilotare l'uscita direttamente, attraverso R130 + R134 (32 Ω), e senza la Vbe del finale. Tutta la
  tensione del moltiplicatore cade così sul finale PNP Q133, che per tenere l'uscita a zero chiederebbe
  ~35 mA. Il limitatore di ADR-099 ne concede ~20 (Q193 conduce 6 mA, il VAS ne porta 19,8). L'anello
  perde: lo specchio d'ingresso si spegne, Q125 va in saturazione e **l'uscita va al rail** (−13,6 V). Il
  VAS resta al limite con ~27 V ai capi, **0,528 W, 126 °C** con 60 °C d'aria. Nel blocco di prima di
  ADR-099 il VAS forniva quei ~30 mA, l'uscita restava a ~0 e la riga diceva «degrado silenzioso, 115 °C».
- **I modi fuori dai quindici** (`confronto.csv`): 91 modi del blocco, rifatti sul sorgente, contro la
  riga della FMEA che portava il calore del blocco di prima di ADR-097 / ADR-099.
  - Si scaldano meno quasi tutti: i finali da 87 a 79 °C grazie ai dissipatori, Q122 e Q146 in corto
    collettore-emettitore da 107 a 95 °C.
  - **Solo D158 in corto esce da P7: 126 °C**, perché è lo stesso guasto.
  - I picchi al jack coincidono con la FMEA entro 0,1 dB, salvo D158 in corto (da 87,9 a 136,6 dB SPL
    alla principale, l'uscita al rail).
- **La Stax** (`p10_stax.csv`): Q132 in corto base-emettitore e D158 in corto stanno **114,3 ms** sopra
  0,87 V, 120,0 ms col condensatore d'uscita a +5 %, contro i 150 di P10. Il caso noto (Q132_ce, Q133_ce)
  torna alla cifra.
- **La rete non conta**: il blocco vede i rail regolati a ±15 V a rete −10 / 0 / +10 % (ADR-099).

## Decisione

Parole dell'utente (2026-11-02), alla domanda con le tre opzioni e i loro numeri: **«Limitatore
36,5 + 18,7 Ω»**.

- R123 (dal rail filtrato alla presa del limitatore) **36,5 Ω**, R192 (dalla presa all'emettitore del VAS)
  **18,7 Ω**, in ciascuna delle otto istanze. Il sorgente, le netlist, i disegni e il deck del corto in
  mute (la potenza di R123 scritta come i² × 36,5) sono di L66.

## Perché

I numeri: `calore_lim365.csv`, `calore_lim365t60.csv`, `sintesi_regressione.csv`, `op_caldo.csv`,
`sintesi_caldo.csv` di `data/2026-11-02/L66/`.

- **Il calore**, 60 °C d'aria, VAS sulla piazzola minima:

  | | sorgente di prima (33 + 22) | 34,0 + 21,0 | **36,5 + 18,7** |
  |---|---|---|---|
  | Q132 in corto base-emettitore | 126 °C | 124 | **120** |
  | D158 in corto | 126 | 125 | **121** |
  | i quattro di ADR-099 (D102 / D103 aperti, Q125, R126 in corto) | 123–124 | 118–123 | **118–119** |
  | Q132 in corto base-emettitore, dispositivi a 60 °C | 121 | 119 | 115 |

- **Il blocco sano quasi non si muove** (21 deck, 42 703 misure): il margine di fase minimo passa da 43,33
  a 43,26°, Zout e continua cambiano entro lo 0,6 %. A caldo (ogni giunzione alla sua temperatura, aria
  a 57 °C) la distorsione a 20 kHz resta 0,000725 %, con 0 casi su 12 fuori e margine 2,7 dB.
  L'intermodulazione CCIF passa da −131,7 a −131,0 dB (margine 21,0 dB).
- **Il costo**: a riposo sulla 36,5 Ω cadono 0,39 V (erano 0,35), e il limitatore toglie alla base del
  VAS 0,25 / 3,3 / **23 µA** a 27 / 60 / 90 °C (erano 0,06 / 0,9 / 7,5) contro 83 / 68,5 / 58 µA di
  base. A 90 °C è il 40 %. Sul segnale la cifra di V4 a caldo non lo vede.
- **Il guasto resta un'uscita al rail**: alla principale ~137 dB SPL, come gli altri guasti del blocco al
  rail (i finali in corto collettore-emettitore). La principale e la fissa 1 contano sulla protezione a
  valle (ADR-081), la Stax sta dentro P10. Al tester si vede (`DIAGNOSI.md`: la continua al test point).

## Alternative scartate

- **34,0 + 21,0 Ω**: lo stesso cambio, più piccolo. D158 in corto a 125 °C esatti, margine zero.
- **Più rame sotto il VAS** (nessun cambio del circuito): basterebbe scendere da 125 a ≤ 123 °C/W. Il
  datasheet però non dà cifre tra la piazzola minima (125 °C/W) e i 50 × 50 mm (62,5), quindi oggi non si
  verifica. Sarebbe un vincolo per il layout (G2) come NC-072. Aggiunge anche capacità sul nodo NX, il
  polo dominante, che ADR-068 voleva evitare.
- **Un limite più alto**, per tenere l'uscita a ~0 come il blocco di prima: riporterebbe il VAS a
  229–307 °C nei guasti per cui ADR-099 ha messo il limitatore.

## Da riaprire se

- La misura sul prototipo dà al limitatore una corrente a riposo, a caldo, che si veda nella distorsione,
  oppure il VAS a caldo sotto il limite di ~20 mA su un carico vero.
- Il layout (G2) non dà la piazzola minima raccomandata al VAS: il margine è di 4–5 °C.
- Un VAS o un transistor del limitatore diverso (un'altra Vbe): la soglia si sposta.
