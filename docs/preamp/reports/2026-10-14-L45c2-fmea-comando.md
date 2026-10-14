# 2026-10-14 — L45c2, i guasti singoli dell'alimentatore: la linea dei relè e il comando

Quarta parte di **L45**, l'analisi dei guasti singoli (NC-042, maggiore, prima di G1), seconda metà
di **L45c** (scelta dell'utente, «Due parti»): T2 e la linea dei relè, la logica, la stella,
l'interruttore dello standby, i sorveglianti e il riferimento, il rivelatore di rete, il ritardo Δ in
hardware, i sink e i loro clamp, il relè di rete e il fusibile di T2, i pull-down e le letture del
micro. È la **prima analisi nella forma di ADR-070**: per ogni modo, oltre all'effetto misurato e al
verdetto, la gravità, la probabilità, la rilevabilità, la priorità e i rimedi candidati. Dati in
`docs/preamp/data/2026-10-14/L45c2/` (README). Nessun cambiamento al circuito; i rimedi sono di
**L45d**.

## In breve

- **Il ritardo Δ si perde in 45 modi** (14 simulati, 31 che si riducono a uno di loro): i relè di
  guadagno cadono fino a 4,3 ms **prima** che
  il jack si apra (ADR-045 li vuole ≥ Δ dopo). Al jack principale arrivano **6,44 mV filtrati**
  (~70 dB SPL a 1 m), sopra l'obiettivo di 2 mV e 42 dB sotto il tetto. È lo **stesso colpo del corto
  della linea a 12 V che ADR-051 ha già accettato** (6,44 mV anche lui, sul blocco di oggi). Durante
  l'ascolto lo danno V5 persa, Q505 o Q506 aperti, C520 o C528 in corto, D505 in corto, VREF aperto.
  **Latenti, che si vedono al mute dopo**: C528 aperto, D522 in corto, e soprattutto **D520 in corto e
  R524 aperta, che fanno perdere Δ a ogni pressione del tasto mute** senza nessun segno prima.
- **Q501 con gate e drain in corto è il mute che non si inserisce**, come Q501 in corto in L45c1. Alla
  perdita di rete il jack si apre solo **685 ms** dopo, quando cade VRELAY: **0,27 V filtrati** al
  jack principale (102 dB SPL), 0,62 V grezzi, sotto il tetto ma **fuori da P9 (b)** (il jack dopo
  10,6 V). Allo spegnimento il jack si apre a 213 ms invece di 31, e il guadagno 145 ms prima.
- **Nove modi mandano una parte oltre i suoi limiti** (gravità 5, PR-22). D506 o D508 in corto
  (lo zener in diretta mette VRELAY in corto attraverso Q501 o Q502, ~1 A per ~20 ms in un 2N7002 da
  115 mA). D505 in corto o la bobina di K501 in corto (VRELAY_REG a massa attraverso Q503 finché il
  firmware abbassa MAINS_REQ). R503, R510, R512 in corto (il riferimento o Q504 bruciati). U504 con
  ingresso e uscita in corto (12 V sul micro, massimo 6 V). E F501 che non apre: latente, il
  trasformatore T2 resta senza protezione.
- **I sorveglianti dei rail sono un punto singolo, ma il firmware fa da riserva.** Con un canale cieco
  (o un suo partitore) il firmware legge il rail dall'ADC e muta **2,2 ms** dopo la soglia, invece di
  1 ms. Il jack si apre prima di 10,6 V, e al jack arrivano 38 / 19 dB SPL. **Fuori da P9 (b) per la
  sola clausola del millisecondo**: per la regola di ADR-070 è gravità 4 e priorità alta. Le dieci righe
  ad alta priorità che vengono da qui sono di natura diversa dalle altre, e L45d deve vederlo.
- **Venti modi accendono il mute da soli** (il sorvegliante, il rivelatore o VRELAY che scattano
  senza guasto dei rail). Si fermano in sicurezza: la musica si ferma senza colpo (≤ 21 nV).
- **In standby**: con Q505 o Q506 in corto, R536 o R537 sbagliate, U508 B cieco, VRELAY resta alla
  scheda audio, ~1 W contro i 0,5 W di P9 (a). Con Q503 in corto o i due poli di K501 saldati resta
  acceso il toroidale. È consumo, non colpo.
- **Le tensioni sbagliate di VRELAY non fanno colpo**: da 5,6 V (il sorvegliante di VRELAY muta) a
  14,7 V (U503 in corto ingresso-uscita, niente interviene). A 14,7 V le bobine e U504 restano nei
  limiti a rete nominale; a rete +10 % e in standby **va verificato** che U504 resti sotto i suoi 16 V.

**Il conto, nella forma di ADR-070**: 215 modi, 20 a priorità **alta**, 11 **media**, 184 **bassa**.
Gravità: 83 a 1, 68 a 2, 44 a 3, 11 a 4, 9 a 5. Probabilità: 160 in classe 1 (< 1 FIT), 53 in classe 2,
2 in classe 3 (U503 e U504 spenti: 17,5 FIT). Rilevabilità: 113 latenti, 23 visti da chi ascolta, 79
dal circuito. La tabella, ordinata per priorità: `data/2026-10-14/L45c2/fmea_comando.md` (e `.csv`).

## Il banco

Il banco di **L45c1**, copiato e **controllato prima di ogni cambio**: `perdita` e `guasto_u501` corsi
dalla copia danno il CSV del firmware e il JSON del ponte **identici byte per byte**. Le aggiunte:

| Che cosa | Perché |
|---|---|
| la primitiva `spento` | un regolatore che si spegne (U504, V5) |
| l'evento `ins`, col suo caso di base senza guasto | il mute inserito dal tasto: è l'evento che mostra i guasti latenti di Δ |
| l'evento `gu503` | U503 spento, col metodo di `carico.txt` come `guasto_u503` |
| `modi.TF`, la fine anticipata | tre corse che si fermano su «Timestep too small» con tutti e due i metodi quando tutto è già spento (README) |
| `psu/accetta.py` | i punti fissi che la regola del ponte non sa riconoscere (sotto) |

Ogni deck di guasto, generato una volta, cambia solo le righe della sua primitiva (50 su 50).

**I punti fissi con un sorvegliante guasto.** `ponte.c` ricostruisce `MUTE_G_IN` dai sorveglianti
**supponendoli sani**, nei tick in cui l'uscita del firmware è cambiata rispetto a quella che ha
pilotato il circuito. Se il guasto è proprio un sorvegliante, il riferimento o la catena di `MUTE_G`,
la ricostruzione contraddice il circuito e la catena rifiuta il caso. `accetta.py` ne accetta nove,
con due regole scritte prima di applicarle:
- **regola A**, quattro casi: le uscite del firmware uguali byte per byte fra gli ultimi due giri, e
  ogni sostituzione nel tick in cui cambia `MUTE_REQ`;
- **regola B**, cinque casi: il firmware oscilla fra i giri, ma alla scheda audio arrivano le stesse
  cose. I rail coincidono entro 0,18 mV, e gli istanti del jack e del guadagno sono uguali.

Lo strumento è stato provato prima dell'uso sui due lati. Un punto fisso normale passa (regola A,
0 sostituzioni). Una copia con il giro 2 sostituito da un altro caso è rifiutata (8,4 V sui rail).

**La stella aperta non si simula**: il dominio del comando galleggia sulla massa audio, e il banco
legge i livelli logici rispetto alla massa. La corsa si ferma all'istante del guasto, e anche con 1 nF
dichiarato sull'apertura. A calcolo, i soli percorsi in continua fra i due domini sono i due partitori
dei sorveglianti: il ritorno dei relè si porta a ~+5,3 V, il canale del + vede 9,7 V e scatta. È il mute
falso, dal lato sicuro.

**I due carichi**: 100 kΩ sui tre jack per il picco filtrato di PR-23, e a vuoto per P10 (ADR-069).
Le 57 sequenze dell'alimentatore arrivano al punto fisso: 46 da sole, 2 accorciate, 9 con
`accetta.py` (una delle quali anche accorciata).
Le 114 corse audio per carico finiscono tutte, senza ripieghi.

**I criteri**: quelli di L45c1, scritti prima delle corse (`script/tabella_l45c2.py`).

| Il guasto | Criterio |
|---|---|
| porta un rail dentro \|13,5 V\| | **P9 (b)**: il sorvegliante entro 1 ms; il jack aperto prima che un rail arrivi a 10,6 V; il picco filtrato al principale ≤ 0,87 V, obiettivo 2 mV |
| lascia i rail fuori da \|13,5 V\| | **P10**: ogni jack ≤ 100 ms sopra 0,87 V, grezzo e a vuoto |
| latente | il criterio del suo evento |

## Le colonne di ADR-070

- **Gravità**: dal picco filtrato al jack principale e alle fisse (100 k), alzata al minimo della riga
  quando il guasto toglie una funzione (2) o manda una parte oltre i suoi limiti (5); 4 quando il
  verdetto è fuori.
- **Probabilità**: il tasso del modo in FIT, cioè il tasso della parte per la quota del modo. Le
  fonti sono in `data/2026-10-14/L45c2/tassi/fonti.md`, e c'è uno **scostamento da ADR-070**: SN 29500
  (parti 3–4), IEC 61709 e FMD-2016 non sono pubbliche. Per scelta dell'utente («Stima dichiarata»):
  - gli integrati prendono il tasso di SN 29500-2 dai documenti di sicurezza funzionale di TI:
    comparatore 12 FIT, LM4040 20 FIT, regolatore 100 FIT a 90 °C, dimezzato perché i nostri
    dissipano meno di 1 W;
  - per le passive e discrete c'è un **ordine di grandezza dichiarato come STIMA**;
  - la ripartizione dei modi viene da **MIL-HDBK-338B, Tabella 7.8-1** (dai dati FMD-91), o da quella
    del costruttore dove c'è.

  Le classi sono decadi. Se la norma arriva, i valori di tabella entrano in L45d.
- **Rilevabilità**: 1 il circuito (il mute in hardware o il firmware), 2 chi ascolta (la musica si
  ferma, un comando non risponde), 3 latente (si vede solo all'evento dopo, o mai).
- **Rimedi candidati**: le opzioni, senza scelta. La scelta è di L45d.

## Che cosa si è trovato

### Il ritardo Δ perso

ADR-045 vuole il permesso K6, e con lui i relè di guadagno, rilasciato **Δ dopo** i relè del jack. In
salute, alla perdita di rete il guadagno si muove 17 ms dopo il jack, allo spegnimento 37 ms dopo.
Questi guasti lo invertono:

| Guasto | Quando | Il guadagno prima del jack | Al jack principale |
|---|---|---|---|
| V5 persa (U504 spento, o un condensatore di V5 in corto, R517 / R518 in corto) | durante l'ascolto | 2,4 ms | 6,44 mV |
| Q505 aperto, J1 pin 4 aperto, C531 in corto | durante l'ascolto | 3,0 ms | 6,44 mV |
| Q506 aperto (e R537, R539, C529, R536, U508 B bloccato basso) | durante l'ascolto | 4,3 ms | 6,42 mV |
| C520 in corto (VRELAY_REG scaricata attraverso D512) | durante l'ascolto | 2,9 ms | 6,43 mV |
| C528 in corto (e R534 in corto, R516 in corto, U508 A bloccato basso) | durante l'ascolto | 3,0 ms | 6,44 mV |
| D505 in corto (e la bobina di K501 in corto) | durante l'ascolto | 1,8 ms | 6,42 mV |
| VREF aperto (U507) | durante l'ascolto | 0,5 ms | 6,44 mV |
| C523 aperto, poi U503 spento | latente | 3,0 ms | 6,44 mV |
| C528 aperto, poi la perdita di rete o U503 spento | latente | 3,0 ms | 6,44 / 6,42 mV |
| D522 in corto, poi la perdita di rete o il mute dal tasto | latente | 3,0 ms | 6,44 mV |
| **D520 in corto**, poi il mute dal tasto o lo spegnimento | latente, **a ogni mute** | 3,0 ms | 6,45 mV |
| **R524 aperta**, poi il mute dal tasto | latente, **a ogni mute** | 3,0 ms | 6,43 mV |
| Q502 aperto | durante l'ascolto, il jack resta chiuso | — | 6,44 mV |
| *riferimento*: l'uscita di U503 a massa (ADR-051, accettato) | | 3,0 ms | 6,44 mV |

Tutti dentro P10 e sotto il tetto di P9 (b) di 42 dB; gravità 3. Due meccanismi:
- **VRELAY che cade tutta insieme** (V5, Q505 / Q506, C520): le bobine del jack e K6 perdono
  l'alimentazione nello stesso istante, e vince la più veloce. È il caso «senza Δ» di L30, già
  accettato per il corto della linea a 12 V.
- **il permesso legato a MUTE_G**: D522 tiene `MUTE_G` sotto `PERMIT_G`, quindi un permesso che cade
  si porta dietro il mute (C528 in corto). Con **R524 aperta** vale anche il contrario: il pull-up del
  permesso non c'è più, e `PERMIT_G` resta su solo grazie a `MUTE_G` attraverso D522 (3,97 V nella
  corsa). Durante l'ascolto non si vede niente, ma a ogni mute permesso e jack cadono insieme. **D520 in
  corto** scarica `PERMIT_T` in `MUTE_REQ` appena il firmware lo abbassa: Δ perso anche lui a ogni
  mute.

I due latenti «a ogni mute» sono i più insidiosi. Non danno nessun segno, ripetono il colpo di 70 dB SPL
a ogni pressione del tasto, e lo fanno proprio con l'ordine che ADR-045 doveva garantire. Il colpo è
piccolo; il guasto lo rende sistematico.

### Il mute che non si inserisce: Q501 con gate e drain in corto

Il gate legato al drain fa di Q501 un diodo: quando il comparatore tira giù `MUTE_G`, tira giù anche
`MUTE_CMD`, cioè le bobine del jack restano alimentate. Il jack si apre solo quando cade VRELAY.

| Evento | Il jack si apre | Il guadagno | Filtrato al principale, 100 k | Grezzo a vuoto, principale / fisse | Verdetto |
|---|---|---|---|---|---|
| perdita di rete | **685 ms** (17 senza guasto) | 20 ms | **0,268 V** (102 dB SPL) | 0,62 / 0,67 V | **FUORI**: il jack dopo 10,6 V |
| spegnimento | 213 ms (31) | 68 ms, 145 ms prima del jack | 6,44 mV | 6,3 mV | entro, sopra l'obiettivo |

È il caso di Q501 in corto di L45c1, con le stesse cifre alla perdita di rete (0,27 V). La bobina
scende fino a 1,4 V prima del rilascio: col G6K all'angolo peggiore (rilascio garantito sotto 1,2 V)
il jack resta chiuso. Un relè vero rilascerebbe prima, ma il banco tiene l'angolo peggiore.

### Le parti oltre i loro limiti

| Guasto | Che cosa succede | Per quanto |
|---|---|---|
| D506 (o D508) in corto | lo zener D507 in diretta da VRELAY a `MUTE_CMD`: VRELAY in corto attraverso Q501, U503 al limite (~1 A), VRELAY_REG a 10,97 V | ~20 ms, finché il sorvegliante di VRELAY muta e Q501 si spegne |
| D505 in corto, bobina di K501 in corto | VRELAY_REG a massa attraverso Q503 | finché il firmware abbassa MAINS_REQ; Δ perso (1,8 ms) |
| R503 in corto | 5 V sul LM4040: ~0,25 A | finché si distrugge (di solito in corto: = VREF a 0, il mute falso) |
| R510 in corto | ~17 V sulla base di Q504 senza limite | Q504 si distrugge |
| R512 in corto | V5 a massa attraverso Q504 a ogni semionda | = V5 persa |
| U504 ingresso-uscita in corto | V5 = 12 V sull'ATtiny3216 (massimo 6 V) | il micro si guasta; dopo, è un guasto del micro (L54) |
| F501 che non apre | latente: un guasto di T2 non è interrotto | fino al secondo guasto |

Un 2N7002 regge 115 mA continui: ~1 A per 20 ms va oltre i suoi limiti. Se poi si guasta in corto, si
torna al mute che non si inserisce di L45c1.

### I sorveglianti ciechi

| Guasto | Chi muta | Dopo la soglia | Jack prima di 10,6 V | Al jack principale |
|---|---|---|---|---|
| U505 canale A cieco, poi U501 spento | il firmware (ADC) | 2,2 ms | sì | 0,17 mV (38 dB SPL) |
| U505 canale B cieco, poi U502 spento | il firmware | 2,1 ms | sì | 18 µV |
| il rivelatore di rete cieco (Q504 o D504 in corto), poi la perdita di rete | il sorvegliante dei rail | 89 ms dopo la perdita, appena il rail passa 13,5 V | sì | 80 µV |
| U506 canale B cieco, poi U503 spento | il firmware | 16 ms dopo il guasto di U503 | — | 17 nV |

La ridondanza c'è e funziona: il firmware, il sorvegliante dei rail e quello di VRELAY si coprono a
vicenda. Il prezzo è il millisecondo di P9 (b) per i due canali dei rail.

### Il resto

- **Il mute falso** (R506 aperta e i suoi simili, VREF a 0, C518 aperto, Q502 gate-drain, T2 o
  F501 aperti, D504 aperto, U503 fra 5,6 e 8,8 V, il toroidale staccato): il jack si apre, il permesso
  resta Δ dopo, ≤ 0,1 mV al jack. Gravità 2: la musica si ferma.
- **Il permesso che non si rilascia** (R534 aperta, R524 in corto, Q502 in corto, U508 A cieco):
  guadagno e trim non si cambiano più in mute. Gravità 2.
- **Le letture e i comandi del micro** (R541, R542, C532, C533, R517, R518 aperte): un comando
  dal frontale che non risponde o che legge a caso. Ogni lettura sbagliata parte con la sua sequenza.
  Gravità 2.
- **Senza effetto**: le tensioni di U503 fra 11,2 e 14,7 V, Q505 gate-drain (VRELAY a 10,76 V), un
  diodo di D503 aperto, C520 aperto a rete nominale, D512, C523, C529 aperti alla perdita di rete, R513
  in corto. Gravità 1.

## Le priorità

Le 20 righe **alte** e le 11 **medie**, per motivo:

| Motivo | Righe | Gravità | Probabilità | Rilevabilità |
|---|---|---|---|---|
| una parte oltre i suoi limiti | D506, D508, D505, K501 bobina in corto, R503, R510, R512 in corto; U504 ingresso-uscita in corto; F501 che non apre | 5 | 1–2 | 1–3 |
| il sorvegliante dei rail cieco (la clausola di 1 ms) | U505 A e B ciechi, la sua alimentazione aperta; R506, R509, R504 in corto; R507, R508, R505 aperte; C516 in corto | 4 | 1–2 | 3 |
| il mute che non si inserisce | Q501 gate-drain, alla perdita di rete | 4 | 1 | 3 |
| Δ perso, latente | C528 aperto (durante l'ascolto, alla perdita di rete, con U503 spento), C523 aperto con U503 spento, D520 in corto (mute e spegnimento), R524 aperta (mute), D522 in corto (perdita e mute), Q501 gate-drain allo spegnimento | 3 | 1–2 | 3 |
| Δ perso, frequente | V5 persa (17,5 FIT) | 3 | 3 | 1 |

Nessuna riga in classe di probabilità 4: il modo più frequente, un regolatore che si spegne, vale
17,5 FIT, cioè circa un apparecchio su 650 in dieci anni sempre acceso.

## Quello che il banco non dice

- **Le bobine sono resistive**: il rilascio allungato da un clamp a diodo semplice (D507 o D509 in
  corto) non si vede. Il jack è il primo a rilasciare finché l'allungamento resta sotto Δ ≥ 17,2 ms.
  Il datasheet del G6K non dice il rilascio col diodo.
- **I regolatori sono comportamentali**: niente anello, niente spegnimento termico. C521, C525 aperti
  (stabilità) sono a datasheet.
- **C520 aperto a rete −10 %** non è corso: a rete nominale VRELAY_REG ha valli a 11,65 V, 0,65 V
  sopra la soglia del sorvegliante di VRELAY. A −10 % potrebbe toccarla, con un mute che va e viene.
  **Da verificare.**
- **U503 ingresso-uscita in corto a rete +10 % e in standby**: il grezzo di VRELAY sale (L41a: ~17 V a
  +10 %), e U504 (MCP1703A) è a 16 V di ingresso massimo operativo. **Da verificare.**
- **La stella aperta** è a calcolo (sopra).
- **Il micro comportamentale con V5 persa** porta i suoi pin a valori negativi dopo ~20 ms: gli istanti
  che contano sono fissati prima (README).
- **Il fusibile non c'è**: un diodo di D503 in corto resta in corto nel banco. Nel telaio F501 apre, ed
  è T2 aperto.
- **Le probabilità sono stime** per le parti passive e discrete (sopra). Le classi reggono un fattore
  2–3, non un ordine di grandezza.

## Che cosa resta, e a chi

- **L45d**, per prima cosa: riporta le tabelle di L45a, L45b e L45c1 alla forma di ADR-070. Poi la
  decisione, con tutti i numeri davanti. Da qui:
  - **Δ perso**: accettarlo come ADR-051 (6,44 mV) per i guasti durante l'ascolto. Per i due latenti
    «a ogni mute» (D520 in corto, R524 aperta) decidere se basta l'accettazione o serve un controllo:
    il firmware che legge `PERMIT_G`, o un percorso ridondante. Un permesso che non dipenda né da
    VRELAY né da `MUTE_G` coprirebbe tutta la classe;
  - **il mute che non si inserisce** (Q501 gate-drain, e Q501 in corto di L45c1): lo stesso rimedio
    per tutti e due;
  - **i sovraccarichi** del comando: un limite di corrente sul ramo del clamp o su VRELAY, o un MOSFET
    che regga il limite di U503;
  - **la sovratensione su V5** (U504 in corto ingresso-uscita, ed eventualmente U503);
  - **la clausola di 1 ms** di P9 (b) quando a mutare è il firmware: lasciarla com'è (dieci righe fuori)
    o scrivere che la riserva del firmware vale per un sorvegliante guasto;
  - lo standby con VRELAY o il toroidale accesi (P9 (a)).
- **L54**: D522 aperta, i pin del micro in corto (R526, R527, R543, R544–R547), U504 in corto
  ingresso-uscita dopo il guasto del micro.
- **G2**: il fusibile F501 dal datasheet di T2; la tensione di U504 con U503 in corto a rete +10 %;
  C520 aperto a rete −10 %.

## Requisiti

- **NC-042**: avanza; con L45c2 l'analisi dei guasti è completa. Si chiude con L45d.
- **PR-23 / P9 (b)**: **non rispettato** per Q501 gate-drain alla perdita di rete (il jack dopo
  10,6 V, 0,27 V), e per la clausola di 1 ms con un sorvegliante dei rail cieco (il firmware muta a
  2,2 ms). Tutti gli altri modi che portano un rail sotto 13,5 V lo rispettano.
- **P10**: rispettato da tutti i modi che lasciano i rail in regolazione (al più 6,45 mV, mai sopra
  0,87 V).
- **ADR-045**: Δ non è garantito in 45 modi (sopra), a 6,44 mV.
- **PR-22**: nove modi mandano una parte oltre i suoi limiti.
- **P9 (a)**: fuori in standby per i modi che lasciano VRELAY o il toroidale accesi.
- **Nessuna non conformità aperta o chiusa**: i casi fuori stanno dentro NC-042, e se aprirne di nuove
  lo decide l'utente in L45d.
- **ADR-070**: applicata per la prima volta, con lo scostamento sulle fonti dei tassi scelto
  dall'utente.
