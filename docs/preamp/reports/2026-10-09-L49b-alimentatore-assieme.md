# L49b — l'alimentatore, i toroidali e l'assieme nel contenitore

Data: 2026-10-09 · Lotto: L49b · Decisioni: nessuna ADR (le scelte dell'utente qui sotto fissano le
condizioni della prova, non cambiano requisiti). Dati: `data/2026-10-09/L49b/` (README, con le
fonti di ogni misura). Sorgenti: `layout/preamp/psu/`, `layout/preamp/assembly/`.

## In breve

- **L'alimentatore si piazza e si sbroglia per intero**: **218,6 × 100 mm**, due strati, 118 parti,
  i rail a **1,0 mm**, segnali 0,4 mm, isolamenti ≥ 0,25 mm. **DRC 0 violazioni, 0 connessioni
  mancanti** (`run_drc.sh`, exit 0, rifatta sulla copia nei dati). 6,9 m di rame, 162 via.
- **La sezione di rete è separata**: una colonna sul bordo sinistro (J510, F501, J511, J512, K501)
  con 8 mm di fascia vuota; la bobina di K501 guarda la bassa tensione. **Misurato sul rame: 11,52 mm
  fra rete e bassa tensione**, contro i 6,4 mm di prova (2 × 3,2 mm, la lettura più severa trovata
  della norma, che **non è ancora identificata**: `SAFETY.md`). Fra L e N 2,41 mm, il passo della
  morsettiera.
- **L'assieme ci sta nel Pesante 3U** (interni 415 × 300 × 115 mm): tutto sul fondo, la scheda
  audio contro il pannello posteriore **sotto** i RCA e la presa IEC, i due toroidali e
  l'alimentatore davanti **sotto** i comandi del frontale. La fila toroidali + alimentatore occupa
  **386 mm su 415**. Ci sta **a una condizione**, che diventa un vincolo per G2: i comandi e i
  connettori a metà pannello, non in basso (gli assi dei comandi ≥ 63,7 mm dal fondo).
- **La stima di L49a non reggeva** perché contava i pannelli come fasce a tutta altezza: davanti
  alla scheda audio restavano 72,2 mm e T1 ne vuole 87,3. In altezza c'è posto: la scheda audio
  arriva a 33,6 mm, l'alimentatore a 43,1, T1 a 45,7, contro 115.
- **I toroidali** (P3): T1 a **214 mm** dagli ingressi e a **250 mm** da volume e bilanciamento,
  sotto i comandi in continua; T2 a 175 / 178 mm.
- **NC-048 chiusa.** Era l'ultima non conformità bloccante per G1.
- **Le piste di potenza**: l'utente ha chiesto di non stringerle («non vorrei ridurre le piste di
  potenza troppo, passiamo a 4 strati?») e ha scelto **«2 strati, stretta solo al piedino»**. I rail
  restano a 1,0 mm; i 114 tratti più stretti (≥ 0,35 mm, **lunghi al più 1,9 mm**) stanno solo
  all'ingresso dei piedini dei tre regolatori VQFN, della giunzione di massa NT501 e di quattro
  SOT-23 / SOIC, misurati uno per uno (`measure.json`).

## All'inizio e durante, con l'utente

Le scelte di L49a valgono (Pesante 3U, due schede, due strati, impostazioni globali di Freerouting
modificabili). In questo lotto:

1. **«poi dimmi per favore di preciso dove trovo i pdf e i png dello sbroglio audio e
   dell'alimentatore»** — sotto, «Le immagini».
2. **Le piste di potenza** — «non vorrei ridurre le piste di potenza troppo, passiamo a 4 strati?».
   La risposta, coi numeri: il collo ≤ 0,45 mm all'ingresso di un piedino VQFN (piazzole da 0,35 a
   passo 0,65) resta con 2 o con 4 strati; i 4 strati danno piani per i rail, ma anticipano la
   massa di L50 e la stella di P4. Scelta: **«2 strati, stretta solo al piedino»** (raccomandata).
3. **Il frontale da 483 mm** (oltre i 450 di P8 / PR-27) — **«Decidere al pre-layout»**: resta un
   punto aperto di G2, la prova vale per qualunque contenitore con almeno 415 × 300 × 115 interni.

## Il metodo

`layout/preamp/psu/run.sh <out> [altezza] [gap] [fascia] [gap logica] [rail]` fa tutto da capo:

1. `make_board.py` — `kinet2pcb` da `circuits/preamp/psu.net` (rigenerata da `psu.py` e verificata
   uguale: 118 parti, stesse reti) e le classi: default 0,4 mm; **POWER** e **POWER_WIDE** 1,0 mm
   (rail, ritorni, `VRELAY_REG`, i secondari); **MAINS** 1,0 mm (`AC_L`, `AC_N`, `T1_PRI_L`,
   `T1_PRI_N`, `T2_PRI_L`). Foro minimo 0,2 mm (vincolo 3). `classes.json`.
2. `place.py` — per gruppi: **rete** in colonna sul bordo sinistro, la fascia vuota, **rail**
   (le parti alte, poi ogni regolatore seguito dai suoi condensatori e diodi), **NT501** nel
   corridoio fra rail e 12 V (la stella fra `GND` e `RLY_RET`), **12 V**, **logica**. I regolatori
   hanno 3 mm di spazio proprio per lato. Il contorno è un risultato.
3. `escape.py` — le uscite dai piedini che il router non sa fare, disegnate e bloccate: i piedini di
   massa nella piazzola centrale, le coppie della stessa rete con un piedino in mezzo (ponticello;
   attorno a NR con una via), le coppie d'angolo, e una via d'ancoraggio per ogni gruppo dei rail.
4. `route.py export` (aggiunge al DSN le regole fra classi: rete ↔ resto a 6,4 mm) → Freerouting
   (fan-out spento, **restringimento automatico acceso solo per questa scheda**) → `route.py import`
   (toglie le vie d'ancoraggio rimaste inutili, copia `psu.kicad_dru`).
5. `run_drc.sh` con la regola su misura `mains_to_low_voltage` (6,4 mm); `measure.py`; `images.sh`.

`layout/preamp/assembly/floorplan.py` mette le due schede (dai loro `placement.json`), i toroidali,
i comandi, i RCA e la IEC nel contenitore, come scatole con la loro fascia d'altezza, e controlla
ogni coppia: si scontrano se si sovrappongono in pianta **e** in altezza (5 mm in pianta, 3 mm in
altezza).

## Le iterazioni

Trentacinque corse; la tabella le raggruppa per quello che hanno insegnato.

| # | Cambiamento | Esito (connessioni aperte / violazioni DRC) | Cosa ha insegnato |
|---|---|---|---|
| 1 | classi 0,4 / 1,0 / rete 6,4 mm nella classe | fermata a 44 / 68 dopo 9 passate | due cause: sotto |
| 2–3 | foro minimo 0,2 mm; gap 1,5 → 2,5 | 27 / 7 | le 7 sono tracce `AC_N` a **2,40 mm** dalla bobina di K501: la regola su misura le vede, il router no |
| 4 | regole Specctra fra classi (6,4 mm); rail 0,44 mm | 5 / **0** | la rete è a posto; le 5 aperte sono piedini VQFN |
| 5 | rail 1,0 mm col restringimento automatico | 7 / 2 | il restringimento funziona (≥ 0,35 mm), ma lascia aperti i piedini VQFN |
| 6–13 | `escape.py`: ponticelli, vie, angoli; K501 a destra, morsettiere a sinistra | 2–8 / 0 | ogni corsa apre punti diversi; il primario K501 → J512 passava a 6,4 mm dalla bobina |
| 14–15 | vie d'ancoraggio senza restringimento | 33–34 | senza restringimento non entrano neanche SOT-23 e SOIC |
| 16–23 | ancoraggi + restringimento; NT501 nel corridoio; logica a 3,5–4,5 mm | 2–4 / 0 | NT501 si collega; tre errori miei nella pulizia delle vie, trovati confrontando con «keep» |
| 24–27 | **rail a 0,6 / 0,8 / 1,0 mm** | 2–3 / 0 a ogni larghezza | **la larghezza dei rail non è la causa**: non c'era ragione di stringerli |
| 28–29 | i regolatori seguiti dai loro satelliti | 3–4 / 0 | i condensatori vicini, ma il regolatore soffocato |
| 30–33 | 3 mm di spazio proprio attorno ai regolatori | 1–4 / 0 | quasi |
| **34** | logica a 4,0 mm | **0 / 0** | **la versione consegnata**, 218,6 × 100 mm |
| 35 | replica della 34 | 2 / 0 | Freerouting non è ripetibile: i file consegnati sono quelli della 34, copiati |

## I vincoli che tornano al progetto

Nessuno cambia il circuito.

1. **L'alimentatore: 218,6 × 100 mm**, densità **22 %** (48,5 cm² di impronte). La rete in colonna
   su un bordo con 8 mm di fascia: **11,52 mm** misurati fra rete e bassa tensione (prova 6,4).
2. **I regolatori VQFN** (TPS7A4701 / TPS7A3301, passo 0,65 mm): una pista entra in un piedino al
   più a **0,45 mm** (0,35 di piazzola, 0,25 di isolamento), con 2 o con 4 strati. Il sorgente
   unisce piedini della stessa rete con un piedino in mezzo (IN su 13 e 15 attorno a NR su 14, OUT
   su 1 e 3): l'uscita va disegnata (`escape.py` lo fa per la prova). I regolatori vogliono
   **≥ 3 mm di spazio proprio** attorno per i rail da 1,0 mm. Per G2: le uscite a mano, e i rail
   come zone di rame si decidono con la massa di L50.
3. **Le vie termiche dell'impronta del sorgente** (`Texas_RGW0020A_..._ThermalVias`) hanno fori da
   **0,2 mm**: la fabbrica deve forarli, o G2 cambia impronta.
4. **Le morsettiere di rete** (Phoenix MKDS 1,5 a passo 5,08 mm) lasciano **2,48 mm** fra L e N,
   appena sotto i 2,5 mm di isolamento base letti per la tabella 17: è isolamento funzionale, e
   la cifra la decide la norma in G2; esistono a passo 7,5 mm. Il portafusibile del sorgente è
   l'**aperto** (`Fuseholder_..._Open`): `SAFETY.md` vuole un portafusibile chiuso.
5. **L'impronta D16 degli elettrolitici**: il 4700 µF 35 V esiste in D16 (Nichicon VY, 16 × 35,5),
   ma i più comuni sono D18: l'impronta vincola la distinta.
6. **L'assieme ci sta solo coi pannelli sopra le schede**: assi dei comandi **≥ 63,7 mm** dal fondo
   (la prova usa 65, circa metà dell'interno), i RCA in due file da 39 mm in su (sopra i 33,6 mm
   della scheda audio), la IEC con l'asse a ~80 mm. La scheda audio sta a 5 mm dal posteriore.
7. **L'ordine del frontale**: il lato di potenza è il sinistro (IEC, toroidali, la rete e i
   raddrizzatori dell'alimentatore), quindi da sinistra **selettore, guadagno, trim, mute** (in
   continua), poi **volume e bilanciamento** (il segnale), sopra la logica dell'alimentatore.
8. **Il filo di rete** dalla IEC al posteriore sinistro all'alimentatore corre ~170 mm lungo il
   fianco sinistro, **a 8 mm dal bordo della scheda audio**. ADR-010 vuole il cablaggio di rete
   lontano dall'audio: intrecciato e fissato al fianco, o la IEC altrove; è di G2 e di L50.
9. **Le altezze**: il più alto dentro è T1 coricato, 45,7 mm col disco di fissaggio; c'è margine
   verso i 115 mm interni (P5 e il calore restano di L30 e G2).
10. **Il frontale da 483 mm** del Pesante venduto oggi: si decide al pre-layout (scelta dell'utente).

## Le immagini

Tutte nel checkout principale, dopo il merge:

- **scheda audio (L49a)**: `/Users/roberto/EDA/docs/preamp/data/2026-10-09/L49a/` —
  `routing_both.pdf` / `.png`, `routing_top.pdf` / `.png`, `routing_bottom.pdf` / `.png`,
  `placement_3d_top.png`;
- **alimentatore (L49b)**: `/Users/roberto/EDA/docs/preamp/data/2026-10-09/L49b/psu/` — gli stessi
  nomi;
- **l'assieme**: `/Users/roberto/EDA/docs/preamp/data/2026-10-09/L49b/assembly/` —
  `assembly_A_tutto_sul_fondo.pdf` / `.png` (la variante che ci sta, pianta quotata e sezione),
  `assembly_A0_come_L49a.*`, `assembly_B_alimentatore_sotto.*`.

## Trappole nuove

- **limitations #51**: Freerouting non unisce due piedini della stessa rete con un piedino in mezzo
  a passo fine, e il suo restringimento automatico (che `FREEROUTING__ROUTER__AUTOMATIC_NECKDOWN=true`
  accende davvero) lascia aperti 2–8 collegamenti in posti diversi a ogni corsa; il suo log non è il
  verdetto («16 unrouted» con la DRC a 0 / 0).
- **limitations #52**: le classi di rete e il foro minimo stanno nel `.kicad_pro`, non nel
  `.kicad_pcb`: una scheda copiata da sola torna ai valori di KiCad, senza errore.
- **limitations #53**: in `pcbnew`, dopo `board.Remove()` la lista di `board.Tracks()` non è più
  iterabile; `GetEffectiveNetClass()` torna un oggetto senza metodi.
- **limitations #54**: Specctra porta un solo isolamento per classe; uno fra due classi diverse va
  aggiunto al DSN (`class_class`), e le regole `.kicad_dru` non arrivano al router.

## Non fatto

- Il layout vero: è di G2. Nessun export di fabbricazione.
- La norma di sicurezza: le distanze sono di prova, da fonti secondarie (`SAFETY.md`).
- La massa e la terra (L50): la massa resta una rete di tracce, con la stella in NT501 come nel
  sorgente.
- Il circuito non è cambiato.
