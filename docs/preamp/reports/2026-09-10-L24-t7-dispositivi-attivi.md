# L24 — T7 su tutti i dispositivi attivi

Data: 2026-09-10 · Lotto: **L24** · Chiude: **NC-017** (parzialmente),
sblocca la metà di **NC-004** che riguarda VAS, cascode e stadio d'uscita
· Decisione prodotta: **ADR-017**

---

## Il risultato in cinque righe

1. **MJE15032, MJE15033 e 1N4148 hanno un modello del costruttore**, e
   ngspice lo carica ed esegue. **Lo stadio d'uscita regge**: non c'è la
   modifica di topologia che ADR-016 temeva.
2. Per **2N5401/2N5551** la conclusione di L8 («nessun modello vendor
   raggiungibile») era **giusta sui percorsi provati e sbagliata come
   affermazione generale**: Diodes Incorporated li pubblica, sotto i nomi
   MMBT5401/MMBT5551.
3. La rosa dei sostituti «veri» è stata cercata prima e **T8 l'ha quasi
   azzerata** — compresa la coppia audio classica KSA992/KSC1845, in
   *last-time buy*.
4. **Nove file congelati** in `vendor/`, tutti scaricati dal costruttore.
   Nessun file preesistente toccato; **tutti e 19 gli sha256 del repo
   verificano**.
5. Due nuovi fallimenti silenziosi in `docs/limitations.md`: **#19** (il
   prefisso micro non sopravvive all'estrazione dai PDF onsemi — errore
   ×1000, exit 0) e **#20** (onsemi serve `1n4148.lib` contenente il
   modello di **un'altra parte**).

---

## 1. Il mandato, e perché l'ordine contava

ADR-016 aveva lasciato tre parti «da verificare» e due «da sostituire», e
STATE.md aveva messo L24 prima di L22 per una ragione precisa: se i due
MJE fossero caduti, la sostituzione dello stadio d'uscita sarebbe stata
una **modifica di topologia**, e conviene saperlo prima di riprogettare lo
specchio d'ingresso.

Quel passo è stato fatto per primo, e la risposta è **no, non cadono**.
Tutto il resto del lotto si è potuto fare a dimensione nota.

## 2. Il metodo, e la trappola che l'ha determinato

Ogni parte è passata per la stessa procedura, e ogni passo di quella
procedura è costato una scoperta a un lotto precedente:

1. scaricare **dal costruttore**, mai da un mirror né da un distributore;
2. registrare stato HTTP, `Content-Type` **e byte** — perché su
   `www.onsemi.com` un 200 non prova nulla (`limitations.md` #18);
3. leggere la revisione dal **footer del documento**, mai dal nome del
   file (lezione di L7);
4. leggere i limiti dalle **Electrical Characteristics con le loro
   condizioni**, mai dagli Absolute Maximum Ratings (lezione di L8);
5. contare **quanti** modelli il costruttore pubblica per la stessa parte
   (`limitations.md` #17);
6. provare che **ngspice lo carica ed esegue**, a 25 °C e non ai 27 °C di
   default (lezione di L6);
7. congelare con sha256, URL e `PROVENANCE.json`.

**Il passo 2 è quello che ha aperto il lotto.** L8 non era riuscito a
trovare i modelli onsemi perché la pagina `models?rpn=` è solo-JavaScript
e ogni percorso indovinato risponde 200 con la stessa pagina HTML da
303 722 byte. L24 ha trovato il pattern vero partendo da un esempio
funzionante esposto da una ricerca (`2n7002`), poi lo ha **provato**:

```
https://www.onsemi.com/download/models/lib/<parte minuscola>.lib
```

Il conteggio di byte è l'unico test onesto su quell'host. Un modello vero
torna `application/octet-stream`; un soft 404 torna `text/html` da
303 722 byte esatti.

| Parte | esito del probe |
|---|---|
| `mje15032.lib` | **978 B, octet-stream** |
| `mje15033.lib` | **976 B, octet-stream** |
| `1n914.lib` | **520 B, octet-stream** |
| `1n4148.lib` | 1189 B, octet-stream — **ma è un'altra parte**, vedi §5 |
| `2n5401.lib` | soft 404 |
| `2n5551.lib` | soft 404 |

La riga che conta per la credibilità del lotto è l'ultima coppia:
**la conclusione di L8 su onsemi regge anche contro un pattern che L8 non
aveva provato.** Non è stata ereditata, è stata rifalsificata.

## 3. MJE15032 / MJE15033 — lo stadio d'uscita

Un solo datasheet per la coppia: titolo «MJE15032 (NPN), MJE15033 (PNP)»,
**dicembre 2024 – Rev. 7**, publication order number MJE15032/D, letto dal
footer.

### T8 — ciclo di vita

Letto dal **JSON-LD della pagina prodotto onsemi**, verbatim, non da un
riassunto e non da un distributore:

| OPN | itemCondition | availability | prezzo |
|---|---|---|---|
| MJE15032 | **Obsolete** | unavailable | 0.0 |
| MJE15032G | **Active** | available | 0.6 |

**Il codice nomina l'OPN sbagliato.** `gain_block.py:367-368` scrive
`"MJE15032"` e `"MJE15033"`, che sono precisamente le versioni piombate
che onsemi marca Obsolete; le ordinabili portano il suffisso **G**. È una
stringa, non una topologia — ma sotto T8 è una non conformità reale, ed è
aperta come **NC-018**.

**MJE15033 non ha una pagina prodotto su onsemi, e la lacuna è
dichiarata.** Lo slug redirige alla categoria; l'API di ricerca risponde
502; la ricerca del sito restituisce la homepage. E l'assenza è specifica,
non generica: la categoria *audio-transistors* elenca 49 parti fra cui
`mje15028`, `mje15029`, `mje15030`, `mje15031`, `mje15032`, `mje15034` e
`mje15035` — **ma non `mje15033`**, e i PNP fratelli (15031, 15035) ci
sono, quindi non è che onsemi ometta i PNP.

L'evidenza che è comunque ordinabile è doppia e viene dal costruttore:
la tabella ORDERING INFORMATION del datasheet di dicembre 2024 elenca
**MJE15033G, TO-220 (Pb-Free), 50 Units/Rail**, e il documento contiene
**zero** occorrenze di «DISCONTINUED». Quell'assenza è significativa
perché la convenzione onsemi per marcare un OPN morto è nota **da un
documento già congelato in questo repo**: `vendor/bjt_npn/onsemi/2N5551/2n5551t-d.pdf`
porta un banner in prima pagina e un blocco «DISCONTINUED (Note 6)» nella
tabella d'ordine. In più, la query di confronto parametrico della pagina
MJE15032 nomina `MJE15033G` accanto agli altri OPN attivi.

È evidenza **più debole** della stringa `Active` che porta il 15032G, ed è
registrata come tale invece di essere pareggiata.

### T7 — il modello, e il controllo incrociato

Entrambi i file dichiarano nella propria intestazione: *«Model Generated
by MODPEX / Copyright(c) Symmetry Design Systems / Modeling services
provided by Interface Technologies»*, generati il **1° febbraio 2004**,
formato PSpice. Sono quindi opera di un contrattista di modellazione,
**distribuiti dal costruttore** — che è ciò che ADR-016 congela. Registrare
l'autore non indebolisce la provenienza: fa parte di cosa la provenienza
*è*.

Misurato con ngspice 47, `set temp = 25`, alle condizioni del datasheet:

| | MJE15032 (NPN) | MJE15033 (PNP) | datasheet |
|---|---|---|---|
| hFE @ I_C = 0,5 A, V_CE = 5 V | **66,4** | **88,2** | min **70** |
| hFE @ I_C = 1,0 A | **61,3** | **66,9** | min 50 |
| hFE @ I_C = 2,0 A | non raggiunto | **42,8** | min 10 |
| f_T @ I_C = 500 mA, V_CE = 10 V | **31,04 MHz** | **31,38 MHz** | min 30 MHz |

**Verdetto misto sul NPN**: 66,4 contro un minimo di 70 è **fuori del
5,1%**. Non è un errore di trascrizione — qui non si è trascritto niente,
il file è byte-per-byte come servito. È il modello del costruttore che non
rispetta il minimo del datasheet dello stesso costruttore, la stessa forma
di NC-013 sull'LSK489. La direzione dell'errore è **pessimistica** sul
guadagno, cioè la più sicura, ma il modello non descrive una parte
conforme.

L'hFE a 2,0 A **non è stato misurato** e non è stato riempito: il modello
si ferma a 1,193 A entro la corrente di base spazzata.

### Il numero che il datasheet non dà

Il datasheet specifica hFE a 0,5/1,0/2,0 A e f_T a 500 mA. **Il progetto
fa lavorare questi dispositivi a 14,71 mA** (`gain_block.py:434`), cioè
34 volte sotto il punto specificato più basso. Lì il datasheet non dice
nulla, e il modello dice:

| | MJE15032 | MJE15033 |
|---|---|---|
| hFE @ 15 mA | **75,7** | **129,3** |
| f_T @ 15 mA | **11,24 MHz** | **12,58 MHz** |

Due cose ne escono. La prima: la f_T al punto di lavoro è **2,8× più
bassa** che al punto di prova, e il segnaposto usava proprio la cifra del
punto di prova — la sua intestazione già ammetteva «OPTIMISTIC for the
actual operating point», e ora c'è il fattore. La seconda: **hFE 75,7
contro 129,3 è uno squilibrio di 1,7× dentro un inseguitore
complementare**, che i segnaposto non potevano mostrare perché erano
simmetrici per costruzione (`BF = 100` entrambi). È materiale per la
Fase 4.

## 4. 2N5401 / 2N5551 — non si sostituisce il dispositivo, si cambia costruttore e package

### Prima si è cercato un sostituto vero, e T8 ha quasi azzerato la rosa

Sedici candidati provati per modello, poi i superstiti letti per ciclo di
vita **dal costruttore**:

| Candidato | modello onsemi | ciclo di vita |
|---|---|---|
| **KSA992** (PNP audio basso rumore) | 977 B | **Last Shipments** su 2 OPN, `Active/unavailable` sugli altri 2 |
| KSC1845 (il suo complementare NPN) | 1082 B | pagina prodotto assente |
| **2N3904 / 2N3906** | 977 / 967 B | **9 e 7 OPN, tutti Obsolete** |
| MPSA06 / MPSA56 / MPSA92 | sì | **tutti Obsolete** |
| KSA733 | 1216 B | **tutti Obsolete** |
| **BC550** | 1288 B | **BC550CBU Active** — unico superstite |
| BC546/547/548/556/557/558/560, BC327/337, BC807, MPSA42, MPSA18, 2N5087/5088/5089, 2N4401/4403, MPS8099/8599, KSP42, KSC945, KSC2690A, KSA1220A, PZT2907A, 2N2907A, 2N2222A | **nessun modello** | — |

Due righe meritano di essere lette due volte.

**KSA992/KSC1845 è la coppia audio classica**, quella che sarebbe entrata
«per reputazione». È in **last-time buy**, che T8 squalifica
esplicitamente. È il THAT320 evitato in anticipo, e solo perché adesso il
controllo di ciclo di vita è obbligatorio invece che implicito.

**2N3904 e 2N3906 sono i due transistor più diffusi al mondo** e presso
onsemi sono interamente fuori catalogo. I cataloghi dei distributori ne
sono pieni — ma di *altri* costruttori, e T7 chiederebbe allora il modello
di *quel* costruttore. È la ragione operativa per cui «lo stato di ciclo
di vita si legge dal costruttore» non è una formalità.

L'unico superstite, **BC550C**, è NPN e non ha complementare conforme
(onsemi non serve `bc560.lib`). E il suo file dichiara «MODEL PARAMETERS
FROM MEASURED DATA: **BC549**» — adattato alla parte sorella, V_CEO 30 V
contro 45 V, con `BF = 228` che non corrisponde alla gradazione C
dell'unico OPN attivo. Non è una base su cui costruire uno stadio.

### Poi si è trovato che le parti originali hanno un modello vendor

L8 aveva registrato «Diodes Incorporated risponde 403 alle richieste
automatiche». **È vero delle pagine HTML sotto `/design/` e `/part/`. Non
è vero dei file di modello**, che stanno su un percorso diverso e
rispondono `200 text/plain` a un `curl` nudo:

```
https://www.diodes.com/spice/download/2587/MMBT5401.spice.txt
https://www.diodes.com/spice/download/2541/MMBT5551.spice.txt
```

MMBT5401 e MMBT5551 sono **lo stesso die** di 2N5401 e 2N5551, in SOT-23
invece di TO-92. Nessuna versione TO-92 è stata trovata presso Diodes: quel
die esiste da loro solo a montaggio superficiale (MMBT, MMST, DXT, DZT, e
il duale MMDT).

### Il controllo incrociato, alle condizioni dei loro datasheet

MMBT5401: DS30057 Rev. 12-2, © 2024. MMBT5551: DS30061 Rev. 15-2, © 2025.
Revisioni lette dal footer. ngspice 47, `set temp = 25`:

| Grandezza | MMBT5401 (PNP) | finestra | MMBT5551 (NPN) | finestra |
|---|---|---|---|---|
| hFE @ I_C = 10 mA, |V_CE| = 5 V | **124,9** | 60…240 | **107,2** | 80…250 |
| f_T @ I_C = 10 mA, |V_CE| = 10 V | **169,5 MHz** | 100 min / 300 tip | **173,1 MHz** | 100 min / 300 tip |
| C_obo @ |V_CB| = 10 V, 1 MHz | **3,706 pF** | ≤ 6 pF | **2,221 pF** | ≤ 6 pF |

**Sei su sei dentro.** È l'unico modello del repo, finora, che non produca
un verdetto misto — l'LSK489 ha NC-013, il MJE15032 sta sotto il proprio
minimo.

Un rischio era esplicito e va registrato perché **non** si è avverato: i
due modelli portano `QUASIMOD`, `RCO`, `VO`, `GAMMA`, parametri di
quasi-saturazione PSpice. ngspice li ha accettati con **zero warning**, e
il confronto che rende quel silenzio significativo è che su
`models/jfet/lsk489.lib` ngspice ne emette **quattro** di
«unrecognized parameter … ignored». Quando non conosce un parametro, lo
dice.

### Il numero che decide il polo dominante

Solo la corrente è stata cambiata rispetto alla condizione di datasheet
(V_CE tenuta a 10 V), così la differenza isola la dipendenza dalla
corrente:

| Dispositivo | ruolo, riga | corrente | f_T |
|---|---|---|---|
| MMBT5401 | VAS, 316 | 6 mA | **137,0 MHz** |
| MMBT5551 | carico VAS, 328 | 6 mA | **151,9 MHz** |
| MMBT5551 | coda 262, cascode 291-292 | 2 mA | **88,8 MHz** |

**A 2 mA il modello sta sotto i 100 MHz di minimo del datasheet**, il che
non è una contraddizione perché quel minimo è specificato a 10 mA. È la
forma concreta dell'avvertimento già scritto in NC-017.

Contro i segnaposto che sostituiscono:

| Segnaposto | f_T implicita | reale al punto di lavoro | errore |
|---|---|---|---|
| `NSS2N5551` | ~318 MHz | 88,8 MHz | **3,6× veloce** |
| `PSS2N5401` | ~265 MHz | 137,0 MHz | **1,9× veloce** |
| `NMJE15032` | ~30 MHz | 11,2 MHz | **2,8× veloce** |
| `PMJE15033` | ~25 MHz | 12,6 MHz | **2,0× veloce** |

E la C_ob di `PSS2N5401` è 6 pF contro **3,71 pF** reali: **1,6× alta**,
cioè un errore che sul polo di Miller spinge nella direzione **opposta** a
quello sulla f_T. Non si compensano in modo noto. È ciò che ADR-016
chiamava «non conservativo in modo noto», ora misurato.

### La dissipazione, contro il punto di lavoro vero del progetto

Non stimata: `gain_block.py:434` registra da `tb_op.cir` **VAS 6,443 mA,
V_CE 13,4 V** → **86,3 mW**. Il SOT-23 dà **310 mW** sul layout di pad
minimo raccomandato. Margine **3,6×**. L'istanza peggiore fra le altre è
il carico del VAS, dello stesso ordine; i cascode stanno intorno ai 10 mW.
Nessuna si avvicina al limite — ma il TO-92 sostituito dava 625 mW, quindi
il margine si dimezza e diventa un vincolo di layout che prima non
esisteva.

### Il costo che non è elettrico

`gain_block.py:350` porta una regola già consegnata a
`pcb-automation-engineer`: il moltiplicatore di Vbe «MUST be thermally
coupled to the NPN output device's tab (thermal compound + cable tie is
enough at 225 mW)». **Un SOT-23 non si fascetta a un tab TO-220.**
L'accoppiamento deve diventare un percorso di rame sul PCB. Aperta come
**NC-019**.

## 5. Le due trappole nuove

### #19 — il prefisso micro non sopravvive all'estrazione dai PDF onsemi

Trovato leggendo il datasheet del 1N4148. `pdftotext` rende il glifo µ
come la lettera **m**: una corrente letta meccanicamente è sbagliata di
**mille volte**, con exit code 0 e nessun avviso.

Provato con le due letture indipendenti che ADR-013 impone, non dedotto.
Il render della pagina mostra «Pulse Width = 1.0 **μ**s»; `pdftotext
-layout` restituisce «Pulse Width = 1.0 **m**s» per la stessa riga.

Contando il glifo su quattro documenti:

| Documento | occorrenze di «µ» estratte |
|---|---|
| `1n914-d.pdf` (onsemi) | **0** |
| `mje15032-d.pdf` (onsemi) | **0** |
| `2n5551t-d.pdf` (onsemi, **già congelato in L8**) | **0** |
| LSK489 (Linear Systems, già congelato) | **11** |
| `MMBT5401.pdf` / `MMBT5551.pdf` (Diodes) | 4 / 8 |

È quindi una proprietà della toolchain documentale **di onsemi**, non di
poppler. E il prefisso *nano* sopravvive — il che è ciò che lo rende
pericoloso: chi controlla a campione una riga che usa `n` conclude che
l'estrazione è a posto.

**Il difetto tocca un documento già congelato, quindi le cifre di L8 sono
state ricontrollate a vista.** Nel 2N5551 le righe interessate sono tre:

| Riga | Il PDF, letto a vista | `pdftotext -layout` |
|---|---|---|
| V(BR)CBO | I_C = **100 μA** | `IC = 100 mA` |
| V(BR)EBO | I_E = **10 μA** | `IE = 10 mA` |
| I_CBO @ 100 °C | 50 **μA** | `50 mA` |

**Nessuna di queste tre è fra le cifre che L8 ha registrato**, e la riga
che L8 *ha* registrato — V(BR)CEO a **I_C = 1,0 mA** — è **corretta**,
verificata sul render. Il `PROVENANCE.json` congelato non va quindi
riscritto e non è stato toccato. Ma il rischio era reale ed è ora un
controllo obbligatorio.

### #20 — il nome di un file non è la sua parte

`https://www.onsemi.com/download/models/lib/1n4148.lib` restituisce un
file **vero** — 1189 byte, `application/octet-stream` — e dentro c'è
`.SUBCKT **1N4148WT**`, la variante SOD-323, «Model Generated by ON MPD»,
2024, «Rev0: Initial release of PSPICE model for 1N4148WT». **Non è il
DO-35 che questo progetto usa.** Lo stesso file è servito byte-identico
anche come `1n4148wt.lib`, il che conferma l'alias.

Il modello giusto sta in `1n914.lib`, che lo dichiara nella propria
intestazione: «Product: 1N/FDLL914/A/B / 916/A/B / **4148** / 4448 ·
Package: **DO-35** / LL-34».

E la conferma che chiude la questione **era sul sito del costruttore**: la
pagina prodotto 1N4148 di onsemi linka **un solo** datasheet, ed è
`1n914-d.pdf`. È onsemi stessa a schedare il 1N4148 sotto il documento
1N914.

È la lezione di L7 spostata di un livello: là il nome di un file non era
la sua **revisione**, qui non è la sua **parte**. Entrambe falliscono in
silenzio — ngspice carica `1n4148.lib` senza una parola e simula un altro
dispositivo.

## 6. Il 1N4148 non si sostituisce: si attribuisce

È un **codice generico di industria**, non la parte di un costruttore.
T7 si soddisfa scegliendo il costruttore di cui il progetto userà modello
e dichiarazione di ciclo di vita.

Scelto **onsemi**, perché pubblica entrambe le cose. Vishay serve un
datasheet recente (Rev. 1.6, 07-Nov-2024) ma la sua pagina prodotto non
offre alcun modello SPICE a un client non-browser, solo modelli ECAD di
terze parti via UltraLibrarian.

T8, dal JSON-LD di onsemi: **sei OPN, tutti Active** — 1N4148 ($0,0073),
1N4148TA, 1N4148TR, 1N4148-T26A, 1N4148-T50A tutti *available*,
1N4148-T50R *unavailable*. Una ricerca web dava «Active» da Octopart,
DigiKey, Sourcengine e TrustedParts: **non è stata usata**, perché T8 dice
costruttore e quella regola esiste per il THAT320.

Datasheet: «1N91x, 1N4x48, FDLL914, FDLL4x48», **settembre 2024 – Rev. 6**,
1N914/D. La tabella d'ordine dà **1N4148, marking 4148, DO-204AH (DO-35),
Bulk** — che è esattamente `FP_DO35` in `gain_block.py`.

Controllo incrociato:

| Grandezza | misurata | datasheet | esito |
|---|---|---|---|
| V_F @ I_F = 10 mA | **0,76619 V** | max 1,0 V | dentro, 23% di margine |
| C_T @ V_R = 0, 1 MHz | **0,8687 pF** | max 4,0 pF | dentro |
| V_F @ I_F = 1 mA (punto di lavoro) | **0,63195 V** | — | nessuna finestra |

**Conforme su entrambi i limiti pubblicati.** Vale però notare che la C_T
del modello sta **4,6× sotto** il tetto garantito: descrive un esemplare
tipico o migliore, non il caso peggiore che il datasheet ammette. Per un
diodo di polarizzazione a 1 mA non conta; conterebbe in un percorso di
segnale.

## 7. Cosa NON è stato verificato, dichiarato e non riempito

- **Le quantità di stock, per nessuna parte e nessun distributore.** Stesso
  esito di L8 e per la stessa ragione. onsemi dà un prezzo e uno stato di
  disponibilità sulla propria pagina, ed è il dato di costruttore che T8
  chiede — non è una cifra di stock.
- **Lo stato di ciclo di vita di MJE15033G da una pagina prodotto**: non
  esiste. Vedi §3.
- **Lo stato di MMBT5401/MMBT5551 da una stringa esplicita**: Diodes
  risponde 403 a un client automatico sulle pagine prodotto. L'evidenza è
  l'assenza del timbro di dismissione su datasheet del 2024 e 2025, e
  quell'assenza è significativa perché il controllo è stato fatto: la
  scheda di una parte davvero dismessa dello stesso costruttore
  (`1N5401.pdf`) contiene «PART OBSOLETE» e due volte «OBSOLETE – PART
  DISCONTINUED».
- **L'hFE del MJE15032 a 2,0 A**: fuori dal range spazzato.
- **L'appaiamento di beta fra i due cascode di ADR-014**: la dispersione
  80…250 è larga e se il progetto la tolleri è una domanda di Fase 4, della
  stessa famiglia di NC-013.
- **Se un modello TO-92 di 2N5401/2N5551 esista dietro una sessione
  browser o un account** presso qualche costruttore.

## 8. Le proprietà verificate, non dichiarate

| Proprietà | Come | Esito |
|---|---|---|
| Il diff non nomina la topologia | `git diff --name-only $(git merge-base HEAD origin/main) HEAD \| grep -E '^(circuits/\|spice/preamp/\|docs/preamp/data/)'` | **vuoto** |
| Nessun file preesistente di `vendor/` modificato | `git diff --name-status`, tutte le righe sotto `vendor/` sono `A` | **9 aggiunte, 0 modifiche** |
| Tutti gli sha256 di `vendor/` verificano | 16 sidecar in formato `shasum -c`, 3 in formato hash nudo verificati per confronto diretto | **19/19** |
| Ogni modello congelato è caricato **ed eseguito** da ngspice | 5 deck, exit 0, `TEMP = 25.000000` | **5/5** |
| La libreria dei modelli è intatta | `validate_models.py` e `--check-provenance` | conteggio invariato |
| La suite | `run_tests.sh` | passa |

**Una nota sui sidecar.** `vendor/` contiene **due formati** di `.sha256`:
16 file in formato `<hash>  <nome>` che `shasum -c` legge, e 3 in formato
hash nudo (i due dell'LSK489 e quello della fixture demo) che `shasum -c`
**rifiuta di leggere e segnala come falliti**. Non è corruzione: i tre
verificano per confronto diretto. È annotato qui perché una verifica
ingenua dell'intero albero produce tre falsi allarmi.

## 9. Cosa resta

**NC-017 non si chiude.** La strada esiste ora per tutti e sette i
dispositivi, ma T7 non è soddisfatto *nel repo* finché `models/` non porta
i modelli e la topologia non li usa. Resta:

1. **promuovere** i cinque modelli in `models/` con le loro
   `.provenance.json` e una ricetta di regressione ciascuno in
   `validate_models.py`, sul modello di `tb_lsk489()`;
2. **sostituire** in `circuits/preamp/` — Fase 4;
3. **L22** per il THAT320, che è l'unico dispositivo ancora senza una
   risposta.

**NC-004 non si chiude nemmeno coi modelli veri**, e adesso si sa perché
con precisione: **nessuno dei cinque modelli congelati ha `KF`/`AF`**. Né i
due Diodes, né i due MJE, né il 1N4148. Nel repo **solo l'LSK489 ha rumore
1/f**. Le cifre di rumore che usciranno dalla Fase 4 restano un pavimento
senza flicker, e va scritto accanto a ogni numero invece che sottinteso.
