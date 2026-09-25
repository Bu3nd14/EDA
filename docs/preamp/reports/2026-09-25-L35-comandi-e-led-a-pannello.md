# L35 — comandi e LED a pannello nel sorgente, con ADR-045 (2026-09-25)

**K6 ha un comando proprio, `PERMIT_CMD`, e il temporizzatore lo rilascia Δ dopo `MUTE_CMD`
all'inserimento del mute.** Guadagno e trim possono muoversi solo dopo lo stacco dei jack. Il caso
che L36 lasciava aperto (la manopola girata fuori mute, poi il mute inserito), fino a **~90 dB
SPL di picco a 1 m**, torna a un cambio sotto mute: **~−22 dB**, circa 55 dB sotto la soglia V2
(~33 dB) e circa 50 dB sotto il fondo di una stanza silenziosa (~25–35 dB(A)). Lo stesso vale per
il trim.

**Sul pannello passa solo la continua di bobine e LED** (ADR-028). I LED escono dalla scheda sui
loro header, l'interruttore di mute è un ingresso del temporizzatore, e il LED rosso di mute legge
lo stato dei due NC di K6. Il 2e prova tutto questo e fallisce su 14 falsi e su `main`.

**Nessuna ADR nuova**: la realizzazione è quella di ADR-045 e ADR-028. Il valore di Δ, che
ADR-045 lasciava a L35, e il contatto del LED di mute, che ADR-028 §5 lasciava a L35, sono scelti
qui (sezioni 1 e 4). **Chiude NC-032**; in NC-028 chiude il residuo di L36. NC-028 resta aperta e
bloccante per lo spegnimento (L30).

- **Dati**: `data/2026-09-25/L35/`, con README.
- **Il sorgente**:
  - `trim.py`: K6 su `permit_cmd`; J5 al posto di D4–D6;
  - `gain_interlock.py`: J6 al posto di D7–D9; il residuo del docstring dichiarato chiuso;
  - `preamp_audio.py`: `PERMIT_CMD`, J4 col contratto, SW3, R3 e J7, il budget;
  - la netlist rigenerata.
- **Il 2e**: `scripts/check_relay_safe_state.py`.

## 1. ADR-045 nel sorgente: il comando del permissivo e il contratto

La bobina di K6 va da `VRELAY` a `PERMIT_CMD`. Nessun'altra parte è su quella rete. **J4**
(`MUTE_TIMER`, 1×03) porta i due comandi al temporizzatore, che sta all'alimentatore:

| J4 | Rete | Cosa |
|---|---|---|
| 1 | `MUTE_CMD` | le bobine di K2–K4, i relè del jack |
| 2 | `PERMIT_CMD` | la bobina di K6, il permissivo di trim e guadagno |
| 3 | `MUTE_SW` | l'interruttore di mute SW3, un **ingresso** del temporizzatore |

I comandi restano dal lato basso, come prima: il temporizzatore porta una bobina su `RLY_RET` per
eccitarla, cioè per uscire dal mute.

**Il contratto**, scritto accanto a J4 come quello delle LDR accanto a J3:
- **All'inserimento**: prima `MUTE_CMD` (jack staccati, lato del condensatore a massa, ADR-044),
  poi `PERMIT_CMD` **Δ dopo**.
  - **Δ = 20 ms nominale, ≥ 10 ms garantito.** Il minimo è più di tre volte i 3 ms di rilascio
    massimo del G6K (en-g6k.pdf p. 3), e lascia margine alla tolleranza del temporizzatore.
  - Il valore nominale è quello proposto da ADR-045.
  - Nella sequenza delle LDR, Δ si conta dal rilascio di `MUTE_CMD`, 0,5 s dopo d = 1.
- **Al rilascio**: `PERMIT_CMD` si eccita **non dopo** `MUTE_CMD`, anche insieme.
  - Il guadagno non si muove, perché lo tiene il polo ponte di L36.
  - Il trim non si muove, perché i bistabili tengono lo stato.
- **All'accensione**: il vincolo di ADR-027 (10 ms di larghezza + 3 ms di set dopo `VRELAY`
  valida) **passa su `PERMIT_CMD`**.
  - È l'eccitazione di K6 che toglie `VTRIM` e ferma il pilotaggio del trim.
  - `MUTE_CMD`, che per contratto non viene prima, lo eredita.
  - È la lettura diretta di ADR-045 §3, non una decisione nuova.
- **F10**: il mute è inserito se SW3 è aperto **oppure** se il temporizzatore d'accensione non è
  scaduto (sezione 3).
- **La nota per il failsafe** (ADR-045 → ADR-043, L30) è riportata accanto a J4 e non si
  realizza qui. Alla caduta di `VRELAY` lo sfasamento sparisce.

## 2. I LED escono dalla scheda

**J5** (`TRIM_LED`) e **J6** (`GAIN_LED`), 1×04: tre anodi e il catodo comune su `RLY_RET`. Le
resistenze R1 e R2 restano sulla scheda, e i contatti che leggono lo stato sono quelli di prima
(K9/K10 per il trim, i poli 2 di K11/K12 per il guadagno).

| Pin | J5 (trim) | J6 (guadagno) |
|---|---|---|
| 1 | 0 dB (`TLED_0`) | 0 dB (`GLED_0`) |
| 2 | −6 dB (`TLED_6`) | +3 dB (`GLED_3`) |
| 3 | −12 dB (`TLED_12`) | +10 dB (`GLED_10`) |
| 4 | `RLY_RET` | `RLY_RET` |

- **Ref**: D4–D9 spariscono e le loro ref non vengono riusate. Le parti nuove hanno ref
  esplicite (J4–J7, SW3, R3). Nessuna parte esistente si rinumera (#22).
- **La mappa pin → stato** sta come dato in `trim.LED_PINS` e `gain_interlock.LED_PINS`, e nel 2e
  in `PANEL_LEDS`, come oggi `SW_TABLE` e `GAIN_KNOB`.
- **SW1 e SW2** restano header a 16 vie col simbolo del commutatore. Il cablaggio non cambia.

## 3. L'interruttore di mute (F10)

**SW3** (`Switch:SW_SPST`, valore `MUTE`, header 1×02, pin 1/2 letti dalla libreria KiCad):
- da `RLY_RET` a `MUTE_SW`, e `MUTE_SW` esce su J4 pin 3;
- **chiuso vuol dire musica**, quindi un filo rotto mette in mute.

**Perché un ingresso del temporizzatore e non un contatto in serie a `MUTE_CMD`.** In serie
staccherebbe insieme i relè del jack e, per avere lo sfasamento, anche K6: Δ andrebbe perso
proprio nel caso che ADR-045 chiude. Così l'OR di F10 («interruttore aperto oppure accensione
non finita») lo fa il temporizzatore, che sfasa sempre allo stesso modo. Anche il debounce è
suo.

**Scelta di realizzazione**: il cablaggio del pannello arriva tutto alla scheda audio, un fascio
solo, e il 2e lo vede. Il filo dell'interruttore riparte su J4. Il temporizzatore resta
all'alimentatore.

## 4. Il LED rosso di mute (F11): da quale contatto

ADR-028 §5 lasciava la scelta a L35. La preferenza era lo stato, non il comando. Il vincolo era
che i poli di K2–K4 portano tutti segnale.

**Il LED legge `VTRIM`**, cioè i due NC di K6 in serie: R3 1,5 k da `VTRIM` all'anodo su **J7**
(`MUTE_LED`, pin 1), con il catodo su `RLY_RET` (pin 2).
- È **lo stato di un contatto**, non il comando, e non costa un relè. Il «Da riaprire se» di
  ADR-028 non si realizza.
- **Con ADR-045 sbaglia solo dal lato sicuro**, nei due versi:
  - si accende Δ dopo lo stacco dei jack;
  - si spegne non dopo il loro riaggancio.
  - Se il contratto regge, non dice mai «mute» a jack collegati.
- **Dice esattamente quando trim e guadagno si possono muovere**, perché `VTRIM` è la loro
  alimentazione di comando.
- **Il limite, dichiarato**: un contatto saldato di K2–K4 non si vede. È lo stesso tipo di guasto
  di un relè solo che ADR-033 accetta per i LED di trim e guadagno.

## 5. Il 2e esteso

`check_relay_safe_state.py` cambia in quattro punti.

**«Fuori mute» diventa «i relè sul comando del mute e quelli sul comando del permissivo
eccitati»** (`command_relays()`), per l'interblocco del trim e per quello del guadagno. Oggi K6
conta come «il mute», come chiede ADR-045 §4. Fino a L36 la prova ricavava «fuori mute» dalle
sole bobine di mute, e con K6 spostato l'avrebbe trattato da «libero»: il 2e vecchio sulla
netlist nuova dà 25 problemi.

**La finestra Δ**: K6 eccitato, K2–K4 già rilasciati. Trim e guadagno devono restare fermi, e il
LED di mute spento. La finestra opposta (jack eccitati, permissivo rilasciato) la esclude il
contratto di J4: il 2e lo dichiara e non lo prova, perché una netlist non ha tempi. Il
trasferimento della corsa di L36 comprende ora K6.

**I comandi** (`check_commands()`):
- `MUTE_CMD` e il comando del permissivo sono due reti **diverse**, con `VRELAY` all'altro capo
  della bobina;
- ognuno sta sul suo pin di J4;
- SW3 va da `RLY_RET` al pin dell'interruttore.
- K6 di nuovo su `MUTE_CMD`, il sabotaggio chiesto da ADR-045, fallisce **col suo nome**.

**I LED a pannello** (`panel_pins()`, `check_panel_leds()`). La prova del guadagno, che fino a
L36 riconosceva i LED dall'anodo sui contatti degli ausiliari, ora legge i pin di J6.
- **Per ogni header**: esiste una volta sola, il ritorno sta su `RLY_RET`, e gli anodi non toccano
  reti di segnale, la massa audio né `VRELAY`.
- **Trim, prova nuova**: fino a L36 i LED del trim non erano provati. `reach()` può fissare lo
  stato di un bistabile (`latched`), e per ciascuno dei quattro stati di SPIA1/SPIA2, in mute e
  fuori, si accende esattamente il pin giusto.
- **Guadagno**: nei tre stati, in mute e fuori, il pin giusto. Ogni anodo deve stare su un
  contatto di un ausiliario.
- **Mute**: acceso in mute; spento fuori mute e nella finestra Δ.

**Fatto fallire** (`data/2026-09-25/L35/falsi/`): la netlist vera passa (rc 0). Falliscono (rc 1),
ciascuno per la ragione voluta (`esito.csv`), la netlist di `main` e 14 falsi:

| Falso | Primo problema trovato |
|---|---|
| `permesso_su_mute_cmd` | K6 sul comando dei relè di mute (ADR-045) |
| `permit_cmd_fuori_da_J4` | J4 pin 2 senza il comando del permissivo |
| `mute_cmd_fuori_da_J4` | J4 pin 1 senza il comando dei relè di mute |
| `comandi_scambiati_su_J4` | J4 pin 1 porta `PERMIT_CMD` |
| `interruttore_fuori_da_J4` | SW3 non arriva al pin 3 di J4 |
| `interruttore_su_mute_cmd` | SW3 in serie al comando dei jack |
| `trim_led_0_6_scambiati` | a trim 0 dB si accende −6 |
| `spia1_reset_set_scambiati` | a trim 0 dB si accende −6 (NC-014 sulla spia) |
| `trim_led_senza_ritorno` | J5 senza ritorno su `RLY_RET` |
| `gain_led_3_10_scambiati` | a +3 dB si accende +10 |
| `gain_led_su_segnale` | un anodo di J6 su `BL_RG`, non su un ausiliario |
| `led_mute_da_vrelay` | LED di mute acceso fuori mute |
| `led_mute_da_vhold` | LED di mute spento in mute (legge il NO di K6) |
| `led_mute_dal_comando` | LED di mute acceso fuori mute (legge il comando) |

**Regressione** (`falsi/regressione.txt`):
- **L16**: cinque falsi cadono e `scala_fuori_finestra` passa per progetto, come allora.
- **L29e**: uguale.
- **L36**: le stesse ragioni.
- **Due falsi non si applicano più**, e ciascuno ha la sua versione di oggi fra i 14:
  - `bobina_K6_altra_net` di L16 metteva K6 su `Net("PERMIT_CMD")`, che da ADR-045 **è il
    progetto**. Il 2e di allora lo rifiutava perché K6 non era su `MUTE_CMD`. Quello di oggi
    rifiuta un `PERMIT_CMD` che non arriva a J4, perché non lo piloterebbe nessuno.
  - `led_scambiati` di L36 sabotava D8/D9, che non esistono più.

## 6. Il segnale non cambia

- **Deck V2** rigenerato dalla netlist (`genera_tb_v2_casopeggiore.py`, matrice `sorgente`, 135
  corse): **byte-identico**.
- **ERC**: 47 avvisi, come a L36. Le parti nuove sono collegate per intero.
- **Diagramma a blocchi**: l'etichetta di K6 dice `PERMIT_CMD` (ADR-045), e le asserzioni
  reggono.
- **`run_tests.sh`**: 10 passati, 0 falliti.

## 7. Il budget per l'alimentatore

- **Le bobine non cambiano**: K6 cambia comando, non numero.
  - **168,8 mA** a 5 V a +10 dB, fuori mute e in mute (72,8 mA a 12 V, 36,8 mA a 24 V).
  - Nella finestra Δ sono di meno.
- **I LED**, ~2 mA ciascuno a 5 V con 1,5 k:
  - trim e guadagno sono accesi **sempre**, in mute e fuori, perché leggono lo stato;
  - il LED di mute è acceso solo in mute.
  - Quindi ~4 mA fuori mute e **~6 mA in mute**.
  - Il commento di prima («~4 mA in mute») contava i LED solo in mute: è corretto.
- **Caso peggiore: ~175 mA a 5 V**, in mute a +10 dB.
- **Il vincolo di L36 resta**: `VRELAY` − V_F(Schottky, 42 mA) ≥ 80 % di 5 V, a −5 % e a caldo.
  `VTRIM` porta ora anche ~2 mA di LED attraverso i due NC di K6: la caduta è quella dei contatti.

## 8. Cosa resta

- **Il temporizzatore vero**: Δ, l'OR di F10, il debounce, i 13 ms all'accensione. È del lotto
  dell'alimentatore, che eredita il contratto di J4 come eredita quello delle LDR di J3.
- **Il failsafe** con la nota di ADR-045: L30 (NC-028, spegnimento).
- **Non misurato su un relè vero**: che Δ ≥ 10 ms basti poggia sul rilascio **massimo** del
  datasheet, 3 ms. Se un catalogo successivo del G6K lo cambia, ADR-045 si riapre.
