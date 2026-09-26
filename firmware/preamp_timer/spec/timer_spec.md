# Specifica del temporizzatore — il contratto del firmware

Versione: L41b1, 2026-09-26. Decisioni: **ADR-048** punto 6, **ADR-049**. Hardware:
`circuits/preamp/psu.py` (U509 ATtiny3216, U510 MCP4822, U508 i ritardi).

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

**Da verificare in L41b2**: SPI0 in modalità host prende PA2 come MISO. PA2 è anche AIN2
(`ADC_I_P`). Se la priorità della periferica lo impedisce, la SPI si fa in software sugli
stessi tre pin di uscita.

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
3. DAC: d = 1 (serie 10 nA, derivazione 20 mA);
4. **calibrazione** delle due stringhe (§ 5), a jack aperti;
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
2. `VRELAY_EN` = 0, **≥ 50 ms** dopo `PERMIT_REQ` = 0 (ADR-046);
3. `MAINS_REQ` = 0 nello stesso istante;
4. DAC in shutdown, poi power-down. In tutto ~7 s (ADR-046).

**4.5 Buco di rete** (MUSICA, RILASCIO, INSERZIONE → BUCO_RETE). Il criterio è `MUTE_G_IN`
basso mentre `MUTE_REQ` = 1:
1. **entro 1 ms** (interruzione su `MUTE_G_IN`): `MUTE_REQ` = 0, `PERMIT_REQ` = 0, d = 1
   subito, senza dissolvenza. Senza questo passo, al ritorno della rete il rivelatore
   rilascerebbe `MUTE_G` e i jack si ricollegherebbero a d = 0, in mezzo alla musica;
2. si classifica la causa con `ADC_MD`, `ADC_SUP_P`, `ADC_SUP_M`, `ADC_SUP_VR`:
   - **rete assente** (`ADC_MD` > 2,5 V) **e rail mai sotto |13,5 V|**: si resta in BUCO_RETE;
     al ritorno della rete e con i rail in regolazione per ≥ 500 ms, RILASCIO (4.3), cioè «la
     sequenza normale» (ADR-048 punto 5);
   - rete assente e un rail sceso sotto soglia: al ritorno si rifà l'ACCENSIONE (4.1) dal
     passo 2. Il micro, su V5, può anche essersi resettato: allora riparte da STANDBY;
   - **rete presente e un rail o `VRELAY_REG` fuori soglia**: GUASTO (4.6).

**4.6 Guasto con la rete presente** (qualunque stato → GUASTO):
1. `MUTE_REQ` = 0, `PERMIT_REQ` = 0, d = 1 (se non già fatto);
2. **≥ 50 ms** dopo: `MAINS_REQ` = 0 e `VRELAY_EN` = 0 (ADR-048 punto 5);
3. si resta spenti finché `FRONT_IN` non passa ad alto (spento) e poi di nuovo a basso: solo
   allora ACCENSIONE.

**4.7 Debounce**. `FRONT_IN` e `MUTE_SW_IN` hanno un primo polo in hardware (1 kΩ + 100 nF,
0,1 ms). Il firmware chiede **20 ms** di livello stabile. `MUTE_SW_IN` alto vale mute (F10,
ADR-028 punto 4): un filo rotto mette in mute.

**4.8 Watchdog**. Il watchdog dell'ATtiny è acceso con finestra ≤ 250 ms. Un firmware bloccato
va in reset, cioè in riposo (§ 1).

## 5. Il comando delle LDR (profilo v4, ADR-039)

**La legge**. Per una corrente di stringa I, con T la temperatura letta dal sensore del micro
(±3 °C tipici, DS40002205A Tabella 36-28):

- V_X = VREF + Vt(T) · ln(I / I_ref) + off + r_ohm · I
- I_ref = (V5 − VREF) / 24,9 kΩ ≈ 100 µA
- Vt = kT/q
- codice DAC = (V_X · (1/100k + 1/22,1k) − VREF / 22,1k) · 100k · 4096 / 4,096 V

**La calibrazione** (`off`, `r_ohm`, per stringa). A jack aperti, all'accensione e poi ogni
volta che la stringa sta ferma a 20 mA: la serie in MUSICA, la derivazione in MUTO. Si legge
`ADC_I_x` a 20 mA e a 2 mA (200 e 20 mV su 10 Ω), e si risolve e(I) = Vt · ln(I_voluta /
I_letta) = off + r_ohm · I. Senza calibrazione la cima sta a −3 dB (le resistenze parassite
dei transistor, L41b1). Con la calibrazione il profilo sta entro ±0,92 dB da 15 a 60 °C.

**La tabella** (profilo v4, Td = 6 s, da ADR-039 e dal contratto accanto a J3). d va da 0 a 1:

| d | Serie | Derivazione |
|---|---|---|
| 0 | 20 mA | 10 nA |
| 0,1 | 0,2 mA | 10 nA |
| 0,45 | 4,5 µA | 10 nA |
| 0,5 | (log-lineare) | 10 nA |
| 0,75 | 0,19 µA (ginocchio) | log-lineare, √(10 nA · 20 mA) = 14,1 µA |
| 0,8 e oltre | 10 nA | log-lineare |
| 1 | 10 nA | 20 mA |

Fra un punto e l'altro l'interpolazione è log-lineare (lineare in ln I). Il riposo è **10 nA,
mai 0**, su tutte e due le stringhe. Con il DAC in reset l'hardware dà 2–9 nA (L41b1).

**Aggiornamento**: ≥ 1 kHz durante le transizioni. C_X (1 µF, 18 ms) leviga i gradini.

**Non conformità aperta** (NC-038): a 58 °C nel telaio il LED della VTL5C4 non regge 20 mA
(40 mA − 0,9 mA/°C sopra 30 °C = 14,8 mA). La cima della tabella è dell'utente, con una ADR.

## 6. Cosa si prova sull'host (L41b2)

Un test per ogni sequenza di § 4, su `timer_core.c` compilato con `clang`:
- tempi ± la risoluzione del tick;
- le inversioni a metà;
- il debounce con rimbalzi;
- il buco di rete nelle tre classi;
- il guasto e la ritenuta;
- la legge del DAC contro la tabella di § 5, a 15, 25, 35, 45 e 60 °C.

Ogni asserzione si fa fallire su un falso. Le forme d'onda delle uscite si scrivono in CSV per
il generatore del banco, che le usa come micro comportamentale.
