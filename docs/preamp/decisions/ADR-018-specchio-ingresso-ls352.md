# ADR-018 — Lo specchio d'ingresso è un LS352, e la sua degenerazione sale da 47 a 220 Ω

Data: 2026-09-10 · Stato: accettata

## Contesto

**ADR-016** ha posto T8 (nessun componente a fine vita) e ha squalificato il
**THAT320**, l'array PNP dello specchio di corrente d'ingresso, fine vita dal
2026-09-01 con last-time buy scartato. È **NC-015**, bloccante.

ADR-016 ha anche scritto che lo specchio va **riprogettato e non
ri-approvvigionato**, perché il THAT320 portava *appaiamento monolitico e
rbb = 25 Ω*, e cambiando parte cambiano punto di lavoro e cifre di rumore.

Dopo **L24** (ADR-017) il THAT320 era l'unico dei sette dispositivi attivi
senza una risposta.

## Decisione

**Lo specchio d'ingresso è un Linear Systems LS352**, dual PNP monolitico
della serie LS350, in **SOIC-8**, e la **degenerazione di emettitore sale da
47 Ω a 220 Ω**.

| | THAT320 (uscente) | LS352 (entrante) |
|---|---|---|
| Costruttore | THAT Corporation | Linear Integrated Systems |
| Ciclo di vita | **EOL dal 2026-09-01** | attivo (evidenza sotto) |
| Modello SPICE | `.lib` vendor, **due modelli** per la parte | PDF vendor, **uno** |
| Appaiamento | monolitico | monolitico, \|V_BE1−V_BE2\| **0,2 mV** tip / 0,5 max |
| Package usato | SOIC-8 **inesistente** (NC-016) | SOIC-8, pinout **pubblicato** |
| rbb del modello | RB = 25 | RB = 200, RBM = 10 |
| BV_CEO | — | 60 V min |

Il grado è **LS352** e non LS350 o LS351 per due ragioni misurabili:
BV_CEO **60 V** contro i 25 V dell'LS350, dove il caso peggiore rail-to-rail
del progetto è 30 V; e |V_BE1−V_BE2| 0,5 mV **max** contro 5 mV.

È anche la parte di **L23**: porta con sé footprint e simbolo, e chiude
**NC-016**.

## Perché, coi numeri

### Il dispositivo è più rumoroso, e lo stadio non lo è

È il risultato che ha deciso la ADR, ed entrambe le metà sono misurate.

**Il dispositivo da solo**, un deck e due modelli allo stesso punto di lavoro
(I_C = 1 mA, V_CB = 10 V, 1 kHz, 25 °C — le condizioni di prova del
datasheet THAT):

| Modello | rumore riferito all'ingresso |
|---|---|
| THAT320 `QPNP_THAT_NS` | **0,758 nV/√Hz** |
| LS350 | **1,685 nV/√Hz** — 2,22× peggio, +6,9 dB |

Il deck non valida sé stesso: il numero del THAT riproduce lo **0,768 nV/√Hz**
che `docs/limitations.md` #17 aveva già registrato per quel modello a quelle
condizioni.

La causa è nel modello: `RB = 200` con `IRB = 1e-05` e `BF = 500`, quindi a
1 mA la corrente di base (≈2 µA) è sotto `IRB` e la resistenza di base sta
vicino a **RB** e non a `RBM = 10`. Il THAT320 portava un `RB = 25` piatto —
quei 25 Ω erano precisamente ciò che ne faceva una parte a basso rumore.

**Lo stadio**, invece, migliora — perché il contributo dello specchio è
fissato dalla sua **transconduttanza**, e la degenerazione la compra indietro
più in fretta di quanto rbb la costi. Sweep di `tb_noise_breakdown.cir`,
configurazione D (caso peggiore, R_sorgente 2500 Ω), e V_BC **interno** della
metà d'uscita dello specchio, che è ciò che dice quanto è vicina al ginocchio:

| R_deg | rumore, caso peggiore | V_BC della metà d'uscita |
|---|---|---|
| 22 Ω | — | −53,1 mV — **satura** |
| 47 Ω | 6,988 µV | −0,4 mV — sul ginocchio |
| 100 Ω | 5,149 µV | +112,5 mV |
| 150 Ω | 4,580 µV | +219,4 mV |
| **220 Ω** | **4,231 µV** ← minimo | **+369,1 mV** ← **scelto** |
| 330 Ω | 4,515 µV — risale | +590,8 mV, ma il clipping negativo perde 0,77 V |

Il valore è stato **spazzato, non argomentato**, e il minimo esiste davvero:
a 330 Ω il rumore risale *e* l'headroom negativo crolla da −13,85 V a
−13,08 V.

Per riferimento, il THAT320 a 47 Ω misurava **5,697 µV** sullo stesso deck.
Quindi lo stadio finisce **25,7% più silenzioso di quando montava la parte
che è uscita di produzione**, con un dispositivo il cui rumore proprio è
2,2× peggiore. Su tutte e quattro le configurazioni:

| Config | THAT320 @ 47 Ω | LS352 @ 220 Ω |
|---|---|---|
| A intrinseco | 1,676 µV | **1,157 µV** |
| B | 1,718 µV | **1,216 µV** |
| C | 1,906 µV | **1,470 µV** |
| D caso peggiore | 5,697 µV | **4,231 µV** |

E resta dentro **E5** (≤ 10 µV) con più margine di prima.

### Perché il ginocchio esiste: RC = 231 Ω

Il modello LS350 porta **`RC = 231,405`**, contro i 18 Ω del THAT320. A
2,1 mA sono **0,49 V** persi *dentro* il dispositivo, su ~1,2 V di V_CE che
la topologia gli concede: la giunzione sta molto più vicina al ginocchio di
quanto dica la tensione ai terminali.

**Non è un artefatto del modello**: il datasheet dichiara V_CE(sat) ≤ 0,5 V a
I_C = 1 mA, che implica esattamente una RC di quell'ordine. È una proprietà
dei duali monolitici, e va tenuta in conto ogni volta che questa parte
finisce in un ramo con poco V_CE.

Il rimedio è controintuitivo e per questo è stato **misurato invece che
dedotto**: aumentare la degenerazione *aumenta* il margine di V_BC invece di
consumarlo, perché il nodo di base dello specchio si sposta con essa mentre
il collettore è inchiodato dal VAS.

### Cosa non è cambiato, verificato

- **Margine di fase**: 63,54° → 63,02° a 0 dB senza carico; 56,94° → 56,46°
  con 4,7 nF. Mezzo grado, su cifre che vengono comunque da segnaposto.
- **Guadagno d'anello DC**: 72,32 dB → 72,38 dB.
- **Clipping**: +13,017 V → +13,002 V, cioè 15 mV, **0,01 dB**. Il guadagno
  a piccolo segnale resta 3,1460.
- **Offset d'uscita**: −11,8 mV → −16,6 mV.

## Il verdetto sul modello è misto, e va detto

Controllo incrociato alle condizioni del datasheet, 25 °C — **cinque su sei
dentro**:

| Grandezza | Misurata | Finestra LS352 | Esito |
|---|---|---|---|
| h_FE @ 10 µA, V_CE 5 V | 441,2 | 200…600 | dentro |
| h_FE @ 100 µA | 483,2 | 200…600 | dentro |
| h_FE @ 1 mA | 490,6 | 200 min | dentro |
| C_OBO @ V_CB 5 V, 1 MHz | 1,584 pF | ≤ 2 pF | dentro |
| NF @ 100 µA, R_G 10 k, 1 kHz | 0,325 dB | ≤ 3 dB | dentro |
| **f_T @ 1 mA, V_CE 5 V** | **129,5 MHz** | **200 MHz min** | **FUORI**, −35% |

f_T è verificata su **tre gambe concordi** (attraversamento |h_fe| = 1:
129,5 MHz; prodotto guadagno-banda a 1 MHz: 124,5 MHz; a 10 MHz: 128,8 MHz).
La direzione è quella sicura — il modello è **più lento** della parte
garantita, quindi le cifre in alta frequenza che ne dipendono sono
pessimistiche — ma non di una quantità nota. È **NC-020**, maggiore.

**Nessun `KF`/`AF`**: niente rumore 1/f, come ogni altro modello del repo
tranne l'LSK489. Le cifre di rumore qui sopra sono un **pavimento senza
flicker**, e cadono proprio dove l'analisi dice che il rumore domina.
**NC-004 resta aperta** e questa ADR non la tocca.

## Come è stato letto il ciclo di vita, e il suo limite

Linear Systems non pubblica né una stringa di stato né un elenco di parti
dismesse, quindi la strada JSON-LD usata per onsemi in L24 qui non esiste.
L'evidenza del costruttore è: pagina prodotto viva con l'intera gamma di
package, datasheet senza timbro di dismissione, e — decisivo — un **modello
SPICE rilasciato dal costruttore il 2026-07-27**, due mesi prima di questo
lotto. Un costruttore non emette una Rev. 2 del modello di simulazione di una
parte che sta ritirando.

**È evidenza più debole di uno stato esplicito**, ed è registrata come tale
invece che promossa. Manca anche il controllo che in L24 rese significativo
il silenzio di Diodes — una parte notoriamente morta dello stesso costruttore,
timbrata OBSOLETE — perché da questo costruttore non è stato trovato alcun
elenco di dismessi contro cui provare il silenzio.

## Alternative scartate

**DMMT5401 (Diodes Incorporated), dual PNP in SOT-26.** Era la strada
attraente: **stesso die** del MMBT5401 che ADR-017 ha già scelto per il VAS,
stesso costruttore di cui il repo ha già congelato due modelli, percorso del
modello già dimostrato. **Scartata sul datasheet**: è appaiato su
h_FE/V_CE(sat)/V_BE(sat) al 2% e **non su V_BE** — la nota 1 lo chiama
«intrinsically matched as this is built with adjacent die from the same
wafer» — e la sua NF è **8 dB max** contro i 3 dB dell'LS350.
L'appaiamento di uno specchio *è* un appaiamento di V_BE: l'unica specifica
che contava è quella che non porta.

**SSM2220 (Analog Devices).** Il sostituto naturale del THAT320 per funzione
e per rumore (0,7 nV/√Hz tip.). **Non verificabile da qui**: `analog.com` e la
sua CDN non rispondono a un client automatico — tre tentativi, un
`HTTP/2 INTERNAL_ERROR` e due timeout a 60 e 90 s, su HTTP/2 e HTTP/1.1, sia
sulla pagina prodotto sia sul PDF. Una ricerca web riportava la parte come
*Obsolete*, e **ADR-016 non accetta un risultato di ricerca come evidenza del
costruttore**: resta **dichiarata non verificata** invece di risolta in un
senso o nell'altro. Se ADI tornasse raggiungibile, è la prima alternativa da
riesaminare.

**Una coppia discreta appaiata a mano** (due MMBT5401 selezionati).
Soddisfarebbe T7 e T8 con modelli già congelati nel repo, ma sono due dadi in
due package: niente appaiamento monolitico e niente accoppiamento termico,
cioè proprio ciò che allo specchio serve. Era il ripiego dichiarato e non è
servito.

**Tenere i 47 Ω.** Scartata dalla misura: a 47 Ω la metà d'uscita dello
specchio sta **sul ginocchio** (V_BC interno −0,4 mV) e il rumore dello stadio
peggiora del 23% rispetto al THAT320 invece di migliorare del 26%.

## Cosa questa decisione NON fa

**Non tocca gli altri dispositivi attivi.** ADR-017 resta intatta: la
sostituzione di MMBT5401/MMBT5551 nella topologia è Fase 4.

**Non chiude NC-004.** Il modello non ha rumore 1/f.

**Non promuove nulla in `models/` oltre a sé stessa.** I cinque modelli di
L24 restano da promuovere in L25.

**Non ri-misura il resto del blocco.** Margine di fase, PSRR, Z_out e risposta
sono stati controllati quanto basta a provare che la sostituzione non li
muove, ma i loro valori canonici restano quelli da rifare in Fase 4 con tutti
i modelli veri. I dati versionati in `data/2026-09-09/` descrivono la
topologia **col THAT320**.

## Da riaprire se

- **Linear Systems dichiara l'LS350 fine vita.** Il controllo T8 si rifà a
  ogni gate, e qui con attenzione particolare, perché la conformità poggia
  sull'assenza di un annuncio e su un modello recente, non su uno stato
  esplicito.
- **ADI torna raggiungibile** e l'SSM2220 risulta in produzione: è una parte
  progettata per questo mestiere, con rbb da parte a basso rumore.
- **La Fase 4**, rifacendo il rumore con tutti i modelli veri, trova che il
  contributo dello specchio non è più dominante: allora l'ottimo di 220 Ω va
  ricalcolato, perché è un ottimo *di questo* bilancio di rumore.
- **Il layout non riesce a garantire l'accoppiamento termico** fra le due
  metà. Qui non è un rischio — sono sullo stesso die — ma se un giorno la
  parte venisse sostituita da due discreti, la degenerazione da 220 Ω non
  basterebbe a coprire la deriva.
