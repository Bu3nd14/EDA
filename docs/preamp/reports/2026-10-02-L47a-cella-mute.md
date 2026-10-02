# L47a — La cella del mute: il sostituto della VTL5C4 e il suo modello

Data: 2026-10-02 · Lotto: L47a · ADR: **ADR-058** · Non conformità: **NC-043** (resta aperta)

Dati: `data/2026-10-02/L47a/` (`nsl32sr3_modello/README.md`, `fonti/`).

## 1. Le decisioni dell'utente all'inizio

Il prompt di L47 chiedeva due cose prima del lavoro, per nome e non per sigle:
- **dividere il lotto?** Scelta: **in due**. L47a la parte e il modello; L47b il tempo del
  mute, il pilota e le misure (S, B, E3, E5, `VRELAY`, il commento di `C_VRELAY`, le catene a
  valle);
- **un tempo massimo del mute nel PRB?** Scelta: **«decido dopo la tabella»**. Il tempo di
  spegnimento della cella scelta entra nella domanda di L47b.

## 2. La ricerca dei sostituti

Fatta dal `bom-component-manager` col web. I candidati, verificati il 2026-10-02:

| Parte | Disponibilità | Buio | Accesa | Spegnimento a 100 kΩ | Esito |
|---|---|---|---|---|---|
| VTL5C4 (Excelitas) | fuori produzione dal 2015 | ≥ 400 MΩ | 125 Ω a 10 mA | 1,5 s | da sostituire |
| **NSL-32SR3** (Advanced Photonix) | **DigiKey 7867 pz, $4,11, Active** | **≥ 25 MΩ** | 150 Ω a 5 mA, ≤ 60 Ω a 20 mA | **10 ms** | **scelta** |
| VTL5C4 (Xvive) | solo rivenditori per hobbisti | **2 MΩ** tipici | ~230 Ω a 10 mA | 1,5 s | scartata |
| NSL-37V5C4 (AP) | non a DigiKey | 400 kΩ (PDF) / 400 MΩ (web) | 150 Ω a 10 mA | — | scartata |
| VTL5C3 (CoolAudio) | Banzai Music | ≥ 10 MΩ | 30 kΩ a 1 mA | 35 ms | scartata |
| NSL-32, NSL-32SR2 (AP) | DigiKey | 0,5 / 1 MΩ | ≤ 40 Ω | 80 ms | scartate |

Le verifiche dell'orchestratore, sui PDF:
- il datasheet vero di **Xvive** («Xvive5C4-R») dà Roff 2,0 MΩ. Quello che Aion FX e
  Synthrotek ospitano come «Xvive VTL5C3/VTL5C4» è la pagina 45 del catalogo Excelitas del 2001
  col titolo cambiato;
- il PDF della **NSL-37V5C4** dà 400 kΩ in intestazione e in tabella, coerenti con i 75 dB di
  dinamica dichiarati. La tabella web del costruttore dice 400 MΩ;
- lo stock di DigiKey della NSL-32SR3 è riletto dall'orchestratore.

Nessun costruttore pubblica la **dispersione fra esemplari**.

Datasheet congelati in `vendor/optocoupler/`:
- `silonex/NSL-32SR3/`, `luna/NSL-32SR3/`: le fonti del modello;
- `xvive/VTL5C4/`, `advanced_photonix/NSL-37V5C4/`: le prove degli scarti.

### Il residuo del mute, in dB SPL (un calcolo)

Prima che chiuda il relè al jack, la musica che passa a mute inserito è il rapporto fra la
cella in derivazione accesa e quella in serie al buio. Caso peggiore: +10 dB di guadagno,
2,7 V RMS alla sorgente, cima a 12 mA.

| Cella | Residuo al jack | dB SPL |
|---|---|---|
| VTL5C4 | ~3 µV | ~4 |
| NSL-32SR3 | ~43 µV | **~26** |
| Xvive | ~1,3 mV | **~55** |

Il limite di B è 100 µV, ~33 dB SPL. Le cifre sono calcoli dai dati dei datasheet: le misura
L47b.

### La scelta dell'utente

Le sue parole: «la NSL-32SR3 può andare bene, ma non posso misurare la curva, quindi dovremo
cercare in rete o fare assunzioni oppure cercare un altro modello».

## 3. Le curve in rete

Seconda ricerca del `bom-component-manager`. Nessuna fonte del costruttore scende sotto 0,1 mA.

| Fonte | Che cosa dà | Usata |
|---|---|---|
| Silonex 104058 Rev 07 (Farnell) | grafico log-log tipico, 5 punti, 0,1–40 mA | **sì**, sopra 0,1 mA |
| Luna Rev 01-04-16 (DigiKey) | grafico lineare, illeggibile sotto ~1 mA; le condizioni del buio | le condizioni |
| JC Maillet 2008, «Cell B» | 10 punti scritti a mano, 2,05 mA → 2,5 µA, **un esemplare** | **sì**, la forma sotto 0,1 mA |
| JC Maillet 2014, 61 pezzi | Ron a 2 mA 103–289 Ω, R a 10 µA 16–89 kΩ, non correlate | **sì**, la dispersione |
| Maillet 2008, schizzo dei tempi | ~e ogni 2,5 ms fino a 400 kΩ; fonte non trovata | no |
| Maillet 2020, polinomio SPICE | non riproduce la sua stessa tabella | no |
| Thread «Lightspeed» su diyAudio | anti-bot; e usa la SR2 | non letto |

L'orchestratore ha riletto:
- l'immagine della Cell B. Il punto a 4,7 µA ha le cifre sovrascritte: **escluso**;
- il grafico a dispersione dei 61 pezzi;
- il grafico Silonex, a pixel (`digit.py`): 2095 / 300 / 82,7 / 62,8 / 48,8 Ω a
  0,101 / 0,974 / 9,82 / 19,6 / 38,3 mA.

## 4. Il modello

`models/optocoupler/nsl32sr3_comportamentale.lib`, generato da
`data/2026-10-02/L47a/nsl32sr3_modello/genera_modello.py`. Ha la stessa struttura della VTL5C4
di L29b: lo stato log10(R) su un nodo, la statica per tabella, l'accensione e lo spegnimento
come equazioni dello stato.

**Le cinque curve**, perché i due estremi dei 61 pezzi non sono correlati:

| Curva | Accesa (2 mA) | Al buio (10 µA) |
|---|---|---|
| A | bassa | bassa |
| B | tipica | tipica |
| C | alta | alta |
| D (la più ripida) | bassa | alta |
| E (la più piatta) | alta | bassa |

Composizione:
- **la tipica B**: il grafico Silonex, e sotto 0,131 mA la forma della Cell B alzata di 1,456
  volte per raccordarsi;
- **l'inviluppo**: fattori in log10 rispetto alla tipica, ancorati agli estremi dei 61 pezzi, al
  buio 0,252–1,404 e accesa 0,513–1,439. Gli alti scendono a 0,962 a 20 mA, per i 60 Ω massimi.

**Le ipotesi**, tutte nell'intestazione del `.lib`:
- sotto 2,5 µA la pendenza dell'ultimo tratto fino a 25 MΩ, poi costante. La curva B arriva al
  buio a 0,33 µA; il comando riposa a 10 nA;
- salita: primo ordine, τ 1,526 ms;
- discesa: 292 decadi/s fino a 100 kΩ (il dato), poi **0,238 decadi/s** fino a 25 MΩ a 10 s,
  il tasso più lento compatibile: pessimistico per il residuo;
- CCELL 5 pF e CIO 0,5 pF della VTL5C4, non pubblicate;
- LED: diodo VTL5C4 + RS 42,5 Ω, 2,5 V a 20 mA (il massimo);
- nessuna temperatura, memoria della luce, distorsione, rumore.

### La verifica

| Controllo | Esito |
|---|---|
| `verifica_statica.py` | **84/84**: 70 nodi entro lo 0,05 %; buio 24,998 MΩ a 10 e 1 nA su ogni curva; C ed E 60,0 Ω a 20 mA; inviluppo 103/289 Ω e 16/89 kΩ esatti |
| `verifica_dinamica.py` (curva B) | **5/5** entro il 3 %: R a 5 ms 191,25 Ω (bersaglio 191,26, il 63 % della conduttanza finale); 99,8 kΩ 10 ms dopo lo spegnimento da 5 mA; 24,98 MΩ a 10 s |
| `sabotaggi.py` | **4/4** rilevati: un nodo +0,1 decadi, τ +30 %, il tasso di discesa −20 %, quello di coda −20 % |
| `validate_models.py` | **59/59** (era 57): ricetta nuova `tb_nsl32sr3`, sei punti più la cella in serie a 1 MΩ |
| `validate_models.py --check-provenance` | **27/27** |

## 5. Le trappole

Nuova voce: **limitations #40**. Dettaglio in `nsl32sr3_modello/README.md`.
- **Il LED.** Il solo diodo con IS ≈ 2·10⁻²³ (per 2,5 V a 20 mA con N = 2) non converge a
  10 nA. Il «transient op» finisce «successfully» con l'anodo a 0,2 V: una resistenza
  **negativa**, senza errore.
- **Le opzioni della verifica di L29b** (`abstol=1e-15`, 1 mV sulla cella). L'op del modello a
  stato dipende dal percorso di Newton: al buio fallisce a 7,30 / 7,3979 / 7,45 decadi e converge
  a 7,35 / 7,39 / 7,40.
  - La VTL5C4 converge solo perché il suo buio è a 8,6 decadi: portata a 7,3979 fallisce anche
    lei.
  - Un'induttanza da 10¹² H fra stato e bersaglio sposta il problema: provata e tolta.
  - Con le opzioni dei banchi veri (`abstol=1e-12`, come `tb_v2_casopeggiore.cir`) e 1 V sulla
    cella converge ovunque.
- **«failed» nel log non vuol dire fallito.** Il gmin stepping che riesce stampa prima «Dynamic
  gmin stepping failed». Le Note vanno su stderr.

## 6. Cosa resta a L47b

Dettaglio in ADR-058, «Cosa resta aperto per L47b».
- **Il tempo massimo del mute**, con l'utente: la NSL-32SR3 scende a 100 kΩ in 10 ms, la
  gradualità la dà il pilota.
- **Il sorgente**: le due celle per canale in `preamp_audio.py` diventano NSL-32SR3, con
  `Isolator:NSL-32` e `OptoDevice:Luna_NSL-32`. Il passo delle piazzole va confrontato col
  disegno (3,81 / 2,53 mm contro ~3,3 / 2,54).
- **La cima del LED (ADR-050)**. Il declassamento della corrente del LED non è pubblicato. Se
  vale quello della dissipazione della cella, a 60 °C restano **~7,2 mA**, sotto i 12 di oggi.
  Decisione dell'utente: ipotesi dichiarata o domanda al costruttore.
- **La caduta di due LED in serie**: fino a 5,0 V contro 4,0 (`psu.py`, riga 182).
- **Il profilo v4**, da rifare sull'inviluppo A–E (~5,5× nella regione del mute). Poi S, B, E3,
  E5, `VRELAY` a rete −10 %, il commento di `C_VRELAY`, le catene a valle.

## 7. Cosa non è cambiato

- `circuits/preamp/*.py`, i deck, il firmware, il PRB e `REQUIREMENTS.md`: nessuna modifica. I
  21 deck e la catena di L41c non si ricorrono, perché il circuito non cambia.
- Il modello della VTL5C4 resta in `models/`: le cifre canoniche lo usano fino a L47b.
- NC-043 resta **aperta**: si chiude con le misure sulla cella nuova.
