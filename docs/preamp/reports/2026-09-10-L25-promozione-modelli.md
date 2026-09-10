# L25 — I cinque modelli congelati entrano in `models/`

Data: **2026-09-10** · Lotto: **L25** · Chiude il primo dei tre passi di
**NC-017** (bloccante) · Apre **NC-024** e **NC-025** (maggiori)

---

## Il risultato in sei righe

1. **I cinque modelli sono in `models/`**, ognuno con la propria
   `.provenance.json`. La libreria passa da **28 a 38 check**, tutti verdi,
   `run_tests.sh` 5/5.
2. **Il testo `.MODEL` promosso è byte per byte quello del costruttore.**
   Nessuno dei cinque portava `mfg=`, quindi non c'è stata nemmeno l'unica
   rimozione che LSK489 e LS350 avevano richiesto. Provato con `diff`, non
   dichiarato.
3. **I lucchetti sono stati provati a fallire**, sei casi su sei: modello
   intatto → PASS, una cifra spostata dell'1÷3% → FAIL, col messaggio giusto.
4. **Due cifre di L24 non riproducono, e la causa è il metodo di misura.** La
   f_T del MMBT5401 era stata misurata a I_C = 12,68 mA invece dei 10 mA del
   datasheet; le f_T dei due MJE erano state lette come attraversamento a
   guadagno unitario invece che come il datasheet le definisce.
5. **La seconda correzione cambia un verdetto, non un decimale.** Letta come
   il costruttore la definisce, **nessuno dei due MJE raggiunge il proprio
   minimo di f_T**. È **NC-025**.
6. **Tutti e sette i dispositivi attivi hanno ora un modello del costruttore
   in `models/`.** T7 è soddisfatto sul piano dei modelli; NC-017 resta
   bloccante per la sola sostituzione in `circuits/preamp/`, che è Fase 4.

---

## 1. Il mandato

Di **NC-017** L24 aveva lasciato tre passi: promuovere, sostituire, e L22 per
il THAT320. Il terzo è chiuso da L22+L23 (ADR-018, LS352). Questo lotto fa il
primo. Il secondo è Fase 4 e **non è stato toccato**: il diff del ramo non
nomina `circuits/`, `spice/preamp/` né `docs/preamp/data/`.

Il lavoro era dichiarato «di esecuzione e non di scoperta», perché il
controllo incrociato contro i datasheet era già fatto in L24. In gran parte lo
era: delle **sedici cifre** di L24 rimisurate qui, **undici riproducono** —
alcune a tutte le cifre significative. Le altre cinque no: **quattro f_T**
(§4 e §5) e un «non raggiunto» che si raggiunge (§6). Una delle quattro
sposta un **verdetto**.

## 2. I cinque file, e la regola di derivazione

| File nuovo | Classe | Derivato da | Modello dentro |
|---|---|---|---|
| `models/bjt_pnp/mmbt5401.lib` | bjt_pnp | `vendor/bjt_pnp/diodes_inc/MMBT5401/MMBT5401.spice.txt` | `MMBT5401` |
| `models/bjt_npn/mmbt5551.lib` | bjt_npn | `vendor/bjt_npn/diodes_inc/MMBT5551/MMBT5551.spice.txt` | `MMBT5551` |
| `models/bjt_npn/mje15032.lib` | bjt_npn | `vendor/bjt_npn/onsemi/MJE15032/mje15032.lib` | `Qmje15032` |
| `models/bjt_pnp/mje15033.lib` | bjt_pnp | `vendor/bjt_pnp/onsemi/MJE15033/mje15033.lib` | `Qmje15033` |
| `models/diodes/1n4148.lib` | diodes | `vendor/diodes/onsemi/1N4148/1n914.lib` | **`D1N914`** |

**La derivazione qui è più stretta che per LSK489 e LS350: zero modifiche.**
Quei due erano trascrizioni a mano da un PDF e avevano richiesto una
rimozione — `mfg=`, che ngspice valuta come espressione e su cui muore.
**Nessuno di questi cinque contiene `mfg=`**, quindi non è stato rimosso
niente, non è stato arrotondato niente, e i nomi dei modelli sono quelli che
il costruttore ha scritto — `Qmje15032` con la Q, `D1N914` per il diodo.

Anche i blocchi di commento del costruttore sono copiati verbatim: il
disclaimer AS-IS di Diodes, l'intestazione MODPEX/Symmetry dei due MJE,
l'attribuzione Fairchild del diodo. Sono tracciabilità di licenza, non rumore.

**La proprietà è falsificabile:**

```sh
diff <(grep -v '^\*' vendor/bjt_pnp/diodes_inc/MMBT5401/MMBT5401.spice.txt) \
     <(grep -v '^\*' models/bjt_pnp/mmbt5401.lib)      # vuoto, e così per tutti e cinque
```

### La trappola nuova, e ha morso durante il lotto

**I file vendor usano CRLF. Il tool di editing normalizza a LF, in silenzio.**

Il primo assemblaggio era corretto. Poi tre modifiche di *sola prosa* alle
intestazioni hanno riscritto ogni file per intero — e con esso **ogni riga
del testo vendor**, togliendo il CR. ngspice non se ne accorge, `git diff`
mostra righe apparentemente identiche, e il `diff` sopra era l'unica cosa che
lo diceva: `1,7c1,7` con sette righe che a occhio coincidono.

Rimedio adottato: le intestazioni si modificano **fuori** dal file e
l'artefatto si ricompone sempre con `cat intestazione vendor > modello`. È
scritto in ognuna delle cinque intestazioni sotto il titolo *LINE ENDINGS ARE
MIXED ON PURPOSE*, perché il file risultante ha davvero due convenzioni
dentro, ed è deliberato.

È la stessa famiglia del `Reference value` di `fourier` (L3) e dei tag casuali
di SKiDL (L3b): **un campo che cambia dentro un artefatto per il resto
deterministico**. Qui però non è il generatore a essere non riproducibile — è
lo strumento con cui lo si edita.

## 3. Le cinque ricette, e l'estensione dell'armatura

`validate_models.py` sapeva consumare **un** file `wrdata` per modello. Le
grandezze da bloccare non stanno in un'analisi sola: h_FE e V_F sono in
continua, f_T, C_obo e C_T sono in alternata, e `wrdata` scrive un plot per
volta.

**L'estensione, retrocompatibile e contenuta in `main()`**: un builder può
restituire una **lista** di percorsi e una lista di conteggi di colonne, e il
suo `check_fn` riceve la lista dei row-set nello stesso ordine. Le quattordici
ricette a un file non sono state toccate. Il conteggio resta **un check
elettrico per modello**: 5 provenienze + 5 elettrici = 10 nuovi, **38** in
tutto.

Una seconda correzione, piccola e indipendente: **gli output vengono
cancellati prima di lanciare ngspice.** Prima, un deck che non riusciva a
scrivere un file lasciava sul disco quello della run precedente e il controllo
leggeva numeri vecchi — un verde per una run che non era avvenuta. Con più
file per ricetta la finestra si allargava.

**Tre cose che ogni deck fa**, e che vale copiare invece di riscoprire:

1. **`destroy all` fra un'analisi e l'altra.** Ogni analisi crea un plot
   numerato nuovo (`limitations.md` #10, il difetto che valeva un fattore 3,4
   in L5).
2. **`save` elenca sia i vettori interni del dispositivo sia le correnti di
   ramo.** `@q1[ic]` non viene registrato se non è salvato, e appena esiste
   una lista esplicita ci deve stare dentro anche `i(Vc)`.
3. **`set temp = 25`**, non i 27 °C di ngspice: tutti e quattro i BJT portano
   `XTB`, quindi ogni h_FE si sposterebbe.

**E una che nessuna ricetta precedente faceva: la polarizzazione della f_T si
autoverifica.** La f_T va misurata a una corrente di collettore precisa, e il
modo semplice di ottenerla è una corrente di base fissa — che però smette di
produrre quella corrente appena un parametro del modello cambia. Quindi ogni
ricetta di f_T scrive un file in più con la I_C che l'`op` produce davvero, e
il controllo **rifiuta** se non è quella del datasheet. Non è cerimonia: è
esattamente ciò che è andato storto in L24 (§4).

### Cosa blocca ciascuna ricetta

Misurato con ngspice 47, alle condizioni del rispettivo datasheet, `set temp = 25`:

| Modello | Grandezza | Misurata | Finestra | Esito |
|---|---|---|---|---|
| **MMBT5401** | h_FE @ I_C = −10 mA, V_CE = −5 V | **124,917** | 60…240 | dentro |
| | f_T @ I_C = −10 mA, V_CE = −10 V, ftest 100 MHz | **160,116 MHz** | ≥ 100 | dentro |
| | C_obo @ V_CB = −10 V, 1 MHz, I_E = 0 | **3,7063 pF** | ≤ 6 | dentro |
| **MMBT5551** | h_FE @ I_C = 10 mA, V_CE = 5 V | **107,218** | 80…250 | dentro |
| | f_T @ I_C = 10 mA, V_CE = 10 V, ftest 100 MHz | **175,683 MHz** | ≥ 100 | dentro |
| | C_obo @ V_CB = 10 V, 1 MHz | **2,2207 pF** | ≤ 6 | dentro |
| **MJE15032** | h_FE @ I_C = 0,5 A, V_CE = 5 V | **66,389** | ≥ 70 | **FUORI −5,1%** |
| | h_FE @ I_C = 1,0 A | 61,335 | ≥ 50 | dentro |
| | h_FE @ I_C = 2,0 A | 53,488 | ≥ 10 | dentro |
| | f_T @ I_C = 500 mA, ftest 1 MHz | **27,667 MHz** | ≥ 30 | **FUORI −7,8%** |
| **MJE15033** | h_FE @ 0,5 / 1,0 / 2,0 A | 88,218 / 66,917 / 42,766 | ≥ 70 / 50 / 10 | dentro |
| | f_T @ I_C = 500 mA, ftest 1 MHz | **29,286 MHz** | ≥ 30 | **FUORI −2,4%** |
| **1N4148** | V_F @ I_F = 10 mA | **0,766187 V** | ≤ 1,0 | dentro |
| | C_T @ V_R = 0, 1 MHz | **0,8687 pF** | ≤ 4,0 | dentro |

**Le ricette dichiarano le voci fuori finestra come tali.** La riga che
`validate_models.py` stampa per il MJE15032 è, verbatim:

```
hFE@0.5A=66.4 BELOW its 70 minimum, hFE@1A=61.3, hFE@2A=53.5,
fT=27.667MHz (7.8% below its 30MHz minimum - NC-025)
```

Una ricetta che avesse dichiarato conformità dove non c'è sarebbe stata
peggio di nessuna ricetta.

### I lucchetti sono stati provati a fallire

Sei casi, ognuno una modifica di **una cifra** su una copia di scratch — il
tipo di «correzione» che un lettore futuro potrebbe fare:

| Modello | Modifica | Intatto | Alterato | Il controllo dice |
|---|---|---|---|---|
| mmbt5401 | `TF` +1,5% | PASS | **FAIL** | f_T 158,522 contro 160,116 |
| mmbt5551 | `CJC` +3,3% | PASS | **FAIL** | C_obo 2,2935 contro 2,2207 (**e** f_T) |
| mje15032 | `BF` +1,3% | PASS | **FAIL** | h_FE 67,282 contro 66,389 |
| mje15033 | `TF` +1,4% | PASS | **FAIL** | f_T 28,935 contro 29,286 |
| 1n4148 | `CJO` +2,5% | PASS | **FAIL** | C_T 0,8907 contro 0,8687 |
| mmbt5401 | `BF` +23% | PASS | **FAIL** | «the fT bias is off: IC = 12,2622 mA» |

L'ultimo è il collaudo della guardia sulla polarizzazione, che è la parte
nuova: una beta diversa sposta la corrente che la base fissa produce, e il
controllo se ne accorge **prima** di attribuire al modello una f_T misurata
altrove.

## 4. La f_T del MMBT5401: L24 l'aveva misurata a un'altra corrente

L24 e ADR-017 registrano **169,5 MHz**. Rimisurata con la corrente di
collettore **verificata** a I_C = 10,000 mA — l'`op` stampa `−1,00000e-02` —
la risposta è **160,1 MHz**, su tre gambe concordi:

| Gamba | Valore |
|---|---|
| definizione del datasheet (GBW a ftest = 100 MHz) | **160,116 MHz** |
| attraversamento \|hfe\| = 1 | 160,084 MHz |
| GBW a 50 MHz | 160,098 MHz |

**La causa non è un disaccordo sul modello: è il punto di lavoro.** Il numero
di L24 si riproduce **esattamente** pilotando una corrente di base tonda di
100 µA — che questo modello trasforma in **I_C = 12,68 mA**, il 27% sopra la
corrente a cui il datasheet specifica la f_T. Lo stesso deck a 100 µA
restituisce **169,4698 MHz**.

Il verdetto non cambia: entrambe le cifre superano il minimo di 100 MHz. **Il
numero sì, del 5,5%** — ed è il numero su cui poggia la discussione del polo
dominante, perché il MMBT5401 è il VAS.

È la trappola che ADR-017 stessa nomina una riga più in là — *«attenzione a
quale corrente»* — presa dal lato opposto.

La stessa rimisura sul MMBT5551 sposta poco: L24 dà 173,1 MHz, la
condizione di datasheet ne dà 175,683.

## 5. La f_T dei due MJE: la definizione cambia il verdetto — NC-025

Questa è la scoperta del lotto, e non nasce da una misura nuova ma dalla
**Nota 2** del datasheet MJE15032/D, letta perché serviva per scrivere la
ricetta:

> `fT = hfe · ftest`

e la riga di prova dà **ftest = 1,0 MHz**. La f_T che il costruttore
garantisce è quindi il **prodotto guadagno-banda misurato a 1 MHz**, non
l'attraversamento a |hfe| = 1.

A 1 MHz questi dispositivi stanno solo ~2,6 ottave sopra il proprio polo di
beta, quindi le due letture non coincidono affatto:

| | a ftest = 1 MHz (il datasheet) | attraversamento \|hfe\| = 1 |
|---|---|---|
| MJE15032 | **27,667 MHz** — 7,8% **sotto** i 30 min | 30,713 MHz — dentro |
| MJE15033 | **29,286 MHz** — 2,4% **sotto** i 30 min | 30,719 MHz — dentro |

**Il confronto che vuol dire qualcosa è quello fatto come il datasheet lo
definisce**, perché è contro quella prova che il minimo è scritto — e la
lettura a 1 MHz è più bassa dell'asintoto anche sulla parte vera, che è
esattamente perché il costruttore specifica una frequenza di prova. Fatto
così, **nessuno dei due modelli raggiunge il minimo del proprio costruttore.**

L24 aveva registrato 31,04 e 31,38 MHz e li aveva letti come dentro.

Polarizzazione verificata in entrambi i casi: l'`op` stampa `5,000000e-01` e
`−5,00000e-01`.

Aperta **NC-025**, maggiore. Direzione dell'errore **pessimistica** — il
modello è più lento della parte garantita — quindi margine di fase e guadagno
d'anello che ne escono sono conservativi, ma di quantità non nota. Da leggere
insieme a **NC-020**: **tre dispositivi su sette** del percorso di segnale
portano ora un modello più lento del proprio minimo pubblicato.

**Cosa dicono insieme le due correzioni di §4 e §5:** le condizioni di prova
sono metà del numero, e **la definizione della grandezza è l'altra metà**.

## 6. Il MJE15032 fuori finestra sull'h_FE — NC-024

Non è una scoperta: L24 lo aveva misurato — h_FE **66,389** a I_C = 0,5 A
contro un minimo di **70**, fuori del 5,1% — e riprodotto qui alla terza
cifra. Quello che mancava era la **voce nel registro**. NC-013 (LSK489) e
NC-020 (LS352) sono la stessa forma e ce l'hanno; questa stava solo in
ADR-017 e nel report di L24, cioè in un posto che non genera lavoro.

Aperta **NC-024**, maggiore, e bloccata dalla ricetta.

**Una correzione a L24 che va con la voce**: l'h_FE a 2,0 A, dichiarato «non
raggiunto», si raggiunge. Era l'estensione dello sweep di base, non una
proprietà del modello — spazzato fino a V_b = 1,6 V il modello arriva a
**I_C = 6,8 A** in modo liscio e monotòno, e a 2,0 A vale **53,488** contro un
minimo di 10: dentro.

## 7. Il diodo, e le tre denominazioni

`models/diodes/1n4148.lib` porta il nome della **parte**; il file vendor si
chiama `1n914.lib`; il modello dentro si chiama `D1N914`. Tutti e tre
corretti, e nessuno da «correggere» — onsemi scheda il 1N4148 sotto il
documento 1N914, e il file che *porta* il nome della parte
(`/download/models/lib/1n4148.lib`) contiene `.SUBCKT 1N4148WT`, cioè la
variante SOD-323, che ngspice caricherebbe senza una parola
(`limitations.md` #20). L'intestazione lo dice a caratteri cubitali, perché è
precisamente la correzione che un lettore futuro tenterebbe.

Le due cifre riproducono L24 alla cifra: **V_F 0,766187 V** a 10 mA (max 1,0)
e **C_T 0,8687 pF** a V_R = 0, 1 MHz (max 4,0). Entrambi i limiti pubblicati
sono rispettati: è uno dei tre — con MMBT5401 e MMBT5551 — a uscirne pulito.

Vale però notare, e sta nell'intestazione: **C_T sta 4,6× sotto il tetto
garantito**. Il modello descrive un esemplare tipico o migliore, non il caso
peggiore che il datasheet ammette. Per un diodo di polarizzazione a 1 mA non
conta; in un percorso di segnale conterebbe.

**Un esemplare vivo di `limitations.md` #19 sta in questo stesso datasheet**:
la riga di corrente inversa a V_R = 20 V, T_A = 150 °C esce da `pdftotext`
come «50 mA» e sul render è **50 µA** — sbagliata di mille volte, in silenzio,
con exit 0. Nessuno dei due limiti bloccati ne è toccato (10 mA e 4,0 pF stanno
sopra il confine del milliampere e sono stati guardati sul render), ma è la
conferma che la limitazione morde ancora, sullo stesso costruttore.

## 8. Il rischio che non si è avverato, riverificato eseguendo

I due modelli Diodes portano `QUASIMOD`, `RCO`, `VO`, `GAMMA`, parametri di
quasi-saturazione PSpice. **ngspice 47 li accetta con zero warning** —
riverificato in L25 eseguendo, non ereditato da L24.

Il silenzio è evidenza solo perché il confronto esiste: su
`models/jfet/lsk489.lib` lo stesso ngspice emette **quattro** «unrecognized
parameter … ignored». Quando non conosce un parametro, lo dice.

Nella stessa famiglia: il MMBT5551 scrive `RB =0.26` e `RE =0.23` con uno
spazio prima dell'uguale. **Lo spazio è stato tenuto** e ngspice lo analizza
senza lamentarsi.

## 9. NC-004 non si muove, e ora si sa esattamente perché

**Nessuno dei cinque modelli ha `KF`/`AF`.** I due MJE lo scrivono
esplicitamente (`KF=0 AF=1`, che è la stessa cosa che non averlo); gli altri
tre non li nominano. **Nel repo solo `models/jfet/lsk489.lib` ha rumore 1/f.**

Quindi le cifre di rumore della Fase 4 restano un **pavimento senza flicker**,
e il pavimento cade dove l'analisi dice che il rumore è dominante. Va scritto
accanto a ogni numero, non sottinteso. È registrato in ognuna delle cinque
intestazioni e in ognuna delle cinque `.provenance.json`.

## 10. Le proprietà verificate, non dichiarate

| Proprietà | Come | Esito |
|---|---|---|
| Il testo `.MODEL` è quello del costruttore | `diff` fra le righe non-commento, 5 file | **5/5 vuoto** |
| Gli hash dei sorgenti vendor | `validate_models.py --check-provenance`, che li **ri-calcola** | **19/19 PASS** |
| La libreria | `validate_models.py` con ngspice vero | **38 PASS, 0 FAIL, 0 SKIP** |
| I lucchetti mordono | 6 falsificazioni su copie di scratch | **6/6** intatto PASS → alterato FAIL |
| Le polarizzazioni di f_T sono quelle del datasheet | `op` dentro ogni deck, controllato dalla ricetta | I_C 10,000 mA e 500,000 mA |
| Nessun file di `vendor/` modificato | `git diff --name-status`, righe sotto `vendor/` | **nessuna** |
| Il lotto non tocca la topologia | `git diff --name-only` filtrato su `circuits/`, `spice/preamp/`, `docs/preamp/data/` | **vuoto** |
| La suite | `run_tests.sh` | **5 passed, 0 failed** |

## 11. Cosa NON è stato fatto, dichiarato e non riempito

- **La sostituzione in `circuits/preamp/`**: è Fase 4 ed è il passo che tiene
  aperta NC-017. Nessuna riga di topologia è stata scritta.
- **Le misure del blocco** (PSRR, Z_out, risposta, margine di fase) **non
  sono state rifatte**: i dati in `data/2026-09-09/` descrivono la topologia
  col THAT320, quelli in `data/2026-09-10/` lo stadio d'ingresso con l'LS352.
- **La f_T al punto di lavoro reale (15 mA) dei due MJE non è stata
  rimisurata.** Le cifre 11,24 e 12,58 MHz restano quelle di L24 e sono
  attribuite come tali nelle intestazioni. Alla luce di §5 vanno rilette con
  cautela: sono attraversamenti a guadagno unitario, non la definizione del
  datasheet — ma a 15 mA il datasheet non specifica nulla, quindi non c'è una
  finestra da mancare.
- **L'h_FE del MJE15032 a 2,0 A** è ora misurato, ma **nessuna delle cifre di
  L24 a corrente diversa dal datasheet** è stata riverificata oltre a quelle
  qui elencate.
- **Il simbolo KiCad dell'LSK489** (L10) e ogni altra non conformità: hanno i
  loro lotti.

## 12. Cosa resta di NC-017

Un passo solo, ed è Fase 4: **sostituire** in `circuits/preamp/`, rigenerare
gli artefatti, rifare le misure. Fino ad allora la voce resta **bloccante**,
perché T7 parla del progetto e non della libreria.

Ma vale registrare il punto raggiunto: **tutti e sette i dispositivi attivi
del percorso di segnale hanno ora un modello del costruttore dentro
`models/`**, ognuno col proprio verdetto contro il proprio datasheet scritto
nella propria intestazione. È la prima volta da G0.

E il quadro che ne esce non è lusinghiero, il che è il motivo per cui vale
averlo: su sette modelli vendor, **quattro portano una deviazione dal proprio
datasheet** — LSK489 (NC-013), LS352 (NC-020), MJE15032 (NC-024 e NC-025),
MJE15033 (NC-025) — e i tre puliti sono MMBT5401, MMBT5551 e 1N4148. **Sei su
sette non hanno rumore 1/f.** Le deviazioni vanno tutte nella direzione
sicura, ma di quantità non nota.
