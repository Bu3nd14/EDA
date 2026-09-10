# ADR-017 — I dispositivi attivi che soddisfano T7 e T8: si cambia costruttore e package, non topologia

Data: 2026-09-10 · Stato: accettata

## Contesto

**ADR-016** ha posto T7 (ogni dispositivo attivo del percorso di segnale
ha un modello SPICE del costruttore) e T8 (nessun componente a fine vita
entra nel progetto), e ha lasciato tre parti **da verificare** —
MJE15032, MJE15033, 1N4148 — e due **da sostituire** — 2N5401 e 2N5551.

Il lotto **L24** ha fatto quelle verifiche alla fonte. Il report è
`reports/2026-09-10-L24-t7-dispositivi-attivi.md`; ogni cifra citata qui
è stata misurata, non dedotta.

Due cose sono cambiate rispetto a ciò che il progetto credeva.

**La prima: i due MJE e il 1N4148 hanno un modello del costruttore.** La
Fase 1 aveva scritto «pagina models esiste, file finale non confermato»,
e ADR-016 registrava quell'ipotesi come tale. onsemi serve i modelli su
`https://www.onsemi.com/download/models/lib/<parte>.lib`, e per tutte e
tre le parti il file esiste, ngspice lo carica e lo esegue.

**Conseguenza che vale più di tutto il resto del lotto: lo stadio
d'uscita regge.** ADR-016 aveva scritto che se i due MJE fossero caduti
«lo stadio d'uscita è una modifica di topologia, non un cambio di
package». Non cadono.

**La seconda: la conclusione di L8 su 2N5401/2N5551 era giusta sui
percorsi che aveva provato e sbagliata come affermazione generale.** L8
aveva registrato «Diodes Incorporated risponde 403 alle richieste
automatiche». È vero delle pagine HTML sotto `/design/` e `/part/`; non è
vero dei **file** di modello, che stanno su `/spice/download/` e
rispondono `200 text/plain` a un `curl` nudo.

Diodes Incorporated pubblica il modello del **2N5401 e del 2N5551**, sotto
i nomi **MMBT5401** e **MMBT5551**: stesso die, package SOT-23 invece di
TO-92.

## Decisione

**Nessuna delle sei parti attive verificate in L24 viene sostituita con un
dispositivo diverso. Cambia il costruttore di riferimento, e per due di
esse il package.**

| Ruolo | Parte oggi | Decisione | T7 | T8 |
|---|---|---|---|---|
| Uscita NPN (×1) | MJE15032 | **resta**, OPN **MJE15032G**, onsemi | modello onsemi | **Active** |
| Uscita PNP (×1) | MJE15033 | **resta**, OPN **MJE15033G**, onsemi | modello onsemi | ordinabile, con lacuna dichiarata |
| Riferimento di polarizzazione (×2) | 1N4148 | **resta**, attribuito a **onsemi** | modello onsemi (`1n914.lib`) | **Active** |
| VAS (×1) | 2N5401 | **MMBT5401**, Diodes Incorporated, **SOT-23** | modello Diodes | nessun marchio di dismissione |
| Coda, 2 cascode, carico VAS, moltiplicatore di Vbe (×5) | 2N5551 | **MMBT5551**, Diodes Incorporated, **SOT-23** | modello Diodes | nessun marchio di dismissione |

Il conteggio è quello reale del codice, non quello dei documenti: cinque
istanze di 2N5551 (`gain_block.py` righe 262, 291, 292, 328, 350) e una
di 2N5401 (riga 316).

Il **THAT320 non è oggetto di questa ADR**: è fuori per T8 e la sua
sostituzione è NC-015, lotto L22.

## Perché

### Perché tenere il die invece di cercare un dispositivo migliore

Il 2N5401 è il **VAS**, e con il Miller da 470 pF fissa il **polo
dominante di tutto l'amplificatore**. Un transistor davvero diverso lì
sposta una cifra su cui la topologia è costruita, e obbligherebbe a
rifare margine di fase, crossover e guadagno d'anello **prima** di sapere
se la topologia regge. Tenere il die tiene ferme tutte le ipotesi
dinamiche del progetto e riduce la sostituzione a ciò che è: un cambio di
costruttore e di contenitore.

I numeri che lo giustificano sono misurati, non asseriti — modello Diodes,
condizioni del datasheet Diodes, 25 °C:

| Grandezza | MMBT5401 | finestra datasheet | esito |
|---|---|---|---|
| hFE @ I_C = 10 mA, V_CE = −5 V | **124,9** | 60…240 | dentro |
| f_T @ I_C = 10 mA, V_CE = −10 V | **169,5 MHz** | 100 min / 300 tip | dentro |
| C_obo @ V_CB = −10 V, 1 MHz | **3,706 pF** | ≤ 6 pF | dentro |

| Grandezza | MMBT5551 | finestra datasheet | esito |
|---|---|---|---|
| hFE @ I_C = 10 mA, V_CE = 5 V | **107,2** | 80…250 | dentro |
| f_T @ I_C = 10 mA, V_CE = 10 V | **173,1 MHz** | 100 min / 300 tip | dentro |
| C_obo @ V_CB = 10 V, 1 MHz | **2,221 pF** | ≤ 6 pF | dentro |

**Sei controlli su sei dentro le finestre del costruttore.** È un esito
migliore di quello dell'LSK489 (verdetto misto, NC-013) e migliore di
quello del MJE15032, che al proprio punto di prova sta **sotto** il minimo
del proprio datasheet.

### Perché la ricerca di un sostituto «vero» è stata fatta lo stesso, e cosa ha trovato

Non si è tenuto il die per pigrizia: la rosa alternativa è stata cercata
prima, e **T8 l'ha quasi azzerata**. Letto dal costruttore, non dal
distributore:

| Candidato | Modello onsemi | Ciclo di vita presso onsemi |
|---|---|---|
| KSA992 (PNP audio basso rumore) | sì | **Last Shipments** — cioè last-time buy, che T8 squalifica |
| KSC1845 (NPN, il suo complementare) | sì | pagina prodotto assente |
| 2N3904 / 2N3906 | sì / sì | **tutti gli OPN Obsolete** |
| MPSA06 / MPSA56 / MPSA92 | sì | **tutti gli OPN Obsolete** |
| KSA733 | sì | **tutti gli OPN Obsolete** |
| BC550 | sì | **BC550CBU Active** — l'unico superstite |

Vale la pena fermarsi su due righe. **KSA992/KSC1845 è la coppia audio
classica**, ed è precisamente il tipo di scelta che sarebbe entrata «per
reputazione»: è in last-time buy. È il THAT320 evitato in anticipo, e
solo perché il controllo di T8 ora è obbligatorio invece che implicito.
**E 2N3904/2N3906 sono i due transistor più diffusi al mondo**, fuori
catalogo presso il costruttore che ne pubblica il modello: i cataloghi dei
distributori ne sono pieni, ma di *altri* costruttori, e T7 chiederebbe
allora il modello di *quel* costruttore.

L'unico superstite, BC550C, è NPN e non ha un complementare conforme —
onsemi non serve alcun modello per BC560. E il file `bc550.lib` dichiara
nella propria intestazione «MODEL PARAMETERS FROM MEASURED DATA:
**BC549**», cioè è adattato alla parte sorella (V_CEO 30 V contro 45 V), con
`BF = 228` che non corrisponde alla gradazione C dell'unico OPN attivo.
Non è una base su cui costruire uno stadio.

### Perché onsemi per il 1N4148, e perché il file si chiama 1N914

Il 1N4148 è un **codice generico di industria**, non la parte di un
costruttore. T7 non si soddisfa sostituendolo ma **attribuendolo**: si
sceglie il costruttore di cui il progetto userà modello e dichiarazione di
ciclo di vita. onsemi lo dichiara **Active** sulla propria pagina (sei OPN,
tutti Active) e serve un modello; Vishay serve un datasheet recente
(Rev. 1.6, 07-Nov-2024) ma **nessun modello SPICE** a un client
non-browser, solo modelli ECAD di terze parti.

Il file da usare è `1n914.lib`, non `1n4148.lib`, e la ragione è verificata
in tre passi: l'intestazione di `1n914.lib` dichiara «Product: 1N/FDLL914/A/B
/ 916/A/B / **4148** / 4448 · Package: **DO-35** / LL-34»; `1n4148.lib`
contiene invece `.SUBCKT 1N4148WT`, la variante SOD-323, ed è servito
byte-identico anche come `1n4148wt.lib`; e **la pagina prodotto 1N4148 di
onsemi linka un solo datasheet, ed è `1n914-d.pdf`**. È il costruttore
stesso a schedare il 1N4148 sotto il documento 1N914.

## Cosa questa decisione costa

Dichiarato, non nascosto.

**1. Sei istanze per blocco passano da TO-92 a SOT-23.** Diodes offre quel
die solo in package a montaggio superficiale — MMBT (SOT-23), MMST, DXT,
DZT e il duale MMDT. Nessuna versione TO-92 è stata trovata.

**2. La dissipazione ammessa si dimezza, e il margine è stato calcolato
sul punto di lavoro vero del progetto, non stimato.** `gain_block.py:434`
registra da `tb_op.cir`: VAS a **6,443 mA con V_CE 13,4 V**, cioè
**86,3 mW**. Il SOT-23 dà **310 mW** sul layout di pad minimo
raccomandato (350 mW su quello grande): margine **3,6×**. L'istanza
peggiore fra le altre è il carico del VAS, dello stesso ordine. Nessuna si
avvicina al limite. Ma il TO-92 sostituito dava 625 mW, quindi il margine
si dimezza, e questo diventa un vincolo di **layout** che prima non
esisteva.

**3. Il moltiplicatore di Vbe perde il proprio metodo di accoppiamento
termico.** `gain_block.py:350` porta una regola esplicita, già consegnata
a `pcb-automation-engineer`: il transistor «MUST be thermally coupled to
the NPN output device's tab (thermal compound + cable tie is enough at
225 mW)». **Un SOT-23 non si fascetta a un tab TO-220.** L'accoppiamento
deve diventare un percorso di rame sul PCB, e questa è una regola di
piazzamento diversa, da risolvere prima del G2. È aperta come **NC-019**.

**4. La BVceo del VAS scende da 160 a 150 V.** Diodes dà −150 V dove
onsemi dava −160 V per lo stesso codice di industria: due seconde fonti di
una parte generica non portano finestre identiche, e il progetto deve
stare su quella che nomina. Contro i 30 V di caso peggiore rail-to-rail
restano **5×**, quindi non è un vincolo — ma è la ragione per cui il
numero va riletto dal datasheet giusto e non copiato.

**5. Tutte le cifre di margine di fase vanno rifatte, e ora si sa di
quanto.** ADR-016 diceva che i segnaposto sbagliano «in direzioni opposte»
senza poterlo quantificare. L24 lo ha misurato:

| Segnaposto | f_T implicita | f_T misurata del modello vendor, al punto di lavoro | errore |
|---|---|---|---|
| `NSS2N5551` (TF 0,5 ns) | ~318 MHz | **88,8 MHz** a 2 mA (cascode, coda) | **3,6× veloce** |
| `PSS2N5401` (TF 0,6 ns) | ~265 MHz | **137,0 MHz** a 6 mA (VAS) | **1,9× veloce** |
| `NMJE15032` (TF 5,3 ns) | ~30 MHz | **11,2 MHz** a 15 mA | **2,8× veloce** |
| `PMJE15033` (TF 6,4 ns) | ~25 MHz | **12,6 MHz** a 15 mA | **2,0× veloce** |

E su `PSS2N5401` la C_ob del segnaposto è 6 pF contro **3,71 pF** reali,
cioè **1,6× alta** — un errore che sul polo di Miller spinge nella
direzione *opposta* a quello sulla f_T. Non si compensano in modo noto:
è esattamente ciò che «non conservativo in modo noto» significa, ora con
i numeri.

**6. Nessuno di questi modelli ha rumore 1/f.** Né i due Diodes, né i due
MJE, né il 1N4148. Come i segnaposto, come i modelli THAT
(`docs/limitations.md` #17). **Nel repo solo l'LSK489 ha `KF`/`AF`.**
Quindi NC-004 non si chiude con «arrivano i modelli veri»: le cifre di
rumore che ne usciranno restano un pavimento senza flicker, e va scritto
accanto a ogni numero.

## Cosa questa ADR NON fa

**Non sostituisce nulla in `circuits/preamp/`.** L24 trova e verifica; la
sostituzione, la rigenerazione degli artefatti e la riesecuzione delle
misure sono **Fase 4**. Nessun numero del dossier è cambiato in questo
lotto, ed è una proprietà verificata sul diff del ramo, non dichiarata.

**Non promuove i modelli in `models/`.** Il controllo incrociato contro i
datasheet è fatto e sta nel report e nelle `PROVENANCE.json`; la
promozione con le ricette di `validate_models.py` è il lotto successivo.

**Non tocca lo specchio d'ingresso.** Il THAT320 è NC-015 → L22.

## Alternative scartate

**Sostituire con una coppia complementare diversa in TO-92.** È la strada
che sembrava ovvia e T8 l'ha chiusa: vedi la tabella sopra. L'unico TO-92
attivo con modello onsemi è il BC550C, che è NPN, senza complementare
conforme, e il cui modello è dichiarato adattato al BC549.

**Accettare un mirror di terze parti per 2N5401/2N5551 in TO-92.**
Scartata: ADR-016 e ADR-013 lo vietano, e accettarlo qui svuoterebbe la
procedura di trascrizione imposta là per l'LSK489.

**Usare il modello onsemi `mmbt5551.lib`** — che esiste (644 byte) anche
se `2n5551.lib` no. Scartata perché mescolerebbe le fonti: il modello di
un costruttore verrebbe controllato contro le finestre del datasheet di un
altro. Il progetto sta su **un costruttore per dispositivo**, ed è la
condizione perché il controllo incrociato voglia dire qualcosa.

**Tenere il THAT320 nella stessa decisione.** Scartata: è una funzione
diversa (specchio d'ingresso appaiato), il suo vincolo è l'appaiamento
monolitico e non il modello, e mescolarla renderebbe questa ADR non
chiudibile. È L22.

## Da riaprire se

- Una delle parti scelte viene dichiarata fine vita. **Il controllo si
  rifà a ogni gate**, come T8 impone — e per MMBT5401/MMBT5551 con
  attenzione particolare, perché la loro conformità a T8 poggia
  sull'**assenza** di un timbro di dismissione sul datasheet e non su una
  stringa di stato esplicita: Diodes risponde 403 a un client automatico
  sulle pagine prodotto.
- Il ciclo di vita di **MJE15033G** diventa leggibile e dice qualcosa di
  diverso da «ordinabile». Oggi onsemi non ha una pagina prodotto per quella
  parte, e l'evidenza è la sola tabella d'ordine del datasheet di dicembre
  2024.
- La Fase 4, rifacendo margine di fase e Z_out con questi modelli, trova
  che il polo dominante si sposta abbastanza da mettere in discussione il
  Miller da 470 pF. In quel caso non è questa ADR a sbagliare — la scelta
  del die è ciò che rende quel confronto possibile — ma il valore di
  compensazione va rideciso con una ADR sua.
- Si decide che la scheda resta interamente a foro passante. In quel caso
  il vincolo da rilassare è T7 per il VAS e i cinque NPN, **con la lacuna
  dichiarata accanto a ogni numero che ne dipende**, secondo la clausola
  «Da riaprire se» di ADR-016.
