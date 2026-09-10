# L8 — Fase 3a: le parti nuove come fatti verificabili

Data: **2026-09-10** · Lotto **L8** · Fase 3a del giro componenti

Documento **datato**: è l'output di un'esecuzione, non si riscrive. Il
«perché» sta nelle ADR; qui c'è cosa è stato letto, con cosa, e che
verdetto ne esce.

---

## Esito in una riga

Le quattro parti sono state verificate, e **tre delle quattro portano una
sorpresa**: il THAT320 è **fine vita da nove giorni** con una finestra
d'acquisto che chiude fra venti; l'assegnazione NO/NC del secondo polo
del relè Omron nel codice è **invertita**, il che rompe il mute proprio
nel verso in cui ADR-012 esiste per non fallire; e per 2N5401 e 2N5551
**non esiste un modello SPICE del costruttore raggiungibile**.

## Il contratto: cosa è stato accettato come «verificato»

| Affermazione | Prova richiesta | Rispettata? |
|---|---|---|
| disponibilità / prezzo | la pagina prodotto vista, non uno snippet | sì, e dove non è stato possibile è **detto** |
| limite di datasheet | la tabella **con le sue condizioni di prova** | sì, sempre |
| modello SPICE | **ngspice lo carica** ed esegue | sì per il THAT320; per gli altri due non c'era niente da caricare |
| revisione di un PDF | letta dal **footer del documento**, mai dal nome | sì, su tutti e cinque i PDF congelati |

## Cosa è entrato in `vendor/`

Cinque documenti nuovi, tutti congelati a 0444 con `.sha256`, URL e
`PROVENANCE.json` accanto. Nessun file già presente in `vendor/` è stato
toccato.

| Percorso | File | sha256 (primi 12) | Revisione, **letta dal footer** |
|---|---|---|---|
| `vendor/relays/omron/G6K/` | `en-g6k.pdf` (1 893 025 B, 10 pp.) | `25d2046127b3` | Cat. No. **K106-E1-11** |
| `vendor/bjt_array/that/THAT320/` | `THAT_300-Series_Datasheet.pdf` (107 680 B, 8 pp.) | `721a07f1fccf` | Document 600041 **Rev 04** |
| " | `THATMacroModels-Rev05.zip` (55 641 B) | `a5699cf253cb` | archivio **Rev05** |
| " | `300_Series_Macro_01.lib` (5 366 B) | `399e1417f83c` | — |
| " | **`THAT-EOL-Memo.pdf`** (98 430 B, 1 p.) | `1e777dd3ac23` | memo **1 settembre 2026** |
| `vendor/bjt_npn/onsemi/2N5551/` | `2n5551t-d.pdf` (293 870 B, 9 pp.) | `4260af8721d6` | **Rev. 7**, gennaio 2026 |
| `vendor/bjt_pnp/onsemi/2N5401/` | `2n5401-d.pdf` (281 224 B, 7 pp.) | `db64ccde8c1b` | **Rev. 2.1** |

---

## 1. Omron G6K-2F-Y — quale contatto è NO e quale NC

### Perché è il primo

Non è un dettaglio di catalogo. `circuits/preamp/preamp_audio.py:70-76`
lo scrive da sé:

> WHICH throw is normally open is NOT yet confirmed against the Omron
> datasheet. Both relays here need a specific form and the design fails
> safe only if they are right.

E ADR-012 dice perché: il ramo cuffie finisce **in un paio di
elettrostatiche in testa**, non in un altoparlante a due metri.

### Il simbolo KiCad non poteva rispondere, e questo è stato verificato

Gli otto pin del simbolo `G6K-2` in `Relay.kicad_sym` hanno il campo
`name` **vuoto**. La deduzione registrata nel codice («pin map deduced
from the KiCad symbol geometry») ricava correttamente chi è bobina, chi è
comune e chi è deviatore, ma non poteva ricavare **quale** deviatore sia
normalmente chiuso, perché quell'informazione non è nei nomi.

Serviva il datasheet. `components.omron.com` risponde **403** a una
richiesta non-browser — come Mouser in L7 — ma `omronfs.omron.com`, che è
l'host documentale di Omron, risponde 200.

### Tre letture indipendenti, che dovevano coincidere

Il diagramma «Terminal Arrangement / Internal Connections» è **grafica
vettoriale**: `pdftotext` recupera i numeri dei pin ma non dice quale
linea tocchi quale. È il caso previsto dal metodo di L6 — due letture
indipendenti che devono coincidere — e qui ne sono state fatte **tre**.

**Lettura A — visiva.** Pagina 6 del PDF (pagina stampata 5), riga
`G6K-2F-Y`, rasterizzata a 2400 dpi con `pdftoppm`. La riga è stata
identificata rendendo l'intera fascia orizzontale insieme all'etichetta di
parte, per non fidarsi della posizione: il blocco è il quarto di sei, e
l'etichetta a sinistra dice `G6K-2F-Y`.

**Lettura B — meccanica, sulle coordinate.** La pagina è stata convertita
in SVG (`pdftocairo -svg`) e i tracciati nella finestra del disegno
estratti in punti PostScript. Non è un'impressione, sono numeri:

| Elemento | Coordinate (pt) |
|---|---|
| pad dei pin, riga alta (8, 7, 6, 5) | x = 481,22 / 495,37 / 509,53 / 523,68 |
| pad dei pin, riga bassa (1, 2, 3, 4) | stesse x |
| **polo alto**: perno (cerchio) | (509,51; 498,43) → **x del pin 6** |
| lama, asse | da (507,56; 505,77) a (509,52; 498,44) |
| punta della freccia di **sinistra** (pin 7) | x = 507,594, y = 503,98 |
| punta della freccia di **destra** (pin 5) | x = 511,426, y = 503,98 |
| **polo basso**: perno | (509,51; 516,48) → **x del pin 3** |

Alla quota y delle due punte, l'asse della lama sta a **x = 508,039**.
Distanza dalla punta di sinistra: **0,445 pt**, cioè meno della semilarghezza
della lama (≈0,38 pt) — **si toccano**. Distanza da quella di destra:
**3,387 pt**, cioè un vuoto pari a circa un quarto del passo fra pin. Il
rapporto è **7,6 a 1**: non è una lettura al limite. Il polo basso dà gli
stessi numeri con lo specchio verticale.

**Lettura C — le polilinee del simbolo KiCad.** Il simbolo non *nomina*
i pin ma li **disegna**. Estratte le polilinee di `G6K-2`:

| Polo | Lama | Punta contatto pin 2 / 7 | Punta contatto pin 4 / 5 |
|---|---|---|---|
| 1 (perno su pin 3) | da (0; −2,54) a (−1,905; 3,81) | (−1,905; 3,175) → **0,19 mm** | (1,905; 3,175) → 3,62 mm |
| 2 (perno su pin 6) | da (10,16; −2,54) a (8,255; 3,81) | (8,255; 3,175) → **0,19 mm** | (12,065; 3,175) → 3,62 mm |

Stesso rapporto, **19 a 1**. L'informazione era **già nel repo**, nelle
polilinee del simbolo: quello che era stato letto erano solo le posizioni
dei pin.

### Il verdetto

| Polo | COM | **NC** (a riposo chiuso) | **NO** (a riposo aperto) |
|---|---|---|---|
| 1 (riga bassa) | **3** | **2** | **4** |
| 2 (riga alta) | **6** | **7** | **5** |

**La trappola, ed è la ragione per cui l'errore è entrato.** Le due lame
pendono **dalla stessa parte** — non sono speculari. Ma nella riga alta i
numeri corrono 8-7-6-5 da sinistra a destra e in quella bassa 1-2-3-4:
quindi «il vicino di sinistra» è il **+1** in un polo e il **−1**
nell'altro. Il codice cabla `K_NO1 = "4" = 3+1` e `K_NO2 = "7" = 6+1`: la
regola «NO = COM+1» è **giusta per il polo 1 e sbagliata per il polo 2**.

Il footprint non c'entra e non è sbagliato: i pad di
`Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y` stanno a y = −3,8 / −0,6 / 1,6 / 3,8
per pin 1-4, cioè passi **3,2 / 2,2 / 2,2 mm**, che riproducono
esattamente le quote della variante **-Y** sul datasheet. La corrispondenza
conferma per una via indipendente anche che il pin 1 è di bobina.

### Cosa rompe, in concreto

`preamp_audio.py` assegna il **polo 1 al canale L e il polo 2 al canale R**
(`mute_lists[i] = [jk_L, pin_L, jk_R, pin_R]`, e il ciclo prende
`(K_COM1, K_NC1)` poi `(K_COM2, K_NC2)`). Con i pin veri:

| Relè | Canale L (polo 1, corretto) | Canale R (polo 2, invertito) |
|---|---|---|
| **mute**, bobina diseccitata (accensione, alimentazione assente) | uscita a massa: **muto** ✓ | pin 7 non collegato: **NON muto** — il transitorio d'accensione passa |
| **mute**, bobina eccitata (ascolto normale) | passa ✓ | pin 5 va a massa: **canale destro cortocircuitato** |
| **guadagno**, bobina diseccitata | R_g flottante: **0 dB** ✓ | pin 7 è NC: R_g a massa, **+10 dB** |

Il secondo guasto è rumoroso — al primo collaudo manca il canale destro.
**Il primo no**: è silenzioso, ed è esattamente quello contro cui ADR-012
è stata scritta. Aperta **NC-014**, bloccante.

Non corretto qui: `circuits/` è Fase 4 e L8 aveva il mandato esplicito di
non toccarlo.

---

## 2. THAT320

### 2.1 Il memo che cambia il lotto

La pagina prodotto di THAT porta in testa «Breaking News: End of Life for
Several THAT ICs». Il memo, congelato in `vendor/`, è firmato **Les Tyler,
President, THAT Corporation**, datato **1 settembre 2026**:

> Effective immediately, the following products are on EOL status:
> … **300-series transistor arrays**

Motivo dichiarato: la serie 300 è fabbricata sul processo Dielectric
Isolation su wafer da 4 pollici di THAT stessa, diventato insostenibile.
E c'è una scadenza:

> until **September 30, 2026**, we are offering a last-time buy (LTB)
> opportunity … please contact our IC sales folks at sales@thatcorp.com

Oggi è il **10 settembre 2026**: restano **venti giorni**.

**Il memo è del 1° settembre, ADR-013 è dell'8.** Era già pubblico quando
la topologia è stata disegnata e quando la Fase 1 ha scritto «Stock esatto
non verificato». Non era assente: è stato mancato. È la stessa lezione di
L6-L7 spostata di un passo — un dato di *ciclo di vita* non è un dato di
datasheet, e nessuno dei due è un dato di catalogo.

Aperta **NC-015**, bloccante. La decisione fra acquisto last-time-buy e
riprogettazione dello specchio è dell'utente; ADR-013 nomina già
l'alternativa nel proprio testo («lo specchio si fa meglio con PNP
appaiati o con l'array THAT320»).

### 2.2 Disponibilità: quello che si è visto, e quello che no

| Canale | Esito | Come |
|---|---|---|
| **DigiKey** | **non distribuisce THAT Corporation**, affatto | ricerche `THAT320` e `320P14-U`: zero risultati, e THAT non compare fra i fornitori |
| Mouser | **non verificato** — `Access to this page has been denied` + captcha | come in L7 |
| Farnell IT / Newark | **non verificato** — HTTP 403 | |
| TME | **non verificato** — HTTP 403 | |
| Musikding (DE, UE) | pagina vista: **€ 8,50**, *«Not available now!»* | l'unica pagina di vendita realmente letta |

**Lo stock non è fissato**, ed è una conclusione, non una lacuna: il solo
canale UE che si è riusciti a leggere è **esaurito**, e il distributore
che la Fase 1 aveva verificato per tutto il resto non tratta il
costruttore. È coerente con l'EOL.

### 2.3 BVceo ≥ 35 V — confermata, e il bar stesso è stato controllato

Datasheet Document 600041 Rev 04. **Due tabelle diverse, e contano in
modo diverso**:

| Fonte | Valore | Condizioni |
|---|---|---|
| *Absolute Maximum Ratings* | −36 V | nessuna: è una **soglia di stress**, non una caratteristica garantita |
| *Electrical Characteristics*, PNP Breakdown Voltage | **min −36 V**, tip −40 V | **IC = −10 µAdc, IB = 0** |

Il limite a cui si progetta è il secondo. **36 V ≥ 35 V: confermata**, con
1 V di margine sul minimo garantito.

**E il bar da dove viene?** Non da un requisito: dalla consegna della
Fase 2 (`reports/2026-09-08-fase2-bozza-topologia.md:179`), cioè i 30 V
fra i rail più margine. Il numero che conta davvero è la V_CE che i due
THAT320 vedono: `gain_block.py:433` registra **0,72 V e 1,17 V** a riposo,
e il limite strutturale assoluto è la campata fra i rail, **30 V**. Quindi
il margine è **≈ 30×** al punto di lavoro e **1,2×** nel caso limite
irrealizzabile. Nessuno dei due è stretto.

### 2.4 Il package nel codice è sbagliato

Tabella 1 «Ordering Information» elenca **esattamente due** varianti
THAT320: **320P14-U (DIP14)** e **320S14-U (SO14)**. Non esiste una
versione a 8 pin. `gain_block.py:303-304` assegna
`FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"`. Aperta **NC-016**,
maggiore.

Due note che il layout dovrà comunque conoscere:

- l'appaiamento specificato è **a coppie** — il datasheet dà
  `|VBE1−VBE2|` e `|VBE3−VBE4|` — quindi lo specchio deve usare 1&2
  oppure 3&4, **mai uno per coppia**;
- «the substrate should be ac-grounded to optimize speed and minimize
  crosstalk»: il package a 14 pin ha un pin di substrato, la topologia
  attuale non ne collega nessuno.

### 2.5 Il modello SPICE: esiste, è in forma macchina, e ngspice lo carica

`THATMacroModels-Rev05.zip` è l'archivio che la pagina *Device Models* di
THAT linka come «Download Macro Models». Dentro, `300 Series_Macro_01.lib`
è **5 366 byte** — esattamente la dimensione che la Fase 1 aveva
riportato, quindi quel dato è **confermato**, non ripetuto. Estratto e
rinominato con l'underscore al posto dello spazio (uno `.include` SPICE
non regge uno spazio nudo), contenuto **non modificato**: l'sha256
registrato è quello del membro dell'archivio.

**La prova.** Deck di scratch fuori dall'albero versionato, eseguito con
`scripts/run_simulation.sh`, alle **condizioni del datasheet** — non a
condizioni scelte per comodità, che è l'errore di L6 — cioè
`VCB = −10 V, IC = −1 mA, 1 kHz`, e `set temp = 25` perché ngspice gira a
27 °C:

```
Vneg vneg 0 DC -11
VbA  ba 0 DC 0 AC 1
IeA  0 ea DC 1m
CeA  ea 0 1
RcA  ca vneg 1k
QA   ca ba ea QPNP_THAT_NS
```

Polarizzazione ottenuta: **V_CB = −10,0136 V**, **I_C = −986,4 µA**
(1 mA nell'emettitore meno i 13,6 µA di base — torna esattamente).

**Esito: ngspice 47 esce 0 e non emette nemmeno un warning.** A differenza
dell'LSK489, che ne dava quattro, i parametri `QCO`, `RCO`, `VO`, `GAMMA`,
`PTF`, `XTF`, `ITF`, `VTF` sono tutti accettati in silenzio.

### 2.6 La scoperta: **THAT pubblica due modelli della stessa parte**

Sono `QPNP_THAT_NS` («Noise performance optimized», `RB = 25`) e
`QPNP_THAT_HF` («High frequency performance optimized», `RB = 103,345`).
Tutto il resto è **identico**.

| Modello | e_N a 1 kHz misurato | Datasheet tip. |
|---|---|---|
| `QPNP_THAT_NS` | **0,768 nV/√Hz** | 0,75 nV/√Hz → **+2,4%** |
| `QPNP_THAT_HF` | **1,314 nV/√Hz** | → **+75%** |

I due distano il **71%**. Il modello NS riproduce la cifra pubblicata dal
costruttore; l'altro no.

**Conseguenza operativa, e non è teorica**: una cifra di rumore e una di
stabilità prese dallo **stesso** modello non possono essere entrambe
giuste. Quale modello è stato usato va scritto **accanto a ogni numero**.
Finisce in `docs/limitations.md` #17.

**Controprova a mano, perché un numero solo non è una misura.** Per il
modello NS: rumore termico di `RB = 25 Ω` = √(4kT·25) = 0,642 nV/√Hz;
shot di collettore riferito all'ingresso = √(2q·I_C)/g_m = 0,463 nV/√Hz;
somma in quadratura **0,791 nV/√Hz** contro i 0,768 simulati — **3%**. La
strada analitica e ngspice concordano.

### 2.7 Nessun rumore 1/f, e la prova è empirica

Né `QPNP_THAT_NS` né `QPNP_THAT_HF` portano `KF` o `AF`. Non è stato
dedotto con un `grep`: lo spettro simulato del rumore riferito
all'ingresso è **piatto alla nona cifra significativa** da 100 Hz a
100 kHz (`7,68279563e-10` sia a 100 Hz sia a 1 kHz, `7,68279595e-10` a
100 kHz).

**Questo vincola NC-004.** L'analisi coi segnaposto diceva che i
contributori dominanti di rumore stanno **nello specchio di corrente**,
non nei JFET. Lo specchio è il THAT320, e il suo modello vendor **non ha
1/f** — esattamente come i segnaposto. Solo l'LSK489 ce l'ha. Quindi le
cifre di rumore che chiuderanno la metà mancante di NC-004 avranno ancora
un pavimento senza flicker proprio dove il rumore è dominante, e questo va
scritto accanto ai numeri e non sottinteso.

### 2.8 Il segnaposto, confrontato con il vendor

Sono grandezze omologhe, confrontate una a una — **non** con i
«~5,3 e ~5,0 nV/√Hz» di `gain_block.py:483`, che sono contributi *in
circuito* e sono un'altra quantità:

| Parametro | Segnaposto `PTHAT320` | Vendor NS | Datasheet |
|---|---|---|---|
| `RB` / rbb | 40 Ω | **25 Ω** | 25 Ω tip. |
| `CJC` / C_ob | 3 pF | 3,375 pF | 3 pF tip. a V_CB = −10 V |
| `TF` | 1,5 ns («f_T ~ 100 MHz») | **241,7 ps** | **f_T 325 MHz** tip. |

Il segnaposto è **~3× lento**: pessimistico sul polo dello specchio, cioè
sui margini di fase di NC-002 e NC-012.

---

## 3. 2N5401 e 2N5551

### 3.1 Disponibilità

Pagine DigiKey viste. Sono jellybean multi-costruttore: **6 costruttori
per il 2N5401**, **7 per il 2N5551**, entrambi in TO-92.

| Costruttore | 2N5401 qty1 | 2N5551 qty1 |
|---|---|---|
| onsemi | **$0,03429** | **$0,03429** |
| Diodes Incorporated | — | $0,07480 |
| Diotec Semiconductor | $0,17 / $0,29 | $0,17 / $1,09 |
| Lumimax | $0,09 | $0,10 |
| Slkormicro | $0,10 | $0,11 |
| GOODWORK (SOT-23) | $0,00956 | $0,00846 |

**Le quantità di stock non sono state verificate**, e va detto invece di
riempirlo: la pagina risultati di DigiKey non rende i numeri di
disponibilità a un client non-browser. Quello che si è visto sono i
prezzi e i costruttori. L'unica riga di stato di ciclo di vita apparsa è
**«Not Available» per l'OPN onsemi `2N5401TA`** (la confezione ammo), che
non dice niente sulla parte in sé.

L'approvvigionamento non è comunque il rischio qui: sono parti da tre
centesimi con sei fonti.

### 3.2 I limiti, letti con le loro condizioni

| Grandezza | 2N5401 (Rev. 2.1) | 2N5551 (Rev. 7) |
|---|---|---|
| BV_CEO | **−150 V min** @ I_C = −1 mA, I_B = 0 | **160 V min** @ I_C = 1,0 mA, I_B = 0 |
| f_T | **100 MHz min / 400 MHz tip** @ I_C = −10 mA, V_CE = −10 V, f = 100 MHz | **100 MHz min** @ I_C = 10 mA, V_CE = 10 V, f = 100 MHz |
| C_ob | **6 pF max** @ V_CB = −10 V, I_E = 0, f = 1 MHz | **6,0 pF max** @ V_CB = 10 V, I_E = 0, f = 1,0 MHz |
| h_FE | — | 50 … 250 |

Le tensioni di rottura non vincolano niente: 150 e 160 V contro 30 V di
campata fra i rail.

**Ma leggere la condizione cambia il verdetto su f_T.** È specificata a
**10 mA**. In questo circuito il VAS 2N5401 lavora a **6,443 mA**
(`gain_block.py:434`) e i 2N5551 fra ~2 e ~6 mA: sotto il punto di prova,
dove f_T è **più bassa**. Quindi «100 MHz» è già una lettura ottimistica
della parte nel suo punto di lavoro — e il segnaposto `NSS2N5551` dichiara
`TF = 0,5 ns`, cioè «f_T ~ 300 MHz», **tre volte** il minimo di datasheet
misurato a una corrente più alta di quella reale.

**Vale la pena metterli accanto**, perché i due segnaposto sbagliano in
**direzioni opposte**: il THAT320 finto è 3× *lento*, i 2N5551/5401 finti
sono ~3× *veloci*. Un margine di fase calcolato con entrambi non è
conservativo in modo noto — non si sa nemmeno da che parte sbagli.

### 3.3 Le varianti graduate del 2N5551 sono state dismesse

La tabella «ORDERING INFORMATION» a pagina 5 del datasheet Rev. 7 ha una
sezione **DISCONTINUED**, ed è il motivo per cui la revisione 7 esiste
(cronologia: *«2N5551YBU OPN Marked as Discontinued», 14/1/2026*):

| Attive | Dismesse |
|---|---|
| 2N5551TA, 2N5551TFR, 2N5551TF, 2N5551BU | 2N5551CTA, **2N5551YTA**, **2N5551YBU** |

Nota 5 del datasheet: il suffisso **-Y significa h_FE 180~240** (a
I_C = 10 mA, V_CE = 5,0 V), cioè le parti **selezionate per beta**. Sono
esattamente quelle sparite. Chi cercasse un 2N5551 graduato per avere beta
coerente nella coppia di cascode o nei generatori di corrente troverà solo
la dispersione piena **50…250**.

Il 2N5401 non ha una sezione dismessa. I suoi due OPN portano una «Y» ma
il Top Mark è `2N5401` e quel datasheet non definisce alcun grado: **le
due schede non condividono la convenzione**, e assumere che lo facciano
sarebbe stato l'errore.

### 3.4 Il modello SPICE: **non trovato in forma macchina dal costruttore**

È la risposta alla domanda che L8 doveva porre, ed è negativa.

| Tentativo | Esito |
|---|---|
| pagina modelli onsemi, `?rpn=2N5551` | elenco caricato via JavaScript: a un client non-browser risponde «Loading…» |
| percorsi indovinati sotto `/pub/Collateral/`, `/download/models/` | vedi la trappola qui sotto |
| Central Semiconductor, che *è* autore di modelli 2N | `my.centralsemi.com/content/engineering/spicemodels/index.php` è anch'essa solo-JavaScript |
| Diodes Incorporated | HTTP 403 a richieste automatiche |

**Mirror di terze parti esistono e non sono stati usati.** Circolano copie
GitHub di un `2N5401.lib` attribuito a Central Semiconductor. Un mirror
**non è provenienza vendor**, ed è precisamente ciò che la procedura di
ADR-013 impone per l'LSK489: si congela quello che il **costruttore** ha
servito, con il suo URL e il suo hash. Registrare un mirror come se fosse
il file del costruttore annullerebbe quella regola.

E non è nemmeno un caso da trascrizione come l'LSK489: **non è stato
trovato nemmeno un PDF del costruttore contenente il testo `.MODEL`**.

Aperta **NC-017**, maggiore: NC-004 non può chiudersi finché VAS e cascode
restano segnaposto.

### 3.5 La trappola del soft-404 di onsemi

`www.onsemi.com` risponde **HTTP 200 con la stessa pagina HTML da
303 722 byte** per *qualunque* percorso inesistente — verificato su tre
URL inventati diversi, tutti con lo stesso identico conteggio di byte. Il
primo `2N5551-D.PDF` scaricato era proprio quello: 200, ma
`text/html;charset=UTF-8`.

Su quel sito **un 200 non prova che il file esista**. È la regola di L8
(«un modello è verificato se ngspice lo carica») spinta un passo più
indietro: perfino il codice di stato HTTP può mentire. Si controlla il
`Content-Type` e la dimensione, o meglio si apre il file. Finisce in
`docs/limitations.md` #18.

---

## 4. Cosa L8 **non** ha toccato, e la verifica che sia vero

Non è un'affermazione a fiducia. `git diff --stat` del ramo contro
`origin/main` **non nomina** `circuits/`, `spice/preamp/` né
`docs/preamp/data/`: nessun numero del dossier è cambiato.

`models/` non è stato toccato, e la prova è il conteggio invariato:
`validate_models.py` dà **26 PASS, 0 FAIL, 0 SKIP**, e
`--check-provenance` **13 PASS**. La promozione dei modelli vendor dentro
`models/` è deliberatamente **fuori** da L8, deciso con l'utente: porta con
sé il controllo incrociato contro il datasheet — il lavoro di L7,
moltiplicato per parte — ed è un lotto suo.

Nessun file già presente in `vendor/` è stato modificato: i sette file
dell'LSK489 e del `1N4148_TEST` sono intatti.

`export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT`
cablato su `/Users/roberto/EDA`. L8 non li ha toccati, quindi restano — è
la regola già scritta in `STATE.md`.

**Fuori da `vendor/` e `docs/preamp/`, L8 tocca due soli file**, e vanno
detti: `docs/limitations.md`, che guadagna le voci **#17** e **#18**; e
`CLAUDE.md`, per **una riga** — dichiarava «12 limitazioni documentate»
quando erano già 16, e questo lotto lo avrebbe peggiorato a 18 lasciandolo
com'era.

## 5. Cosa **non** è stato verificato

Dichiarato, non riempito:

- **Le quantità di stock**, per nessuna parte. DigiKey non le rende a un
  client non-browser; Mouser, Farnell/Newark e TME rifiutano le richieste
  automatiche. Sono numeri che l'utente può leggere in trenta secondi da
  un browser, e che nessuno dovrebbe leggere da qui.
- **Se un modello SPICE di 2N5401/2N5551 esista dietro una sessione
  browser o dietro un account** sui siti onsemi e Central Semiconductor.
  L'assenza qui è «non raggiungibile senza browser», non «non esiste».
- **Il modello del THAT320 contro il datasheet**, oltre alla sola cifra di
  rumore che è tornata a 2,4%. C_ob, f_T e h_FE non sono stati incrociati:
  è il lavoro di promozione a `models/`, fuori scopo per decisione.
- **Il pinout del THAT320** (Figura 2 del datasheet), che serve al simbolo
  e al footprint. Non richiesto da L8; lo chiederà il lotto del package.
- **MJE15032/33**, gli altri due dispositivi ancora segnaposto: non erano
  nel mandato di L8.

## 6. Le non conformità aperte

| # | Titolo | Severità |
|---|---|---|
| **NC-014** | L'assegnazione NO/NC del polo 2 del G6K-2F-Y è invertita: mute e relè di guadagno falliscono nel verso sbagliato sul canale destro | **bloccante** |
| **NC-015** | Il THAT320 è fine vita dal 2026-09-01, con last-time buy che chiude il 2026-09-30 | **bloccante** |
| **NC-016** | Il footprint del THAT320 nel codice è SOIC-8, ma la parte esiste solo a 14 pin | maggiore |
| **NC-017** | Nessun modello SPICE del costruttore per 2N5401 e 2N5551: NC-004 non può chiudersi | maggiore |

## 7. Riproducibilità

Ogni riga di sopra ha il comando che la falsifica.

```sh
# le revisioni, dal footer e mai dal nome del file
/opt/homebrew/bin/pdftotext -layout vendor/relays/omron/G6K/en-g6k.pdf - | grep -i 'Cat. No.'
/opt/homebrew/bin/pdftotext -layout vendor/bjt_array/that/THAT320/THAT_300-Series_Datasheet.pdf - | grep -i 'Rev 0'
/opt/homebrew/bin/pdftotext -layout vendor/bjt_npn/onsemi/2N5551/2n5551t-d.pdf - | grep -i 'Rev. 7'
/opt/homebrew/bin/pdftotext -layout vendor/bjt_pnp/onsemi/2N5401/2n5401-d.pdf  - | grep -i 'Rev. 2.1'

# l'EOL, alla lettera
/opt/homebrew/bin/pdftotext -layout vendor/bjt_array/that/THAT320/THAT-EOL-Memo.pdf - | grep -i -A2 'EOL status'

# i contatti del relè, lettura visiva: pagina 6, riga G6K-2F-Y
/opt/homebrew/bin/pdftoppm -png -r 2400 -f 6 -l 6 -x 16000 -y 16050 -W 3000 -H 2100 \
  vendor/relays/omron/G6K/en-g6k.pdf /tmp/g6k_zoom

# i contatti del relè, lettura meccanica sulle coordinate
/opt/homebrew/bin/pdftocairo -svg -f 6 -l 6 vendor/relays/omron/G6K/en-g6k.pdf /tmp/g6k.svg

# gli hash congelati - tutti e 10, inclusi i due dell'LSK489 di L6/L7,
# che devono restare intatti. I sidecar hanno DUE formati (L6 ne scrisse
# uno col solo hash), quindi il controllo li gestisce entrambi.
/usr/bin/python3 -c "
import hashlib,os
for r,d,fs in os.walk('vendor'):
    for f in sorted(fs):
        if not f.endswith('.sha256'): continue
        parts=open(os.path.join(r,f)).read().split()
        name=os.path.basename(parts[1]) if len(parts)>1 else f[:-7]
        t=os.path.join(r,name)
        h=hashlib.sha256(open(t,'rb').read()).hexdigest()
        print('OK  ' if h==parts[0] else 'FAIL', t)
"

# che models/ non sia cambiato
/usr/bin/python3 scripts/validate_models.py            # 26/26
/usr/bin/python3 scripts/validate_models.py --check-provenance   # 13/13
```

Il deck che prova il modello THAT320 è riprodotto per intero al §2.5 ed è
stato tenuto fuori dall'albero versionato di proposito: è una prova di
caricamento, non un banco di prova del progetto.
