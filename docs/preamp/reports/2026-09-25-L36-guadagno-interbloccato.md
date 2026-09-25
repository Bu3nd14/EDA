# L36 — il guadagno interbloccato dal mute (2026-09-25)

**Il guadagno si cambia solo a mute inserito, come il trim, e si tiene da sé fuori mute. La
corsa al rilascio del mute di ADR-030 è chiusa per struttura, non per temporizzazione.** Il 2e
lo prova sulla netlist, anche nello stato di trasferimento di K6. Simulato su 480 celle:
**0 cadute**, contro **373** della strada B senza il polo ponte. Tre LED dicono lo stato vero.

**Resta un caso ordinato ma non chiuso dal datasheet**, lo stesso del trim: la manopola girata
fuori mute e poi il mute inserito. Si porta all'utente (sezione 7).

Nessuna ADR nuova: la realizzazione è la strada B di ADR-030, nella forma di ADR-041. Il polo
ponte è un contatto del selettore che la strada B non esclude, e non accumula carica.

- **Dati**: `data/2026-09-25/L36/`, con README.
- **Il sorgente**:
  - `circuits/preamp/gain_interlock.py`, nuovo;
  - `trim.py`, che restituisce anche K6, `VTRIM` e `RLY_RET`;
  - `preamp_audio.py`: K1 e K5 li crea il modulo nuovo, e il commento sul budget delle bobine
    è aggiornato;
  - la netlist rigenerata.

## 1. Il vincolo che ha deciso la forma: il datasheet non dà la dinamica della bobina

`vendor/relays/omron/G6K/en-g6k.pdf`, pagina 3: per il G6K-2F-Y a 5 V il datasheet dà solo:
- 21,1 mA e 237 Ω ±10 %;
- must operate 80 % max e must release 10 % min;
- **operate 3 ms max** e **release 3 ms max**.

**Non dà l'induttanza della bobina, né un tempo minimo di rilascio, né il tempo di
trasferimento** fra l'apertura dell'NC e la chiusura dell'NO.

La corsa di ADR-030 si svolge così. Quando K6 commuta:
1. il comando (`VTRIM`, dai suoi NC) si spegne;
2. la tenuta (dal suo NO) arriva solo dopo il trasferimento;
3. nel mezzo la bobina si scarica sul diodo di ricircolo.

Che K1 cada o no dipende da L/R, dalla corrente a cui l'ancora rilascia e dal buco. Sono tre
cifre che il datasheet non dà, quindi **nessun ragionamento sui tempi la chiude**. La sezione 5
lo mostra in simulazione. Va chiusa per struttura: una bobina accesa non deve mai restare senza
alimentazione mentre K6 si muove.

## 2. La realizzazione

In `gain_interlock.py`, con ref nuove ed esplicite, senza rinumerare niente (#22):
- **K11 `HOLD3`** e **K12 `HOLD10`**: gli ausiliari di K1 e K5, bobina in parallelo;
- **SW2** (4 poli e 3 posizioni, un header a 16 vie come SW1);
- **D10–D11**: Schottky del comando;
- **D12–D13**: diodi della tenuta;
- **D14–D15**: ricircolo;
- **D7–D9**: i LED;
- **R2**: la resistenza dei LED.

**Le bobine** passano al lato alto come quelle del trim: K1 + K11 fra `G3_HI` e `RLY_RET`, K5 +
K12 fra `G10_HI` e `RLY_RET`. La polarità è riletta alla pagina 6 del PDF (rendering a 300 dpi):
**pin 1 +, pin 8 −**, lo stesso verso di prima. Spariscono `GAIN_CMD` e `GAIN10_CMD`: nessun
deck né script le leggeva, a parte il 2e.

**Cosa alimenta `G3_HI`** (per `G10_HI` è lo stesso, ma solo a +10 dB):

| Percorso | Da | Attraverso | Vivo quando |
|---|---|---|---|
| **a** comando | `VTRIM` | SW2 polo a (+3, +10) → `C3` → Schottky D10 | in mute e manopola su |
| **b** ponte | `VRELAY` | SW2 polo b (+3, +10) → `H3` → **NO di K11** | manopola su e K1 già acceso |
| **c** tenuta | `VHOLD` | D12 → `H3` → **NO di K11** | fuori mute e K1 già acceso |

- **`VHOLD`** è il NO del polo 1 di K6: COM su `VRELAY`, quindi viva fuori mute. Il pin era libero
  fino a L36, e la logica del trim non cambia.
- **Il diodo D10** impedisce a `G3_HI`, tenuto a `VRELAY` fuori mute, di rientrare su `VTRIM`:
  riaprirebbe il trim fuori mute (F8). Il falso `diodo_comando_in_corto` lo prova.
- **Il diodo D12** impedisce che, in mute, il ponte di K1 (vivo a +3) arrivi a `H10` attraverso
  `VHOLD` sospesa, tenendo K5 acceso a +3. Il falso `senza_diodo_tenuta` lo prova.

**Cosa fa, stato per stato:**
- **In mute**: a accende la bobina, e a + b la tengono finché la manopola lo chiede. Girare in giù
  la spegne, perché `VHOLD` è morta. Le bobine seguono la manopola nei due versi.
- **Fuori mute**: una bobina spenta non ha sorgente, perché a è morto e b e c passano per il suo
  contatto aperto. Una bobina accesa la tiene c, qualunque cosa dica la manopola. **La manopola
  non muove nulla.**
- **Al rilascio e all'inserimento del mute**: la manopola coincide con lo stato, perché si è
  girata in mute. La bobina è alimentata da b, **un percorso senza contatti di K6**, per qualsiasi
  L e qualsiasi trasferimento. **È la chiusura della corsa.**

**I LED** stanno sul polo 2 degli ausiliari, come il trim fa con le spie:
- `VRELAY` → R2 1,5 k → COM di K11. Il NC accende il LED 0 dB; il NO va al COM di K12;
- da K12: il NC accende il LED +3 dB e il NO il LED +10 dB;
- catodi su `RLY_RET`.

Stanno sulla scheda come quelli del trim, e L35 li porta a pannello.

**Guasti** (F5, ADR-030):
- **Bobina di un ausiliario interrotta**: fuori mute il guadagno torna a 0 dB. È il verso che F5
  vuole; il LED lo dice.
- **Bobina di K1 interrotta**: l'ausiliario tiene e il LED dice +3 senza K1. È la spia che mente,
  accettata da ADR-033 per il trim.
- **Bobina di K6 interrotta**: trim e guadagno diventano comandabili a caldo, come ADR-027 e
  ADR-030 dicono già.

**ERC**: da 42 a **47** avvisi.
- +6: i lanci della posizione 0 dB di SW2, lasciati liberi;
- +2: gli NC degli ausiliari (pin 2 di K11 e K12);
- −2: `GAIN_CMD` e `GAIN10_CMD` a un solo pin;
- −1: il pin 4 di K6, ora usato.

SKiDL 2.3 non esporta un marcatore NC. Il sorgente lasciava già scollegato il pin 5 di K6.

## 3. Il 2e esteso

`scripts/check_relay_safe_state.py`:
- **Ruolo nuovo `HOLD`**: la bobina deve stare sulle stesse net del suo `GAIN`, con la stessa
  polarità.
- **Diodi e LED orientati** nella visita (da anodo a catodo); resistori, bobine e TVS nei due
  versi. Senza questo, la visita troverebbe ritorni che il circuito non ha. E passerebbe un diodo
  montato al contrario: il falso `diodo_tenuta_invertito` lo prova.
- **Il selettore del guadagno posizione per posizione**, contro la tabella `GAIN_KNOB` tenuta nel
  checker come dato (ADR-026). Per il trim resta «qualsiasi posizione».
- **La prova**, per ogni stato coerente (0, +3, +10) e ogni posizione:
  - **fuori mute**: bobine alimentate = stato;
  - **in mute**: bobine alimentate = tabella della manopola;
  - **trasferimento**: K2, K3, K4 e K6 fra i due lanci, nessun contatto chiuso, con la manopola
    allo stato. Le bobine alimentate devono restare = stato. **È la corsa, provata sulla netlist.**
- **In più**:
  - ADR-026 in ogni posizione;
  - i tre LED, uno acceso per stato e quello giusto;
  - gli ausiliari mai sul segnale o sulla massa audio;
  - la prova del trim, rifatta con i diodi orientati: 16 stati.

**Fatto fallire** (`data/2026-09-25/L36/falsi/esito.csv`). La netlist vera passa con rc 0; le
11 varianti e la netlist di `main` danno rc 1, ciascuna per la ragione voluta:

| Variante | Primo problema trovato |
|---|---|
| `main` prima di L36 | mancano gli ausiliari HOLD3 / HOLD10 |
| `senza_ponte_K1` | **CORSA APERTA** nel trasferimento, a +3 dB |
| `ponte_senza_ausiliario` | fuori mute, da 0 dB, la manopola a +3 accende K1 |
| `tenuta_da_vrelay` | in mute K1 non si spegne con la manopola a 0 |
| `diodo_comando_in_corto` | il **trim** diventa raggiungibile fuori mute (F8) |
| `diodo_tenuta_invertito` | fuori mute, a +3 con la manopola a 0, K1 non si tiene |
| `senza_diodo_tenuta` | in mute, da +10 con la manopola a +3, K5 resta acceso |
| `hold3_bobina_su_g10` | la bobina di K11 non è sulle net di K1 |
| `k5_senza_k1` | in mute la posizione 2 alimenta K5 e non K1 (ADR-026) |
| `led_scambiati` | a +3 dB si accende il LED +10 |
| `nc_no_polo2_K11` | a 0 dB si accende il LED +3 (NC-014 sul polo dei LED) |
| `nc_no_polo1_K11` | fuori mute, a 0 dB, K1 si accende (NC-014 sul polo della tenuta) |

**Regressione**: i falsi di L16 (trim) e di L29e (mute) rifatti col 2e nuovo danno gli stessi
esiti dei loro lotti (`falsi/regressione.txt`). In L16 sei cadono, e `scala_fuori_finestra`
passa il 2e e cade al 2f, come allora.

## 4. Il percorso del segnale non cambia

Il deck V2 versionato (`spice/preamp/tb/tb_v2_casopeggiore.cir`), rigenerato dalla netlist nuova
col generatore di L29c, è **byte-identico** (`git status` non lo elenca). I contatti di K1 e K5
sulle gambe di R_g e la geometria iii del mute non sono stati toccati.

## 5. La corsa, simulata

`data/2026-09-25/L36/corsa/`. Il modello è comportamentale e **dichiarato**, perché il datasheet
non ne dà uno:

| Grandezza | Valore nella spazzata | Da dove |
|---|---|---|
| Resistenza di bobina | 213 / 237 / 261 Ω | datasheet ±10 % |
| Induttanza | **5–200 mH, ipotetica** | il datasheet non la dà |
| Chiusura dell'ancora | 4 V / R | must operate 80 % |
| Apertura dell'ancora | 0,1 / 0,3 / 0,5 / 0,7 × 5 V / R | 10 % garantito; di più è il caso peggiore per chi tiene |
| Buco di trasferimento di K6 | 0,1 / 0,3 / 1 / 3 ms | 3 ms = release massimo intero |
| VRELAY | 4,75 / 5 V | — |

- **Nessun ritardo meccanico accreditato**: l'ancora si apre appena la corrente scende sotto
  soglia.
- **I diodi sono generici**, non del costruttore: il pezzo si sceglie al giro BOM.
- Sequenza: mute rilasciato a 5 ms, inserito a 30 ms, fine a 50 ms. **1440 corse, tutte rc 0,
  nessuna col transient op** (#33).

| Variante | Cade al rilascio | Cade all'inserimento | Corrente minima / regime |
|---|---|---|---|
| **progetto** (col ponte) | **0 su 480** | **0 su 480** | **1,000000** |
| ingenua (strada B senza ponte) | **373 su 480** | 387 su 480 | 0 |

Per la variante ingenua conta **dove** cade. Le celle che cadono al rilascio, su 24 per casella:

| L \ buco | 0,1 ms | 0,3 ms | 1 ms | 3 ms |
|---|---|---|---|---|
| 5 mH | 24 | 24 | 24 | 24 |
| 20 mH | 18 | 24 | 24 | 24 |
| 50 mH | 7 | 20 | 24 | 24 |
| 100 mH | 4 | 12 | 24 | 24 |
| 200 mH | 0 | 6 | 18 | 24 |

Senza il ponte, il risultato dipende esattamente dalle cifre che mancano nel datasheet. Col
ponte la corrente non si muove nemmeno. Le cifre di corrente sono del modello; la **forma** del
risultato no: col ponte la bobina non perde mai la sorgente, ed è quello che il 2e prova sulla
netlist.

**Chi cade all'inserimento, nell'ingenua**: sono le celle cadute al rilascio e rimaste spente
fuori mute, più quelle che cadono nel secondo trasferimento. Rientrano accese a fine corsa,
perché il comando in mute le riprende.

## 6. Il budget per l'alimentatore

Scritto nel commento del budget in `preamp_audio.py` e nella sezione di STATE per `psu-engineer`.
Dal datasheet, ±10 %, per bobina: 21,1 mA a 5 V, 9,1 mA a 12 V, 4,6 mA a 24 V.

| Condizione, a +10 dB | Bobine | 5 V | 12 V | 24 V |
|---|---|---|---|---|
| fuori mute: K1, K5, K11, K12, K2–K4, K6 | 8 | **168,8 mA** | 72,8 mA | 36,8 mA |
| in mute: K1, K5, K11, K12, K7–K10 pilotati | 8 | **168,8 mA** + ~4 mA di LED | 72,8 mA | 36,8 mA |

Prima erano 126,6 mA in entrambe le condizioni.

**Un vincolo nuovo.** L'accensione di K1 e K5 passa per lo Schottky del comando. Deve valere
VRELAY − V_F(42 mA) ≥ 80 % della tensione nominale di bobina, a −5 % e a caldo: la resistenza
della bobina sale con la temperatura, e con lei la tensione di must operate (curva del datasheet).
- Col modello generico dello Schottky (~0,26 V) si ha 4,49 V a 4,75 V, il 90 %;
- con un 1N4148 (~0,9 V) non ci si sta.

La tenuta (percorsi b e c) non ha questo vincolo: tenere chiede meno che accendere.

## 7. Cosa resta, e cosa si porta all'utente

**Il residuo: la manopola girata fuori mute, e poi il mute inserito.**
- La manopola non muove niente fuori mute. All'inserimento il guadagno va dove la manopola dice.
- Succede quando si apre il NO di K6, cioè quando muore `VHOLD`, **un rilascio di K1 dopo**.
- K6 si muove con K2–K4 (stessa net di bobina, stessa parte): il cambio segue lo stacco dei jack
  di quel tempo.
- La simulazione (variante `residuo`) dà la sola parte elettrica: **2,6–33,6 µs a 5 mH**, fino a
  **84–1322 µs a 200 mH**, senza il ritardo meccanico.
- Il trim ha la stessa forma: si muove al richiudersi dell'NC di K6, un tempo di set dopo
  (ADR-027).

Se la dispersione dei rilasci fra K4 e K6 supera quel tempo, un gradino d'offset (fino a ~69 mV
misurati a caldo in L29c) arriva al jack prima dello stacco. **Non è chiuso dal datasheet e non è
misurato su un relè vero.** Le strade sono tre:
1. accettarlo come il trim, e misurarlo al prototipo;
2. scrivere la regola d'uso «prima il mute, poi la manopola» sul pannello (per ADR-032 non rende
   conforme V2);
3. chiederlo a un permissivo in più, cioè riaprire ADR-030.

**Sceglie l'utente.** NC-028 lo registra, ma non blocca L36.

**La proposta per il trim** (punto 6 del mandato; ADR-030, «Da riaprire se: la corsa è chiusa sul
guadagno»).

La stessa strada, col ponte, si applica al trim:
- K7 e K8 **monostabili**, con due ausiliari al posto delle spie K9 e K10;
- SW1 a 4 poli come oggi: per ogni bobina un polo di comando da `VTRIM` e un polo ponte da
  `VRELAY`, al posto del ponte H;
- nessun relè in più.

Guadagni:
- un solo meccanismo per guadagno e trim;
- niente bistabili pilotati a lungo in mute (il rischio termico di ADR-027);
- niente ponte H né TVS;
- un guasto di bobina porta il trim verso **−12 dB**, se la scala si ricabla «diseccitato =
  −12 dB», cioè più piano: nel verso sicuro.

Costi:
- fino a **+84,4 mA fuori mute** a −12 dB (4 bobine), cioè ~253 mA in tutto;
- ricablare la scala «diseccitato = −12 dB» e rifare le misure di L16 (V1, E3, E5 col trim);
- all'inserimento, il residuo del trim passa dal tempo di set (bistabile) al rilascio
  (monostabile), come quello del guadagno.

**La raccomandazione è quella di ADR-030: quasi un pareggio.** Si tiene il lavoro verificato di
L16, a meno che l'utente voglia un solo meccanismo. È una proposta, non una modifica: niente di
questo è nel sorgente.
