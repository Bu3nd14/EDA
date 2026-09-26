# L41b1 — il temporizzatore dell'alimentatore: l'hardware, Δ in hardware, lo standby, il pilota delle LDR (2026-09-26)

**Mandato**: la prima metà di L41b (ADR-048 punto 6; NC-036, NC-037). Decisione: **ADR-049**.
Dati: `data/2026-09-26/L41b1/` (README). Sorgente: `circuits/preamp/psu.py` → `psu.net`, con
J509 `TIMER_IO` sostituito. Specifica del firmware: `firmware/preamp_timer/spec/timer_spec.md`.

**Sintesi.** L'utente ha approvato le tre proposte portate con le cifre:
- l'ATtiny3216 col DAC MCP4822;
- il firmware in `firmware/preamp_timer/`, provato sull'host;
- L41b diviso in due.

In `psu.py` ci sono ora:
- il micro;
- Δ in hardware;
- l'interruttore che toglie `VRELAY` alla scheda audio in standby, tenuto in hardware anche lui;
- i due convertitori esponenziali delle LDR.

Simulato sul circuito:
- **Δ ≥ 16,9 ms** col micro in reset, a zero, o in reset durante una perdita di rete o un guasto
  di U503; il controfattuale senza RC dà 0;
- **`VRELAY` a J1 = 0 V in standby**, con 92,5 mW dal secondario di T2;
- **il profilo v4 calibrato entro ±0,92 dB** da 15 a 60 °C;
- **il rumore all'anodo ~500 volte sotto il limite**.

Il 2j e il 2e sono estesi e fatti fallire su 15 falsi e sulla netlist di `main`. La scheda audio
non è toccata, e il deck V2 rigenerato è byte-identico.

**Aperte**:
- **NC-037** resta aperta, con un criterio numerico: la perdita a vuoto di T2 ≤ ~0,40 W;
- **apre NC-038**: il LED della VTL5C4 non regge 20 mA sopra ~52 °C, e il contratto di J3 li
  chiede anche a 58 °C;
- NC-036 resta aperta (L41b2, L41c).

## 1. Le decisioni

Portate all'utente nel piano del lotto, conversando e con i numeri. **L'utente ha approvato il
piano senza commenti**, il 2026-09-26: vale come risposta alle tre proposte. Sono in ADR-049:
1. **ATtiny3216 + MCP4822.**
   - In power-down il micro fa 0,1 µA tipici e 2 µA massimi (DS40002205A Tabella 36-5); il DAC
     in shutdown 3,3 µA (DS20002249B): meno dell'1 % dello standby.
   - Dopo un reset le uscite del micro sono in alta impedenza (§ 16.3.1).
   - Si programma via UPDI con strumenti liberi.
   - I tre datasheet sono ora in `vendor/` con la loro provenienza.
2. **Il firmware in `firmware/preamp_timer/`**: una specifica a tabella come contratto, la logica
   pura provata sull'host con `clang`, e le forme d'onda dei test come sorgenti del banco.
3. **L41b1 e L41b2.**

Le scelte di progetto (ADR-049 punti 4–7) non sono dell'utente: sono dimensionate in
`scelte/dimensiona.py` **prima** di entrare nel sorgente.

## 2. Il circuito

- **Δ in hardware.**
  - `PERMIT_T` si carica attraverso due diodi, da `MUTE_REQ` **e** da `PERMIT_REQ`; la scarica è
    332 kΩ · 100 nF C0G.
  - U508 A (TLV1702) lo confronta con `VREF` e libera `PERMIT_G`.
  - D522 (BAT54) tiene `MUTE_G` ≤ `PERMIT_G` + 0,3 V.
  - C527 (22 nF) ritarda la salita di `MUTE_G`.
- **Lo standby** (NC-037).
  - Q505 (AO3401A) fra `VRELAY_REG` (l'uscita di U503) e `VRELAY` (J1 pin 4, nome del
    contratto invariato).
  - Il suo gate lo tiene U508 B su `VR_T`, caricato da `PERMIT_T` e da `VRELAY_EN`: 1 MΩ ·
    100 nF, tre volte più lento di `PERMIT_T`.
  - K501, U504, C523 e U506 ch B restano su `VRELAY_REG`: il comportamento di L41a al guasto di
    U503 non cambia.
- **Il pilota delle LDR**, uno per stringa.
  - La coppia accoppiata BCM847BS: base di Q1 a `VREF`, e il collettore tenuto a `VREF`
    dall'op-amp (MCP6004) attraverso un inseguitore PNP, così I_ref = (V5 − VREF) / 24,9 k =
    100 µA.
  - La base di Q2 dal DAC, attraverso la rete 100 k / 22,1 k verso `VREF` e un buffer.
  - Uno specchio BCM857BS degenerato con 10 Ω fornisce la corrente all'anodo di J3.
  - Il catodo torna a GND attraverso 10 Ω, letti dal micro.
  - Un 56 Ω sul collettore dell'inseguitore limita la corrente a ~30 mA.
  - Un pull-down da 100 k sull'uscita del DAC fa del reset del DAC uno stato della scheda:
    2–9 nA.
- **Il micro**, U509, su V5:
  - quattro richieste, ciascuna col suo pull-down;
  - la SPI verso il DAC;
  - due ingressi a pannello con 1 kΩ + 100 nF;
  - sette letture: quattro sorveglianti e due correnti attraverso 47 kΩ, e `MUTE_G` attraverso
    1 MΩ;
  - il connettore UPDI J515.
- **ERC**: 21 avvisi e 2 «errori», spiegati nel sorgente. Sono le stesse due classi di L41a,
  più PC3 lasciato libero di proposito.

**Due difetti trovati dal 2e esteso**, prima di dare un numero:
- `MAINS_REQ` senza pull-down proprio;
- la rilettura di `MUTE_G` a 47 kΩ: un pin configurato come uscita alta avrebbe alzato `MUTE_G`
  scavalcando `MUTE_REQ`. Ora 1 MΩ: al massimo ~0,25 V.

## 3. Il banco (modelli dichiarati)

`deck/genera_tb_psu.py` è il generatore di L41a copiato ed esteso. Genera **da `psu.net`** e
rifiuta le parti che non conosce; i modelli sono nell'intestazione e nel README dei dati.
- **Micro, DAC, op-amp** sono comportamentali, con le cifre dei datasheet: uscite in alta
  impedenza al reset, 500 kΩ in shutdown, ±23 mA e 1 MHz.
- **Il 2N7002** ha VTO = 1,0 V: la soglia bassa è il caso peggiore per Δ, perché `MUTE_G`
  scende lento e i jack si staccano per ultimi.
- **Per i punti di lavoro** l'op-amp è una variante liscia. Con quella a gradino e guadagno 1e5,
  in 7 punti su 85 ngspice ripiegava sul «transient op», che restituiva uno stato non
  assestato: le due stringhe a 25 pA, un falso aggancio (limitations #33, aggiornata).
- **Un difetto del generatore stesso**, preso dal log: `%g` scriveva TE + 1 µs come «2», un PWL
  che non scendeva mai («non-increasing PWL time points»). Ora `%.12g`.

**Non modellati** (dichiarati):
- l'autoriscaldamento di Q2 a 20 mA (~44 mW);
- il calo del β e le perdite a bassa corrente;
- gli offset degli op-amp (±4,5 mV) e il rumore di op-amp e DAC;
- la perdita a vuoto di T2.

La caduta del LED nel modello **cresce** con la temperatura, al contrario di un LED vero: per
la tensione di conformità a 60 °C è una stima pessimistica.

## 4. Le cifre

**I criteri sono stati scritti prima delle corse** (intestazioni di `analizza_timer.py` e
`analizza_ldr.py`).

**Il temporizzatore**, nominale / angolo minimo (C −5 %, R −1 %, V5 4,90 V, `VREF` 2,505 V):

| Caso | Δ | `VRELAY` a J1 < 9,6 V |
|---|---|---|
| micro in reset | **18,8 / 16,9 ms** | 60 / 56 ms dopo `PERMIT_CMD` |
| micro a zero | 20,1 / 18,1 ms | idem |
| perdita di rete + micro in reset | 18,8 / 16,9 ms | idem |
| U503 cede + micro in reset | 18,8 / 16,9 ms | 25 / 27 ms dopo |
| controfattuale senza C528 | **0 ms: fallisce come deve** | — |

Poi i casi senza Δ da misurare:
- **perdita di rete col micro bloccato alto**: jack staccati a +14,3 ms dal rivelatore, e il
  permissivo non cade mai prima di Δ (qui mai, nei 400 ms);
- **firmware che abbassa solo `PERMIT_REQ`**: nessun relè si muove;
- **rilascio con solo `MUTE_REQ`**: `PERMIT_CMD` si eccita 0,04 ms prima di `MUTE_CMD`. È
  simultaneo ai fini pratici e ammesso dal contratto di J4; la sequenza di relè la decidono i
  loro ≤ 3 ms d'operazione;
- **standby**: `VRELAY` a J1 = 0,000 V; dal secondario di T2 **92,5 mW** (90,8 all'angolo
  minimo), senza la perdita a vuoto del trasformatore.

**Le LDR** contro la tabella v4 (errore in dB, 15–60 °C):

| Modo | Peggiore |
|---|---|
| legge a 25 °C, senza compensazione | +8,7 dB al riposo, +5,9 dB al ginocchio, −6,6 dB alla cima (60 °C) |
| compensata col sensore del micro | −3,1 dB alla cima (la parte ohmica, ~0,43 Ω), ≤ ±0,3 dB altrove |
| **compensata e calibrata a 20 mA / 2 mA** | **−0,92 dB alla cima, ≤ +0,41 dB altrove** |
| LED a 2,0 V (massimo) e V5 4,90 V, calibrata | −0,92 dB; lo specchio ha 0,59 V (15 °C) e 0,34 V (60 °C) ai capi |
| DAC in reset | 2,1–8,9 nA: mai 0, sotto il ginocchio di 190 nA |

**Il rumore** all'anodo della derivazione, contro 690 µV/√Hz:
- 1,05 µV/√Hz a 10 nA dal simulatore;
- ~1,4 µV/√Hz col DAC e gli op-amp aggiunti a mano, senza il filtro di C_X.

**I controlli**:
- 2j esteso: 7 falsi nuovi;
- 2e `--timer`: 8 falsi, uno per regola T1–T5;
- tutti falliscono col messaggio giusto, e falliscono anche sulla netlist di `main`
  (`falsi/esito.txt`).

## 5. Quello che resta aperto

- **NC-037 (standby)**: la causa è tolta, perché le bobine del trim non ricevono più `VRELAY` in
  standby. Il bilancio è 92,5 mW più la perdita a vuoto di T2, quindi per stare sotto 0,5 W T2
  deve perdere a vuoto **≤ ~0,40 W** a 230 V + 10 %. Si chiude:
  - col pezzo di T2 scelto sul suo datasheet (giro BOM, G2);
  - e con la misura sul prototipo.
- **NC-038 (nuova)**: la VTL5C4 declassa la corrente del LED di 0,9 mA/°C sopra 30 °C (40 mA a
  25 °C). A 52,2 °C il massimo è 20 mA; a 58 °C, il telaio chiuso di ADR-048, è 14,8 mA. Il
  contratto di J3 (ADR-039) chiede 20 mA a d = 0 e d = 1.
  - Il pilota li fa, e il limite hardware è ~30 mA: è la tabella a chiedere troppo.
  - Si chiude con una decisione dell'utente e una ADR: la cima a ~12 mA, o un limite di
    temperatura, o un altro pezzo.
  - La cima conta per E5 (la cella in serie accesa, 118 Ω a 20 mA): va rimisurata.
- **Il firmware** (L41b2): la specifica c'è, e il codice e i test no.
- **La sequenza sul circuito col firmware vero**: L41b2, con le forme d'onda del core come
  sorgenti.
- **NC-036** resta aperta: L41b2, poi L41c.

## 6. Cosa cambia nel repo

- `circuits/preamp/psu.py`, `psu.net`: il temporizzatore al posto di J509.
- `firmware/preamp_timer/`: il README e la specifica.
- `scripts/check_psu_harness.py` (2j) e `scripts/check_relay_safe_state.py --timer` (2e), che
  entra in `run_tests.sh`.
- `vendor/`: i datasheet di ATtiny3216, MCP4822 e MCP6004.
- `docs/limitations.md` #33: la forma DC del falso aggancio.
- ADR-049; NC-037 aggiornata, NC-038 aperta, NC-036 aggiornata; `SAFETY.md` (lo standby).
