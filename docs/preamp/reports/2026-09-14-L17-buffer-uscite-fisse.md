# L17 — Un buffer per ogni uscita fissa (2026-09-14)

Lotto **L17**. Chiude **NC-010** (bloccante). Registra **ADR-023**. Apre
**NC-029**. Dati: `data/2026-09-14/L17/`.

## La decisione dell'utente

Il mandato chiedeva di scegliere con l'utente fra due strade, prima di
progettare:
- (a) un'ADR che estendesse l'eccezione di ADR-021 all'apparecchio spento a
  valle;
- (b) un buffer sulle fisse.

L'orchestratore le ha presentate coi numeri, ricontrollati dai CSV di
`data/2026-09-14/`:
- I_C(Q132) minima 2,395 mA a 100 Ω e −0,23 µA a 10 Ω;
- MJE a 299,5 mW col corto su una fissa, 483,7 mW col mute.

Le ha distinte in (b1) `GAINBLOCK` per fissa e (b2) buffer in classe A anche
in corto.

La risposta ha corretto la domanda invece di scegliere un'opzione. Parole
esatte:

> «Ti stai perdendo il punto principale, se c´é un corto sul un´uscita OPPURE
> se c´é un componente a bassa impedenza da spento e collegato a un´uscita
> secondaria, tutto l´ascolto "primario" non sará piú in classe A. Questo non
> é accettabile, mentre é ininfluente (se la termica é apposto) che un blocco
> NON in ascolto esca da classe A. Il punto della classe A é che deve restare
> per i path ascoltabili»

**Cosa l'orchestratore non aveva visto.** Anche il corto su una fissa, che
ADR-021 rendeva conforme, portava in classe B il blocco A e con lui il
percorso principale. Il principio esclude (a) e il buffer condiviso, e rende
superfluo (b2). Resta (b1), approvato col piano.

## Cosa è stato scritto

**ADR-023**, due decisioni:
1. la classe A si giudica sui **percorsi ascoltabili**, con definizione e
   verbo;
2. **un `GAINBLOCK` per ogni uscita fissa**, che supera ADR-008.

**Altre ADR, solo il campo `Stato:`:**
- ADR-008 superata;
- ADR-006 e ADR-021 precisate;
- l'indice.

**`REQUIREMENTS.md`:**
- T1, T3, T5;
- la colonna ADR di F3;
- la riga «Blocco» di V1;
- la «Nota su P7», con verdetto e vincoli di distinta rimisurati;
- il diagramma «Architettura», che portava ancora 100 Ω e 2,2 µF.

## La topologia

`circuits/preamp/preamp_audio.py`, in `channel()`: per ogni fissa
`gain_block(tag="F<k><ch>", base=base+400+100k, switchable=False, r_in=None)`.
- Il suo ingresso è collegato all'uscita del blocco A, e la 47 Ω della fissa
  parte dalla sua uscita.
- I riferimenti dei buffer sono 5xx e 6xx (canale L), 7xx e 8xx (canale R).
- Le 47 Ω, i condensatori e le scariche delle fisse restano R161-R166 e
  R361-R366.
- La netlist rigenerata passa **da 197 a 357 componenti**, con ERC a 0
  errori.
- `gain_block.py` non cambia, quindi `gain_block.subckt` e `_flat.inc`
  restano quelli di prima.

**R_IN non è montata sui buffer.** Il gate lo riporta a massa in continua
l'uscita del blocco A, accoppiata in continua. È la stessa ragione del
blocco B.

**Il nome della net.** Il nodo d'uscita del blocco A si è chiamato
`F1L_IN`, `F2L_IN` o `AR_OUT` a seconda dell'esecuzione e del canale, e
nessun ordine di collegamento l'ha reso stabile. È la limitazione #23, già
nota. Nessun controllo del repo legge quel nome, e il commento nel codice lo
dice.

## I guardiani, ciascuno visto fallire

**2e, `check_relay_safe_state.py`.** Verde sulla netlist nuova: 357
componenti, 4 relè. Su una copia con il contatto NC di K2 spostato su NO dà
3 rilevazioni ed exit 1. Il cablaggio del mute non è cambiato.

**2f, `preamp_blocks_draw.py`.** Ha un'asserzione nuova, ADR-023, sulla
netlist:
- la 47 Ω di ogni fissa parte da una net fatta **solo** di riferimenti del
  proprio buffer;
- il buffer è pilotato dal nodo del blocco A che porta l'attenuatore;
- il buffer non ha una rete `_RG`.

**Controprova.** Sulla netlist di `main`, esportata con `git show`, fallisce
con exit 1:

    R161 (L_FIX1) parte da L_ATT_TOP, che porta riferimenti delle centinaia [1]

Sulla netlist nuova passa. La prima versione falliva anche lì, perché fra i
nodi con J120 contava GND: corretta prima di fidarsene. Il disegno ora mostra
i due buffer, riletto su un'anteprima PNG.

**2g, `check_deck_refs.py`.** Verde su tutti i 16 deck, i due nuovi compresi.
`run_tests.sh` a fine lotto: **8 passed, 0 failed**.

## Le misure

Tutti i deck girano con `run_simulation.sh`, con ngspice rc 0. Nei log
compare solo il noto «model type mismatch» dell'LS350.

### 1. `tb_blockA_carichi.cir` — chi esce dalla classe A

**Circuito.** Tre `GAINBLOCK` da subckt. La fissa 1 porta l'apparecchio
spento, spazzato 470 kΩ → 0,01 Ω. La fissa 2 porta lo Stax da 50 kΩ. Frequenze
1 kHz e 20 kHz, 3,818 V di picco (E6).

**Il controllo che il deck sappia fallire.** Resistenze di selezione
riportano le fisse sul nodo del blocco A, cioè il cablaggio di ADR-008.

| | Blocco A, I_C(Q132) min | Buffer F2 | Buffer F1 |
|---|---|---|---|
| **Cablaggio nuovo**, tutte le 18 righe | **14,356 mA** | **14,509 mA** | classe A fino a 100 Ω; classe B a ≤ 22 Ω (1 kHz) e ≤ 47 Ω (20 kHz) |
| **Cablaggio vecchio**, controllo | classe B a ≤ 22 Ω (1 kHz), ≤ 47 Ω (20 kHz) | 14,551 mA (a vuoto) | 14,551 mA (a vuoto) |

**Il controllo riproduce L11** (L11 senza la sorgente da 1,5 Ω e senza gli
ingressi dei buffer):

| Impedenza a valle | Controllo, I_C(Q132) | L11 |
|---|---|---|
| 10 Ω, 1 kHz | min −0,0002 mA, max 57,33 mA | −0,23 µA, 57,258 mA |
| 100 Ω | min 2,360 mA | 2,395 mA |
| 0,01 Ω | max 65,52 mA | 65,456 mA |

**Il flag di ngspice** coincide col ricalcolo da `icmin_q132` e `icmax_q133`
in 108 righe su 108.

**Il livello.** Sul jack dello Stax passa da 3,80862 a 3,80865 V fra 470 kΩ e
0,01 Ω sulla fissa 1. In AC, vdb(OUTA) e vdb(J2) sono identici a cinque cifre.
In L11 la stessa spazzata AC muoveva il nodo di 0,0034 dB.

### 2. `tb_mute_corto.cir` — P7 e i percorsi ascoltabili

**Circuito.** Il deck di L11 esteso a quattro blocchi: A, F1, F2, B. Due casi
nuovi, apparecchio spento sulla fissa 1 a 10 Ω (5) e a 100 Ω (6). A +10 dB
anche i casi 2 e 5, per il verbo sul blocco B. In tutto 110 corse, 440 righe.

**ADR-023: 294 righe di percorsi ascoltabili, 0 fuori dalla classe A.**
Vanno in classe B soltanto questi stadi:

| Condizione | Stadi in classe B |
|---|---|
| mute | F1, F2, B |
| corto FIX1 | F1 |
| corto FIX2 | F2 |
| corto MAIN | B |
| spento a 10 Ω | F1 |
| spento a 100 Ω | nessuno |

Il blocco A non scende mai sotto **14,354 mA**.

**P7: nessuna violazione**, Tj con RθJA di ADR-021 a 60 °C.

| | MJE peggiore | Tj |
|---|---|---|
| Blocco A | 214,0 mW (riposo, in ogni caso) | 73,4 °C |
| Buffer F1 / F2 | **298,1 mW** (corto sulla propria fissa, o mute) | 78,6 °C |
| Blocco B | 348,2 mW (corto MAIN, +10 dB, 20 kHz, k 0,5) | 81,8 °C |
| Il più caldo | Q125 del blocco B, 87,3 mW | **96,4 °C** |

- **LS352** ≤ 3,3 mW, **LSK489** ≤ 38,3 mW in totale.
- **Apparecchio spento su F1**: 261,3 mW a 10 Ω, 214,2 mW a 100 Ω, contro
  298,1 mW del corto. Il corto resta il caso peggiore, ora misurato e non più
  argomentato.
- **Resistenze e contatti:**
  - 47 Ω principale 1,097 W;
  - 47 Ω delle fisse 0,154 W;
  - 22 Ω del blocco B 0,271 W, dei buffer 0,037 W;
  - contatti ≤ 152,7 mA RMS contro 2 A.
- **Confronto con L11, righe comuni.** Blocco A a mute da **483,7 a 214,0 mW**,
  corto su una fissa da 299,5 a 214,0 mW. Blocco B invariato entro 1 mW.

**Le prove che il deck non passa sempre:**
- **controprova indipendente**, corto FIX1 a 20 kHz. XF1.Q132: 297,94 mW da
  `@q[p]` contro 297,83 mW da (Vc−Ve)·Ic + (Vb−Ve)·Ib. RSEP1: 154,42 mW dalla
  corrente e dalla tensione;
- **stazionarietà**: scarto massimo 0,74 % fra le due metà della finestra;
- **riposo**: 14,556-14,557 mA come `tb_op-LS352`;
- **la classe B misurata dove deve esserci**: nei casi 1-5 compare proprio
  negli stadi silenziati;
- **il controllo sul cablaggio vecchio** è quello del deck 1.

**Transitorio del mute:**
- buffer F1: picco di potenza 0,728 W all'inserzione, contro 0,707 W a mute
  tenuto;
- blocco A a 0,266 W, non più caricato;
- rilascio senza segnale: picovolt.

**Calore.** A riposo **3,2248 W** per canale, **6,45 W** per i due, 0,806 W
per blocco. Vedi NC-029.

### 3. `tb_loop_blockA.cir` — il margine del blocco A col carico nuovo

**Il deck.** Portato ai valori veri, com'era richiesto da NC-002: prima aveva
100 Ω, 2,2 µF e 50 kΩ. Due carichi selezionabili:
1. nuovo: attenuatore e due buffer da subckt coi loro carichi;
2. il carico canonico di ADR-008 che NC-002 aveva misurato a mano, come
   controllo.

Sonda sul nodo d'uscita.

| C | Carico nuovo | Controllo | NC-002 (THAT320, 2026-09-09) |
|---|---|---|---|
| a vuoto | 69,30° | 69,31° | 69,83° |
| 1 nF | 63,45° | 63,47° | 64,08° |
| 2,2 nF | 55,87° | 55,91° | 56,65° |
| 4,7 nF | **40,96°** | 41,02° | 41,98° |

**Il controllo** sta entro 1° da NC-002, su una topologia diversa
(THAT320 → LS352).

**I buffer non cambiano il margine del blocco A**: con la sonda sul nodo lo
decide la sonda, non le fisse.

### 4. `tb_loop_bufferfissa.cir` — il margine del buffer

**Circuito.** Il blocco sotto prova da `_flat.inc`, sorgente da 1 Ω (Zout del
blocco A). Carico 47 Ω + 4,7 µF + 470 kΩ, e Singxer da 10 kΩ o Stax da 50 kΩ.
Sonda in due posizioni.

| C | Sonda al jack, 10 k | Sonda sul nodo, 10 k |
|---|---|---|
| a vuoto | 69,31° | 69,31° |
| 1 nF | 64,34° | 63,46° |
| 2,2 nF | **61,78°** | 55,88° |
| 4,7 nF | 62,27° | **40,98°** |

- Al jack il minimo, su entrambi i carichi, è **61,74°** (50 k, 2,2 nF).
- Guadagno d'anello a 10 Hz: 72,30 dB. Attraversamento fra 0,87 e 1,06 MHz.

**La prima esecuzione era sbagliata, e i suoi numeri non sono registrati.**
- **Cosa dava**: 105,85°, attraversamento a 76 MHz, 22,25 dB a 10 Hz.
- **La causa**: il nodo della sorgente si chiamava `SRC`. `_flat.inc` mette i
  dispositivi a livello superiore, e `SRC` è la sorgente comune della coppia
  JFET: la sorgente del deck cortocircuitava la coda.
- **Nessun errore**, e `check_deck_refs.py` non vede collisioni di nodi.
  Registrata come limitazione #24.
- **Il deck corretto** ha il nodo `VSRCN` e un commento che racconta la
  trappola.

### 5. `tb_uscite_fisse.cir` — E4 ed E5 sulle fisse nuove

**E4**, jack J1, carico tolto, 1 A iniettato:

| | 20 Hz | 1 kHz | 20 kHz |
|---|---|---|---|
| \|Z\| al jack | 1693,6 Ω | 57,95 Ω | 47,05 Ω |
| **Re(Z) al jack** | **53,13 Ω** | 47,03 Ω | 47,03 Ω |
| \|Z\| al nodo del buffer | 0,036 Ω | 0,039 Ω | 0,274 Ω |

Il verbo è Re(Z) < 100 Ω su 20 Hz–20 kHz: il massimo è **53,13 Ω**,
conforme. La parte reale esclude la reattanza del condensatore in serie, come
E4 chiede.

**E5**, catena A → F1 → J1, Singxer da 10 kΩ, 20 Hz–20 kHz:

| Sorgente | Rumore |
|---|---|
| 1 Ω | 1,624 µV |
| 430 Ω | **1,667 µV** |
| 2,5 kΩ | 1,859 µV |

- Contro **9,90 µV**: conforme.
- Il solo blocco A a 430 Ω dà 1,211 µV, coerente con 1,216 µV di
  `data/2026-09-10`.
- La somma in quadratura di due blocchi uguali prevedeva ≈ 1,64 µV.
- Pavimento, non previsione: KF = 0 nei segnaposto.

**Anche questa tabella è stata persa una volta.** Si chiamava
`tb_uscite_fisse_zout.csv`, lo stesso nome che il secondo passaggio di
`run_simulation.sh` dà alla conversione di `tb_uscite_fisse_zout.txt`, e
l'echo è stato sovrascritto in silenzio. Ora si chiama
`tb_uscite_fisse_e4.csv`. Registrata come limitazione #25.

## Non conformità

- **NC-010 chiusa.** Ogni percorso ascoltabile resta in classe A con un
  apparecchio spento, un corto o un mute su una fissa; P7 regge sui buffer.
  Nessun «cosa serve» della voce resta aperto.
- **NC-002 aggiornata**, senza rimedio:
  - le istanze sotto soglia sono ora sei su otto: in ogni canale il blocco A
    e i suoi due buffer, più il blocco B di NC-021;
  - il deck del blocco A è ai valori veri;
  - la domanda che L12 deve fare per prima: **dove si applica la sonda da
    4,7 nF**. Per il buffer, 40,98° sul nodo e 62,27° al jack.
- **NC-029 aperta** (maggiore): 6,45 W a riposo per la scheda audio, contro
  i 3-4 W che P5 prevede per l'apparecchio intero. Da lì dipende l'ipotesi di
  60 °C di ADR-021. Lotto **L30**.

Conteggio: **19 aperte, 4 bloccanti**.

## Visto e non toccato

- **Il pannello 3 del diagramma a blocchi** dice ancora «NON ANCORA
  CONFERMATO quale contatto del G6K-2F-Y sia NO e quale NC (lotto L8)». L21
  l'ha confermato e il guardiano 2e lo asserisce. Testo superato, fuori da
  questo lotto.
- **NC-028 vale anche sulle fisse coi buffer**: al rilascio del mute con
  segnale il jack J1 arriva a 5,57 V di picco, contro 3,81 V prima del mute.
- **R113 = 1 MEG nel subckt** sta anche sui buffer, dove `preamp_audio.py`
  non la monta: in parallelo a ~1 Ω non conta. È una differenza in più per V5.
- **E4 sull'uscita principale e a manopola che gira** resta NC-008 / L13.
  Qui è misurata solo la fissa 1, a guadagno unitario, dove la manopola non
  entra.
- **I file dati del dossier** leggono ancora `data/2026-09-09`.
- **ADR-003 stimava ~0,55 W per blocco**: la misura dà 0,806 W. È in NC-029.
