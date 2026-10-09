# L49a — la scheda audio, placement e routing di prova

Data: 2026-10-09 · Lotto: L49a · Decisioni: nessuna ADR (le scelte dell'utente qui sotto fissano
le condizioni della prova, non cambiano requisiti). Dati: `data/2026-10-09/L49a/` (README).
Sorgenti: `layout/preamp/audio/`.

## In breve

- **La scheda audio si piazza e si sbroglia per intero**, con le impronte del sorgente e la
  tecnologia scelta dall'utente: **399,0 × 162,8 mm**, due strati, tracce e isolamenti ≥ 0,25 mm
  (0,6 mm sui rail e sulla massa), fori passanti dove il sorgente li ha e relè, SOT-23 e SOIC-8 in
  superficie. 458 parti, 305 reti; Freerouting chiude **il 100 % in 45 s** (656 connessioni,
  21,7 m di rame, 117 via); **DRC 0 violazioni, 0 connessioni mancanti** (`run_drc.sh`, exit 0).
- **Nel Pesante 3U** (interni 415 fra i fianchi × 300 × ~115 mm) la scheda lascia **8 mm per lato**
  e **137 mm di profondità** davanti, che devono contenere l'alimentatore, i due toroidali, il
  corpo dei comandi del frontale e l'ingresso nel telaio dei connettori RCA posteriori. È il
  vincolo che passa a **L49b**, e a occhio è stretto: si misura là, non qui.
- **NC-048 aggiornata, resta aperta**: la scheda audio regge, l'assieme no ancora. Si chiude in
  L49b con l'alimentatore, i toroidali e il contenitore.
- **Nessun segnale passa da un canale all'altro.** I 16 relè sono condivisi (un polo per canale):
  stanno in una spina al centro, il sinistro a sinistra, il destro specchiato. Il router non ha
  portato **nessuna** rete di segnale dall'altra parte della spina. Il prezzo è la lunghezza:
  ogni segnale va al centro e torna — l'uscita principale **247 mm** a sinistra e **270 mm** a
  destra, la rete più lunga **288 mm** (uscita del blocco A → primo buffer sinistro).
- **Freerouting stringeva le tracce a 0,187 mm** sui piedini dei SOIC-8 (sotto lo 0,25 scelto) nel
  suo stadio di fan-out; non lo ferma l'impostazione di neckdown. Lo stadio è spento nelle
  impostazioni globali di Freerouting, **col permesso dell'utente**; `run.sh` rifiuta di partire
  senza. **limitations #50**, nuova.

## All'inizio, con l'utente

Le domande per nome, coi numeri misurati prima sulle netlist di oggi e sulle pagine dei
costruttori: la scheda audio **458 parti, 204 cm² di sole impronte** (~500 cm² di scheda stimati,
≈ 340 × 150 mm); l'alimentatore **118 parti, 48 cm²**; i 14 RCA e i 6 comandi del frontale
cablati; nessun dissipatore (gli MJE dissipano 0,3 W, L11).

1. **Il contenitore** — «Modushop Pesante 3U». La pagina del costruttore oggi (prodotto 162,
   «Pesante 03PN 3U 4mm BLACK», 72 €) dà esterni 435 × 305 × 122, **interni 430 × 300 × 120**,
   **frontale 483 × 132 × 4 mm**; hifi2000 dà **415 mm fra i fianchi**. Si prova sul minore, 415.
2. **Quante schede** — «Audio + alimentatore»: due, come dice P4.
3. **La tecnologia** — «2 strati, misto come oggi»: le impronte del sorgente, ≥ 0,25 mm.
4. **Dividere** — «Divisa»: L49a la scheda audio, **L49b** l'alimentatore, i toroidali e
   l'assieme nel contenitore.

A metà lotto, sulla domanda se toccare le impostazioni globali di Freerouting: **«puoi cambiare i
setting globali se serve»**. Alla fine: «fammi poi vedere in qualche modo placement e routing»
(le immagini sotto).

## Il metodo

`layout/preamp/audio/run.sh <out_dir> [gap] [block_w] [spine_gap]` fa tutto, da capo:

1. `make_board.py` — `kinet2pcb` dalla netlist del sorgente (`circuits/preamp/preamp_audio.net`,
   rigenerata e verificata uguale: 458 parti, nessun `_1` di #47, i nomi delle reti fuse diversi
   come vuole #23) e le regole: classe di default 0,25 / 0,25 mm, via 0,8 / 0,4; classe POWER
   0,6 mm su `GND`, `VPLUS`, `VMINUS`, `VRELAY`, `RLY_RET` (nomi espliciti, mai fusi).
2. `place.py` — il piazzamento **per gruppi funzionali**, letti dalla netlist (`SKiDL Line` e
   centinaia del riferimento): i blocchi A / B / F1 / F2 per canale (1xx/2xx/5xx/6xx a sinistra,
   3xx/4xx/7xx/8xx a destra), la striscia del canale (condensatori d'uscita e di disaccoppiamento,
   C_T, R_G, il partitore del trim), la spina dei relè, i connettori ai bordi. Dentro un gruppo le
   parti seguono la connettività (una visita in ampiezza sulle reti di segnale); il MMBT5551 subito
   dopo il suo MJE15032. Il contorno è un **risultato**: i gruppi impaccati più 4 mm, quattro fori
   M3. Un riferimento che cadrebbe su un vicino va sul livello F.Fab.
3. `route.py export` → Freerouting 2.4.1 (`-mp 40`, fan-out spento) → `route.py import`, che
   conta ciò che arriva (#9) e porta all'ampiezza minima le tracce più strette (in questa versione:
   **0**).
4. `run_drc.sh` e `drc_summary.py`; poi `measure.py` per i numeri di questo report.

## Le iterazioni

| # | Parametri (gap / blocco / spina, mm) | Scheda (mm) | Routing | DRC | Note |
|---|---|---|---|---|---|
| 1 | 1,5 / 55 / 1,5 | 364 × 231 | — | — | troppo profonda: strisce dei connettori da 26 mm (pettini 2×8 in piedi), canale in colonna |
| 2 | 1,5 / 75 / 1,5 | 375 × 200 | 100 %, 68 s | 32 errori + 6 avvisi | **0,187 mm** a 32 tracce sui SOIC-8 (fan-out) |
| 3 | idem, fan-out spento | 375 × 200 | **1 non sbrogliata** | — | K1 pin 6 (`BR_RG`) non esce dalla spina a 1,5 mm |
| 4 | 1,5 / 75 / **3,0** | 379 × 200 | 100 %, 39 s | **0 / 0** | prima versione pulita |
| 5 | 1,0 / 85 / 3,0 | 399 × 158 | 2 non sbrogliate | 2 cortile sovrapposti, 1 corto | **errore mio**: la striscia del canale dimensionata sul blocco nominale entrava nella spina |
| 6 | **1,0 / 85 / 3,0**, striscia corretta | **399,0 × 162,8** | **100 %, 45 s** | **0 / 0** | **la versione consegnata** |

Il passo 4 → 6 toglie **37 mm** di profondità alla stessa tecnologia. La scansione delle sole
dimensioni (`sweep_size.sh`, 12 combinazioni) è nel README dei dati; oltre 400 mm di larghezza
non si va (8 mm per lato su 415).

## I vincoli che tornano al progetto

Ognuno col suo numero. Nessuno cambia il circuito: quelli che lo cambierebbero sono **proposte**
per l'utente, non applicate.

1. **L'ingombro della scheda audio: 399,0 × 162,8 mm**, densità **32 %** (211 cm² di impronte su
   650). Nel Pesante: **8 mm** per lato, **137,2 mm** davanti (300 − 162,8), da cui L49b toglie la
   profondità dei RCA nel pannello posteriore, quella dei comandi del frontale (potenziometro ALPS
   RK27, i tre commutatori rotativi) e cerca posto per l'alimentatore (~160 × 100 mm stimati) e i
   due toroidali. **Se non ci stanno, le leve sono due**: compattare la scheda audio (il
   piazzatore è semplice, la densità è bassa; il routing a 1,0 mm chiude in 45 s, quindi c'è
   margine) o metterla a sbalzo sopra l'alimentatore. Lo decide L49b coi numeri.
2. **La spina dei relè condivisi** — 32 parti, **53,5 × 105,7 mm** al centro. **0 reti di segnale** con
   rame da entrambe le parti: i canali restano separati. Ma il polo del canale sta al centro, quindi
   le reti lunghe sono tutte del segnale:

   | Rete | mm |
   |---|---|
   | `F1L_IN` (uscita A sinistro → primo buffer) | 288,5 |
   | uscita principale destra (`R_MAINOUT`, J430) | 269,6 |
   | prima uscita fissa destra (`R_FIXOUT1`) | 264,0 |
   | `L_FIXC1` | 251,5 |
   | `L_TRIM_OUT` (trim → C_T → volume) | 247,0 |
   | uscita principale sinistra (`L_MAINOUT`, J230) | 246,6 |
   | ingressi, RCA → relè del selettore | 35,6 – 112,8 |

   Le uscite sono a bassa impedenza (47 Ω d'uscita) e reggono la lunghezza; la capacità di 25 cm
   di traccia si somma a quella del cavo, che V1 già prova. **Per G2** (vincolo di layout, non di
   circuito): i connettori delle uscite **vicino alla spina** e non all'estremo del bordo
   (qui, per semplicità, l'uscita principale sta all'estremo: è la causa dei 247 / 270 mm).
   L46a aveva lasciato «un dato per L49»: le celle non di verdetto perdono 10–17° col carico
   capacitivo sul nodo; la capacità di queste tracce va misurata dalla scheda di G2, non stimata
   da questa.
3. **I relè SMD della spina vogliono ≥ 3 mm** fra le impronte. A 1,5 mm il piedino 6 di K1 non
   esce senza il fan-out che stringe le tracce (iterazione 3).
4. **La coppia termica MJE15032 – MMBT5551**: centri a **10,94 mm** in tutti gli otto blocchi,
   uno accanto all'altro. L'accoppiamento **via rame senza unione galvanica** (ADR-034, NC-019,
   `gain_block.py`) **non è disegnato**: è del layout di G2, come dice il sorgente.
5. **Le altezze**: dai modelli 3D di KiCad la più alta è **C_T, 26 mm** (MKS4 31,5 × 17), poi i
   4,7 µF (21 mm) e i TO-220 (18,8 mm), contro ~115 mm interni. Il modello del 1000 µF D10 è
   generico (10 mm); uno vero è ~20–25 mm: lo dice la distinta, non cambia l'esito.
6. **La massa**: in questa prova è una rete di tracce da 0,6 mm (1,99 m), senza piano e senza
   stella. È un draft: la massa e la terra sono di **L50** (NC-044) e del layout di G2.
7. **I connettori** sono i pettini del sorgente (14 per i RCA, i pettini 2×8 dei commutatori):
   la scelta fra RCA sul circuito stampato e RCA sul pannello cablati cambia il bordo posteriore,
   ed è di G2.

## Il rilievo sul contenitore

Il frontale del Pesante 03PN venduto oggi è **483 mm**: oltre i **450 mm** di P8 / PR-27. ADR-029
citava una variante con frontale da 10 mm, 450 × 130, e il link del 2026-09-15 oggi apre il
prodotto da 483. **Non si risolve qui**: gli interni (415 × 300) sono quelli su cui si prova, e il
contenitore si sceglie entro G2 (P8). Va all'utente: un'altra variante del Pesante col frontale da
450, o un altro contenitore con almeno 415 × 300 interni.

## Le immagini

In `data/2026-10-09/L49a/`:

- `placement_3d_top.png` — la scheda vista dall'alto (render 3D di `kicad-cli`);
- `routing_both.png` / `.pdf` — i due strati di rame insieme (rosso sopra, blu sotto); il PDF si
  ingrandisce senza perdere dettaglio;
- `routing_top.png` / `.pdf` — rame sopra e serigrafia; `routing_bottom.png` / `.pdf` — rame sotto.

## Trappole nuove

- **limitations #50**: lo stadio di fan-out di Freerouting 2.4.1 stringe le tracce sotto l'ampiezza
  della classe, senza errore; `router.automatic_neckdown=false` e le variabili
  `FREEROUTING__ROUTER__*` non lo fermano. La DRC lo vede (`track_width`).
- Il jar di Freerouting e il file delle impostazioni non sono nel repo: `run.sh` usa il percorso
  assoluto del jar e verifica che il fan-out sia spento.
- Freerouting scrive una cartella `en/` nella directory da cui parte: in `.gitignore`.

## Non fatto

- L'alimentatore, i toroidali, i comandi del frontale e l'assieme nel contenitore: **L49b**.
- La chiusura di NC-048: L49b.
- Il layout vero: è di G2. Nessun export di fabbricazione (`export_fab.sh` non è stato lanciato).
- Il circuito non è cambiato.
