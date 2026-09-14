# Requisiti — Preamplificatore di linea

**Documento vivo.** Riscritto quando i requisiti cambiano. Ogni modifica
sostanziale deve avere una ADR corrispondente in `decisions/`.

Ultimo aggiornamento: 2026-09-14 (L27: E2, F5, V1, V2 e Architettura — ADR-026; L17: T1, T3, T5, F3, V1, Nota su P7 e Architettura — ADR-023; L11: F6, F7, T1, requisito P7 e Nota su P7 — ADR-021, ADR-022; L18: Nota su E5 — quota del ripple, ADR-020; L15: Nota su E3) · Stato: **congelati** (Fase 0 chiusa)

Le motivazioni non stanno qui: stanno nelle ADR referenziate e nel
report `reports/2026-09-08-analisi-catena.md`.

## Contesto d'uso

| Ruolo | Apparecchio |
|---|---|
| Sorgente | Phono MC a valvole autocostruito — uscita cathode follower ECC82, Zout ≈ 430 Ω, ~0,5 V |
| Sorgente | FiiO K11 R2R (Raspberry Pi / Volumio / Tidal) — 2,7 V RMS |
| Carico principale | conrad-johnson Evolution 250 (= **MV50 in triodo**, 30 W) — **Zin 100 kΩ confermata**, sensibilità 612–750 mV |
| Carico fisso | Singxer SA-1 V2 — volume proprio |
| Carico fisso | Stax SRM-T1 — Zin ~50 kΩ, volume proprio |
| Diffusori | Klipsch Heresy I — 96 dB/1W/1m |

## Requisiti funzionali

| # | Requisito | ADR |
|---|---|---|
| F1 | **4 ingressi** sbilanciati RCA, commutati a **relè** | ADR-009 |
| F2 | **Trim di livello comune, a valle del selettore d'ingresso**: 0 / −6 / −12 dB, **a relè bistabili**. Uno solo per tutti gli ingressi: cambiando sorgente si ritocca il trim o il volume | ADR-011, **ADR-027** |
| F3 | **3 uscite**: principale (attenuata) + 2 a livello fisso, **ciascuna fissa col proprio buffer** | ADR-008, **ADR-023** |
| F4 | **Attenuatore a scatti**, commutatore rotativo, 10 kΩ, resistenze 0,1% | ADR-009 |
| F5 | **Guadagno commutabile 0 / +3 / +10 dB**, relè sulla rete di controreazione. **A relè diseccitati il guadagno è 0 dB**: nessun guasto di bobina e nessuno stato di accensione può portare a un guadagno più alto. Due rami di R_g **in parallelo**: nessuno stato dei contatti supera il +10 dB | ADR-004, **ADR-019**, **ADR-026** |
| F6 | **Relè di mute** su tutte le uscite: accensione, commutazione guadagno e regolazione del trim (F8). **Tenibile a tempo indefinito**: il mute inserito rientra nel requisito P7 | ADR-012, **ADR-021** |
| F7 | **Nessun telecomando.** Operazionali e microcontrollore **ammessi solo fuori dal percorso del segnale**, alle condizioni di ADR-022: stato sicuro senza firmware, protezione dal corto non affidata solo al firmware, quota ausiliaria di rumore **1 µV RMS** | ADR-009, **ADR-022** |
| F8 | **Il trim d'ingresso funziona solo a mute inserito**, con interlock **elettrico**: il comando del trim raggiunge i propri relè solo se il mute è attivo. Due comandi distinti, il mute abilita il trim. Fuori mute agire sul trim non cambia nulla; il valore impostato resta applicato all'uscita dal mute | ADR-011, **ADR-019**, **ADR-027** |
| F9 | **Indicazione a LED del trim impostato**, letta dai **contatti** dei relè del trim e non dalla posizione del comando: fuori mute il comando può non corrispondere allo stato (F8), e il LED deve dire lo stato vero | **ADR-027** |

## Requisiti elettrici

| # | Parametro | Valore | Origine |
|---|---|---|---|
| E1 | Guadagno nominale | **0 dB** | ADR-001 |
| E2 | Guadagni alternativi | **+3 dB** e **+10 dB**, commutabili. Dal dimensionamento: **+3,05 dB** (finestra ±0,1 dB) e **+9,97 dB** (finestra 9,5–10,5 dB), entrambi asseriti sulla netlist | ADR-004, **ADR-019**, **ADR-026** |
| E3 | Impedenza d'ingresso | **≥ 100 kΩ**, al connettore d'ingresso, **in ogni posizione del trim** | Cap di accoppiamento del phono — vedi report e **nota sotto** |
| E3b | Attenuazione tipica all'ascolto | ~29–31 dB con il nuovo preamp | Guadagno finale 20,7×–25,3× |
| E4 | Impedenza d'uscita | **< 100 Ω in banda passante** (misurata escludendo la reattanza del condensatore d'accoppiamento), costante con la posizione del volume | ADR-002 |
| E5 | Rumore in uscita | **< 10 µV RMS** (20 Hz–20 kHz, non pesato), ripple dei rail compreso: **1 µV** è la quota dell'alimentazione | vedi note sotto · **ADR-020** |
| E6 | Livello massimo d'ingresso | 2,7 V RMS | FiiO K11 R2R |
| E7 | Alimentazione | **±15 V** regolati — confermati contro ±18 V. Ripple e rumore dei rail: **≤ 1 µV RMS riportati in uscita** (nota su E5) | ADR-015, **ADR-020** |
| E8 | Accoppiamento d'uscita | Capacitivo, **4,7 µF su tutte e tre le uscite** | ADR-007 |

**Nota su E5.** Con il guadagno del finale (21,1×) e le Heresy a
96 dB/1W/1m, 10 µV in uscita dal preamplificatore producono circa
**+13 dB SPL a 1 m**, cioè ~+4 dB in poltrona a 3 m — ben sotto il
rumore di fondo di una stanza silenziosa (25-30 dB SPL). A 2 µV si
scende a −0,5 dB SPL a 1 m. Il margine è ampio ma **non illimitato**: le
trombe da 96 dB rendono il rumore più udibile che su diffusori normali,
quindi il target va rispettato, non trattato come formalità.

**Nota su E5 — la quota del ripple d'alimentazione** (2026-09-13, L18,
**ADR-020**; chiude la metà «scritta» di **NC-011**).

**Il vincolo.** Dei 10 µV di E5, **1 µV RMS** spetta all'alimentazione. Il
ripple e il rumore dei **due** rail, riportati in uscita attraverso il PSRR
del blocco e sommati in quadratura su 20 Hz–20 kHz, devono restare
**≤ 1 µV**:

√( Σ_rail∈{+,−} Σ_k [ V_rail,k · 10^(−PSRR_rail(f_k)/20) ]² ) ≤ 1 µV

- **V_rail,k** è il valore RMS di ciascuna componente (un tono, o una densità
  di rumore integrata), preso **al nodo di alimentazione del blocco**.
- **PSRR(f)** è il **minimo fra le modalità di guadagno** sulla topologia
  vigente.

**Come si decide.** Si prende lo spettro dei rail, prima simulato da chi
progetta l'alimentatore e poi misurato sul prototipo, e la PSRR(f) dai CSV
vigenti: oggi `data/2026-09-13/tb_zout_psrr_noise_psrr{p,m}_10db.csv`,
topologia LS352. La modalità +10 dB è la peggiore su tutti gli 81 punti di
entrambi i rail. Il vincolo passa se la somma resta ≤ 1 µV. La verifica finale
è la misura in uscita sul prototipo.

**I limiti per tono, se tutta la quota cade su una sola frequenza**
(1 µV · 10^(PSRR/20), modalità +10 dB; 50 Hz interpolato sulla griglia). Con
più componenti vale la somma, non la tabella.

| f | PSRR rail + | V+ massimo | PSRR rail − | V− massimo |
|---|---|---|---|---|
| 50 Hz | 62,76 dB | 1,37 mV RMS (1,94 mV pk) | 69,51 dB | 2,99 mV RMS |
| 100 Hz | 62,17 dB | 1,28 mV RMS (1,81 mV pk) | 74,37 dB | 5,23 mV RMS |
| 1 kHz | 49,62 dB | 0,303 mV RMS | 87,75 dB | 24,4 mV RMS |
| 10 kHz | 29,82 dB | **31,0 µV RMS** | 86,23 dB | 20,5 mV RMS |
| 20 kHz | 23,81 dB | **15,5 µV RMS** | 81,91 dB | 12,5 mV RMS |

Rumore bianco sul solo rail +, su 20 Hz–20 kHz: **≤ 190 nV/√Hz**.

**Perché c'è una ADR, e non solo questa nota.** Col criterio di L15 la
ripartizione è **sostanziale**. Un progetto con 5 µV di rumore e 5 µV di
ripple faceva 7,07 µV e passava E5; con la quota non passa più. La nota sta
qui, accanto a E5 ed E7, perché è lì che la legge chi progetta
l'alimentatore. Il perché del numero sta in ADR-020, non in un'aggiunta ad
ADR-010 o ADR-015.

**Cosa la nota non copre.**
- **Sopra 20 kHz** E5 non vede niente, e il vincolo nemmeno: 100 mV a 100 kHz
  sul rail + passano. Eppure lì il PSRR+ vale **10,20 dB** e lavora uno
  switching. Il limite fuori banda, come la scelta del rimedio, è del lotto
  dell'alimentatore.
- **Il ronzio indotto dal toroide** (ADR-010) non passa dai rail.
- **Le cifre di PSRR** vengono da modelli in parte ancora segnaposto
  (NC-017). Quando la PSRR cambia, i limiti per tono si ricalcolano; la quota
  no.

Ragionamento completo: `reports/2026-09-13-L18-vincolo-psrr.md`.

**Nota su E3 — vale anche per il trim** (2026-09-13, L15; chiude la metà
«scritta» di **NC-005**).

**Il vincolo.** L'impedenza d'ingresso misurata **al connettore
d'ingresso**, col blocco A collegato (la sua `R_IN` compresa), deve restare
**≥ 100 kΩ in ciascuna delle tre posizioni del trim** (0 / −6 / −12 dB, F2),
comunque il trim sia commutato. *(Dal 2026-09-14, L16: il trim è uno solo, a
valle del selettore e a relè bistabili — F2, ADR-027. Il connettore
d'ingresso è quello della sorgente selezionata.)*

**Come si decide.** Analisi AC al connettore, una per posizione del trim:
passa se il **minimo di |Zin| su 20 Hz–20 kHz** è ≥ 100 kΩ in tutte e tre.
La misura non esiste ancora: il trim non è in `circuits/preamp/`, e la
misura è del lotto che ce lo mette (L16, NC-005 e NC-009). Oggi `R_IN = 1 MΩ`
in `gain_block.py` fissa la Zin del **solo** blocco A.

**Perché è E3 e non un requisito nuovo.** E3 nasce dal condensatore
d'uscita del phono a valvole (`reports/2026-09-08-analisi-catena.md`), e quel
condensatore vede l'impedenza **al connettore**, qualunque cosa ci sia
dietro: un trim che la porta a 13 kΩ viola E3 già com'è scritto. Il criterio
usato per dire che questa nota **non è una modifica sostanziale** — e quindi
non vuole una ADR — è verificabile: **non cambia l'insieme dei progetti
conformi**. Nessun progetto che E3 accettava viene rifiutato, e nessuno che
rifiutava viene accettato; la nota dice solo dove E3 si misura.

**Il controesempio che la nota esiste per fermare** (NC-005): un partitore
10 kΩ / 3,3 kΩ per i −12 dB, con `R_IN` in parallelo al ramo verso massa, dà
**Zin = 13,3 kΩ** (e −12,1 dB) — E3 violata di un ordine di grandezza.

**I due fatti che il dimensionamento dovrà conciliare.** Questa nota non
dimensiona il trim; registra ciò contro cui andrà dimensionato.

1. **L'attenuazione è portante**, non una comodità: con **ADR-015** il trim è
   ciò che separa il +10 dB col K11 a fondo scala dal clipping (K11 a −6 dB →
   4,27 V RMS richiesti in uscita invece di 8,54). Vedi **NC-009**, che porta
   anche le tre cifre di margine ancora da riconciliare.
2. **Alzare la Zin alza la resistenza del partitore vista dal blocco A.** Per
   un partitore di attenuazione k (tensione) e resistenza totale Z, la
   resistenza di Thévenin verso il blocco A vale **Z·k·(1−k)**: con Z al
   minimo di 100 kΩ, sorgente e `R_IN` trascurate, fa **≥ 25,0 kΩ a −6 dB** e
   **≥ 18,8 kΩ a −12 dB**. Quella resistenza porta **rumore Johnson** all'ingresso
   di una catena a 0 / +3 / +10 dB, da confrontare con **E5** — e l'affermazione
   di ADR-011 «non aggiunge rumore significativo» non ha ancora un numero. È
   anche la **«sorgente a monte»** della matrice **V1** («le tre posizioni del
   trim»), quindi entra nel margine di fase del blocco A.

**Dove questa nota non sta, e perché.** Non in ADR-011 come aggiunta in coda:
le ADR non si riscrivono (`decisions/README.md`, regola 2), e dopo il
2026-09-08 il progetto ha aggiunto condizioni ad ADR-011 con una ADR nuova
(ADR-019), non con un addendum. Non in una ADR nuova: non c'è una decisione da
registrare, c'è una conseguenza di E3. Quando il trim entrerà in
`circuits/preamp/`, i suoi valori porteranno un commento che rimanda qui.
Ragionamento completo: `reports/2026-09-13-L15-vincolo-e3.md`.

## Requisiti di topologia

| # | Requisito | ADR |
|---|---|---|
| T1 | **Classe A pura, tutto a discreti.** Nessun operazionale nel percorso del segnale. **Percorso del segnale** = ciò che il segnale attraversa fra i connettori, più ciò che chiude un anello su un nodo di segnale; un ingresso di sola rilevazione è ammesso entro le soglie di ADR-022. **La classe A si giudica sui percorsi ascoltabili**: ogni stadio fra un ingresso e un'uscita non silenziata resta in classe A, qualunque condizione ci sia sulle altre uscite. **Eccezione**: classe B ammessa solo negli stadi che servono esclusivamente uscite silenziate — mutate, in corto al connettore, o caricate da un apparecchio a bassa Zin — alle condizioni di P7 | ADR-003, **ADR-021**, **ADR-022**, **ADR-023** |
| T2 | **Nessun servo di continua** (sarebbe un operazionale mascherato) | ADR-007 |
| T3 | **Un solo blocco di guadagno**, progettato una volta, usato **quattro volte per canale**: blocco A, blocco B e un buffer per ogni uscita fissa | ADR-006, **ADR-023** |
| T4 | Coppia JFET d'ingresso: **LSK489 duale monolitico** — appaiamento intrinseco, supera il "stesso lotto" di ADR-005 | ADR-013 |
| T5 | **Un buffer per ogni uscita fissa**, pilotato dal blocco A; dopo ciascuno resistenza d'isolamento **47 Ω**, 4,7 µF e 470 kΩ di scarico. Supera il buffer unico di ADR-008 | **ADR-023** |
| T6 | **Coppia d'ingresso cascodata** in entrambi i blocchi | ADR-014 |
| T7 | **Ogni dispositivo attivo del percorso di segnale ha un modello SPICE del costruttore.** Un modello pubblicato come PDF conta (è il caso dell'LSK489, ADR-013); un mirror di terze parti **no** — la provenienza è ciò che si verifica | ADR-016 |
| T8 | **Nessun componente a fine vita entra nel progetto.** Un annuncio di EOL già pubblicato squalifica la parte anche se esiste una finestra di last-time buy. **Il controllo si rifà a ogni gate**, non una volta sola | ADR-016 |

**Nota su T7 e T8, perché sono più giovani degli altri** (2026-09-10, dopo
L8). Non sono preferenze di rigore: T7 è la condizione perché **NC-004**
possa chiudersi — oggi sei dispositivi attivi su sette sono segnaposto
scritti a mano con `KF = 0`, e due di essi sbagliano la f_T in direzioni
**opposte**, quindi i margini di fase attuali non sono conservativi in
modo noto. T8 nasce dal THAT320, che era fine vita da una settimana quando
la topologia lo ha scelto: ADR-013 aveva già la clausola giusta, ma solo
per il JFET, e all'array non l'aveva applicata nessuno.

## Requisiti fisici e di sicurezza

| # | Requisito | ADR |
|---|---|---|
| P1 | **Telaio unico**, alimentatore a bordo | ADR-010 |
| P2 | **Analisi di sicurezza rete obbligatoria** — assente = BLOCK automatico a G3 | ADR-010 |
| P3 | Trasformatore toroidale, massima distanza e orientamento ottimale rispetto agli ingressi | ADR-010 |
| P4 | Due circuiti stampati (alimentazione / audio), massa a stella | ADR-010 |
| P5 | Ventilazione prevista: ~3-4 W in mobile chiuso | ADR-010 |
| P6 | **Condensatori di segnale e resistenze critiche facilmente sostituibili** — passi multipli, per permettere all'utente di provare per ascolto | vedi nota |
| P7 | **Ogni uscita regge un corto, e il mute si tiene a tempo indefinito.** Con un corto franco al connettore di una qualsiasi uscita, o a mute inserito, con segnale e senza limite di tempo, **nessun componente esce dai propri limiti termici e SOA**: Tj ≤ 125 °C a 60 °C ambiente, a regime e nel transitorio prima di un'eventuale protezione. La tecnica è libera | **ADR-021** — vedi nota |

**Nota su P6.** Nessun agente di questo progetto giudica come suona un
circuito: è una regola di `AGENTS.md`. La valutazione soggettiva spetta
all'utente, sull'hardware reale. Il progetto la serve rendendo lo scambio
dei componenti **banale invece che richiedere un dissaldatore**.

**Nota su P7 — mute e corto sulle uscite** (2026-09-14, L11, **ADR-021**; chiude
**NC-001**).

**Il verbo.** Per ogni componente e ogni punto del dominio:
- **attivi**: 60 °C + P_media · RθJA ≤ 125 °C; ogni punto istantaneo
  (V_CE, I_C) dentro la SOA pubblicata; nel transitorio, Tj di picco ≤ 125 °C
  con la Zθ(t) del datasheet;
- **resistenze**: potenza ≤ quella nominale a 60 °C della parte scelta;
- **contatti di relè**: corrente RMS ≤ quella nominale di conduzione
  (G6K-2F-Y: 2 A).

**Il dominio:**
- il **mute** come è cablato, cioè tutti e tre i jack a massa insieme;
- un **corto ≤ 0,01 Ω** al connettore di una qualsiasi uscita;
- segnale sinusoidale 20 Hz–20 kHz d'ampiezza qualsiasi fino a E6, ogni
  posizione dell'attenuatore, ogni modalità di guadagno.

La tabella delle RθJA e delle potenze ammesse per parte sta in ADR-021.

**Come si decide.** `spice/preamp/tb/tb_mute_corto.cir`, dati in
`data/2026-09-14/L17/`, sulla topologia coi buffer delle fisse (ADR-023). I
dati di L11, un livello sopra, sono della topologia di prima. **Senza
protezione e senza dissipatore** il verdetto è **conforme**:
- MJE peggiore: 348 mW, Tj 81,8 °C, contro 1,04 W ammessi (blocco B, corto
  MAIN, +10 dB, 20 kHz); i buffer delle fisse 298 mW, Tj 78,6 °C;
- dispositivo più caldo: Q125, Tj 96,4 °C;
- L11 misurava 484 mW sul blocco A a mute, con le due fisse in parallelo sul
  suo nodo: coi buffer quel caso non esiste più.

Lo stesso deck verifica anche **T1 sui percorsi ascoltabili** (ADR-023): 294
righe, nessuno stadio ascoltabile fuori dalla classe A.

**I vincoli di distinta che il verdetto consegna** (a L9, che sceglie le parti):

| Resistenza | Potenza misurata | Nominale richiesta a 60 °C |
|---|---|---|
| 47 Ω dell'uscita principale | 1,10 W (corto MAIN, +10 dB, 20 kHz fondo scala) | **≥ 1,1 W** |
| 22 Ω d'emettitore, blocco B | 0,27 W | ≥ 0,27 W |
| 47 Ω delle uscite fisse | 0,155 W | ≥ 0,16 W |
| 22 Ω d'emettitore dei buffer delle fisse (L17) | 0,037 W | ≥ 0,04 W |

**Cosa la nota non copre.**
- **Un apparecchio spento a valle con Zin bassa** rientra da L17 (ADR-023):
  il buffer della fissa lo regge meglio di un corto (261 mW a 10 Ω, contro
  298 mW), e gli altri stadi restano in classe A.
- **Il gradino che il rilascio del mute porta sul jack** è V2, non P7: vedi
  NC-028.
- **Le cifre dipendono dal punto di lavoro.** Coi modelli vendor la corrente
  di riposo sale a 20,1 mA, perché il moltiplicatore di Vbe è tarato sui
  segnaposto, e il MJE peggiore arrivava a 496 mW (L11, prima dei buffer). Si ripete quando la Fase 4
  ritara la polarizzazione.

Ragionamento completo: `reports/2026-09-14-L11-mute-e-corto.md`.

## Requisiti di verifica

Nascono da una conseguenza scoperta tardi: il relè di ADR-004 **commuta
la rete di controreazione**, e la capacità d'ingresso (ADR-014) forma un
polo con quella rete. Impedenza diversa significa **polo in posizione
diversa**, quindi **margine di fase diverso nelle due modalità di
guadagno**.

Non c'è un caso di stabilità da verificare: ce ne sono molti. Se non
sono enumerati qui, verrà verificata solo la configurazione in cui il
circuito passa il test.

### V1 — Stabilità in tutte le configurazioni statiche

Il margine di fase va misurato per **ogni combinazione** di:

| Variabile | Valori da coprire |
|---|---|
| Blocco | A (buffer, guadagno 1) · **buffer delle fisse** (guadagno 1, ADR-023) · B a 0 dB · B a **+3 dB** · B a **+10 dB** |
| Posizione dell'attenuatore | minimo · **metà corsa (Zout massima, 2,5 kΩ)** · massimo |
| Carico d'uscita | cj 100 kΩ · Stax ~50 kΩ · Singxer (Zin ignota) · **carico capacitivo** (cavo, spazzata di lunghezza) |
| Sorgente a monte | phono 430 Ω · K11 <1,5 Ω · le tre posizioni del trim |

La posizione dell'attenuatore **non è un dettaglio**: la sua impedenza
d'uscita varia da ~0 a 2,5 kΩ e ritorno, quindi **il margine di fase
varia con la manopola del volume**.

**SOGLIA DI ACCETTAZIONE: margine di fase ≥ 60°**, deciso dall'utente il
2026-09-10 e registrato in **ADR-019**. Vale su **ogni** combinazione della
matrice qui sopra — blocco A compreso, e **caso peggiore capacitivo
compreso**, cioè la sonda da 4,7 nF che i banchi usano come margine di prova.

È la lettura più severa fra quelle proposte, ed è stata scelta esplicitamente.
Chiude **NC-012**, che chiedeva questa soglia e faceva notare che una soglia
senza il carico a cui si riferisce non sarebbe stata un requisito migliore.

**Dove si applica la sonda** (**ADR-024**, decisione dell'utente del
2026-09-14):
- la sonda è il **cavo d'interconnessione**, e sta **al jack**, dopo i 47 Ω e
  il 4,7 µF, sul blocco B e sui buffer delle fisse;
- il verdetto è il **minimo sulla spazzata fino a 4,7 nF**, non il valore a
  4,7 nF: al jack il minimo cade fra 2,2 e 3,3 nF;
- il **blocco A** si giudica col suo cablaggio verso l'attenuatore, con una
  capacità realistica presa **≤ 1 nF**;
- la sonda sul nodo d'uscita resta nei deck come informazione.

**Stato, da L27** (C_f a 330 pF, **ADR-025**; rete a tre livelli, **ADR-026**):
**conforme su ogni cella misurata.**
- Blocco B, carico 100 kΩ e 10 kΩ, `data/2026-09-14/L27/dopo/`:
  - 0 dB **61,83°** (attenuatore a metà corsa, 3,3 nF), 61,45° agli spigoli di
    tolleranza;
  - **+3 dB 69,79°** (2,8 nF, griglia fitta), 68,67° agli spigoli;
  - +10 dB 102,99°.
- Blocco A: **63,36°** (sorgente phono 430 Ω, 1 nF di cablaggio), L12.
- Buffer delle fisse: **61,63°** (Stax, 2,7 nF), L12. Rieseguiti in L27 con le
  curve entro 1,2·10⁻⁴.

**Resta senza misura** una riga della matrice, che non esiste ancora nel
circuito: le **tre posizioni del trim** (L16).

Una riga senza misura non è un circuito instabile: 60° è un **margine di progetto** —
copre la dispersione dei componenti, la capacità di cavi che nessuno ha
misurato e i modelli che non sono ancora tutti veri.

### V2 — Stabilità ai transienti di commutazione

Comportamento dinamico durante e dopo ogni commutazione:

- **Relè del guadagno (0 ↔ +3 ↔ +10 dB, ADR-019).** Vincolo di progetto: la rete va
  disposta in modo che **l'anello di controreazione non si apra mai**
  durante la transizione. Concretamente: il relè commuta la resistenza
  verso massa (R_g), mentre R_g mai in serie all'anello — così a
  contatti aperti il guadagno è 1 e l'anello resta chiuso. Se si
  commutasse R_f, l'anello si aprirebbe e lo stadio sbatterebbe contro
  un rail. **Da verificare sul circuito, non da assumere.**
  **Verificato in L27** (`tb_switch_v2.cir`), con due contatti che rimbalzano:
  in ogni passaggio fra 0, +3 e +10 dB, e in entrambi gli ordini dei contatti
  sul salto diretto, l'uscita resta dentro l'inviluppo del +10 dB. Il
  controfattuale con R_f commutata porta l'uscita a −13,77 V.
- **Relè del selettore d'ingresso**: commutazione a caldo fra sorgenti,
  con l'eventuale carica residua sui condensatori di accoppiamento a
  monte.
- **Relè di mute** (ADR-012): il transitorio all'inserzione e al
  rilascio.
- **Accensione e spegnimento**: salita e discesa asimmetrica dei rail.

### V3 — Recupero dalla saturazione

Un amplificatore discreto retroazionato può impiegare molto tempo a
riprendersi da un sovraccarico, o restare agganciato. Da verificare
esplicitamente. Nota di margine: a +10 dB con il K11 a fondo scala
l'uscita sarebbe 2,7 × 3,16 = **8,5 V**, contro rail a ±15 V — margine
adeguato ma non enorme, e quella combinazione è raggiungibile per errore.

### V4 — Le misure audio

THD/THD+N, risposta, rumore in banda (target E5), PSRR, Zout in
funzione della frequenza. Ognuna con la **provenienza del modello**
dichiarata accanto: una cifra di distorsione ottenuta da un modello
trascritto a mano da PDF (ADR-013) va riportata con quel caveat.

### V5 — Equivalenza fra netlist SPICE e netlist KiCad

La Fase 2 **non** ha usato il percorso documentato
`generate_schematic()` → `kicad-cli sch export netlist --format spice`:
per ~40 componenti finisce dritto nelle limitazioni #3 e #5. Al suo
posto `circuits/preamp/spice_export.py` percorre gli stessi oggetti
`Part`/`Net` di SKiDL, quindi **la definizione della topologia resta
una sola**.

Ma il rischio si sposta sull'esportatore: un suo difetto farebbe
divergere ciò che si simula da ciò che si manda in produzione, **senza
errori da nessuna delle due parti**. Non è teorico — è già successo una
volta in Fase 2 con i suffissi dei valori (vedi `docs/limitations.md`
#13), ed è rimasto invisibile per diverse analisi.

Prima di G2, le due netlist vanno **confrontate per equivalenza
topologica**, non lette a occhio: stessi nodi, stessi collegamenti,
stessi valori tradotti correttamente. È un controllo automatizzabile e
va automatizzato.

## Architettura

```
                                                          ┌─ BUFFER F1 ─47Ω─C 4,7µ─[mute]──► Singxer SA-1
 phono ECC82 ──┐                                          │  guadagno 1
 K11 R2R    ───┤  selettore    trim      BLOCCO A         ├─ BUFFER F2 ─47Ω─C 4,7µ─[mute]──► Stax SRM-T1
 (spare)    ───┤   a relè    0/-6/-12   guadagno 1  ──────┤  guadagno 1
 (spare)    ───┘             comune,    Zin ≥ 100k        │
                             LED
                                                          └─ ATTENUATORE ── BLOCCO B ─47Ω─C 4,7µ─[mute]──► cj EV250
                                                              10k, a scatti   0/+3/+10 dB
                                                                              K1, K5 su R_g
```

Quattro blocchi identici per canale, otto in totale (T3, ADR-023). Un'uscita
silenziata porta in classe B soltanto lo stadio che la serve.

## Requisiti espliciti di NON-obiettivo

- Nessun ingresso o uscita bilanciata.
- Nessuno stadio phono integrato (l'utente ne ha già uno).
- Nessun controllo di tono, filtro o loudness.
- Nessun telecomando, nessuna interfaccia digitale.

## Aperti

| Cosa | Impatto | Assegnato a | Stato |
|---|---|---|---|
| ~~Conferma specifiche cj EV250~~ | Struttura di guadagno | utente | **CHIUSO** — email costruttore + manuale MV50, vedi report 2026-09-08 |
| Impedenza d'**ingresso** Singxer SA-1 V2 | Dimensionamento C uscita fissa | Fase 1 | **NON PUBBLICATA.** Verificato sul manuale ufficiale. Vie residue: chiedere a Singxer, misurare, o adottare 4,7 µF e chiudere la questione |
| ~~Scelta del JFET d'ingresso~~ | Topologia dello stadio d'ingresso | utente | **CHIUSO** — **LSK489**, vedi ADR-013 |
| Valore del cap d'uscita del phono a valvole | Verifica del margine su E3 | utente | **RINVIATO** — non ha accesso agli schematici né può aprire agevolmente il telaio. Non blocca: E3 ≥ 100 kΩ copre il caso peggiore ragionevole |
| ~~Modello SPICE LSJ74~~ | — | — | **DECADUTO** — LSJ74 non è più in progetto (ADR-013) |
| Trascrizione del modello LSK489 da PDF | Credibilità della simulazione di distorsione | Fase 2 | **APERTO** — procedura obbligatoria in ADR-013, con controllo incrociato su datasheet |
