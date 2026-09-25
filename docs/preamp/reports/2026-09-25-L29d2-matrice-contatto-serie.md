# L29d2 — la matrice del contatto in serie sulla geometria iii (2026-09-25)

**La geometria iii regge V2 su tutta la matrice di L29c: 0 celle fuori su 253, e 0 su 47 nelle
varianti di progetto.** Lo spegnimento resta fuori, com'era atteso: è di L30 (ADR-043). La
scelta è registrata in **ADR-044**.

- **Dati**: `data/2026-09-25/L29d2/`, con README.
- **Banco**: `data/2026-09-25/L29d2/deck/tb_v2_l29d2.cir`, generato dal generatore di L29c esteso
  (`--matrice l29d2`). Rigenerati col generatore esteso, gli 8 deck versionati di L29c e L29d
  sono **byte-identici** (`script/identici.sh`).
- **Etichetta di ogni cifra**: il circuito e i modelli di L29c (L39, ADR-042). La geometria esiste
  **solo nel banco**: `circuits/` non è cambiato.

## 1. Le decisioni dell'utente, prima di correre

Le tre domande lasciate dalla sonda di L29d, poste una alla volta il 2026-09-25:

| Domanda | Risposta dell'utente |
|---|---|
| Quale geometria | «iii» |
| Lo stato sicuro (ADR-012) | «Il bleed basta» |
| I valori | «C dal datasheet + cavo realistico» |

**Una precisazione sullo stato sicuro.** La domanda parlava del «bleed dal lato condensatore»,
ma a riposo il jack va a massa attraverso il bleed **al jack**: `RBLM` 220 k, `RBL1` e `RBL2`
470 k, già nel blocco CANALE. Il bleed lato condensatore (`RBCx`) è un'altra resistenza, con gli
stessi valori, ed è un'ipotesi del banco. La risposta vale per il bleed al jack, che esiste.
L'imprecisione è della domanda, e l'utente la trova segnalata qui.

## 2. I valori

**La capacità del contatto aperto** (`script/c_contatto.py`, `c_contatto.txt`). Viene dal
datasheet del G6K, `vendor/relays/omron/G6K/en-g6k.pdf`, pagina 5: «High-frequency
Characteristics (Isolation)», G6K-2G(F/P)(-Y), media di 10 pezzi. La curva è una retta: 86,5 dB
a 1 MHz, 66,5 dB a 10 MHz e 46 dB a 100 MHz, cioè **20,2 dB/decade**, capacitiva pura.

Il contatto aperto si modella come una C in serie fra due porte da 50 Ω:
|S21| ≈ ω·C·2·Z0. Ne viene **C = 0,075–0,080 pF**; nel banco va **0,1 pF**, per eccesso.
- La lettura del grafico vale ±2 dB, cioè C ×1,26 / ×0,79.
- È la C misurata **sul PCB di prova di Omron** (nota *2 del datasheet). Le piste della scheda
  vera si aggiungono: vedi § 5.

**Gli altri valori:**
- **cavo al jack**: 0 pF, il caso peggiore per il passaggio capacitivo; 100 pF nella variante
  `c100`;
- **bleed lato condensatore** 220 k / 470 k e **trasferimento** 1 ms: invariati.

## 3. Come si è fatto fidare

| Controllo | Esito |
|---|---|
| Deck versionati rigenerati | 8 su 8 byte-identici (`cmp`) |
| **Controfattuale N** (8 corse, nomi della sonda L29d) contro L29c | A del cambio 111,5 → 111,5 µV; accensioni 11,28 / 6,45 mV identiche; il peggior scarto relativo su grandezze sopra 1 nV è 0,59 % (B2 a 0,37 µV). Gli scarti del 13 % stanno su valori < 1 nV, rumore numerico. `cf/controfattuale_N.csv` |
| Il valore del contatto arriva davvero al circuito (#29) | ogni corsa stampa `@cksx[capacitance]` e `@ccavx[capacitance]`: 1e-13, e 1e-18 o 1e-10 |
| Corse della matrice | 111 su 111 rc=0; nessun «Transient op» |
| Corse delle varianti | 43 su 43 rc=0 |
| Punto di partenza (`verifica_partenza.py`) | 0 fuori su 109 + 43 (le 2 corse di pavimento non scrivono gli stati) |
| **Il ponte con L29d**: iii col contatto a 5 pF (`k5`) | accensione 300 ms: **204,8 µV**, contro i 205 della sonda |

## 4. I risultati

Picchi col metodo di V2: il peggiore sulle tre uscite. A e B2 sono in µV (soglia 100), S in dB
(soglia 20). Fonti: `tabella.csv`, `matrice/verdetto.csv`, `varianti/verdetto.csv`.

### 4.1 La matrice, 0 pF di cavo e 100 kΩ

| Punto | Cella peggiore | L29c | **iii** |
|---|---|---|---|
| 1 cambio di guadagno a relè chiuso, senza segnale | `gm0x10_lz_c`, A | **111,5** | **0,17** |
| | tutti e sei i passaggi, A | 27–116 | ≤ 0,17 |
| 2 cambio di trim a relè chiuso | `tm0x12_lz_c`, A | **101,7** | **0,10** |
| 3 dispersione `dp{a,min,max}max`, cambio | `x10000_dp*max_c`, A | **267** | **≤ 0,60** |
| 3 dispersione, dissolvenza (inserzione / rilascio) | `x10000_i` / `x01000_c`, A | 28,1 / 69,7 | **28,0 / 69,7** |
| 4 mute col relè (0,1 / 1 / 2 / 20 s), senza segnale | A_ins / A_rel | 0,013 / 0,032 | 0,013 / 0,032 |
| 4 con musica, B2 col contatto aperto | `mh01_20`, 20 Hz | 8,5 | 8,7 |
| 4 con musica, S d'inserzione / rilascio | `mh01_1k` | 7,16 / 5,45 dB | 7,16 / 5,45 dB |
| 1-2 con musica, S | `gm0x3_1k_i` | 7,16 dB | 7,16 dB |
| 5 accensione, 6 celle | `on_r300p`, A | **11 280** | **4,4** |
| | le altre cinque | 1 608–6 450 | 0,17–1,34 |

Verdetti: **253, nessuno fuori**. Di questi, 61 A_ins, 37 A_rel, 99 B2 e 56 S.

**La cella più vicina alla soglia non dipende dal contatto.** Sono i 69,7 µV al rilascio con
la dispersione, e i 28 µV all'inserzione:
- sono **identici in L29c e in iii**, entro lo 0,05 %, e identici nel mute semplice `xm`, dove il
  relè si muove come sempre;
- il picco cade **1,32 s dopo il rilascio** (11,32 s contro 10,0 s) e 1,36 s dopo l'inserzione:
  dentro la dissolvenza di 6 s delle LDR, non alla commutazione del contatto.

È la LDR che porta al jack i ±20 mV di VOS dell'LSK489. L29c lo aveva già misurato e accettato.

### 4.2 Le varianti sulla cella peggiore di ogni punto

| Cella | iii | cavo 100 pF | carico 10 kΩ |
|---|---|---|---|
| guadagno `gm0x10_lz_c`, A | 0,17 | 0,039 | 0,020 |
| trim `tm0x12_lz_c`, A | 0,099 | 0,033 | 0,014 |
| dispersione `x01000_dpmaxmax_c`, A_ins / A_rel | 0,49 / 69,7 | 0,089 / 69,7 | 0,057 / 64,6 |
| mute con musica `mh01_20`, B2 | 8,7 | 8,7 | 10,2 |
| mute con musica `mh01_1k`, S d'inserzione / rilascio | 7,16 / 5,45 dB | uguale | uguale |
| accensione `on_r300p`, A | 4,4 | 3,0 | 0,52 |

Il cavo e il carico basso **abbassano** tutte le cifre del contatto: fanno da partitore al
passaggio capacitivo. Lo 0 pF e i 100 kΩ della matrice sono davvero il caso peggiore.

### 4.3 Lo spegnimento (diagnostica per L30, non verdetto)

24 corse, come in L29c. **17 finiscono, 7 si fermano** su «Timestep too small» nel JFET del
blocco A. Sono tutte a rampa 10 ms, con il relè in ritardo di 5 ms o più. Si fermano nel ms del
trasferimento: la serie è aperta, la derivazione non ancora chiusa, e l'uscita scatta. Con
`method=gear` la corsa non riparte (una prova). Le corse fallite sono elencate in
`spegnimento/fallite.txt`.

Sulle 17 corse finite:
- **iii migliora alcune celle**: rampa 300 ms col rail + in ritardo e relè immediato da 235 a
  **5,1 µV**; rampa 10 ms col rail − in ritardo e relè immediato da 17,5 a 3,96 mV;
- **resta fuori quasi tutto**: 120 µV–5,0 mV con la rampa da 300 ms, fino a 2,3 V con la rampa da
  10 ms e il relè in ritardo di 100 ms.

I 3,96 mV del relè immediato **non sono spiegati**. Il passaggio attraverso 0,1 pF ne dà µV:
c'è un altro percorso, da cercare in L30.

**Per L30.** A macchina spenta la bobina è diseccitata, e con la iii il jack è isolato dal lato
condensatore. Se il relè cade prima che i rail perdano la regolazione, il salto non ha un percorso
resistivo verso il jack. È un elemento da considerare per il failsafe di ADR-043. È un
ragionamento, non una misura: le corse col relè in ritardo dicono che il tempo conta.

## 5. Cosa ne viene per il circuito

**Un deviatore, non un contatto in più.** Nella iii la serie (da `MAINC` al jack) e la
derivazione (da `MAINC` a massa) hanno un capo in comune. Sono quindi **un deviatore per
uscita**:
- il **comune** va al lato del condensatore;
- l'**NC** va a massa: a riposo e a mute inserito, lo stato sicuro;
- l'**NO** va al jack.

Il «prima apre, poi chiude» è quello del deviatore:
- all'inserzione la bobina si diseccita: l'NO apre, poi l'NC chiude;
- al rilascio si eccita: l'NC apre, poi l'NO chiude.

È l'ordine simulato. Il G6K-2F-Y è già a due scambi: un relè continua a servire L e R, e il
numero di relè non cambia. È un **ragionamento sulla geometria**: il cablaggio nel sorgente va
fatto e riletto (ERC, 2e) nel lotto che lo porta in `circuits/`.

**Il bleed lato condensatore** conta solo nel ms del trasferimento: a riposo l'NC tiene il nodo a
massa, e a mute rilasciato lo tiene il jack. Potrebbe essere superfluo, ma **non è misurato**:
tutte le corse l'hanno a 220 k / 470 k.

**Un vincolo per il layout (G2).** L'accensione scala con la capacità fra il lato condensatore e
il jack: 4,4 µV a 0,1 pF e 205 µV a 5 pF. È circa lineare, **~41 µV/pF**, e la soglia di 100 µV
si passa verso **2,4 pF**, contatto e piste insieme. È un calcolo sui due punti misurati.

## 6. Cosa resta

- **NC-028**: tutte le celle di verdetto stanno sotto 100 µV, lo spegnimento escluso. La
  chiusura della parte del mute la decide l'utente (vedi NONCOMPLIANCE.md).
- **Il sorgente**: il deviatore in `circuits/`, con l'utente.
- **L30**: lo spegnimento, le 7 corse che non finiscono e i 3,96 mV non spiegati.
- **20 kHz**: non corsi. Il passaggio del contatto aperto a 20 kHz è calcolato: 0,1 pF
  valgono ~80 MΩ contro un lato condensatore tenuto a massa da 0,1 Ω. È trascurabile.

## 7. I tempi

| Blocco | Corse | Durata |
|---|---|---|
| Controfattuale | 8 | ~3 min |
| Matrice | 111 | ~1 h 45, 8 in parallelo (dispersione e mute a 1 kHz fino a 36 min l'una) |
| Varianti | 43 | ~40 min |
| Spegnimento | 24 | ~5 min |

`analizza_par.py`: la matrice in ~15 min con 8 processi, le varianti in 13 min con 4.
