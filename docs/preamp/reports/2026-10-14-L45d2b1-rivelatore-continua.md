# L45d2b1 — il rivelatore di continua sulle uscite dei blocchi

Data: 2026-10-14 · Lotto: L45d2b1 (prima parte di L45d2b) · Non conformità: NC-042 (avanza), **NC-063 (aperta)**

## In breve

L'utente ha diviso L45d2b in **tre parti** («Tre parti»): questa costruisce il rivelatore di
continua di **ADR-072**, le altre due fanno i diodi, il comando e i 5 V (L45d2b2) e i guasti rifatti
(L45d2b3). La realizzazione è **ADR-079**.

- **Il rivelatore** misura la **persistenza**, non usa un filtro.
  - Per ognuna delle sei uscite (F1, F2 e B per canale) c'è una finestra di ±0,58 V.
  - Scatta se l'uscita resta fuori dallo stesso lato per **71,6 ms** di fila (62,7–81,6 agli angoli).
  - Vive del maggiore fra il rail + e la linea dei relè.
- **La linea `DC_FLT`** è nuova, sul pin 4 di J4. Sull'alimentatore apre il mute, stacca la linea
  dei relè e il toroidale **in hardware**.
- **Il firmware** la legge su PA1, e va in GUASTO fino al frontale.
- **Sul banco dei guasti del blocco**, 762 corse in sette posizioni, **nessun guasto resta fuori da
  P10** (≤ 100 ms sopra 0,87 V al jack). Senza rivelatore erano fuori **45–53 per posizione**. Il
  peggiore ora è **90,0 ms**, e lo scatto tipico è a 73 ms.
- **Con la musica** non scatta mai.
  - Si è provato su 11 segnali, con B a +10 dB fino al clip e oltre E6.
  - Nessun segnale periodico sopra i 16 Hz lo fa scattare.
- **Le scelte 8 e 9 sono verificate.**
  - Il filo del rail aperto fra le schede: ≤ 73 ms col +, ≤ 59 ms col −.
  - Il condensatore d'uscita in corto seguito da un guasto del blocco: 0 corse fuori.
- **Trovata e aperta NC-063.** La partenza morbida dei regolatori, coi 10 µF di oggi, porterebbe il
  rail − su in **~12 s** contro i 2 s che il firmware concede. Il banco dell'alimentatore non l'aveva
  mai vista, perché i suoi regolatori non hanno partenza morbida. Va all'utente in L45d2b2.

## Le domande e le risposte

| Domanda | Risposta |
|---|---|
| Dividere il lotto? | «Tre parti» (il rivelatore; i diodi, il comando, i 5 V e i massimi; i guasti rifatti) |

Nessun «Da riaprire se» di ADR-072 è scattato: la soglia separa la continua dalla musica entro
100 ms, e i rail scendono in tempo. Le scelte di realizzazione stanno in ADR-079, con le alternative
scartate.

## Perché la persistenza e non un filtro

Il jack è accoppiato in alternata (τ ~1 s a vuoto). Quindi una continua di ~0,95 V all'uscita di un
blocco tiene già il jack sopra 0,87 V per più di 100 ms. Dei 148 guasti di L45b fuori da P10, 15
finiscono sotto 1 V e 57 sotto 2 V (`data/2026-10-14/L45d2b1/studio/dist_dc.py`).

Un filtro passa-basso da 1 a 4 poli, abbastanza pronto da vedere 0,95 V entro ~95 ms, scatta anche
sul primo semiperiodo di un basso a 20 Hz da 14 V (`studio/studio_filtro.py`). La persistenza lo
evita: nella banda di E9 la musica passa per zero almeno ogni 50 ms, e il T_HOLD minimo è 62,7 ms.

## Il circuito

| Dove | Cosa | Perché |
|---|---|---|
| `dc_detector.py` | per uscita: 300k / 150k / 300k allo 0,1 % (S = (v + 2 VDP) / 4), 4,7 nF | l'uscita portata a VDP / 2, senza rail negativo; 0,35 ms di filtro |
| | **634k dall'uscita a VMINUS** | toglie i 24 µA che lo spostamento mette nell'uscita: +0,18 µA netti (sotto, «Un difetto trovato») |
| | soglie 100k / 4,12k / 100k allo 0,1 %, 6,8 nF | ±0,58 V all'uscita (0,39–0,66 agli angoli) |
| | 12 canali TLV1704, temporizzatori 976k × 100 nF C0G, diodi su TMAX | uno per lato per uscita, ripartono a ogni rientro |
| | TLV1702: lo scatto a VDP / 2; l'inibizione all'accensione 1,43M × 100 nF (99 ms) | ratiometrico; i rail che salgono |
| | VDP = max(VPLUS, VRELAY) − 0,65 V, due 1N4148W | la scelta 8 |
| | MMBT5551 a collettore aperto su `DC_FLT`, verso RLY_RET | conduce solo sopra 3,7 V su TRIP |
| `preamp_audio.py` | le sei prese, J4 a quattro pin | 490 → 583 parti sulla scheda |
| `psu.py` | R548 10k a V5, C535 10 nF, **D525–D527 BAT54 su `MUTE_G`, `VR_G`, `MAINS_G`**, R549 47k a PA1 | in hardware, come D522 |
| firmware | `DC_FLT_IN` su PA1: ≥ 2 ms con l'alimentazione buona → GUASTO (spec 4.9) | la ritenuta |

Dimensionamento: `data/2026-10-14/L45d2b1/scelte/dimensiona.py`, che ha la sua `--prova` contro
un'integrazione a passi.

## La prova dello strumento

Il comparatore è **comportamentale** (`banco/inc/cmpoc.lib`), perché il modello del costruttore non
gira in ngspice. Il rivelatore da solo, su dodici casi noti contro la formula chiusa
(`banco/prova.csv`), dà **12 su 12**:
- gli scatti stanno 1,2–1,7 ms sopra il calcolo (il diodo e la corrente di TMAX);
- non scattano 0,50 V, il seno e la quadra a 20 Hz da 14 V, gli impulsi al 95 % a 20 Hz;
- scattano gli impulsi a 10 Hz, il guasto senza VPLUS e il guasto già presente all'accensione
  (180 ms).

## I guasti del blocco

Il banco di L45a / L45b col rivelatore vero al posto del ritardo ideale (`--taglio`). I deck sono
`banco/script/genera_rivelatore.py`, P10 lo misura `L45b/script/analizza_p10.py` invariato, la
sintesi è in `banco/guasti.md`.

| Posizione | Corse | P10 fuori prima (L45b) | **P10 fuori ora** | Scattati | Scatto mediano | P10 massimo ora |
|---|---|---|---|---|---|---|
| A | 108 | 45 | **0** | 50 | 69,8 ms | 90,0 ms |
| F1 | 106 | 52 | **0** | 53 | 73,2 ms | 76,4 ms |
| F2 | 106 | 51 | **0** | 53 | 73,2 ms | 76,4 ms |
| B | 112 | 48 | **0** | 52 | 73,2 ms | 76,3 ms |
| B a +10 dB | 112 | 53 | **0** | 59 | 73,1 ms | 76,4 ms |
| B, condensatore d'uscita in corto (scelta 9) | 112 | — | **0** | 51 | 73,2 ms | 76,4 ms |
| F1, condensatore d'uscita in corto (scelta 9) | 106 | — | **0** | 53 | 73,2 ms | 76,4 ms |

Ogni guasto che senza rivelatore usciva da P10 ora fa scattare il rivelatore. Alcuni scattano tardi,
fino a 1,9 s, perché la loro uscita deriva piano, ma il jack resta sotto il tetto. Il calore e le
colonne di ADR-070 dopo il rimedio sono di L45d2b3.

**Le corse che non finiscono**, trattate come in L45a / L45b:
- **R120 in corto**, in ogni posizione: il simulatore avanza di ~2 ms al minuto. Le corse arrivano
  a 0,45 s, oltre lo scatto (~73 ms) e il contatto staccato; P10 è 67,8–76,2 ms.
- **Q133 a emettitore aperto e R135 aperta**: corse fino a 0,6 s, P10 0 ms, nessuna continua.
- **R131 aperta**: col metodo gear arriva oltre 0,6 s, P10 0 ms.
- **Q146 in corto**: anche gear si ferma all'istante dello scatto. Con `rshunt = 1e10` (100 pS su
  ogni nodo) finisce, e P10 è 76,1–76,2 ms.

## Un difetto trovato, e corretto

Nella prima corsa dei guasti, Q106 in corto base-emettitore usciva da P10 in cinque posizioni
(111–124 ms), e sul principale era **peggio di prima**: 122 ms contro 66.
- **La causa.** Lo spostamento d'ingresso, a VDP / 2, spingeva **24 µA** nell'uscita del blocco. Un
  blocco che ha perso la spinta all'uscita (~150 kΩ) si spostava da −0,81 a +2,9 V. L'uscita passava
  per zero, il temporizzatore ripartiva, e il rivelatore cambiava il guasto che doveva vedere.
- **Il rimedio**: **634 kΩ dall'uscita a VMINUS**, che riporta la stessa corrente (+0,18 µA netti).
  Rifatte tutte le corse, Q106 è dentro P10 dappertutto.

## La musica, i rail, l'accensione

`banco/piccole.csv`:

| Caso | Esito |
|---|---|
| 20 Hz a E6 e al clip (B a +10 dB), quadra al clip, un periodo isolato | non scatta; TMAX ≤ 3,3 V contro ~7,2 V |
| impulsi a 20 Hz al 90 %, a media nulla | non scatta; TMAX 5,3 V, il margine minimo |
| 1 kHz a E6 e 1 kHz / 5 kHz al clip 2,3 dB oltre E6 | non scatta |
| 16 Hz e 10 Hz al clip (sotto la banda) | non scatta; TMAX 5,7 V a 10 Hz |
| il filo del rail + aperto fra le schede (scelta 8) | scatta a 221–223 ms; jack sopra 0,87 V ≤ 73 ms |
| il filo del rail − aperto | scatta a 454–463 ms; jack ≤ 59 ms |
| accensione: rail insieme in 20 o 200 ms, sfasati di 20 o 50 ms nei due sensi, + avanti di 100 ms | non scatta |
| spegnimento, anche storto | non scatta |
| − avanti di 100 ms | scatta a 378 ms: il blocco A tiene davvero −1 V per ~0,5 s, che arriverebbe alle fisse |
| **le partenze morbide dei datasheet** (+ in 1,4 s, − in 12 s) | **scatta a 0,79 s → NC-063** |

Una prima stesura col filtro d'ingresso a 3,5 ms mediava il clip asimmetrico di B a 1 kHz (−1,1 V
di media) e scattava dopo 325 ms: per questo il filtro è a 0,35 ms. Nella stessa stesura le soglie
avevano un ritardo diverso da quello degli ingressi, e all'accensione davano un falso scatto: ora
hanno lo stesso.

## L'alimentatore e il firmware

Il banco di L45c2, copiato (`data/2026-10-14/L45d2b1/psu/`), con la primitiva `riv`: `DC_FLT` tirata
finché il rivelatore ha alimentazione, al punto fisso col firmware.

**Prima di ogni cambio**, sul `psu.net` coi diodi nuovi, `perdita` ha dato il CSV del firmware
**identico byte per byte** a quello di L56.

| Caso | Mute | K501 | VRELAY < 6 V | VPLUS < 13,5 / < 1 V | GUASTO | Linea rilasciata | Fine |
|---|---|---|---|---|---|---|---|
| il rivelatore scatta in musica | subito | 3,5 ms | 19,7 ms | 92 / 797 ms | 2 ms | 576 ms | GUASTO, rete giù |
| C145 in corto (R144, 10 Ω, sul +), il rivelatore 72 ms dopo | 3,6 ms (sorvegliante) | 75,5 ms | 91,6 ms | 3,7 / 212 ms | 23 ms | 174 ms | GUASTO |
| C145 in corto, senza rivelatore | 3,6 ms | 106,5 ms | 183 ms | 3,8 / 244 ms | 23 ms | — | GUASTO |

**Il calore della scelta 10.** Il rivelatore toglie il toroidale prima:

| | Col rivelatore | Senza |
|---|---|---|
| Energia in R144 | 1,14 J | 1,37 J |
| Tempo sopra 1 W | 158 ms | 191 ms |
| Picco | 22,5 W | 22,5 W |

Che R144 lo regga è una domanda sulla parte, per la distinta (G2) e per L45d2b3.

**I test del firmware**: 84 controlli. **23 falsi su 23** fanno fallire il loro test; i quattro
nuovi sono:
- 31: la linea non letta;
- 32: PA1 ancora fra i liberi;
- 33: niente 2 ms;
- 34: la linea contata coi rail giù, cioè un buco di rete trasformato in GUASTO.

`ponte.c` legge `v(dc_flt_in)` se c'è; i banchi di prima non la scrivono, e lì vale alta.

## NC-063, la partenza morbida

I datasheet, coi 10 µF di `psu.py` sul piedino NR:
- **U501**: t_SS = 10⁵ · C_NR · ln 4 = **1,39 s** (SBVS204G, eq. 5);
- **U502**: t_SS = 1,2 ms/nF · C_NR = **12 s** (SBVS169D, eq. 1).

Il banco dell'alimentatore usa regolatori senza partenza morbida, e lì i rail salgono in 31 ms,
insieme entro 0,2 ms. Coi tempi veri il firmware (rail entro 2 s) andrebbe in GUASTO a ogni
accensione, e l'inibizione del rivelatore (0,1 s) non basterebbe. La scelta dei condensatori è anche
una scelta di rumore (ADR-020), quindi dell'utente: va a **L45d2b2**, che lavora sugli stessi
regolatori. Severità proposta: maggiore, prima di G1.

## Regressione

- `run_tests.sh`: **13 passati, 0 falliti**, col circuito finale. Ci sono dentro i relè a riposo, il
  cablaggio a quattro pin sulle due schede, i due disegni a blocchi (coi loro asserti sul rivelatore)
  e il firmware.
- `check_psu_harness.py` rifiuta la netlist audio di prima (J4 a tre pin) contro il `psu.net` nuovo.
- Netlist confrontate per contenuto (`netlist/confronta.py`): sull'audio solo parti aggiunte e J4;
  sull'alimentatore sei parti e J4.

## Limiti dichiarati

- Un segnale sotto i 16 Hz oltre ~0,6 V su un'uscita può farlo scattare.
- Il comparatore è comportamentale, e l'offset è solo a calcolo (±5,5 mV, in `dimensiona.py`).
- Per ~0,1 s dall'accensione non scatta (NC-063 per i tempi veri).
- Con un firmware vivo ma sbagliato (un secondo guasto) l'apparecchio può ciclare.
- Il rivelatore cieco è un guasto latente, ed è di L58.

## Il prossimo

**L45d2b2**: i diodi della tenuta e U502 (ADR-074), il comando e i 5 V (ADR-075), i massimi del
blocco col rail a ±20,3 V (ADR-078), e **NC-063** con l'utente, con l'inibizione del rivelatore
rifatta sulle rampe vere.
