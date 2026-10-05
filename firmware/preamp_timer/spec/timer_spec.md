# Specifica del temporizzatore — il contratto del firmware

Versione: **L47c2a, 2026-10-05** (prima: L41b2, L41b1). Decisioni: **ADR-048** punto 6,
**ADR-049**, **ADR-062** (il mute taglia: niente sfumatura, niente pilota delle LDR, i relè subito
dopo il tasto). Hardware: `circuits/preamp/psu.py` (U509 ATtiny3216, U508 i ritardi).
Realizzazione: `src/timer_core.c`; prove: `test/`.

**Cosa ha cambiato L47c2a** (ogni voce ha la sua ragione nel testo sotto e nel report di L47c2a):
- via la legge delle LDR, la calibrazione, la sfumatura (d) e la SPI verso il MCP4822: l'hardware
  che servivano è uscito da `psu.py` in L47c1 (ADR-062). Il § 5 di prima non c'è più;
- l'inserzione del mute: `MUTE_REQ` giù **appena il tasto è stabile**, poi Δ (§ 4.2). Non è più
  reversibile a metà: lo stato d'inversione non esiste;
- il rilascio: i relè, i 10 ms del G6K, MUSICA (§ 4.3);
- l'accensione senza zeri né calibrazione (§ 4.1); lo spegnimento in ~0,12 s invece di ~7 (§ 4.4);
- **i pin liberi** (PA1, PA2, PA3, PA4, PB4, e PC3 che lo era da L41b1): il buffer d'ingresso
  digitale disattivato, scelta dell'utente (§ 2).

**Cosa aveva cambiato L41b2**: la cima a 12 mA e la calibrazione (superate da ADR-062); 80 ms, non
50, fra `PERMIT_REQ` e il relè di rete (§ 4.4, § 4.6); la finestra di classificazione del buco
(§ 4.5); il polo del fronte d'apertura dei due interruttori (§ 4.7).

Questo file è il **contratto** del firmware. Ogni riga delle tabelle è una cosa che un test
sull'host (`test/`) deve poter asserire, e che si deve poter far fallire con un falso.
Quello che il firmware **non** deve garantire, perché lo garantisce l'hardware, è scritto in
§ 1: il firmware non lo deve né rifare né contraddire.

## 1. Quello che fa l'hardware, qualunque cosa faccia il firmware

Verificato sul circuito in L41b1 (`docs/preamp/data/2026-09-26/L41b1/timer/`), **ricorso senza
il pilota delle LDR in L47c2a** (`docs/preamp/data/2026-10-05/L47c2a/timer/`), e sulla netlist
dal 2e (`check_relay_safe_state.py --timer`):

| Garanzia | Come | Cifra (L41b1 → L47c2a) |
|---|---|---|
| Micro in reset, a zero, fermo: ogni relè a riposo | pull-down su `MUTE_REQ`, `PERMIT_REQ`, `MAINS_REQ`, `VRELAY_EN`; le uscite dell'ATtiny dopo un reset sono in alta impedenza (DS40002205A § 16.3.1) | 2e, T1–T2 |
| `PERMIT_CMD` si rilascia **≥ Δ dopo** `MUTE_CMD` | RC su `PERMIT_T` caricato da `MUTE_REQ` **o** da `PERMIT_REQ`, comparatore U508 A | Δ 18,8 ms nominale, **16,9 ms** all'angolo minimo (uguali) |
| `PERMIT_CMD` si eccita **non dopo** `MUTE_CMD` | D522: `MUTE_G` ≤ `PERMIT_G` + 0,3 V | anticipo 0,04 ms col Vth minimo |
| Un firmware che abbassa solo `PERMIT_REQ` non muove niente | `PERMIT_T` resta carico da `MUTE_REQ` | nessun rilascio |
| `VRELAY` della scheda audio cade **dopo** `PERMIT_CMD` | RC su `VR_T` caricato da `PERMIT_T` e da `VRELAY_EN`, U508 B, Q505 | ≥ 56 ms dopo (24,7 col guasto di U503) → **60,4 / 56,5 ms** nominale / angolo minimo (**42,0 / 43,2** col guasto di U503) |
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
| `MUTE_REQ` | PB0 | uscita | alto = chiedo musica (jack collegati) |
| `PERMIT_REQ` | PB1 | uscita | alto = chiedo il permissivo K6 |
| `MAINS_REQ` | PB2 | uscita | alto = relè del toroidale K501 chiuso |
| `VRELAY_EN` | PB3 | uscita | alto = `VRELAY` alla scheda audio |
| — | PA1, PA2, PA3, PA4, PB4, PC3 | **liberi** | niente in `psu.py`: ingressi col buffer digitale disattivato (sotto) |
| `UPDI` | PA0 | programmazione | J515 |

**I pin liberi (L47c2a, scelta dell'utente).** PA1, PA3, PA4 erano la SPI verso il MCP4822, PA2 e
PB4 leggevano le correnti delle stringhe: tutto uscito con ADR-062. PC3 è libero da L41b1. Dopo un
reset i buffer d'ingresso digitali sono **accesi** (DS40002205A § 16.3.1, p. 131), e un pin
aperto col buffer acceso può assorbire corrente quando deriva attraverso la soglia. Il datasheet
(stessa pagina): «For lowest power consumption, disable the digital input buffer of unused pins».
L'adattatore lascia questi pin ingressi senza pull-up e scrive **`ISC` = `INPUT_DISABLE` (0x4)**
nel loro `PORTx.PINnCTRL` (§ 16.5.11, p. 145). Il core non tocca registri: espone la lista
(`TIMER_PIN_LIBERI`) e il valore (`TIMER_PIN_LIBERI_ISC`), e il test `pin_liberi` li confronta coi
pin di U509 che `psu.net` lascia senza rete e con la piedinatura SOIC-20 del datasheet (§ 4.1,
p. 14). Le altre due strade proposte all'utente (pull-up, uscite basse) non sono state scelte.

Il datasheet raccomanda lo stesso per i pin usati come ingressi analogici (PA5–PA7, PB5): è
compito dell'adattatore, che non è ancora scritto (`main_attiny.c`).

## 3. Gli stati

| Stato | `MAINS_REQ` | `VRELAY_EN` | `MUTE_REQ` | `PERMIT_REQ` | Micro |
|---|---|---|---|---|---|
| STANDBY | 0 | 0 | 0 | 0 | power-down, risveglio su `FRONT_IN` (entrambi i fronti) |
| ACCENSIONE | 1 | 0 → 1 | 0 | 0 | attivo |
| MUTO | 1 | 1 | 0 | 0 | attivo |
| RILASCIO | 1 | 1 | 1 | 1 | attivo (10 ms) |
| MUSICA | 1 | 1 | 1 | 1 | attivo |
| INSERZIONE | 1 | 1 | 0 | 1 → 0 | attivo (Δ) |
| SPEGNIMENTO | 1 → 0 | 1 → 0 | 0 | 0 | attivo |
| BUCO_RETE | 1 | 1 | 0 | 0 | attivo |
| GUASTO | 0 | 0 | 0 | 0 | attivo finché `FRONT_IN` non va spento |

## 4. Le sequenze

Ogni tempo porta la decisione che lo fissa. «Dopo X» vuol dire misurato da X.

**4.1 Accensione** (STANDBY → ACCENSIONE → MUTO o RILASCIO). `FRONT_IN` basso stabile per il
debounce:
1. `MAINS_REQ` = 1 (ADR-048 punto 4);
2. si aspetta che i rail siano in regolazione: `ADC_SUP_P` > 2,55 V e `ADC_SUP_M` < 1,20 V per
   ≥ 100 ms consecutivi. Senza rail entro **2 s**, si va in GUASTO;
3. `VRELAY_EN` = 1 (L47c2a: gli zeri e la calibrazione della derivazione non ci sono più);
4. si aspetta **≥ 50 ms**. Il minimo è 13 ms da `VRELAY` valida (ADR-027: 10 ms di set/reset
   più 3 ms di set time), e l'interruttore Q505 ci mette ~3 ms a chiudersi. Intanto le bobine
   del trim si pilotano col mute inserito;
5. se `MUTE_SW_IN` è basso: RILASCIO (4.3); altrimenti MUTO.

**4.2 Inserzione del mute** (MUSICA o RILASCIO → INSERZIONE → MUTO). Per `MUTE_SW_IN` alto, o
per il frontale spento (4.4):
1. **`MUTE_REQ` = 0 nello stesso istante** in cui il debounce conferma il tasto (ADR-062: i relè
   subito dopo il tasto; prima c'erano 6 s di sfumatura e 0,5 s di ritenuta);
2. **20 ms** dopo: `PERMIT_REQ` = 0 (Δ nominale, ADR-045; l'hardware tiene comunque ≥ Δ);
3. **non reversibile** (L47c2a): `MUTE_REQ` è già giù dal passo 1. Un tasto che torna a musica
   dentro Δ lascia finire l'inserzione, e da MUTO parte il rilascio (4.3).

**4.3 Rilascio** (MUTO → RILASCIO → MUSICA). `MUTE_SW_IN` basso stabile, e l'alimentazione buona
da ≥ 100 ms:
1. `PERMIT_REQ` = 1 e `MUTE_REQ` = 1 nello stesso istante: l'hardware eccita `PERMIT_CMD`
   non dopo `MUTE_CMD`;
2. si aspettano **10 ms**, il tempo d'operazione del G6K, senza guardare `MUTE_G_IN` (il gate sale
   0,22 ms dopo `MUTE_REQ`, `psu.py`, C_MUTE_G);
3. se `MUTE_G_IN` è ancora basso l'hardware ha rifiutato il rilascio: BUCO_RETE (4.5).
   Altrimenti MUSICA. La musica torna di colpo al livello di prima (PR-21, ADR-062).

**4.4 Spegnimento** (qualunque stato acceso → SPEGNIMENTO → STANDBY). `FRONT_IN` alto stabile:
1. l'inserzione del mute (4.2), passi 1–2, se non è già in MUTO;
2. `VRELAY_EN` = 0, **80 ms** dopo `PERMIT_REQ` = 0. ADR-046 vuole il relè di rete ≥ 50 ms dopo
   **`PERMIT_CMD`**, che l'hardware rilascia Δ dopo `PERMIT_REQ` (18,8 ms nominali, ~21 ms
   all'angolo alto): 50 + 21, arrotondato. L41b1 aveva scritto 50 ms da `PERMIT_REQ`, e sul
   circuito K501 si apriva 33 ms dopo `PERMIT_CMD` (L41b2);
3. `MAINS_REQ` = 0 nello stesso istante, poi power-down. In tutto **~0,12 s** da MUSICA (20 ms di
   debounce, Δ, 80 ms); ADR-046 diceva ~7 s per la sfumatura che non c'è più.

**4.5 Buco di rete** (MUSICA, RILASCIO, INSERZIONE → BUCO_RETE). Il criterio è `MUTE_G_IN`
basso mentre `MUTE_REQ` = 1:
1. **entro 1 ms** (interruzione su `MUTE_G_IN`): `MUTE_REQ` = 0, `PERMIT_REQ` = 0. Senza questo
   passo, al ritorno della rete il rivelatore rilascerebbe `MUTE_G` e i jack si ricollegherebbero
   in mezzo alla musica. Anche `ADC_MD` > 2,5 V da solo fa scattare questo passo, e in MUTO (dove
   `MUTE_REQ` è già 0) è l'unico criterio. Nei 10 ms del RILASCIO in cui il G6K si chiude,
   `MUTE_G_IN` non si guarda (4.3);
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
1. `MUTE_REQ` = 0, `PERMIT_REQ` = 0 (se non già fatto);
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

## 5. Il comando delle LDR

**Tolto in L47c2a** (ADR-062): niente legge, niente calibrazione, niente profilo, niente DAC. La
versione di L41b2 di questo paragrafo, con la tabella v4 e la cima di ADR-050, è nella storia del
repository (`git log -- firmware/preamp_timer/spec/timer_spec.md`) e nel report di L41b2.

## 6. Cosa si prova sull'host (L41b2, L47c2a)

`test/run_host_tests.sh` (in `run_tests.sh`, blocco 2k). Un test per ogni sequenza di § 4 e uno
per i pin liberi di § 2, su `timer_core.c` compilato con `/usr/bin/clang -std=c11 -Wall -Wextra
-Werror -pedantic`. Il mondo (`mondo.c`) dà gli ingressi e registra le uscite:
- `test_sequenze`: accensione, inserzione (col tasto che torna a musica dentro Δ), rilascio (col
  rifiuto dell'hardware), spegnimento, debounce, buco di rete di classe 1 e 2, guasto e ritenuta,
  pin liberi (contro `psu.net`, con `--root`).

L47c2a ha tolto `test_legge` (la legge, la calibrazione, il bilancio dell'ADC delle stringhe) e il
test della calibrazione.

`--falsi <file>`: **19 difetti** (`FALSO_n` in `timer_core.c`), ognuno deve far fallire il proprio
test. I dieci sopravvissuti di L41b2 tengono il loro numero (1, 4, 5, 6, 7, 9, 10, 15, 16, 18);
gli undici legati alla legge, alla calibrazione o alla sfumatura (2, 3, 8, 11, 12, 13, 14, 17, 19,
20, 21) sono usciti con loro; i nove nuovi sono 22–30 (le sequenze nuove e i pin liberi). Le forme
d'onda delle uscite si scrivono in CSV (`--csv`), e `test/ponte.c` fa girare il core sui pin del
circuito simulato.

**Sul circuito** (L47c2a, `docs/preamp/data/2026-10-05/L47c2a/seq/`): accensione, rilascio,
spegnimento, buco di 20 e di 200 ms, guasto, ognuno iterato fino al punto fisso fra il core e il
circuito, coi criteri di `analizza_seq.py` (quelli che la sfumatura definiva riscritti prima delle
corse). L'inversione non c'è più. Prima: L41b2, 7 su 7 (`docs/preamp/data/2026-09-26/L41b2/seq/`).
