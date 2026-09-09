# L6 — Trascrizione del modello SPICE LSK489

Data: **2026-09-09** · Lotto **L6** · ADR-013 passi 1-3

Documento **datato**: è l'output di un'esecuzione, non si riscrive. Serve
a rendere la trascrizione controllabile **senza rifarla**, e a consegnare
a L7 quello che L7 deve verificare.

---

## Cosa fa questo lotto, e cosa deliberatamente non fa

ADR-013 sceglie l'LSK489 accettando **consapevolmente** un costo: Linear
Systems pubblica il modello SPICE come **PDF contenente il testo
`.MODEL`**, non come `.lib`. Va trascritto a mano, e la trascrizione da
PDF è un punto in cui si introducono errori silenziosi.

L6 esegue i passi **1-3** (congela, trascrivi, dichiara la provenance).
Il passo **4** — il controllo incrociato di I_DSS e V_P contro i limiti
del datasheet — è **L7**, e **non è stato fatto**. La separazione non è
burocratica: il passo 4 è il punto in cui la trascrizione può risultare
sbagliata, e in quel caso il lavoro è tornare qui, non andare avanti.

Quindi, detto senza ammorbidire: **questo modello è trascritto e
verificato sintatticamente, non validato contro i limiti pubblicati della
parte.**

## Perché conta: NC-004

`NONCOMPLIANCE.md` NC-004 è **bloccante**: rumore e distorsione non hanno
evidenza, perché nel repo non esisteva **nessun** modello vendor e i
segnaposto di `spice/preamp/placeholder_devices.lib` hanno `KF = 0` —
quindi nessun rumore 1/f, e ogni cifra ricavata da lì è un **pavimento**,
non una previsione.

Questo file è il primo modello vendor reale del repo. Non chiude NC-004:
la chiudono L6 + L7 più una riesecuzione di `tb_noise_breakdown.cir` coi
dati versionati.

## 1. Gli originali congelati

`vendor/jfet/linear_systems/LSK489/`, scaricati con `curl` **dalla pagina
prodotto del costruttore** (`linearsystems.com/jfet-amplifiers-duals/lsk489-series`),
non da un mirror di distributore:

| File | Ruolo | Byte | Pagine | sha256 |
|---|---|---|---|---|
| `LSK489DSRevA38.pdf` | datasheet | 530 957 | 7 | `f5c359ba70088bb70f3aa75d89f67d0b69db0c49694547173f63edc3eab0096b` |
| `Copy_LSK489A_NJF.pdf` | modello SPICE | 27 178 | 1 | `27c209bf0b8d6344092e2e83c02f13853884231ba736cc3f916f9269fa3d7778` |

Entrambi serviti con `HTTP/2 200`, `content-type: application/pdf`, e il
`content-disposition` registrato in `PROVENANCE.json`. Il secondo file è
stato salvato con un **underscore** al posto dello spazio del nome
servito (`Copy_LSK489A NJF.pdf`); il **contenuto è intatto** e lo sha256
sopra è l'hash esatto di ciò che il server ha inviato.

Congelati a **0444** da `scripts/freeze_vendor.sh`.

## 2. La trascrizione: due letture indipendenti che dovevano coincidere

È il metodo che ADR-013 rende obbligatorio. Entrambe le letture sono
state fatte sulla **copia congelata**, non sul file scaricato al volo.

**Lettura A — visiva.**

```sh
/usr/bin/qlmanage -t -s 2000 -o <dir> vendor/jfet/linear_systems/LSK489/Copy_LSK489A_NJF.pdf
```

poi si guarda l'immagine e si trascrive quello che c'è scritto.

**Lettura B — meccanica**, `scripts/pdf_glyphs.py`: solo stdlib,
decomprime i content stream con `zlib` e ricava i caratteri dagli
operatori `Tj`.

Qui c'è una cosa che vale la pena aver trovato. Il PDF è prodotto da
*Skia/PDF (Google Docs Renderer)* e usa un **font CID con stringhe
esadecimali**: `<0011> Tj` disegna un `.`. I codici nel content stream
**non sono codici di carattere**, sono glyph ID, e sul file lo scarto è
`+0x1D`. Quello scarto **non è stato indovinato**: il PDF porta la
propria `/ToUnicode` CMap, 52 voci, e lo script la legge e la usa. Che
poi la mappa si riduca a una costante `+0x1D` è un **risultato**
verificato dallo script, non un'ipotesi di partenza — ed è la differenza
fra una trasformazione dichiarata e una silenziosa.

**Lettura C — `pdftotext -layout`** (poppler 26.09.0, installato in
questo lotto). Non era richiesta: è una terza gamba.

### L'esito del confronto

Le tre letture, normalizzate solo sulle righe vuote:

| Lettura | Byte | sha256 |
|---|---|---|
| A — visiva | 223 | `67012770a95340afcd346d8a32181f055350bd9d49f3e976b579001d5fc93888` |
| B — meccanica (`pdf_glyphs.py`) | 223 | `67012770a95340afcd346d8a32181f055350bd9d49f3e976b579001d5fc93888` |
| C — `pdftotext -layout` | 224 | `b543b9b059fdfbbcb62aa1de351ba0ed6945395458e5a26eb308478d73f96bf5` |

**A e B sono byte-identiche.** C differisce per **un solo byte**: il
`\f` di fine pagina che `pdftotext` aggiunge; tolto quello, anche C ha lo
stesso sha256. Il confronto carattere per carattere l'ha fatto `diff`,
non l'occhio.

Il testo, verbatim:

```
.model LSK489A NJF(Beta=2.2m Betatce=-.5 Rd=11 Rs=30 Lambda=4.3m Vto=-1.13
Vtotc=-2.5m Is=3f Isr=0 N=1 Xti=0 Alpha=30u VK=120 Cgd=3.19p Mj=0.32 Pb=0.8 Fc=0.5
Cgs=2.92p Kf=0.0009f Af=1 Gdsnoi=2.15 Nlev=3 Mfg=Linear_Systems)
```

Per rifare la lettura B, che è la parte rieseguibile senza dipendenze:

```sh
/usr/bin/python3 scripts/pdf_glyphs.py \
  vendor/jfet/linear_systems/LSK489/Copy_LSK489A_NJF.pdf
```

## 3. Cosa è stato cambiato: una cosa sola

`models/jfet/lsk489.lib` differisce dal testo vendor **per la sola
rimozione di `Mfg=Linear_Systems`**. Nessun valore arrotondato,
riordinato o "corretto". La riga è spezzata su tre righe fisiche con le
continuazioni `+` di SPICE negli stessi punti in cui il PDF va a capo.

### Perché `Mfg` va tolto — verificato, non assunto

Eseguendo la riga **verbatim**:

```
Error in netlist line no. 3, new internal line no. 2:
Undefined parameter [linear_systems]
ERROR: fatal error in ngspice, exit(1)
```

exit **1**. ngspice valuta il valore del parametro sconosciuto come
un'espressione e muore. È un fallimento **rumoroso**, che è la ragione
per cui non è pericoloso.

### I quattro parametri accettati e ignorati

Tolto `Mfg`, ngspice accetta la riga (exit **0**) ed emette **esattamente
quattro** warning, nessun altro:

```
Warning: Model issue on line 78 :
  .model lsk489a njf(beta=2.2m betatce=-.5 rd=11 rs=30 lambda=4.3m vto=-1. ...
unrecognized parameter (isr) - ignored
unrecognized parameter (alpha) - ignored
unrecognized parameter (vk) - ignored
unrecognized parameter (mj) - ignored
```

`isr`, `alpha`, `vk`, `mj` sono raffinamenti PSpice/LTspice della
giunzione di gate e della corrente di saturazione. **Restano nel file**
(decisione dell'utente in apertura di lotto): il diff dal vendor resta
minimo e un simulatore che li supporta riceve i valori del costruttore. I
quattro warning sono **output atteso**, non un difetto da inseguire.

**I parametri che servono a NC-004 sono invece accettati**: `Kf`, `Af`,
`Nlev`, `Gdsnoi`. È il punto dell'intero lotto — questo modello ha il 1/f
che i segnaposto non hanno.

## 4. `docs/limitations.md` #13 — controllata, non morde

#13 dice che `"1M"` è 1 MΩ in KiCad e 1 mΩ in SPICE: sei ordini di
grandezza senza errore da nessuna delle due parti. Ogni suffisso del
modello è stato controllato contro di essa:

| Suffisso | Nel modello | Verdetto |
|---|---|---|
| `m` | `2.2m`, `4.3m`, `-2.5m` | milli in **entrambe** le convenzioni |
| `f` | `3f`, `0.0009f` | femto |
| `p` | `3.19p`, `2.92p` | pico |
| `u` | `30u` | micro |

**Nessuno è ambiguo.** È scritto qui e nell'intestazione del `.lib`
proprio *perché* i valori sono giusti: è il punto in cui qualcuno, avendo
letto #13, "correggerebbe" un numero corretto.

## 5. Il test nella libreria: fumo dichiarato

`scripts/validate_models.py` scopre i `.lib` da solo e marca `SKIP`
quelli senza ricetta — **e uno SKIP fa uscire 1**, quindi senza ricetta
`run_tests.sh` sarebbe diventato rosso. Aggiunta `tb_lsk489()`, sul calco
di `tb_jfet()`:

| Condizione | Misura |
|---|---|
| `Vgs = 0`, `Vds = 5 V` | **2,500 mA** — conduce |
| `Vgs = −3 V` | **8,003e-12 A** — interdetto (`Vto = −1,13 V`) |

La libreria passa da **24 a 26 check**, 26/26 PASS, exit 0.
`run_tests.sh`: **5 passed, 0 failed**.

**Questo non è un controllo contro il datasheet.** I 2,5 mA non sono
stati confrontati con nessun limite di I_DSS: farlo qui cancellerebbe la
ragione per cui L6 e L7 sono separati.

## 6. Un difetto trovato eseguendo, non leggendo

`scripts/validate_models.py` aveva **`ROOT = "/Users/roberto/EDA"`
cablato** (riga 36). Eseguito da un worktree validava **i modelli del
checkout principale**, non quelli del ramo — in silenzio.

Non è stato dedotto: la prima esecuzione di `--check-provenance` da qui
ha stampato **12 PASS** e `jfet/lsk489.lib` **non compariva
nell'elenco**, pur essendo sul disco. È la stessa famiglia di difetti di
`REPO` in `gain_block.py` (L3b) e di `ROOT` in `run_tests.sh`, ma con una
conseguenza peggiore: `chunk_close.sh` esegue `run_tests.sh` dal ramo,
quindi la suite poteva passare **verde su un ramo di cui non aveva
guardato i modelli**.

Corretto derivando `ROOT` da `__file__`. Riesecuzione: 13 provenance su
13, e `lsk489.lib` compare.

Corretto nello stesso lotto anche `scripts/freeze_vendor.sh`, che aveva
`VENDOR_DIR` cablato allo stesso modo (riga 7) e avrebbe congelato il
checkout principale invece dei file appena aggiunti. Provato guardando:
il freeze stampa il percorso del worktree, i cinque file nuovi sono
`0444` **qui**, e `vendor/jfet/` del checkout principale è rimasta vuota.

**Cosa resta della famiglia**: `export_fab.sh` (riga 28) e `setup.sh`
(riga 24) hanno ancora `ROOT` cablato. Non sono stati toccati da questo
lotto, quindi restano dove sono, come `STATE.md` prescrive.

## 7. Cosa L6 consegna a L7

1. **La revisione del datasheet.** Il costruttore serve **RevA38**;
   Mouser serve una revisione **più recente**, **RevA40 (04/12/2022)**.
   È congelata la copia del costruttore, che è la fonte autorevole. L7
   deve **confermare che i limiti I_DSS / V_P non siano cambiati** fra le
   due revisioni prima di usarli come riferimento.
2. **Il passo 4 vero e proprio**: I_DSS e V_P trascritti contro i limiti
   del datasheet. Il datasheet è di **7 pagine** e la tabella sta oltre
   la prima, quindi `sips`/`qlmanage` non bastano: per questo poppler è
   stato installato in L6.
3. **Il valore da spiegare, se non torna**: il modello dà 2,500 mA a
   `Vgs = 0`, `Vds = 5 V`. Se cade fuori dalla finestra I_DSS del
   datasheet, la risposta **non** è ritoccare il modello — è rileggere la
   trascrizione, che è esattamente ciò che il passo 4 esiste per fare.
4. **Il gruppo di selezione.** La parte è divisa in **due** gruppi, non
   tre: **A** (ΔIDSS = 6 mA) e **B** (ΔIDSS = 7 mA). Il modello è
   `LSK489A`, quindi il confronto va fatto con la finestra **A**.

**Una cosa vista di striscio, e registrata come tale.** Il datasheet è
stato aperto in L6 per una domanda sola — quanti gruppi di selezione
esistono — e nella stessa riga si è vista la finestra I_DSS del gruppo A:
**2,5 / 5,5 / 8,5 mA** (min/tip/max). I 2,500 mA misurati qui stanno sul
**bordo inferiore**.

**Questo non è il controllo incrociato, e non va scambiato per uno.** La
misura di L6 è a `Vds = 5 V`, scelto per copiare `tb_jfet()` e non perché
il datasheet lo prescriva: le condizioni di prova di I_DSS non sono state
lette. Un confronto fra un numero misurato in condizioni arbitrarie e una
finestra di datasheet non dice niente, ed è il tipo di cifra che sembra un
esito senza esserlo. Va rimisurato **alle condizioni del datasheet**, in
L7. È registrato qui perché nasconderlo sarebbe peggio che qualificarlo.

## 8. Cosa L6 non ha toccato, e la verifica che sia vero

Il segnaposto `LSK489X` resta in `circuits/preamp/`: la sostituzione
nella topologia è **Fase 4**, non questo lotto. **Nessun numero del
dossier è cambiato**, e non è un'affermazione a fiducia —
`git diff --stat` del ramo non nomina `circuits/`, `spice/preamp/` né
`docs/preamp/data/`.
