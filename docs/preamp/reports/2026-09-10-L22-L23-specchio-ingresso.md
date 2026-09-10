# L22 + L23 — Lo specchio d'ingresso senza THAT320

Data: 2026-09-10 · Lotto: **L22 + L23** · Decisione: **ADR-018**
Chiude: **NC-015** (bloccante), **NC-016** · Apre: **NC-020**

---

## Il risultato in cinque righe

1. **La parte è un Linear Systems LS352**, dual PNP monolitico in SOIC-8,
   |V_BE1−V_BE2| 0,2 mV tip / 0,5 max. Modello del costruttore pubblicato
   come PDF, **Rev. 2 del 2026-07-27**, trascritto sotto la procedura a due
   letture di ADR-013: **byte-identiche**, stesso sha256.
2. **Il dispositivo è più rumoroso e lo stadio non lo è.** Da solo fa
   1,685 nV/√Hz contro gli 0,758 del THAT320 sullo stesso deck — 2,2× peggio.
   Ma portando la degenerazione da 47 a **220 Ω**, valore **spazzato e non
   argomentato**, lo stadio d'ingresso finisce **25,7% più silenzioso** di
   quando montava la parte uscita di produzione.
3. **Il duale è ora UNA parte, non due.** Prima erano due Part con un
   footprint SOIC-8 ciascuna, cioè due package sul PCB per un dispositivo
   solo. Con la libreria di simboli del progetto — la prima del repo — il
   conteggio dei componenti su SOIC-8 scende da quattro a tre.
4. **Il verdetto sul modello è misto**: cinque grandezze su sei dentro le
   finestre del datasheet, ma la **f_T sta il 35% sotto il minimo**, su tre
   gambe concordi. È NC-020.
5. **Due candidati sono stati scartati alla fonte**, non per preferenza: il
   DMMT5401 di Diodes perché appaiato su h_FE e **non su V_BE**, e l'SSM2220
   di Analog Devices perché `analog.com` **non risponde** a un client
   automatico — dichiarato non verificato, non risolto.

---

## 1. Il metodo, e la trappola nuova che ha trovato

La procedura è quella di L6+L7+L24, e ogni passo costa una scoperta a un
lotto precedente: scaricare dal costruttore; registrare stato HTTP,
`Content-Type` **e byte**; leggere la revisione dal **footer**; leggere i
limiti dalle Electrical Characteristics con le loro condizioni; contare
**quanti** modelli il costruttore pubblica per la stessa parte; provare che
ngspice lo carica **a 25 °C**; congelare con sha256 e `PROVENANCE.json`.

**La trappola nuova è `docs/limitations.md` #21**, e ha morso subito. I
modelli SPICE di Diodes stanno su `/spice/download/<id>/<PARTE>.spice.txt`.
Il segmento `<PARTE>` **non viene verificato dal server**:

```sh
curl -sS -L -D - -o /dev/null \
  https://www.diodes.com/spice/download/2587/DMMT5401.spice.txt
# 200 ... content-type: text/plain; name="MMBT5401.spice.txt"
```

L'id 2587 è quello del **MMBT5401**, registrato in questo repo da L24. Si
chiede `DMMT5401`, si riceve `MMBT5401`: un file vero, 1609 byte, nessun
errore. La verità sta nel `name=` del `Content-Type`, non nell'URL che si è
scritto. È la #20 spostata di un passo indietro — là il costruttore serviva
la parte sbagliata sotto un nome giusto, qui è il richiedente a poter
scrivere un nome che nessuno controlla.

Il modello vero del DMMT5401 sta all'id **3323**.

---

## 2. La rosa, e perché si è ridotta a una

### DMMT5401 (Diodes) — scartato sul datasheet, non per preferenza

Era il candidato che partiva avanti: **stesso die** del MMBT5401 che ADR-017
ha già scelto per il VAS, stesso costruttore di cui il repo ha già congelato
due modelli, percorso del modello già dimostrato in L24. Il modello esiste ed
è un duale vero (`.SUBCKT DMMT5401 1 2 3 4 5 6`).

**Cade su due righe del suo datasheet** (DS30437 Rev. 9-2, letta dal footer):

- l'appaiamento è su **h_FE, V_CE(sat), V_BE(sat) al 2%**, e la nota 1 lo
  chiama «intrinsically matched pair as this is built with adjacent die from
  the same wafer». **Non c'è una specifica di |V_BE1−V_BE2|**, ed è quella
  che serve a uno specchio: il rapporto di uno specchio è un rapporto di
  V_BE;
- **NF ≤ 8 dB**, contro i 3 dB dell'LS350.

Registrato per intero perché è il tipo di scelta che sarebbe passata "per
comodità": stessa famiglia, stesso fornitore, un URL che funziona.

### SSM2220 (Analog Devices) — non verificabile da qui, e dichiarato tale

È il sostituto naturale del THAT320 per funzione e per rumore. **Non è stato
possibile leggere nulla dal costruttore**: `analog.com` e la sua CDN non
rispondono a un client automatico. Tre tentativi, due strade, due protocolli:

| Tentativo | Esito |
|---|---|
| WebFetch pagina prodotto | `ETIMEDOUT` |
| `curl` HTTP/2 pagina prodotto | `curl: (92) HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR` |
| `curl --http1.1` pagina prodotto | timeout dopo 60 s, 0 byte |
| `curl` PDF datasheet sulla CDN | `curl: (92) INTERNAL_ERROR` |
| `curl --http1.1` PDF datasheet | timeout dopo 90 s, 0 byte |

Una ricerca web riportava la parte come *Obsolete*. **Non è stata usata**:
ADR-016 non accetta un risultato di ricerca come evidenza del costruttore, ed
è la stessa regola che in L24 ha impedito di dichiarare *Active* il 1N4148 su
quattro aggregatori. La voce resta **dichiarata non verificata**, non
risolta — e se ADI tornasse raggiungibile è la prima alternativa da
riesaminare.

### Come si è arrivati all'LS350

Guardando cosa il repo ha già in casa (la trappola 7 di L24): **Linear
Systems è già il costruttore dell'LSK489**, il suo host serve PDF a un `curl`
nudo, e la procedura di trascrizione da PDF esiste apposta. Il catalogo dei
duali PNP monolitici ha quattro serie; **LS350 è quella dichiarata *tight
matching***.

---

## 3. La parte, letta dal suo datasheet

`LS350SeriesDSRevA5.pdf`, **Rev#A5 10/14/2020**, letta dal footer. Il nome del
file servito dal costruttore è `LS350SeriesDSRevA5.pdf` e **stavolta concorda
col footer** — il controllo è stato fatto lo stesso, perché sull'LSK489 non
concordava (L7).

Una parte è tre gradi dello stesso die:

| | LS350 | LS351 | **LS352** |
|---|---|---|---|
| BV_CEO min | 25 V | 45 V | **60 V** |
| h_FE min @ 1 mA | 100 | 150 | **200** |
| \|V_BE1−V_BE2\| | 1 mV tip / 5 max (SOT-23) | 0,4 / 1,0 | **0,2 / 0,5** |

**Scelto LS352**: il caso peggiore rail-to-rail del progetto è 30 V, quindi i
25 V dell'LS350 non bastano; e l'appaiamento è la proprietà per cui la parte
è stata scelta.

**Il pinout è stato guardato, non estratto** — è grafica, come il relè di L8.
Render a 170 dpi delle due pagine:

- **SOIC-8**: 1=C1 2=B1 3=E1 4=N/C 5=N/C 6=E2 7=B2 8=C2
- **SOT-23-6**: 1=B1 2=E2 3=B2 4=C2 5=E1 6=C1

Il costruttore elenca anche **PDIP-8 e DFN-8** sulla pagina prodotto, ma il
datasheet **non ne disegna il pinout**. Non sono stati usati: un pinout non
pubblicato è esattamente il modo in cui il SOIC-8 fantasma del THAT320 è nato.

**Una nota sui metadati.** Il PDF del datasheet ha `Title`/`Subject`/`Keywords`
= «ID100 ID101 PICO AMPERE DIODES», residuo del template Word del costruttore
per un altro prodotto. Il contenuto è LS350 dappertutto, verificato sul
render. È la terza variante della stessa trappola: il nome di un file non è la
sua revisione (L7), non è la sua parte (#20), e i metadati di un PDF non sono
la sua parte.

---

## 4. Il modello: trascrizione e controllo incrociato

### La trascrizione regge, su tre letture

Il modello è pubblicato come **PDF**, come per l'LSK489, quindi vale la
procedura vincolante di ADR-013:

| Lettura | Strumento | sha256 del testo estratto |
|---|---|---|
| A — meccanica | `scripts/pdf_glyphs.py`, solo stdlib | `7639b915…774410` |
| B — poppler | `pdftotext -layout` | `7639b915…774410` |
| C — visiva | render a 200 dpi, letto | concorda carattere per carattere |

A e B sono **byte-identiche**. Il confronto l'ha fatto `diff`, non l'occhio.

**Una sola rimozione**: `mfg=Linear_Systems`, che ngspice valuta come
espressione e su cui muore (`Undefined parameter [linear_systems]`, exit 1).
È **rumoroso, non silenzioso**, e in questo lotto è stato **riverificato
eseguendolo** invece di ereditarlo da L6.

**Una differenza che NON è stata fatta.** Il costruttore scrive
`.model LS350 (PNP ...` — tipo dentro le parentesi — dove la forma canonica è
`.model LS350 PNP (...`. ngspice accetta e stampa `warning, model type
mismatch in line`. La forma canonica è stata eseguita **in parallelo** e dà
numeri **identici a sette cifre**: il testo vendor è tenuto verbatim e il
warning documentato come output atteso, come L6 fece per i quattro parametri
ignorati dell'LSK489.

### Il controllo incrociato, alle condizioni del datasheet, 25 °C

| Grandezza | Misurata | Finestra LS352 | Esito |
|---|---|---|---|
| h_FE @ I_C = 10 µA, V_CE = 5 V | **441,2** | 200…600 | dentro |
| h_FE @ I_C = 100 µA | **483,2** | 200…600 | dentro |
| h_FE @ I_C = 1 mA | **490,6** | 200 min | dentro |
| C_OBO @ V_CB = 5 V, 1 MHz | **1,584 pF** | ≤ 2 pF | dentro |
| NF @ 100 µA, R_G = 10 k, 1 kHz | **0,325 dB** | ≤ 3 dB | dentro |
| **f_T @ I_C = 1 mA, V_CE = 5 V** | **129,5 MHz** | **200 MHz min** | **FUORI**, −35% |

**Cinque su sei dentro.** La f_T è verificata su tre gambe concordi
(|h_fe| = 1 → 129,5 MHz; GBW a 1 MHz → 124,5; a 10 MHz → 128,8), quindi non
è un artefatto di una singola misura. È **NC-020**, maggiore: la direzione è
sicura — il modello è più lento della parte garantita, quindi le cifre di
stabilità sono pessimistiche — ma non di una quantità nota.

**I numeri sono bloccati** da una ricetta nuova in `scripts/validate_models.py`
(`tb_ls350`), sul modello di `tb_lsk489` di L7: la libreria passa da 26 a
**28 check**, tutti verdi. La ricetta ha trovato subito il suo primo difetto,
ed era **nel controllo e non nel modello**: leggendo il campione che
attraversa la soglia invece di interpolare come fa `meas`, l'h_FE a 10 µA
usciva 438,2 contro 441,2 — 0,7%, cioè il passo dello sweep. Corretto
interpolando; è annotato nel codice perché sarebbe un rosso per la ragione
sbagliata.

---

## 5. Il rumore: il numero che ha deciso la ADR

### Il dispositivo da solo

Un deck, due modelli, stesso punto di lavoro (I_C = 1 mA, V_CB = 10 V, 1 kHz,
25 °C — le condizioni di prova del datasheet THAT):

| Modello | rumore riferito all'ingresso |
|---|---|
| THAT320 `QPNP_THAT_NS` | **0,758 nV/√Hz** |
| LS350 | **1,685 nV/√Hz** — 2,22× peggio, +6,9 dB |

**Il deck non valida sé stesso**: il numero del THAT riproduce lo
**0,768 nV/√Hz** che `limitations.md` #17 aveva già registrato per lo stesso
modello alle stesse condizioni. È la taratura che rende credibile l'altro
numero.

La causa è leggibile nel modello: `RB = 200` con `IRB = 1e-05` e `BF = 500`,
quindi a 1 mA la corrente di base (≈2 µA) sta sotto `IRB` e la resistenza di
base siede vicino a **RB** e non a `RBM = 10`. Il THAT320 portava un `RB = 25`
piatto: quei 25 Ω erano ciò che ne faceva una parte a basso rumore.

**E il datasheet non promette altro.** L'LS350 specifica il rumore come
NF ≤ 3 dB a R_G = 10 kΩ, che consente un rumore equivalente d'ingresso fino a
~12,8 nV/√Hz. È una coppia appaiata **general purpose**, non una a basso
rumore. Gli 1,685 nV/√Hz sono ciò che dice il **modello**, a un'impedenza di
sorgente che il datasheet non prova: non vanno citati come garanzia della
parte.

### Lo stadio, e il valore della degenerazione

ADR-016 chiedeva di **riprogettare** lo specchio. Il riprogetto è questo, ed è
uno sweep, non un ragionamento — `tb_noise_breakdown.cir` configurazione D
(caso peggiore, R_sorgente 2500 Ω) e il V_BC **interno** della metà d'uscita:

| R_deg | rumore, caso peggiore | V_BC della metà d'uscita |
|---|---|---|
| 22 Ω | — | −53,1 mV — **satura** |
| 47 Ω (valore ereditato) | 6,988 µV | −0,4 mV — sul ginocchio |
| 100 Ω | 5,149 µV | +112,5 mV |
| 150 Ω | 4,580 µV | +219,4 mV |
| **220 Ω** | **4,231 µV** ← minimo | **+369,1 mV** ← scelto |
| 330 Ω | 4,515 µV — **risale** | +590,8 mV, ma il clipping negativo perde 0,77 V |

Il minimo esiste davvero, e a 330 Ω il degrado si vede su due assi
indipendenti: il rumore risale **e** il clipping negativo scende da −13,85 V
a −13,08 V, col guadagno a piccolo segnale che scende da 3,1460 a 3,1330 —
cioè lo specchio comincia a perdere compliance.

**Il confronto che conta**, tutte e quattro le configurazioni:

| Config | THAT320 @ 47 Ω | LS352 @ 220 Ω | |
|---|---|---|---|
| A intrinseco | 1,676 µV | **1,157 µV** | −31,0% |
| B | 1,718 µV | **1,216 µV** | −29,2% |
| C | 1,906 µV | **1,470 µV** | −22,9% |
| D caso peggiore | 5,697 µV | **4,231 µV** | **−25,7%** |

Lo stadio è più silenzioso di quando montava il THAT320, **con un dispositivo
il cui rumore proprio è 2,2× peggiore**. Ed è ancora dentro **E5** (≤ 10 µV),
con più margine di prima.

**Perché funziona**: il contributo dello specchio al rumore dello stadio è
fissato dalla sua transconduttanza, non dal solo rbb, e la degenerazione la
riduce più in fretta di quanto rbb costi. Il valore di 47 Ω era stato scelto
per il THAT320, un dispositivo con rbb basso, dove quel bilancio cadeva in un
punto diverso.

### La ragione per cui il ginocchio esiste: RC = 231 Ω

Il modello porta **`RC = 231,405`** contro i 18 Ω del THAT320. A 2,1 mA sono
**0,49 V** persi *dentro* il dispositivo, su ~1,2 V di V_CE che la topologia
gli concede. La giunzione sta molto più vicina al ginocchio di quanto dica la
tensione ai terminali — a 47 Ω, **−0,4 mV**, cioè esattamente sopra.

**Non è un artefatto**: il datasheet dichiara V_CE(sat) ≤ 0,5 V a I_C = 1 mA,
che implica una RC di quell'ordine.

E il rimedio è **controintuitivo**, per questo è stato misurato invece che
dedotto: aumentare la degenerazione **aumenta** il margine di V_BC invece di
consumarlo, perché il nodo di base dello specchio si sposta con essa mentre
il collettore è inchiodato dal VAS. La prima intuizione — «meno degenerazione,
più V_CE» — è stata provata a 22 Ω e **falsificata**: il margine peggiora.

---

## 6. L23 — package e simbolo, e la prima libreria del repo

`library/preamp.kicad_sym` è la prima libreria di simboli del progetto.
Nasce qui perché serviva qui, ed è destinata a ospitare anche l'LSK489 di
**L10**.

**Il duale è UNA parte, non due.** Era il residuo peggiore di NC-016: due
Part con un footprint SOIC-8 ciascuna, cioè **due package sul PCB per un
dispositivo solo**. Ora è una Part a tre unità (due transistor più i due
N/C), e la verifica è sulla netlist, non dichiarata:

| | prima | dopo |
|---|---|---|
| componenti totali | 44 | **43** |
| componenti su footprint SOIC-8 | 4 | **3** (LS352 + i due LSK489) |

I due LSK489 restano due Part: è il gap noto di **L10**, e ora costa molto
meno, perché l'infrastruttura che serviva esiste.

**Verificato con KiCad, non a occhio**: `kicad-cli sym upgrade` accetta il
file e `kicad-cli sym export svg` disegna **tutte e tre le unità**. E SKiDL lo
carica dalla libreria del progetto, vedendo 3 unità e tutti gli 8 pin
accessibili per numero.

**Una modifica di infrastruttura è servita**, ed è piccola:
`spice_export.spice_dev()` ha ora un parametro `suffix`. Senza, le due metà
di una parte multi-unit emetterebbero due righe SPICE **con lo stesso nome**,
e una netlist con due `Q122` non è una netlist. Con esso diventano `Q122A` e
`Q122B`.

**La rinumerazione è stata ricavata, non dedotta a mano.** Fondendo due
componenti in uno, tutti i riferimenti successivi slittano di −1. La mappa
vecchio→nuovo è stata ricostruita **confrontando i nodi** di ogni dispositivo
fra il `.inc` vecchio e quello nuovo, e applicata in **una sola passata** ai
tre deck che citano riferimenti espliciti e al disegno dello schematico.

**Il controllo dello schematico ha fatto il suo mestiere**: alla prima
esecuzione `check_schematic.py` ha rifiutato con 15 discordanze, tutte dovute
ai riferimenti slittati. È esattamente ciò per cui esiste — il disegno è fatto
a mano e diverge in silenzio. Dopo l'allineamento: 44 dispositivi su 44,
corrispondenza in entrambe le direzioni.

---

## 7. Cosa NON è stato verificato, dichiarato e non riempito

- **Lo stato di ciclo di vita esplicito dell'LS352.** Linear Systems non
  pubblica né uno stato né un elenco di parti dismesse. L'evidenza usata è:
  pagina prodotto viva, datasheet senza timbro, e **un modello SPICE
  rilasciato il 2026-07-27**, due mesi fa. È più debole di una stringa di
  stato e manca il controllo che in L24 rese significativo il silenzio di
  Diodes — nessun elenco di dismessi da questo costruttore contro cui provare
  il silenzio.
- **L'SSM2220.** Costruttore irraggiungibile: vedi §2.
- **Le scorte presso i distributori**, per nessun distributore. Come L8 e L24.
- **Il PDIP-8 e il DFN-8** dell'LS352: elencati dal costruttore, pinout non
  disegnato, quindi non usati.
- **Le altre cifre del blocco.** Margine di fase, guadagno d'anello e
  clipping sono stati misurati **quanto basta a provare che la sostituzione
  non li muove** (mezzo grado, 0,06 dB, 15 mV). Non sono state rimisurate
  PSRR, Z_out e risposta in frequenza: restano da rifare in Fase 4 coi modelli
  veri ovunque, e i dati versionati in `data/2026-09-09/` descrivono la
  topologia **col THAT320**.
- **Se la parte reale rispetti la finestra di appaiamento.** Il modello
  descrive il die, non il grado: solo la misura su un esemplare può dirlo.

---

## 8. Le proprietà verificate, non dichiarate

- **Nessun file preesistente di `vendor/` è stato toccato**: `git diff
  --name-status` sotto `vendor/` mostra solo righe `A`.
- **Tutti gli sha256 di `vendor/` verificano**, i 19 di prima e i 2 nuovi.
- **Il documento è stabile alla sorgente**: entrambi i PDF sono stati
  scaricati **due volte** e i due download sono byte-identici.
- **La suite passa**: `run_tests.sh` 5/5, `validate_models.py` **28/28** con
  0 SKIP.
- **Gli artefatti sono rigenerati davvero**, non modificati a mano:
  `gain_block.py` e `preamp_audio.py` rieseguiti sul venv SKiDL.

---

## 9. Cosa resta

- **NC-020** (f_T del modello): si chiude con una misura su un esemplare o
  con la constatazione, in Fase 4, che nessuna cifra di stabilità dipende
  dalla f_T di questo dispositivo entro il margine d'errore.
- **NC-004** resta aperta e questo lotto non la muove: l'LS350 **non ha
  KF/AF**, quindi le cifre di rumore qui sopra sono un pavimento senza
  flicker — e cadono proprio dove l'analisi dice che il rumore domina.
- **L10** (simbolo LSK489) è ora molto più economico: la libreria esiste, il
  meccanismo multi-unit è collaudato e il `suffix` di `spice_dev` è già lì.
- **L25**: promuovere in `models/` i cinque modelli congelati da L24.
