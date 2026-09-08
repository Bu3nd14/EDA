# Fase 1 — Verifica delle parti che vincolano la topologia

Data: 2026-09-08 · Owner: `bom-component-manager` · Tipo: report (datato)

Scopo: sapere **prima** di disegnare il circuito se lo stadio d'ingresso
previsto è realizzabile. Nessun file scritto in `models/` o `vendor/` —
in questa fase il deliverable era conoscenza.

## Esito in una riga

**La topologia regge: le parti esistono e sono disponibili.** Il punto
debole non è l'approvvigionamento — è la **provenienza dei modelli
SPICE**, cioè l'opposto di quanto temuto.

## 1. JFET d'ingresso — disponibili

Verificato via fetch diretto delle pagine prodotto DigiKey (non snippet
di ricerca), 8 settembre 2026. DigiKey spedisce in Italia, MOQ 1 pezzo.

| Parte | Grado | Stock | qty1 | qty10 |
|---|---|---|---|---|
| LSK170A TO-92 | A | 1.421 | $12,13 | $8,41 |
| LSK170B TO-92 | B | 1.040 | $7,62 | $5,15 |
| LSJ74A TO-92 | A | 1.523 | $11,12 | $7,67 |

**ADR-005 è confermata nella sostanza** — non servono coppie appaiate di
precisione e i pezzi si trovano. Ma con una precisazione: comprare N
pezzi in un solo ordine DigiKey **normalmente** arriva dallo stesso
lotto, e questo **non è garantito contrattualmente**. Se il lotto conta,
va richiesto il date-code in fase d'ordine. Azione manuale, non
automatizzabile.

## 2. Il vero problema: i modelli SPICE

| Dispositivo | Modello vendor | Formato | Raggiungibile |
|---|---|---|---|
| LSK170 | Sì, Linear Systems | **PDF** con testo `.MODEL` | Sì (HTTP 200) |
| LSK489 | Sì, Linear Systems | **PDF** con testo `.MODEL` | Sì (HTTP 200) |
| **LSJ74** | Elencato, link non risolto | — | **No — da riverificare** |
| JFE2140 (TI) | Sì | **.zip nativi** PSpice + TINA-TI | Sì (entrambi 200) |
| 2SK209 | Non trovato | — | Presumibilmente assente |
| KSC1845 / KSA992 | Sì (onsemi) | — | Esiste, **qualità dubbia** |
| MJE15032/33 | Pagina "models" esiste | — | File finale non confermato |
| SSM2212 / SSM2220 | Menzionato | — | URL diretto non risolto |
| **THAT300 / THAT320** | Sì, THAT Corp | **.lib nativo** in zip | **Sì, scaricato e ispezionato** |

Tre osservazioni che contano:

**Il modello Linear Systems è un PDF**, non un file `.lib`. Portarlo in
`models/` secondo la convenzione del repo richiede di congelare il PDF in
`vendor/` con sha256 e URL, poi **trascrivere a mano** i parametri in un
`.lib`, con `.provenance.json` che dichiari esplicitamente la
trascrizione manuale. La trascrizione da PDF è un punto in cui si
introducono errori facilmente: va incrociata con IDSS e VP del datasheet
come controllo di sanità.

**Il modello LSJ74 non è confermato.** È l'unico buco reale sulla parte
raccomandata.

**Il modello onsemi per KSC1845/KSA992 è segnalato come inaccurato** da
più discussioni su diyAudio. Non scartato, ma da validare con una
simulazione di controllo (curva Ic-Vce nota) prima di fidarsene per la
distorsione — che è precisamente lo scopo per cui ci serve.

## 3. Alternative con provenienza più pulita

**TI JFE2140** — N-ch duale monolitico, SOIC-8/WSON, ~$4,78, in stock.
Modelli SPICE nativi TI scaricabili e verificati. **Impatto topologico
nullo**: resta una coppia differenziale N-ch, cambiano solo i valori di
polarizzazione da ricalcolare. Se la pulizia della provenienza conta più
della genealogia Toshiba 2SK170, è il candidato più semplice da
certificare.

**LSK489** — N-ch duale monolitico, $9,73, 921 pz. Appaiamento e
tracking termico **intrinseci** (stesso die), superiore a "stesso lotto".
Elimina del tutto il problema del date-code. Stesso problema del modello
PDF.

**2SK209** — solo SMD, nessun modello SPICE Toshiba trovato, e **nessun
complementare P-ch oggi in produzione** (2SJ103 introvabile). Se scelto,
il generatore di corrente andrebbe fatto con BJT o MOSFET: conseguenza
topologica reale.

## 4. Coppia complementare d'uscita

**KSC1845 / KSA992** — lifecycle in movimento: KSA992 risulta obsoleto o
"last shipments" su DigiKey ma **27.585 pz disponibili su Mouser** più
56.000 in arrivo. Il dispositivo non è morto, ma la variante di package
va scelta distributore per distributore e riverificata all'ordine.

**MJE15032 / MJE15033 (onsemi)** — raccomandazione primaria.
Confermati **Active** su DigiKey: 8.952 e 3.330 pz, $3,11 e $3,17.
TO-220, 250 V / 8 A.

Enormemente sovradimensionati per 15 mA — e l'agente lo inquadra
correttamente come **vantaggio**, non come spreco: a 15 mA e ~15 V la
dissipazione è ~225 mW contro una capacità dell'ordine delle decine di
watt, quindi il punto di lavoro resta lontanissimo dal ginocchio termico
e la deriva di polarizzazione è trascurabile. Proprietà desiderabile in
Classe A. Impatto topologico nullo; cambia il package (TO-220), che pesa
sul layout ma non richiede dissipatore a 225 mW.

**BC550C / BC560C** — scartati: BC550C risulta obsoleto su DigiKey. Non
raccomandabili per un progetto che deve restare riproducibile.

## 5. Generatori di corrente e specchi

In ordine di preferenza:

1. **JFET a due terminali** dalla stessa famiglia già verificata —
   nessun componente nuovo da qualificare, ma tolleranza IDSS ampia
   (serve resistore di source).
2. **THAT300 / THAT320** (array di 4 transistor appaiati monolitici) —
   **la provenienza SPICE più pulita di tutto il giro**: `.lib` nativo,
   scaricato e ispezionato (`300 Series_Macro_01.lib`, 5.366 byte). Stock
   esatto non verificato.
3. **SSM2212 / SSM2220** (ADI) — appaiamento di precisione, ma modello
   SPICE con URL non risolto e stock non fissato.

Sconsigliato un **LM334**: non è un operazionale, ma resta un circuito
integrato, e ADR-003 dice "tutto a discreti".

## 6. Singxer SA-1 V2 — risposta definitiva

**L'impedenza d'ingresso non è pubblicata.** L'agente ha scaricato e
letto il **manuale utente ufficiale**: specifica in dettaglio le
impedenze di *uscita* (1,4/0,7 Ω cuffia bassa-Z; 11,4/10,7 Ω alta-Z;
45/22,5 Ω uscita PRE) e i guadagni (0/+11 dB), ma **in nessun punto
riporta un'impedenza d'ingresso**, né RCA né XLR. Controllate anche le
schede Audiophonics e headphones.com: stesso esito.

Non è "non trovata": è **non pubblicata**. Le uniche vie sono chiedere a
Singxer o misurarla.

## Decisioni che questo report chiede

1. **Quale JFET d'ingresso**: LSK170/LSJ74 (genealogia, modello da
   trascrivere da PDF, LSJ74 non confermato), LSK489 (appaiamento
   monolitico, stesso problema PDF) o JFE2140 (provenienza SPICE pulita).
   → serve una ADR.
2. **Il condensatore sull'uscita Singxer**: senza il dato d'impedenza,
   dimensionarlo a 4,7 µF come quello principale elimina il rischio al
   costo dell'ingombro. → aggiorna ADR-007.

## Nota di metodo

L'agente ha verificato con `curl` lo stato HTTP reale dei link ai modelli
prima di darli per buoni, e ha dichiarato esplicitamente ogni punto non
verificato fino in fondo invece di riempirlo. I file scaricati per
ispezione stanno in `/tmp`, fuori dal repository.
