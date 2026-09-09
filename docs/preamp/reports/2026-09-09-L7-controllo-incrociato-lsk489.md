# L7 — Controllo incrociato dell'LSK489 contro il datasheet

Data: **2026-09-09** · Lotto **L7** · ADR-013 passo 4

Documento **datato**: è l'output di un'esecuzione, non si riscrive. Il
«perché» sta nelle ADR; qui c'è cosa è stato misurato, con cosa, e che
verdetto ne esce.

---

## Il mandato, e cosa cambia rispetto a come era stato scritto

ADR-013 rende obbligatorio il passo 4 e ne dice il motivo senza
ammorbidire:

> Il punto 4 non è un di più: è ciò che rende accettabile il punto 2.

L6 aveva consegnato a L7 due cose. **Entrambe sono risultate diverse da
come erano state descritte**, e in un caso è la domanda stessa a cadere.
Vale la pena leggerlo come un risultato su come si scrive un compito per
la sessione dopo: due affermazioni plausibili, nessuna delle due
verificata alla fonte, e tutt'e due sbagliate.

## 1. La trascrizione regge — rieseguita, non ereditata

Prima di misurare qualsiasi cosa: il verdetto sul modello ha senso solo
se il modello è ancora quello che L6 ha verificato.

| Controllo | Esito |
|---|---|
| sha256 di `LSK489DSRevA38.pdf` | `f5c359ba…0096b`, **identico** al `.sha256` congelato |
| sha256 di `Copy_LSK489A_NJF.pdf` | `27c209bf…d7778`, **identico** al `.sha256` congelato |
| Lettura B rieseguita (`scripts/pdf_glyphs.py`) | 223 byte, sha256 `67012770a95340afcd346d8a32181f055350bd9d49f3e976b579001d5fc93888` — **lo stesso di L6** |
| Riga `.model` del `.lib` contro il testo vendor meno `Mfg=Linear_Systems` | `diff` **vuoto** |

```sh
/usr/bin/python3 scripts/pdf_glyphs.py \
  vendor/jfet/linear_systems/LSK489/Copy_LSK489A_NJF.pdf
```

Quindi ciò che segue misura **la trascrizione di L6**, non una sua copia
alla deriva.

### Una cosa notata qui: il congelamento a 0444 non attraversa un checkout

I file di `vendor/` sono `0444` nel checkout principale, ma in questo
worktree arrivano `0644`. Non è un guasto di `freeze_vendor.sh`: **git non
versiona il bit di sola lettura**, quindi il congelamento protegge il
filesystem su cui lo script è girato, non il contenuto dentro il repo. La
protezione che attraversa un clone è l'**sha256**, e infatti tiene su
entrambi i file. Registrato perché «i file sono congelati» è vero in un
senso più stretto di quanto sembri.

## 2. La questione della revisione non si risolve: si dissolve

L6 aveva scritto che il costruttore serve **RevA38** e Mouser **RevA40
(04/12/2022)**, e aveva lasciato a L7 il compito di confermare che i
limiti non fossero cambiati fra le due.

**Non esistono due revisioni.** Il file congelato si *chiama*
`LSK489DSRevA38.pdf` — il nome che il server manda nel
`content-disposition` — ma il suo **contenuto** dichiara, su **tutte e 7
le pagine**:

```
Doc 201151 04/12/2022 Rev# A40 ECN# LSK489
```

```sh
/opt/homebrew/bin/pdftotext -layout \
  vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf - | grep 'Rev#'
```

Data e numero di revisione coincidono **esattamente** con quelli che L6
aveva attribuito alla copia Mouser. L6 aveva dedotto la revisione dal
**nome del file**, che è l'unico posto dove compare «A38».

**Provato alla sorgente, non dedotto.** Rieseguita oggi la richiesta
all'URL registrato in `PROVENANCE.json`, il server del costruttore
risponde `HTTP/2 200`, `content-disposition: inline;
filename="LSK489DSRevA38.pdf"`, e consegna 530 957 byte il cui sha256 è
`f5c359ba…0096b` — **byte-identico alla copia congelata**. Il nome
obsoleto è quindi alla sorgente, non un errore di L6 nel salvare.

La gamba indipendente su Mouser non è disponibile: la richiesta torna
`HTTP 200` con una pagina HTML `Access to this page has been denied`, non
un PDF. Non serve: la domanda presupponeva due documenti e ce n'è uno.

**Conseguenza operativa**: il repo ha già congelato la RevA40. Non c'è
niente da aggiungere a `vendor/`. C'è una `revision_note` da correggere,
e siccome il `PROVENANCE.json` è congelato la correzione va **accanto**,
in `PROVENANCE-L7-addendum.json`, non al posto suo.

## 3. Le condizioni di prova, che sono metà del controllo

Datasheet **RevA40, pagina 2**, tabella *Electrical Characteristics*. Le
condizioni contano quanto i limiti, ed è il punto che L6 aveva
esplicitamente lasciato aperto:

| Grandezza | LSK489**A** min / tip / max | Condizioni prescritte |
|---|---|---|
| I_DSS | **2,5 / 5,5 / 8,5 mA** | **V_DG = 15 V**, V_GS = 0 |
| V_GS(off) | **−1,5** / — / **−3,5 V** | V_DS = 15 V, **I_D = 1 nA** |
| V_GS operativa | −0,5 / — / −3,5 V | V_DS = 15 V, I_D = 500 µA |

Tre cose che decidono se la misura è valida:

1. **Il gruppo.** La parte è divisa in due, A (ΔIDSS = 6 mA) e B
   (ΔIDSS = 7 mA); solo I_DSS è separata per gruppo, V_GS(off) no. Il
   modello si chiama `LSK489A`, quindi la finestra è quella di A.
2. **V_DG = 15 V con V_GS = 0 significa V_DS = 15 V ai terminali.**
   `Rd = 11 Ω` e `Rs = 30 Ω` sono **interni al modello**: la tensione si
   applica ai terminali esterni. L6 aveva misurato a V_DS = 5 V, scelto
   per copiare `tb_jfet()` e non perché il datasheet lo prescriva.
3. **Il datasheet è specificato @ 25 °C; ngspice gira a 27 °C per
   difetto**, e questo modello porta `Vtotc=-2.5m` e `Betatce=-.5`.
   Misurare alla temperatura sbagliata è esattamente il tipo di errore
   che questo lotto esiste per non fare. Si misura a 25 °C con
   `set temp = 25` dentro il blocco `.control`, e si registra anche
   27 °C per quantificare lo scarto.

## 4. Le misure

Tutte con ngspice reale, `set temp = 25`, `.include` del `.lib` del ramo.
I quattro warning `unrecognized parameter (isr|alpha|vk|mj)` sono output
atteso, verificato in L6.

### I_DSS

```
Vdd d 0 DC 15
Vgs g 0 DC 0
J1  d g 0 LSK489A
.control
set temp = 25
op
print i(Vdd)
```

| Condizione | I_DSS |
|---|---|
| **V_DG = 15 V, V_GS = 0, 25 °C** — datasheet | **2,59283 mA** |
| V_DG = 15 V, V_GS = 0, 27 °C — default ngspice | 2,59188 mA |
| V_DS = 5 V, 27 °C — la condizione arbitraria di L6 | **2,50019 mA** |

L'ultima riga **riproduce i 2,500 mA di L6**, il che prova che la
differenza col numero nuovo viene dalle condizioni e non da altro. La
temperatura sposta lo **0,04%**: non è lei a decidere niente qui.

### V_GS(off) e V_GS, dallo stesso sweep

```
dc Vgg -1.30 0 20u        (65 001 campioni, V_DS = 15 V, 25 °C)
```

Il pavimento di perdita a V_GS = −1,30 V è **1,63e-11 A**, cioè
0,016 nA: la soglia di 1 nA prescritta dal datasheet è quindi
**effettivamente attraversata** e non annegata nel pavimento.

| Grandezza | Misura a 25 °C | Misura a 27 °C |
|---|---|---|
| V_GS(off) all'attraversamento di I_D = 1 nA | **−1,124355 V** | −1,129352 V |
| V_GS all'attraversamento di I_D = 500 µA | **−0,650211 V** | −0,652918 V |

**Tre strade indipendenti verso V_P, e concordano.** Un numero solo non
sarebbe una misura:

| Strada | Valore a 25 °C |
|---|---|
| Attraversamento di I_D = 1 nA (definizione del datasheet) | −1,124355 V |
| Estrapolazione ai minimi quadrati di √I_D → 0, su 6315 campioni fra 1 e 50 µA (residuo max 8,9e-06) | −1,125398 V |
| `Vto + Vtotc·(T − Tnom)` letto dal modello | −1,125000 V |

Le tre cadono entro **1,0 mV**. La finestra del fit è a corrente bassa di
proposito: così la caduta su `Rs = 30 Ω` resta sotto il millivolt e non
curva l'estrapolazione.

**Controprova sulla temperatura**: fra 25 e 27 °C il V_P si sposta di
**4,997 mV**, contro i 5,000 mV che `Vtotc = −2,5 mV/°C × 2 °C` prescrive.
Quindi `set temp` ha davvero avuto effetto — non è stato assunto.

## 5. Il verdetto

Un verdetto è «dentro la finestra» oppure «fuori, di tanto».

| Grandezza | Misurata (25 °C) | Finestra LSK489A | **Verdetto** |
|---|---|---|---|
| I_DSS | 2,59283 mA | 2,5 … 8,5 mA | **DENTRO** — 3,7% sopra il minimo, 52,9% sotto il tipico |
| V_GS(off) | −1,124355 V | −1,5 … −3,5 V | **FUORI** — **0,376 V** sotto il minimo in modulo, cioè il 25% |
| V_GS @ 500 µA | −0,650211 V | −0,5 … −3,5 V | **DENTRO** |

## 6. Perché questo **non** è un errore di trascrizione

È la domanda che il passo 4 esiste per porre, e la risposta è misurata,
non argomentata.

**Primo: la trascrizione è stata riverificata oggi** (sezione 1) e
coincide byte per byte con quella di L6, che a sua volta veniva da due
letture indipendenti byte-identiche più una terza concorde.

**Secondo, e più forte: i due scarti sono uno solo.** Dentro il modello
I_DSS e V_P non sono indipendenti — sono legati da `Beta`, che è
trascritto. Tenendo `Beta = 2.2m` e muovendo solo `Vto`:

| `Vto` | I_DSS misurata (V_DG = 15 V, 25 °C) |
|---|---|
| **−1,13 V** — il modello vendor | **2,593 mA** — spigolo basso della finestra A |
| −1,50 V — minimo V_GS(off) del datasheet | 4,392 mA — **dentro** A, vicino al tipico |
| −1,58 V | 4,833 mA |
| −3,50 V — massimo V_GS(off) del datasheet | 19,83 mA |

Le due finestre del datasheet sono quindi **compatibili fra loro** con il
`Beta` trascritto: un esemplare con V_P al minimo pubblicato avrebbe
I_DSS ≈ 4,4 mA, cioè comodamente dentro A. Il modello vendor sta **sotto
entrambe, in modo coerente**. Se `Vto` fosse stato trascritto male, I_DSS
e V_P sarebbero scivolati in direzioni **scorrelate**: sono invece
esattamente dove la legge quadratica li mette. È **uno scarto solo**, non
due.

(L'ultima riga della tabella dice anche perché la finestra V_GS(off) è
larga: −3,5 V con questo `Beta` darebbe 19,8 mA, fuori anche dal gruppo
B. Quella finestra copre A e B insieme e ammette la dispersione di `Beta`
da esemplare a esemplare — non è una finestra che un singolo modello
possa riempire.)

**Conclusione**: la discrepanza è fra il modello SPICE del costruttore e
il **datasheet dello stesso costruttore**, non fra il PDF e ciò che il
repo ne ha trascritto. Il lavoro **non** è tornare su L6.

## 7. Cosa significa per il progetto

Il modello descrive un esemplare allo **spigolo a bassa I_DSS** del
gruppo A, non un esemplare tipico. Non lo rende inutilizzabile — è il
modello che il costruttore pubblica, ed è pur sempre il primo modello
vendor del repo, con il `Kf` che i segnaposto non hanno. Ma cambia cosa
si può dire dei numeri che ne usciranno:

- le polarizzazioni che la **Fase 4** calcolerà con esso sono un **caso
  d'angolo**, non il tipico. Un preamplificatore costruito con esemplari
  reali vedrà transconduttanze **più alte** di quelle simulate;
- di conseguenza le cifre di rumore che chiuderanno la metà mancante di
  **NC-004** sono conservative sul contributo del JFET d'ingresso — il che
  è la direzione giusta in cui sbagliare, ma va detto e non sottinteso;
- il progetto **non deve** dipendere da una I_DSS di 2,6 mA: è il minimo
  garantito, non il valore atteso.

Aperta per questo **NC-013** in `docs/preamp/NONCOMPLIANCE.md`, severità
**maggiore, non bloccante**: non ferma un avanzamento di fase, vincola
come si leggono i numeri. Il lotto che la chiude è **L20**.

**Non è stata riaperta ADR-013.** La sua clausola «da riaprire se il
controllo incrociato non torna» è scritta per il caso in cui la parte o
la trascrizione siano sbagliate; qui la parte è quella scelta e la
trascrizione è corretta. La decisione se ripiegare sul JFE2140 resta
dell'utente, ora informata da un numero invece che da un dubbio.

## 8. La ricetta di validazione: da fumo dichiarato a blocco di regressione

`tb_lsk489()` in `scripts/validate_models.py` misurava a V_DS = 5 V e
dichiarava di essere fumo. Ora misura **alle condizioni del datasheet** e
asserisce il verdetto di sopra — **non** una conformità che non c'è:

- I_DSS dentro `[2,5; 8,5] mA`;
- V_GS @ 500 µA dentro `[−0,5; −3,5] V`;
- V_P **uguale a −1,124355 V entro 1 mV**, cioè bloccato al valore che L7
  ha misurato.

Uno sweep solo risponde a tutte e tre: I_DSS è il suo ultimo punto
(V_GS = 0) e le due tensioni sono attraversamenti lungo la strada. Il
docstring dichiara per esteso che V_GS(off) del datasheet **non** è
asserita e di quanto il modello se ne scosta.

Il conteggio **non cambia: 26/26**. Cambia cosa asserisce.

**Collaudato facendolo fallire di proposito**, che è l'unico modo di
sapere che un controllo controlla:

| Mutazione su `Vto` | Esito |
|---|---|
| −1,13 → **−1,53** (la «correzione» che farebbe tornare il datasheet) | **FAIL** — «the model's threshold has moved» |
| −1,13 → **−1,20** (70 mV, I_DSS resta **dentro** la finestra) | **FAIL** — «V_P=-1.194355V has moved … by more than 1.0mV», exit **1** |

La seconda riga è quella che conta: con 70 mV di scarto la I_DSS resta
dentro la finestra del datasheet, quindi **la finestra da sola non
l'avrebbe visto**. Il lucchetto sì. È la protezione contro la modifica
silenziosa che `docs/limitations.md` #13 rende plausibile — qualcuno che,
avendo letto #13, «corregge» un valore giusto.

Modello ripristinato con `git checkout` dopo il collaudo, e la libreria
riverificata: **26 PASS, 0 FAIL, 0 SKIP, exit 0**.

## 9. Cosa L7 non ha toccato, e la verifica che sia vero

Il segnaposto `LSK489X` resta in `circuits/preamp/`: la sostituzione
nella topologia è **Fase 4**. Nessun numero del dossier è cambiato, e non
è un'affermazione a fiducia — `git diff --stat` del ramo non nomina
`circuits/`, `spice/preamp/` né `docs/preamp/data/`.

`export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT`
cablato su `/Users/roberto/EDA`. L7 non li ha toccati, quindi restano —
è la regola già scritta in `STATE.md`.
