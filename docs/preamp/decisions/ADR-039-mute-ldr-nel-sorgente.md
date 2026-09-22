# ADR-039 — Il mute graduale a LDR entra nel sorgente: due celle per canale, i LED in serie fra i canali su un cablaggio proprio, e il profilo v4 da 6 s come contratto del comando

Data: 2026-09-22 · Stato: accettata

## Contesto

ADR-038 ha scelto il mute graduale **a monte**, con due fotoresistenze VTL5C4 per
canale all'ingresso del blocco A, e L29b l'ha misurato in uno scratch sulla catena.
Il report di L29b lo diceva: il profilo del comando dei LED «diventa decisione di
progetto quando va nel sorgente, in L29b2». Questa è quella decisione. Fissa:
- dove stanno le celle in `circuits/preamp/preamp_audio.py`;
- come arriva il comando;
- che cosa il comando, fuori scheda, deve rispettare.

## Decisione

**1. Le celle** (`channel()`, riferimenti U101/U102 a sinistra e U301/U302 a destra;
nessun riferimento esistente cambia):
- la **serie** fra il pin 1 del connettore d'ingresso e l'ingresso del blocco A;
- la **derivazione** dall'ingresso del blocco A (il nodo di R_IN = 1 MΩ) a GND.

Simbolo `Isolator:VTL5C`, footprint `OptoDevice:PerkinElmer_VTL5C`.

**2. Il comando** esce su un connettore proprio, **J3 `LDR_CMD`**:
- pin 1–2, la stringa della serie;
- pin 3–4, la stringa della derivazione.

Sulla scheda nessun LED tocca una rete di segnale (ADR-022). **I LED della stessa
funzione sono in serie fra i due canali**: serie L poi serie R, derivazione L poi
derivazione R. È una scelta di L29b2, non dell'utente.

**3. Il contratto del comando**, fuori scheda come il temporizzatore del mute
(psu-engineer / L35). È il **profilo v4 con Td = 6 s**: Td è la scelta dell'utente del
2026-09-21, il profilo v4 la sua scelta del 2026-09-22 (ADR-040), al posto della v3:
- una sola profondità d ∈ [0, 1], reversibile: da 0 a 1 in 6 s all'inserzione, e
  indietro alla stessa velocità da dove si trova;
- **serie**, log-lineare a tratti: 20 mA a d = 0, 0,2 mA a d = 0,1, 4,5 µA a
  d = 0,45, **0,19 µA a d = 0,75** (il ginocchio del buio), 10 nA a d = 0,8 e oltre;
- **derivazione**: 10 nA fino a d = 0,5, poi log-lineare fino a 20 mA a d = 1;
- **10 nA di riposo** su entrambe le stringhe, mai zero;
- il **relè al jack** (`MUTE_CMD` diseccitato, jack a massa, ADR-012) si chiude
  0,5 s dopo d = 1 e si riapre all'inizio del rilascio, prima che d si muova;
- il rumore all'anodo della derivazione resta **sotto 0,69 mV/√Hz** piatto
  (`tb_e3_e5_ldr.cir`, per 1 µV al jack attraverso gli 0,5 pF LED–cella). Con un
  generatore di corrente è largo: a 10 nA la resistenza dinamica del LED è
  ~5 MΩ, quindi 130 pA/√Hz di rumore di corrente;
- il comando **non ha accelerazione limitata**: un'inversione a metà cambia il verso
  di d di colpo. Col criterio di ADR-040 non serve (l'inversione della v4 salta di
  3 dB in 100 ms); resta un margine disponibile (vedi «Da riaprire se»).

## Perché

- **I LED in serie fra i canali**: una corrente per funzione. Un errore del comando
  non può far dissolvere un canale più in fretta dell'altro. Resta solo la
  dispersione delle parti, che è di L29c. Costa il doppio della tensione di
  conformità del generatore: 2 × ~1,7 V a 20 mA.
- **Il connettore J3 invece del comando sulla scheda**: il generatore della
  profondità, il temporizzatore e il comando dei relè stanno insieme fuori scheda
  (ADR-012, `preamp_audio.py`, «cosa non è qui»). Mettere sulla scheda audio solo
  le celle tiene il comando lontano dal segnale, com'è scritto in ADR-022.
- **La v4 al posto della v3.** Al rilascio la cella in serie si accende alla velocità
  del LED: con la v3 il tratto 10 nA → 4,5 µA (d da 0,5 a 0,45) portava il livello da
  −62 a −26 dB in 150 ms (`data/2026-09-22/L29b2/v3_td6_nd15/stati_ev.txt`). La v4
  distende quel tratto fino al ginocchio del buio. Sulla catena, a 1 kHz e 100 kΩ, col
  tempo scritto a 16 cifre (`docs/limitations.md` #30) e il modello comportamentale
  dal datasheet con estrapolazione dichiarata:

  | Principale / fisse | v3 | v4 |
  |---|---|---|
  | salto in 100 ms (ADR-040): inserzione / rilascio / inversione | 7 / **30** / 7 dB | 7 / 4 / 3 dB |
  | C2 (diagnostica): inserzione | 2,50 / 0,60 mV | 2,50 / 0,60 mV |
  | C2: rilascio | 3,41 / 0,88 mV | 1,47 / 0,30 mV |
  | C2: inversione a d = 0,75 | 7,36 / 2,15 mV | 5,01 / 1,40 mV |
  | relè; A; B2 | 0,067 mV; ≤ 33 nV; 0,29 µV | uguali |
  | carico minimo sulla sorgente | 714 kΩ | 714 kΩ |

  La sovrapposizione con la derivazione (d da 0,5 a 0,75) avviene con R_s ≥ 2 MΩ: la
  sorgente non vede mai un carico basso (ADR-038 punto 3).
- **E3 ed E5** reggono con le celle nel sorgente (`tb_e3_e5_ldr.cir`):
  - |Zin| ≥ 111,6 kΩ con 68 pF, in gioco, in mute e a metà, in ogni posizione del
    trim;
  - E5 ≤ 4,957 µV contro 9,90, con +0,04 µV per la cella in serie a 118 Ω (curva D).

## Alternative scartate

- **Un generatore per cella** (quattro stringhe): i canali possono dissolversi a
  velocità diverse per un errore del comando, e J3 raddoppia.
- **Il comando dei LED sulla scheda audio**: porta il generatore e la sua
  alimentazione accanto al nodo a 1 MΩ, contro ADR-022, e anticipa il progetto del
  temporizzatore, che non è di questo lotto.
- **Il profilo v3** (scelta dell'utente del 2026-09-21, report L29b): al rilascio salta
  di 30 dB in 100 ms, oltre i 20 dB di ADR-040. Resta generabile nel deck per
  confronto.
- **Un profilo progettato per C2 ≤ 1 mV** (ricerca di L29b2, `transizione/`): non
  realizzabile in 6 s coi limiti di spegnimento della cella; superato da ADR-040.

## Da riaprire se

- Serve margine sul salto: un comando con **accelerazione limitata** all'inversione
  (in v4 il picco di C2 dell'inversione cade all'istante in cui d cambia verso,
  t = 5,502 s). Cambia il contratto al punto 3 e il profilo di `tb_v2_mute_ldr.cir`,
  non le celle.
- La VTL5C4 non si trova (ADR-038). Serve una parte con due canali e una curva
  pubblicata; il simbolo e il footprint cambiano.
- La tensione di conformità del comando non basta per due LED in serie. Allora le
  stringhe si separano, e il confronto fra i canali passa alla dispersione del
  comando.
- Il prototipo contraddice il modello comportamentale: rumore in eccesso della cella,
  memoria della luce, estrapolazione ad alta resistenza.
