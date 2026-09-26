# Specifica del temporizzatore — il contratto del firmware

Versione: L41b2, 2026-09-26 (prima: L41b1). Decisioni: **ADR-048** punto 6, **ADR-049**,
**ADR-050**. Hardware: `circuits/preamp/psu.py` (U509 ATtiny3216, U510 MCP4822, U508 i
ritardi). Realizzazione: `src/timer_core.c`; prove: `test/` (L41b2).

**Cosa ha cambiato L41b2** (ogni voce ha la sua ragione nel testo sotto e nel report di L41b2):
- la cima della tabella a 12 mA (ADR-050, § 5);
- la calibrazione: il fit sulla corrente letta, lo zero dell'ADC, la cima che si assesta prima di
  `VRELAY_EN` (§ 4.1, § 5);
- 80 ms, non 50, fra `PERMIT_REQ` e il relè di rete (§ 4.4, § 4.6);
- la finestra di classificazione del buco (§ 4.5);
- il polo del fronte d'apertura dei due interruttori (§ 4.7);
- la SPI su PA2 verificata (§ 2).

Questo file è il **contratto** del firmware. Ogni riga delle tabelle è una cosa che un test
sull'host (`test/`, L41b2) deve poter asserire, e che si deve poter far fallire con un falso.
Quello che il firmware **non** deve garantire, perché lo garantisce l'hardware, è scritto in
§ 1: il firmware non lo deve né rifare né contraddire.

## 1. Quello che fa l'hardware, qualunque cosa faccia il firmware

Verificato sul circuito in L41b1 (`docs/preamp/data/2026-09-26/L41b1/timer/`) e sulla
netlist dal 2e (`check_relay_safe_state.py --timer`):

| Garanzia | Come | Cifra (L41b1) |
|---|---|---|
| Micro in reset, a zero, fermo: ogni relè a riposo | pull-down su `MUTE_REQ`, `PERMIT_REQ`, `MAINS_REQ`, `VRELAY_EN`; le uscite dell'ATtiny dopo un reset sono in alta impedenza (DS40002205A § 16.3.1) | 2e, T1–T2 |
| `PERMIT_CMD` si rilascia **≥ Δ dopo** `MUTE_CMD` | RC su `PERMIT_T` caricato da `MUTE_REQ` **o** da `PERMIT_REQ`, comparatore U508 A | Δ 18,8 ms nominale, **16,9 ms** all'angolo minimo |
| `PERMIT_CMD` si eccita **non dopo** `MUTE_CMD` | D522: `MUTE_G` ≤ `PERMIT_G` + 0,3 V | anticipo 0,04 ms col Vth minimo |
| Un firmware che abbassa solo `PERMIT_REQ` non muove niente | `PERMIT_T` resta carico da `MUTE_REQ` | nessun rilascio |
| `VRELAY` della scheda audio cade **dopo** `PERMIT_CMD` | RC su `VR_T` caricato da `PERMIT_T` e da `VRELAY_EN`, U508 B, Q505 | ≥ 56 ms dopo (24,7 ms col guasto di U503) |
| Il sorvegliante scavalca `MUTE_REQ` | U505, U506 tirano giù `MUTE_G` (L41a) | rete persa: jack staccati a +14 ms |

Quindi il firmware **non** conta Δ per la sicurezza: lo chiede (`PERMIT_REQ` giù 20 ms dopo
`MUTE_REQ`), e l'hardware lo garantisce comunque.

## 2. Ingressi e uscite

| Segnale | Pin | Verso | Significato |
|---|---|---|---|
| `FRONT_IN` | PC0 | ingresso | frontale: basso = acceso (tira a RET), alto = spento |
| `MUTE_SW_IN` | PC1 | ingresso | SW3: basso = musica; **alto = mute** (anche un filo rotto) |
| `MUTE_G_IN` | PC2 | ingresso | il verdetto dell'hardware (attraverso 1 MΩ): basso = mute imposto |
| `ADC_SUP_P` | PA5 (AIN5) | analogico | `VPLUS` × 10 / 54,2: 2,5 V a 13,55 V |
| `ADC_SUP_M` | PA6 (AIN6) | analogico | nodo del rail −: 1,25 V a −13,50 V, ~1,13 V a −15 V, ~2,3 V senza rail |
| `ADC_SUP_VR` | PA7 (AIN7) | analogico | `VRELAY_REG` × 10 / 44: 2,5 V a 11,0 V |
| `ADC_MD` | PB5 (AIN8) | analogico | rivelatore di rete: > 2,5 V = rete assente da ~15 ms |
| `ADC_I_S`, `ADC_I_P` | PB4 (AIN9), PA2 (AIN2) | analogico | corrente delle stringhe: 10 Ω a GND, 200 mV a 20 mA |
| `MUTE_REQ` | PB0 | uscita | alto = chiedo musica (jack collegati) |
| `PERMIT_REQ` | PB1 | uscita | alto = chiedo il permissivo K6 |
| `MAINS_REQ` | PB2 | uscita | alto = relè del toroidale K501 chiuso |
| `VRELAY_EN` | PB3 | uscita | alto = `VRELAY` alla scheda audio |
| `DAC_SDI`, `DAC_SCK`, `DAC_CS` | PA1, PA3, PA4 | uscita | SPI0 verso il MCP4822; VA = serie, VB = derivazione |

**SPI0 e PA2 (verificato in L41b2 sul datasheet)**. In modalità host MISO è un **ingresso**: la
periferica ne forza soltanto la direzione (DS40002205A, Tabella 25-1 e la nota sotto: «the pin
data direction for the signals marked with Input … is overridden»), e non pilota mai il pin. Un
pin d'ingresso è quello che l'ADC legge attraverso il proprio multiplexer (§ 30.2, AIN2), e lo
scavalcamento di una periferica riguarda solo quello che la periferica dichiara (§ 16.3.2.4).
PA2 resta quindi AIN2 (`ADC_I_P`), e la SPI è quella hardware. L'adattatore:
- scrive `SSD` = 1 in `SPI0.CTRLB` (§ 25.3.2.1.3): PA4 resta un'uscita qualunque, il `DAC_CS`;
- mette PA2 in `INPUT_DISABLE` (`PORTA.PIN2CTRL`, § 16.3.2.2): niente buffer digitale sul nodo
  analogico.

La SPI legge su MISO dati privi di senso, e non importa: il MCP4822 non risponde. **Da provare
sulla scheda**: una conversione su AIN2 con la SPI attiva, contro una a SPI spenta.

## 3. Gli stati

| Stato | `MAINS_REQ` | `VRELAY_EN` | `MUTE_REQ` | `PERMIT_REQ` | DAC (d) | Micro |
|---|---|---|---|---|---|---|
| STANDBY | 0 | 0 | 0 | 0 | shutdown | power-down, risveglio su `FRONT_IN` (entrambi i fronti) |
| ACCENSIONE | 1 | 0 → 1 | 0 | 0 | d = 1 | attivo |
| MUTO | 1 | 1 | 0 | 0 | d = 1 | attivo |
| RILASCIO | 1 | 1 | 1 | 1 | d: 1 → 0 | attivo |
| MUSICA | 1 | 1 | 1 | 1 | d = 0 | attivo |
| INSERZIONE | 1 | 1 | 1 → 0 | 1 → 0 | d: 0 → 1 | attivo |
| SPEGNIMENTO | 1 → 0 | 1 → 0 | 0 | 0 | d = 1 | attivo |
| BUCO_RETE | 1 | 1 | 0 | 0 | d = 1 | attivo |
| GUASTO | 0 | 0 | 0 | 0 | d = 1 → shutdown | attivo finché `FRONT_IN` non va spento |

## 4. Le sequenze

Ogni tempo porta la decisione che lo fissa. «Dopo X» vuol dire misurato da X.

**4.1 Accensione** (STANDBY → ACCENSIONE → MUTO o RILASCIO). `FRONT_IN` basso stabile per il
debounce:
1. `MAINS_REQ` = 1 (ADR-048 punto 4);
2. si aspetta che i rail siano in regolazione: `ADC_SUP_P` > 2,55 V e `ADC_SUP_M` < 1,20 V per
   ≥ 100 ms consecutivi. Senza rail entro **2 s**, si va in GUASTO;
3. **gli zeri**: si leggono `ADC_I_S` e `ADC_I_P` col DAC ancora spento (2–9 nA, ≤ 0,1 µV sui
   10 Ω), poi il DAC a d = 1 (serie 10 nA, derivazione 12 mA);
4. **calibrazione della derivazione** (§ 5): 200 ms alla cima, lettura; 200 ms a 2 mA, lettura;
   il fit; poi **200 ms alla cima corretta**, che si assesta con C_X (L41b2: sul circuito, 50 ms
   dopo il fit la cima era ancora a 10,6 mA, −1 dB). La serie resta a 10 nA: la sorgente non vede
   mai due celle accese insieme (ADR-038 punto 3). La serie si calibra in MUSICA (§ 5);
5. `VRELAY_EN` = 1;
6. si aspetta **≥ 50 ms**. Il minimo è 13 ms da `VRELAY` valida (ADR-027: 10 ms di set/reset
   più 3 ms di set time), e l'interruttore Q505 ci mette ~3 ms a chiudersi. Intanto le bobine
   del trim si pilotano col mute inserito;
7. se `MUTE_SW_IN` è basso: RILASCIO (4.3); altrimenti MUTO.

**4.2 Inserzione del mute** (MUSICA o RILASCIO → INSERZIONE → MUTO). Per `MUTE_SW_IN` alto, o
per il frontale spento (4.4):
1. d va verso 1 alla velocità del profilo, da dove si trova: 6 s da 0 a 1 (ADR-039);
2. a d = 1 più **0,5 s**: `MUTE_REQ` = 0 (contratto di J3);
3. **20 ms** dopo: `PERMIT_REQ` = 0 (Δ nominale, ADR-045; l'hardware tiene comunque ≥ Δ);
4. **reversibile a metà**: se `MUTE_SW_IN` torna basso prima del passo 2, d inverte il verso
   da dove si trova, senza accelerazione limitata (ADR-039). Dopo il passo 2 si fa un RILASCIO
   intero.

**4.3 Rilascio** (MUTO → RILASCIO → MUSICA). `MUTE_SW_IN` basso stabile:
1. `PERMIT_REQ` = 1 e `MUTE_REQ` = 1 nello stesso istante: l'hardware eccita `PERMIT_CMD`
   non dopo `MUTE_CMD`;
2. d va da 1 a 0 in 6 s, e parte **dopo** il passo 1 («il relè si riapre all'inizio del
   rilascio, prima che d si muova», ADR-039). Il firmware aspetta 10 ms, il tempo
   d'operazione del G6K;
3. reversibile a metà, come 4.2.

**4.4 Spegnimento** (qualunque stato acceso → SPEGNIMENTO → STANDBY). `FRONT_IN` alto stabile:
1. l'inserzione completa del mute (4.2), passi 1–3, se non è già in MUTO;
2. `VRELAY_EN` = 0, **80 ms** dopo `PERMIT_REQ` = 0. ADR-046 vuole il relè di rete ≥ 50 ms dopo
   **`PERMIT_CMD`**, che l'hardware rilascia Δ dopo `PERMIT_REQ` (18,8 ms nominali, ~21 ms
   all'angolo alto): 50 + 21, arrotondato. L41b1 aveva scritto 50 ms da `PERMIT_REQ`, e sul
   circuito K501 si apriva 33 ms dopo `PERMIT_CMD` (L41b2);
3. `MAINS_REQ` = 0 nello stesso istante;
4. DAC in shutdown, poi power-down. In tutto ~7 s (ADR-046).

**4.5 Buco di rete** (MUSICA, RILASCIO, INSERZIONE → BUCO_RETE). Il criterio è `MUTE_G_IN`
basso mentre `MUTE_REQ` = 1:
1. **entro 1 ms** (interruzione su `MUTE_G_IN`): `MUTE_REQ` = 0, `PERMIT_REQ` = 0, d = 1
   subito, senza dissolvenza. Senza questo passo, al ritorno della rete il rivelatore
   rilascerebbe `MUTE_G` e i jack si ricollegherebbero a d = 0, in mezzo alla musica;
   Anche `ADC_MD` > 2,5 V da solo fa scattare questo passo, e in MUTO (dove `MUTE_REQ` è già 0)
   è l'unico criterio. Nei 10 ms del RILASCIO in cui il G6K si chiude, `MUTE_G_IN` non si
   guarda: il gate sale 0,22 ms dopo `MUTE_REQ` (`psu.py`, C_MUTE_G). Alla fine di quei 10 ms,
   se `MUTE_G_IN` è ancora basso, l'hardware ha rifiutato il rilascio, e si entra qui (L41b2);
2. si classifica la causa con `ADC_MD`, `ADC_SUP_P`, `ADC_SUP_M`, `ADC_SUP_VR`, **entro una
   finestra di 20 ms** (L41b2). `MUTE_G` può cadere ~1 ms prima che `ADC_MD` passi 2,5 V: in
   L41b1 i jack si staccano a +14,3 ms e il rivelatore arriva a 2,5 V a ~15 ms. Finita la
   finestra senza la rete assente, un rail fuori soglia è la terza classe. Una caduta che
   niente spiega si tratta come la prima;
   - **rete assente** (`ADC_MD` > 2,5 V) **e rail mai sotto |13,5 V|**: si resta in BUCO_RETE;
     al ritorno della rete e con i rail in regolazione per ≥ 500 ms, RILASCIO (4.3), cioè «la
     sequenza normale» (ADR-048 punto 5);
   - rete assente e un rail sceso sotto soglia: al ritorno si rifà l'ACCENSIONE (4.1) dal
     passo 2. Il micro, su V5, può anche essersi resettato: allora riparte da STANDBY;
   - **rete presente e un rail o `VRELAY_REG` fuori soglia**: GUASTO (4.6).

**4.6 Guasto con la rete presente** (qualunque stato → GUASTO):
1. `MUTE_REQ` = 0, `PERMIT_REQ` = 0, d = 1 (se non già fatto);
2. **80 ms** dopo: `MAINS_REQ` = 0 e `VRELAY_EN` = 0 (ADR-048 punto 5, «completato il mute»:
   come in 4.4);
3. si resta spenti finché `FRONT_IN` non passa ad alto (spento) e poi di nuovo a basso: solo
   allora ACCENSIONE.

**4.7 Debounce**. `FRONT_IN` e `MUTE_SW_IN` hanno un primo polo in hardware, diverso sui due
fronti (corretto in L41b2):
- **alla chiusura** dell'interruttore, 1 kΩ + 100 nF: 0,1 ms;
- **all'apertura**, il pull-up di 100 kΩ (R517, R518) carica i 100 nF: τ = 10 ms, e il pin
  passa V5/2 dopo **7,0 ms** (misurato sul circuito in L41b2). L41b1 aveva scritto 0,1 ms per
  entrambi.

Il firmware chiede **20 ms** di livello stabile, contati dal primo campione che vede il nuovo
livello. `MUTE_SW_IN` alto vale mute (F10, ADR-028 punto 4): un filo rotto mette in mute.

**4.8 Watchdog**. Il watchdog dell'ATtiny è acceso con finestra ≤ 250 ms. Un firmware bloccato
va in reset, cioè in riposo (§ 1).

## 5. Il comando delle LDR (profilo v4, ADR-039)

**La legge**. Per una corrente di stringa I, con T la temperatura letta dal sensore del micro
(±3 °C tipici, DS40002205A Tabella 36-28):

- V_X = VREF + Vt(T) · ln(I / I_ref) + off + r_ohm · I
- I_ref = (V5 − VREF) / 24,9 kΩ ≈ 100 µA
- Vt = kT/q
- codice DAC = (V_X · (1/100k + 1/22,1k) − VREF / 22,1k) · 100k · 4096 / 4,096 V

**La calibrazione** (`off`, `r_ohm`, per stringa; ADR-049, ADR-050). La stringa a 12 mA, poi a
2 mA (120 e 20 mV su 10 Ω), 200 ms ciascuno per l'assestamento di C_X. Si legge `ADC_I_x` meno
**il suo zero** e si risolve

  e_k = Vt · ln(I_voluta,k / I_letta,k) = off + r_ohm · **I_letta,k**

aggiungendo il risultato alla calibrazione in uso.
- **Lo zero** di un pin si legge mentre la sua stringa sta a 10 nA (0,1 µV): la serie in MUTO,
  la derivazione in MUSICA, tutte e due all'accensione col DAC spento. Toglie l'offset dell'ADC
  e la perdita del pin attraverso i 47 kΩ: da soli costavano fino a ±0,95 dB, e −2,06 dB con
  50 nA di perdita (L41b2, `test_legge` bilancio).
- **L'ascissa è la corrente letta**: la caduta ohmica avviene alla corrente che scorre. Con quella
  voluta (L41b1) una pianta esattamente lineare lasciava −0,38 dB alla cima.
- **Quando**:
  - la derivazione all'accensione (§ 4.1, a jack aperti, la serie al buio) e in MUTO 1 s dopo
    l'arrivo;
  - la serie in MUSICA 1 s dopo d = 0: 200 ms a 2 mA, cioè ~850 Ω contro R_IN = 1 MΩ,
    −0,007 dB. Mai tutte e due le stringhe accese insieme (ADR-038 punto 3).
- Una lettura che chiede più di 30 mV di correzione è una stringa rotta, non un errore da
  correggere: la calibrazione si rifiuta e si tiene quella di prima.

Sul banco in continua (L41b2, cima a 12 mA) il profilo calibrato sta entro **+0,28 dB** da 15 a
60 °C, e la cima entro ±0,02 dB. Con gli errori tipici di ADC e sensore (±3 °C), sull'host: entro
**−0,88 dB**, quasi tutto il sensore al ginocchio.

**La tabella** (profilo v4, Td = 6 s, da ADR-039, **la cima da ADR-050**). d va da 0 a 1:

| d | Serie | Derivazione |
|---|---|---|
| 0 | **12 mA** | 10 nA |
| 0,1 | 0,2 mA | 10 nA |
| 0,45 | 4,5 µA | 10 nA |
| 0,5 | (log-lineare) | 10 nA |
| 0,75 | 0,19 µA (ginocchio) | log-lineare, √(10 nA · 12 mA) = 10,95 µA |
| 0,8 e oltre | 10 nA | log-lineare |
| 1 | 10 nA | **12 mA** |

Fra un punto e l'altro l'interpolazione è log-lineare (lineare in ln I). Il riposo è **10 nA,
mai 0**, su tutte e due le stringhe. Con il DAC in reset l'hardware dà 2–9 nA (L41b1).

**Aggiornamento**: ≥ 1 kHz durante le transizioni. C_X (1 µF, 18 ms) leviga i gradini.

**NC-038 è chiusa da ADR-050**: la VTL5C4 regge 13 mA a 60 °C, e la cima è 12 mA.

## 6. Cosa si prova sull'host (L41b2)

`test/run_host_tests.sh` (in `run_tests.sh`, blocco 2k). Un test per ogni sequenza di § 4, su
`timer_core.c` compilato con `/usr/bin/clang -std=c11 -Wall -Wextra -Werror -pedantic`:
- `test_sequenze`: accensione, inserzione, rilascio, inversione, spegnimento, debounce, buco di
  rete di classe 1 e 2, guasto e ritenuta. Il mondo (`mondo.c`) dà gli ingressi e una pianta
  delle stringhe con un errore vero (4,5 mV, 0,43 Ω);
- `test_legge`:
  - i codici del DAC contro quelli del banco di L41b1, 250 su 250;
  - `cal.json` di L41b1 ritrovato con la sua ascissa;
  - la tabella a 15, 25, 35, 45 e 60 °C;
  - il bilancio dell'ADC e del sensore.

`--falsi <file>`: 20 difetti (`FALSO_n` in `timer_core.c`), ognuno deve far fallire il proprio
test. Le forme d'onda delle uscite si scrivono in CSV (`--csv`), e `test/ponte.c` fa girare il
core sui pin del circuito simulato (`docs/preamp/data/2026-09-26/L41b2/deck/`).
