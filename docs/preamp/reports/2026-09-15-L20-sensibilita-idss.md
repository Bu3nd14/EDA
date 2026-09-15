# L20 — Quanto il progetto dipende da I_DSS (2026-09-15)

Lotto **L20**. Chiude **NC-013** (maggiore). ADR nuova: **ADR-031**. Dati:
`data/2026-09-15/L20/`.

**Nessun valore del circuito cambia.** Nessun file generato, nessun file di
`models/` o `vendor/` toccato. Il dossier non è rigenerato.

Documento **datato**: è l'output di un'esecuzione, non si riscrive.

## 0. Una domanda all'utente, prima di misurare

Leggendo il sorgente: `gain_block.py:315` dichiara `value="LSK489B"`. È entrato
con L10 (`0f2f3c4`), un lotto sul simbolo, senza una riga di motivazione.

Il datasheet RevA40 a pag. 2 separa la I_DSS per gruppo:
- **A** 2,5 / 5,5 / 8,5 mA;
- **B** 8,0 / 11,5 / 15,0 mA.

NC-013 e il mandato ragionavano sulla finestra A, quella del modello. Il gruppo
cambia i punti da misurare, quindi la domanda è andata all'utente. La risposta:
**«Solo B, il gruppo del sorgente»**.
- La tolleranza si scrive su 8,0 · 11,5 · 15,0 mA.
- Il gruppo B diventa scelta di progetto (ADR-031).
- Il modello com'è (2,59 mA) e il tipico A (5,5 mA) restano come riferimento,
  come NC-013 chiedeva.

## 1. Il JFET da solo: che cosa simula il progetto oggi

**Il meccanismo, provato prima di usarlo.** Sonda di scratch, JFET singolo
`LSK489A`:
- senza `altermod` ridà L7 (2,59283 mA);
- `vto = -1.50` dà 4,39247 mA e `-1.58` dà 4,83303 mA, le cifre della tabella di
  L7 (4,392 e 4,833);
- l'alterazione regge `set temp`, i rami `if` dentro `foreach` e una `dc`;
- `kf = 0` si applica;
- **un nome di modello sbagliato stampa una riga `Error` e non cambia niente**:
  limitazione **#29**.

**I `Vto`.** `esplorazione/script/cerca_vto.py`: bisezione a V_DG = 15 V, 25 °C,
`Vto` arrotondato al mV, I_DSS rimisurata col valore arrotondato.
- **Trovato**: l'arrotondamento al mV più vicino dava al minimo B **7,99795 mA**,
  sotto gli 8,0 della finestra.
- Gli estremi si arrotondano ora verso l'interno: −2,086 V → 8,00484 mA.

**Il deck** è `data/…/L20/deck/tb_idss_jfet.cir`: `LSK489X` e `LSK489A`
affiancati, condizioni di L7, 25 e 27 °C.
- **La prima esecuzione ha scritto 10 righe vuote**, con 80 righe `Error` e rc 0:
  gli `echo` stavano dopo `destroy all`. Corretto con variabili stringa. Annotato
  in #26.

| 25 °C | I_DSS | Gfs | V_GS(off) a 1 nA | V_GS a 500 µA |
|---|---|---|---|---|
| **`LSK489X`** | **4,8422 mA** | 6,672 mS | **−1,49935 V** | −1,02873 V |
| `LSK489A` com'è | 2,59283 mA | 4,952 mS | −1,12435 V | −0,65021 V |
| `LSK489A`, `Vto` −1,696 | 5,50250 mA | 7,212 mS | −1,69036 V | −1,21621 V |
| `LSK489A`, `Vto` −2,086 | 8,00484 mA | 8,697 mS | −2,08035 V | −1,60621 V |
| `LSK489A`, `Vto` −2,557 | 11,49940 mA | 10,421 mS | −2,55136 V | −2,07721 V |
| `LSK489A`, `Vto` −2,976 | 14,99650 mA | 11,897 mS | −2,97036 V | −2,49621 V |

La riga di `LSK489A` com'è **riproduce L7**: 2,59283 mA, −1,124355 V (stampato
−1,12435), −0,650211 V.

**Il segnaposto contro il datasheet, per la prima volta.**
- **I_DSS 4,842 mA**: dentro la finestra A, **12 % sotto il tipico**. Fuori
  dalla B, al 60,5 % del minimo.
- **V_GS(off) −1,49935 V**: 0,65 mV sotto il minimo in modulo, cioè sul bordo.
- V_GS a 500 µA e Gfs (≥ 1,5 mS) dentro.
- Non ha coefficienti di temperatura: stesse cifre a 25 e 27 °C.

**Chi sta più vicino al tipico.** Sul gruppo A, di gran lunga il segnaposto:
−12 % contro −52,9 % del modello del costruttore. Sul gruppo B, che è quello del
sorgente, nessuno dei due.

Tutte le cifre del progetto fino a oggi descrivono quindi un JFET **quasi tipico
del gruppo A**, non il B che il sorgente nomina. §3–§5 misurano che per punto di
lavoro, rumore e V1 non fa differenza.

## 2. Come istanziare `LSK489A` senza toccare niente di generato

Il nome del modello è un letterale, `gain_block.py:325-326` (`"LSK489X"`), e
finisce così in `gain_block_flat.inc` e `gain_block.subckt`. Le strade chiuse,
lette sui file:

| Strada | Perché no |
|---|---|
| Una seconda `.model LSK489X` coi valori del costruttore | due modelli con un nome (#17), e `provenance()` lo direbbe segnaposto |
| Un modello «LSK489B» o un `LSK489A` alterato in un file nuovo | `provenance()` (`build_dossier.py:373`) rifiuta un modello che non sta in `models/` con provenance né nel file dei segnaposto: il 2h cadrebbe con rc 2 |
| `Vto` ritoccato in `models/jfet/lsk489.lib` | vietato dal mandato; cancella la traccia di NC-013; il lucchetto di `validate_models.py` cadrebbe |
| Copia a mano di `gain_block_flat.inc` | AGENTS.md regola 2; diventa stantia al primo cambio di topologia, in silenzio |
| Parametro in `gain_block.py` | tocca il sorgente di verità per un lotto che non adotta il modello (Fase 4, NC-017) |

**La scelta, in due parti.**
1. **Il nome si deriva.** `scripts/derive_jfet_variant.py` legge l'include
   generato e asserisce **esattamente due** righe JFET su `LSK489X`. Sostituisce
   il nome e scrive `spice/preamp/derived/gain_block_flat_lsk489a.inc`, con
   un'intestazione che nomina la sorgente e il suo sha256.
   - Tutto il resto è copiato byte per byte, compresa la riga «External nodes»
     che il 2g legge (#27).
   - `--check` rifiuta un derivato che non coincide con la derivazione fresca:
     è il **blocco 2i** di `run_tests.sh`.
2. **Il `Vto` si altera a runtime.** `altermod` dentro `.control`, sul modello
   incluso intatto.
   - Il modello alterato porta ancora il nome del costruttore, e `provenance()`
     non lo vede (#29). Per questo ogni variante stampa `showmod`.
   - Una **JFET sonda** sullo stesso modello, su nodi propri (#24), misura nella
     stessa esecuzione la I_DSS che il blocco simula.

**`build_dossier.PART` + `"LSK489A": "LSK489"`.** Senza, il 2h legge le frasi su
«LSK489» come riferite a una parte che il deck non simula. Si prova sotto (§7)
che senza la voce cadeva per la ragione sbagliata. L'output del 2h sui 18 deck
esistenti è **byte per byte identico** prima e dopo.

## 3. Il punto di lavoro

`spice/preamp/tb/tb_idss_op_noise.cir`: blocco B a 0 dB, sorgente 430 Ω, 27 °C.

| | I_DSS sonda 27 °C | coda Q106 | I_D (A / B) | V_GS | gm | V_DS | VAS | uscita | v(SRC) | v(OUT) |
|---|---|---|---|---|---|---|---|---|---|---|
| `xa` | 4,8422 mA | 4,37385 mA | 2,21131 / 2,16255 mA | −0,4914 V | 4,3851 mS | 8,739 V | 6,44250 mA | 14,5573 mA | +0,248 V | −16,5757 mV |
| `a_come_e` | 2,59188 | 4,37306 | 2,21091 / 2,16215 | −0,1465 | 4,4958 | 9,129 | 6,44244 | 14,5573 | −0,141 | −17,2606 |
| `a_tip` | 5,48711 | 4,37421 | 2,21149 / 2,16272 | −0,7112 | 4,4911 | 8,564 | 6,44252 | 14,5573 | +0,424 | −17,2720 |
| `b_min` | 7,97616 | 4,37500 | 2,21188 / 2,16312 | −1,1003 | 4,4879 | 8,175 | 6,44257 | 14,5574 | +0,813 | −17,2799 |
| `b_tip` | 11,4520 | 4,37894 | 2,21229 / 2,16353 | −1,5702 | 4,4839 | 7,705 | 6,44265 | 14,5574 | +1,283 | −17,2910 |
| `b_max` | 14,9306 | 4,37952 | 2,21272 / 2,16395 | −1,9883 | 4,4805 | 7,287 | 6,44271 | 14,5574 | +1,701 | −17,2995 |

Il cascode (NCASC 9,8866 V, 2,193–2,194 mA) e Q125 non si muovono oltre la
quinta cifra. I_G sta fra −9,3 e −11,2 pA: gate in inversa ovunque.

**Lettura.** La coda impone la corrente, quindi I_DSS sposta V_GS e il nodo di
sorgente, di 1,84 V su tutta la corsa, e quasi niente altro:
- I_D varia di 1,8 µA, gm dello 0,34 %, la coda di 6,5 µA (0,15 %);
- l'offset varia di **0,039 mV**.

Il passaggio dal segnaposto al modello del costruttore pesa di più di tutta la
finestra: gm +2,5 %, offset −0,685 mV.

**Le capacità di giunzione al punto di lavoro**, *calcolate dalla formula del
modello* e non stampate da ngspice: C₀/√(1 − V/PB), con `mj` ignorato.
- Cgd **0,899 pF** col modello del costruttore, 0,311 pF col segnaposto. V_GD è
  −9,27 V in tutte le varianti, perché il cascode la tiene ferma.
- Cgs da 2,685 a 1,564 pF fra 2,59 e 15 mA.

## 4. Il modo comune

Spazzata di VSRC fino al picco di E6, ±3,82 V, a 0 dB. Il margine di saturazione
è (V_D − V_G) − |V_P(27 °C)| sulle tensioni ai terminali, con V_P dalla colonna
a 1 nA di §1.

| | margine min A / B | a | V_CE Q106 min | a | max \|OUT − VSRC\| |
|---|---|---|---|---|---|
| `xa` | 3,891 / 3,909 V | +3,82 V | 10,846 V | −3,82 V | 19,36 mV |
| `a_come_e` | 4,261 / 4,280 V | +3,82 | 10,448 | −3,82 | 19,97 |
| `a_tip` | 3,695 / 3,714 | +3,82 | 11,012 | −3,82 | 19,98 |
| `b_min` | 3,305 / 3,324 | +3,82 | 11,401 | −3,82 | 19,99 |
| `b_tip` | 2,834 / 2,853 | +3,82 | 11,871 | −3,82 | 20,00 |
| `b_max` | **2,415 / 2,434** | +3,82 | 12,289 | −3,82 | 20,01 |

**È la grandezza che I_DSS consuma**: 1,85 V fra 2,59 e 15 mA. Al massimo del
gruppo B restano 2,4 V.

## 5. Il rumore (E5)

`onoise_total`, µV RMS, 20 Hz–20 kHz. **Pavimento senza flicker per ogni
dispositivo tranne la coppia d'ingresso**: `LSK489A` ha `Kf`, il resto no.

| | A 0 dB 1 Ω | B 0 dB 430 Ω | C 0 dB 2,5 k | **D +10 dB 2,5 k** | E +3 dB 2,5 k |
|---|---|---|---|---|---|
| `xa` (= L27, nessun 1/f) | 1,15653 | 1,21628 | 1,47030 | 4,22886 | 2,01070 |
| `a_come_e` | 1,18414 | 1,24257 | 1,49213 | 4,30327 | 2,04279 |
| `a_come_e_kf0` | 1,18357 | 1,24203 | 1,49168 | 4,30171 | 2,04212 |
| `a_tip` | 1,18463 | 1,24304 | 1,49252 | 4,30459 | 2,04335 |
| `b_min` | 1,18497 | 1,24336 | 1,49279 | 4,30550 | 2,04375 |
| `b_tip` | 1,18538 | 1,24376 | 1,49312 | 4,30660 | 2,04423 |
| `b_max` | 1,18575 | 1,24410 | 1,49341 | **4,30759** | 2,04466 |

Nel caso D:
- l'1/f del JFET vale **0,116 µV** in quadratura;
- tutta la finestra 2,59–15 mA aggiunge 0,004 µV;
- il cambio di modello aggiunge 0,074 µV.

| Spettro D | 20 Hz | 100 Hz | 1 kHz | 20 kHz |
|---|---|---|---|---|
| `a_come_e` | 32,057 | 30,814 | 30,528 | 30,308 nV/√Hz |
| `a_come_e_kf0` | 30,499 | 30,497 | 30,496 | 30,307 |
| `xa` | 29,980 | 29,978 | 29,977 | 29,798 |

**E5: conforme** in ogni variante e caso. Il peggiore è 4,308 µV, contro
√(10² − 1²) = 9,95 µV (ADR-020). **Non chiude NC-004**: il flicker degli altri
dispositivi non c'è.

## 6. V1 — deciso coi numeri

**Prima dei dati.**
- A corrente fissata gm = 2√(β·I_D) non dipende da `Vto`, e il cascode tiene
  V_GD: I_DSS dovrebbe spostare poco.
- Il cambio di modello invece cambia Cgd (1,1 → 3,19 pF di C₀), `Beta` e `Rs`,
  e il margine più stretto del prodotto stava a 1,63° dalla soglia.
- Quindi si misura il caso peggiore del blocco B. La regola è scritta prima:
  **se la dispersione del gruppo B in una cella supera 1,63°, o un minimo scende
  sotto 60°, si estende al buffer delle fisse e al blocco A.**

`spice/preamp/tb/tb_idss_loop.cir` è `tb_loop.cir` ristretto a:
- 0 dB e sonda al jack;
- sorgenti 1 mΩ / 1 k / 2,5 k / 2,571 k / 2,611 k;
- 11 cavi fino a 4,7 nF;
- carichi 100 k e 10 k.

In tutto 550 celle.

| | min 100 k | min 10 k | dove | f di attraversamento |
|---|---|---|---|---|
| `xa` (= L16, 110 celle su 110) | 61,8030° | 61,8447° | 2,611 k, 3,3 nF | 847,7 kHz |
| `a_come_e` | 62,5076° | 62,5505° | idem | 814,8 kHz |
| `b_min` | 62,7076° | 62,7504° | idem | 814,4 kHz |
| `b_tip` | 62,7629° | 62,8057° | idem | 814,0 kHz |
| `b_max` | 62,8018° | 62,8446° | idem | 813,7 kHz |

- **Dispersione del gruppo B nella stessa cella: ≤ 0,104°.** Con `a_come_e`:
  ≤ 0,323°.
- Il cambio di modello sposta ogni cella di **+0,59 … +0,92°**. Il margine
  **sale**, e l'attraversamento scende da 848 a 815 kHz.
- |T| a 10 Hz fra 71,92 e 72,40 dB su tutte le righe (#24).
- **La regola dice: non serve estendere.** Il buffer delle fisse (61,63°) e il
  blocco A non sono rimisurati col modello del costruttore. È scritto in
  ADR-031 fra i casi da riaprire.

## 7. I controlli, e quale cade

`esplorazione/script/verifica.py` sui dati veri: **tutti passati**. Esito in
`esplorazione/verdetto.txt`.

| Controllo | Esito sui dati veri |
|---|---|
| 0 righe `Error` nei tre log | 0 / 0 / 0 |
| Tabelle senza celle vuote, con le righe attese | 10, 8, 40, 550 |
| `LSK489X` non si muove fra le varianti | identico |
| `LSK489A` com'è = L7 | 2,59283 mA, −1,12435 V, −0,650212 V |
| I_DSS di ogni variante = `vto_dichiarati.csv`; sonda del blocco = colonna 27 °C | tutte |
| `a_ripristinato` = `a_come_e` cella per cella | identiche (punto di lavoro e rumore) |
| `kf` non tocca il punto di lavoro | identico |
| `xa` = gli 81 valori di `tb_op` di L27 | tutti entro 1 ppm, IN e G1 meno lo spostamento previsto |
| `xa` = i cinque totali di `tb_noise_breakdown` di L27 | tutti |
| il 1/f del JFET si vede: D a 20 Hz, `kf` sopra `kf0` | rapporto 1,0511 |
| `xa` = le 110 celle di L16 `tb_loop` | tutte, entro 5e-4° |
| \|T\| a 10 Hz 71,5–72,6 dB | 71,92–72,40 |

**Un controllo che ha trovato un errore nel deck.**
- La prima versione del confronto `xa`/`tb_op` è **caduta su due valori soli**:
  v(IN) 4,17 nV e v(G1) 5,14 nV.
- `tb_op` pilota IN direttamente, questo deck attraverso 430 Ω.
- Il commento del deck stimava lo spostamento in «~4 pV». È 9,7 pA × 430 Ω =
  **4,17 nV**, mille volte di più.
- Il controllo ora **prevede** lo spostamento (I_G × 430 Ω, entro lo 0,1 %) e lo
  sottrae; il commento è corretto.

**I sabotaggi dei deck**, su copie in scratch, `sabotaggi_deck/`:

| # | Sabotaggio | Controlli caduti | Atteso |
|---|---|---|---|
| s1 | `altermod lsk489x` al posto di `lsk489a` in `b_min` | riga `Error`; sonda `b_min` a **5,487 mA** (la variante precedente) | sì |
| s2 | `Vto` −2,068 invece di −2,086 | **solo** la sonda (7,853 contro 7,976 mA) | sì: nessuna riga `Error`, la vede solo la sonda |
| s3 | `xa` senza `rs = 10` | solo i tre controlli di `xa`: sonda, `tb_op`, rumore | sì |
| s4 | `kf = 0` tolto da `a_come_e_kf0` | **solo** il controllo del 1/f (rapporto 1,000000) | sì |

**I sabotaggi della derivazione**, `sabotaggi_derive.txt`, 6 su 6 come attesi:

| Caso | Esito |
|---|---|
| copia intatta | rc 0 |
| derivato ritoccato a mano (R136) | rc 1 «STALE», riga 50 |
| blocco generato cambiato (C137) senza rigenerare | rc 1 «STALE» sullo sha256 |
| una riga `LSK489X` | rc 2 |
| tre righe `LSK489X` | rc 2 |
| `LSK489X` su una riga BJT | rc 2 «not a JFET» |
| `--model LSK489X` | identico alla sorgente, cmp rc 0 |

**Il 2h, fatto cadere apposta**, `2h/`. Il deck nuovo è partito con
l'intestazione copiata da `tb_op.cir` («Its halves are LSK489X, a hand-written
placeholder with KF=0»).

| Passo | Esito | Ragione |
|---|---|---|
| 1. prima della voce in `PART` | rc 1 | «claims about LSK489, which this deck does not simulate»: **la ragione sbagliata** |
| 2. dopo la voce | rc 1 | «calls LSK489 a placeholder; the includes give LSK489A (models/jfet/lsk489.lib): vendor»: **la giusta** |
| 3. i 18 deck esistenti, prima e dopo | rc 0, output byte per byte identico | la voce non cambia niente altrove |
| 4. intestazione vera | rc 0 | **2 affermazioni lette** sul deck, «vendor by includes: LS352, LSK489»: il guardiano non è muto |

Il deck d'anello, scritto con l'intestazione vera: rc 0, 2 affermazioni lette. 2g
su entrambi: rc 0.

**Solo commento in `gain_block.py`**: `ast_identico.py` contro `HEAD`, AST
identico. Gli artefatti generati non sono rigenerati.

## 8. La tolleranza — ADR-031

**Il JFET è del gruppo B, e il progetto ne tollera l'intera finestra, 8,0–15,0
mA.** Criterio misurato ai tre punti; peggiore nel gruppo:
- saturazione a modo comune di E6: 2,415 V;
- gate in inversa;
- V_CE di Q106 ≥ 11,40 V;
- classe A entro lo 0,15 %;
- E5 4,308 µV;
- V1 62,708°;
- offset −17,28 … −17,30 mV, senza soglia (L29).

Scritto anche in `REQUIREMENTS.md`, riga T4 e «Nota su T4».

**Il progetto non risulta sensibile**, quindi ADR-013 non si riapre. ADR-031 la
precisa sul gruppo.

## 9. NC-013

**Chiusa.**
- La sensibilità a I_DSS è quantificata ai due estremi di NC-013 (2,59 e 5,5
  mA) e sulla finestra del gruppo che il progetto usa.
- La dispersione tollerata è scritta, con il criterio (ADR-031).
- Il modello non è ritoccato.

## 10. Che cosa L20 non ha fatto, detto chiaro

- **Nessun modello del costruttore del gruppo B.** Le cifre B sono `LSK489A` con
  `Vto` spostato e `Beta` fisso: un parametro solo, come prescritto. Un
  esemplare B con un altro `Beta` non è simulato.
- **Il gruppo B non è verificato contro T8** (disponibilità, ciclo di vita).
- **Solo 27 °C**: i 60 °C del telaio (ADR-021) non sono simulati. Il modello ha
  `Vtotc` e `Betatce`; i segnaposto degli altri dispositivi hanno una
  dipendenza generica.
- **V1 solo sul blocco B a 0 dB**, per la regola di §6. Buffer delle fisse,
  blocco A, +3 e +10 dB restano misurati col segnaposto.
- **La sostituzione del modello nei deck di `main`** è Fase 4 (NC-017): tutti i
  deck di prima istanziano ancora `LSK489X`.
- **Il dossier** non pubblica niente di L20.
