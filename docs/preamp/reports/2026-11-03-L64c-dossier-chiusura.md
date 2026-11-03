# L64c — il dossier rigenerato, la chiusura

Data: 2026-11-03 · Lotto: L64c (la terza delle tre parti di L64) · Decisioni: **ADR-114**. Non
conformità: **aperta NC-078**. Dati: `data/2026-11-03/L64c/` (README). Il circuito non è cambiato.

## In breve

- **Le scelte dell'utente**: le righe della FMEA che dicevano il micro, **«Riscriverle ora»**; la FMEA
  nella pagina, **«Sintesi + alte + medie»**; le schede di prova del 9 ottobre, **«Togliere la
  sezione»**; la consegna, **«qui sul mac nella folder che dici tu, ma 3 PDF»**; R517 / R518 in corto,
  **«Accettare come C536»**, e i 5 V persi al jack, **«Accettare come U503»** (ADR-114); la FMEA del
  temporizzatore, **«Non conformità, lotto apposta»** (NC-078, L68).
- **Il dossier è completo**: `PARTI = ("audio", "alimentatore", "chiusura")`, e il generatore scrive
  accanto a sé `index.html` (282 KB), le figure, gli schemi e il riepilogo; la pagina autoconsistente
  fuori dal repo pesa 4,3 MB, il PDF A4 ha 65 pagine. «OK: tutti i controlli incrociati sono passati».
  **Sabotaggi 56 su 56**.
- **Il primo giro con `PARTI` completa non rifiutava niente**, ma la pagina diceva tre cose false: le
  schede di prova «sbrogliate dalle netlist di oggi», il firmware nella riga dell'alimentatore di «Cosa
  non dice», e «nessun modello del costruttore» nella provenienza dell'alimentatore. Nessun controllo le
  vedeva.
- **Le sezioni nuove**: gli schemi completi di L63 nelle loro sezioni; «I guasti singoli: la FMEA con le
  misure adottate»; «Cosa questo dossier non dice» riscritta; la provenienza dell'alimentatore letta
  dalle `.provenance.json`.

## Gli schemi completi

`audio.svg` (653 parti) e `psu.svg` (187) accanto a `index.html`, sotto il diagramma a blocchi della
loro sezione, coi PDF A2 nominati. Due controlli: `scripts/check_schematic.py` sul manifesto contro la
netlist di oggi, nei due sensi; e i due disegni **rifatti dal sorgente** fuori dal repo
(`script/ridisegna.sh`), uguali a quelli versionati — i manifesti byte per byte, gli SVG a meno della
data e degli identificativi casuali delle clip di matplotlib. Su A4 lo schema è illeggibile: va
all'utente anche come PDF a parte.

## La FMEA di oggi

Le fonti, dalla più vecchia: L45d2b3b3 (539 righe), L58a2 (15), L58b (60), L66 (145), L64c (28); la
riga più recente per chiave (ref, modo, caso). **563 righe: 15 alte, 67 medie, 476 basse, 5 escluse**
(prima dei rimedi: 101 alte, 56 medie, 327 basse; 79 righe di parti aggiunte dopo L45 senza un prima).
Il generatore le ricompone da sé e le confronta col CSV colonna per colonna; ricalcola ogni priorità
dalla matrice di ADR-070 (scritta come tabella, non copiata); cerca ogni parte nelle tre netlist; e
rifiuta una riga ancora «alla diagnosi», uno stato che si regge su una decisione superata, un micro o un
firmware nell'effetto o nello stato.

### Le 28 righe che dicevano il micro

Il controllo «decisione superata» ne ha trovate dieci, il controllo «parte che non esiste» altre: le
righe sono state riscritte dalle corse del circuito di oggi, sul banco di L64b (`psu/`, `modi.py` con i
dodici modi degli ingressi in più), **44 corse**, due alla volta.

| Righe | Prima | Oggi | La cifra |
|---|---|---|---|
| il sorvegliante dei rail, 10 righe (U505, il partitore, il riferimento), accettate con ADR-073 — la riserva del firmware, superata da ADR-102 | alta | **bassa** (gravità 1) | il jack staccato a 48,9 ms (canale +) e 16,2 ms (canale −) dal regolatore spento; al jack **87,5 µV, 32,3 dB SPL** e **14,4 µV, 16,6 dB SPL**: sotto V2. Le due sequenze ricorse uguali a L64b colonna per colonna |
| R517, R518 in corto (i pull-up del tasto del mute e dell'interruttore frontale) | bassa | **alta** (gravità 5), accettata (ADR-114) | i 5 V a 0,275 V attraverso l'interruttore chiuso, U504 **2,93 W, 241 °C** a calcolo (R518 anche U512 128 °C); niente musica, nessun colpo |
| R517, R542, C533 (aperto / corto): il tasto del mute | bassa | bassa | il tasto non inserisce il mute |
| R518, R541, C532 (aperto / corto): l'interruttore frontale | bassa | bassa | il frontale non spegne; si accende con la rete |
| R541, R542 in corto; C532, C533 aperti | bassa | bassa | come la corsa sana, o il comando 7 ms prima senza il polo del filtro |
| R543, R544–R547 | bassa | **esclusa** | le parti sono uscite col micro |
| C536 in corto | alta | alta, accettata (ADR-097, ADR-114) | i 5 V persi; U504 **2,99 W, 245,6 °C** (L45d2b3b1 uguale); al jack **6,51 mV, 69,7 dB SPL** |
| U512 spento | bassa | **media**, accettata (ADR-114) | i 5 V persi; al jack **6,51 mV, 69,7 dB SPL**, alle tre reti |

**I 5 V persi al jack**: i relè cadono tutti insieme, il guadagno si muove a 3,5 ms e il jack si stacca a
6,6 ms, 3,1 ms col jack collegato — la stessa sequenza del corto di U503. La catena di L64b, copiata
con il generatore del deck che prende i casi dall'ambiente, ridà `corto_u503` a **6,492 mV**, alla
cifra di L64b; il criterio (≤ 2 mV) era scritto prima delle corse.

### La copertura: NC-078

`script/copertura.py`: dell'alimentatore, **59 parti su 187 senza nessuna riga** — **37 del
temporizzatore a comparatori** (U513–U515, Q513 / Q514, D533, D537–D540, C545–C555, R569–R584), entrate
il 26 ottobre, due giorni dopo la chiusura di NC-042; 5 connettori; 17 test point. Solo R585 e i
quattro BAS416 hanno avuto le loro righe (L58a2). Sulla scheda audio il conto per nome non vale: le
righe nominano le parti per ruolo. **NC-078**, maggiore, prima di G1, col lotto L68.

## Le schede di prova

Le prove del 9 ottobre (L49a, L49b) sono di una netlist vecchia: alla scheda audio mancano 195 parti di
oggi (25 test point, 50 diodi, 92 resistenze, 24 transistor, …) e 67 valori sono cambiati;
l'alimentatore di prova ha 118 parti contro 187 e porta ancora il micro (U509 ATtiny3216) e il suo
connettore (J515). La sezione esce dalla pagina; «Cosa non dice» le nomina coi conti
(`parti_schede.csv`, rifatto dal generatore a ogni giro).

## Trovato

- **R517 / R518 in corto** scaldano U504 come C536 in corto: una riga a gravità 3 come «letture del
  micro» era in realtà a gravità 5. Accettata (ADR-114).
- **Il sorvegliante cieco è oggi un guasto di gravità 1**: il temporizzatore a comparatori stacca il jack
  in tempo, sotto la soglia di V2.
- **La FMEA non copre il temporizzatore** (NC-078).
- **La provenienza dell'alimentatore** diceva «nessun modello del costruttore»: i deck di oggi includono
  BAT54, BC847B, BC857B, 1N4148 e BAV199 del costruttore (ADR-104). Ora la classe si legge dalla
  `.provenance.json` di ogni file.

## Errori

- `copertura.py` applicava la mappa dei blocchi (R2xx…R8xx sul primo blocco) anche all'alimentatore, e
  C545 risultava coperta da C145: il conto diceva 58 e 36 invece di 59 e 37, e così l'ho detto
  all'utente nella domanda. Il generatore lo ha trovato confrontando il suo conto col CSV; corretto, e
  NC-078 dice 37.
- Le forme d'onda dei canali ciechi stavano solo nel worktree di L64b: la catena è caduta, le due
  sequenze sono state ricorse qui (uguali).
- Un sabotaggio scritto sulla priorità «prima» invece che su quella di oggi: corretto prima di correrlo.
