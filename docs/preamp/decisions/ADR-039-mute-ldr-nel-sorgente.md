# ADR-039 — Il mute graduale a LDR entra nel sorgente: due celle per canale, i LED in serie fra i canali su un cablaggio proprio, e il profilo v3 da 6 s come contratto del comando

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
(psu-engineer / L35). È il **profilo v3 con Td = 6 s**, scelta dell'utente del
2026-09-21:
- una sola profondità d ∈ [0, 1], reversibile: da 0 a 1 in 6 s all'inserzione, e
  indietro alla stessa velocità da dove si trova;
- **serie**, log-lineare a tratti: 20 mA a d = 0, 0,2 mA a d = 0,1, 4,5 µA a
  d = 0,45, 10 nA a d = 0,5 e oltre;
- **derivazione**: 10 nA fino a d = 0,5, poi log-lineare fino a 20 mA a d = 1;
- **10 nA di riposo** su entrambe le stringhe, mai zero;
- il **relè al jack** (`MUTE_CMD` diseccitato, jack a massa, ADR-012) si chiude
  0,5 s dopo d = 1 e si riapre all'inizio del rilascio, prima che d si muova;
- il rumore all'anodo della derivazione resta **sotto 0,69 mV/√Hz** piatto
  (`tb_e3_e5_ldr.cir`, per 1 µV al jack attraverso gli 0,5 pF LED–cella). Con un
  generatore di corrente è largo: a 10 nA la resistenza dinamica del LED è
  ~5 MΩ, quindi 130 pA/√Hz di rumore di corrente;
- il comando **non ha ancora accelerazione limitata**: un'inversione a metà cambia
  il verso di d di colpo (vedi «Da riaprire se»).

## Perché

- **I LED in serie fra i canali**: una corrente per funzione. Un errore del comando
  non può far dissolvere un canale più in fretta dell'altro. Resta solo la
  dispersione delle parti, che è di L29c. Costa il doppio della tensione di
  conformità del generatore: 2 × ~1,7 V a 20 mA.
- **Il connettore J3 invece del comando sulla scheda**: il generatore della
  profondità, il temporizzatore e il comando dei relè stanno insieme fuori scheda
  (ADR-012, `preamp_audio.py`, «cosa non è qui»). Mettere sulla scheda audio solo
  le celle tiene il comando lontano dal segnale, com'è scritto in ADR-022.
- **Il profilo v3** è la scelta dell'utente sulle cifre di v2 (report L29b §2.1). Con
  il tempo scritto a 16 cifre (`docs/limitations.md` #30), a 1 kHz e 100 kΩ
  (principale / fisse), sempre col modello comportamentale dal datasheet con
  estrapolazione dichiarata:
  - C2 d'inserzione **2,50 / 0,60 mV**;
  - rilascio **3,41 / 0,88 mV**;
  - inversione a d = 0,75 **7,36 / 2,15 mV**;
  - relè 0,067 / 0,057 mV;
  - A ≤ 33 nV, B2 0,29 µV;
  - carico sulla sorgente ≥ 714 kΩ lungo la sequenza.

  Il pavimento di C2 lungo tutta la sequenza vale ≤ 31 µV. Rilascio e inversione sono
  **fuori soglia**, e la ragione è misurata: al rilascio la cella in serie si
  accende alla velocità del LED, e il tratto 10 nA → 4,5 µA (d da 0,5 a 0,45) porta
  il livello da −62 a −26 dB in 150 ms (`data/2026-09-22/L29b2/v3_td6_nd15/stati_ev.txt`).
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
- **Il profilo v4** (proposta di L29b2, misurata e non adottata: la scelta del profilo
  è dell'utente, ADR-038). Serie come v3 fino a 4,5 µA a d = 0,45, poi fino a 0,19 µA
  a d = 0,75 e 10 nA a d = 0,8:
  - rilascio **1,47 / 0,30 mV**;
  - inserzione, relè, A, B e carico invariati;
  - inversione 5,01 / 1,40 mV.

  È scritta qui perché si ritrovi, non perché sia stata scartata: si aspetta la
  decisione dell'utente.

## Da riaprire se

- L'utente sceglie un altro profilo: la v4, o un comando con **accelerazione
  limitata** all'inversione. In v4 il picco dell'inversione cade all'istante
  dell'inversione (t = 5,502 s), dove d cambia verso di colpo. Cambia il contratto
  al punto 3 e il profilo di `tb_v2_mute_ldr.cir`, non le celle.
- La VTL5C4 non si trova (ADR-038). Serve una parte con due canali e una curva
  pubblicata; il simbolo e il footprint cambiano.
- La tensione di conformità del comando non basta per due LED in serie. Allora le
  stringhe si separano, e il confronto fra i canali passa alla dispersione del
  comando.
- Il prototipo contraddice il modello comportamentale: rumore in eccesso della cella,
  memoria della luce, estrapolazione ad alta resistenza.
