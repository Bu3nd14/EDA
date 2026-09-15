# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

## In breve

| | |
|---|---|
| Ultimo aggiornamento | **2026-09-15** |
| Ultimo lotto chiuso | **L20** — quanto il progetto dipende da I_DSS. Col modello del costruttore, dal modello com'è (2,59 mA) a tutto il gruppo B (15 mA): punto di lavoro, E5 e V1 non ne dipendono, il margine di modo comune scende a 2,4 V. ADR-031 (gruppo B, tolleranza 8,0–15,0 mA); chiude NC-013. Prima: **L13** — E4 sulle tre uscite, chiude NC-008, apre NC-033 |
| **Prossimo lotto** | **L37** — E4 nel dossier, NC-033 (mandato in «Prossimo passo concreto») |
| Non conformità | **14 aperte, 2 bloccanti** |
| Le bloccanti | NC-004 · NC-017 (Fase 4) |
| Suite | `run_tests.sh` **10 passed / 0 failed** a fine L20 (nuovo il 2i: il blocco derivato con `LSK489A` coincide con quello generato) |

## Diario degli ultimi lotti

Il più recente in alto. Il dettaglio di ciascuno sta nella sua sezione più
sotto e nel report datato in `reports/`.

### L20 — quanto il progetto dipende da I_DSS (2026-09-15)

**Chiude NC-013.** ADR nuova: **ADR-031**. Report:
`reports/2026-09-15-L20-sensibilita-idss.md`. Dati: `data/2026-09-15/L20/`.
Nessun valore del circuito cambia; dossier non rigenerato.

- **Una domanda all'utente, prima di misurare.** Il sorgente nomina `LSK489B`
  (da L10, senza motivazione), mentre NC-013 ragionava sul gruppo A.
  - Risposta: «Solo B, il gruppo del sorgente».
  - La tolleranza si scrive su 8,0 · 11,5 · 15,0 mA; il modello com'è e il tipico
    A restano come riferimento.
- **Il segnaposto, misurato contro il datasheet**: `LSK489X` ha I_DSS
  **4,842 mA**, V_GS(off) −1,49935 V (sul bordo). Le cifre del progetto fino a
  oggi descrivono un JFET quasi tipico del gruppo A, non il B.
- **Come entra `LSK489A` senza toccare niente di generato.**
  - Il nome del modello si **deriva**: `scripts/derive_jfet_variant.py` scrive
    `spice/preamp/derived/gain_block_flat_lsk489a.inc`, e il blocco **2i**
    rifiuta un derivato stantio.
  - Il `Vto` si **altera a runtime** con `altermod`, sul modello incluso intatto.
    Una JFET sonda misura la I_DSS in ogni variante.
  - Trappola nuova, **#29**: un `altermod` su un nome sbagliato non cambia
    niente, e ngspice esce 0.
  - `build_dossier.PART` conosce ora `LSK489A`: senza, il 2h cadeva per la
    ragione sbagliata.
- **I numeri**, da 2,59 a 15 mA, 27 °C:
  - I_D varia di 1,8 µA, gm dello 0,34 %, l'offset di 0,039 mV. Si muovono solo
    V_GS e v(SRC), di 1,84 V;
  - margine di saturazione a ±3,82 V di modo comune: da 4,26 a **2,42 V**;
  - E5 peggiore **4,308 µV**; l'1/f del JFET vale 0,116 µV in quadratura;
  - V1, blocco B a 0 dB: il modello del costruttore alza il minimo da 61,80° a
    **62,51°**, il gruppo B lo muove di ≤ 0,10°. Per la regola scritta prima,
    nessuna estensione.
- **Controlli fatti cadere**, guardando quale cade: 4 sabotaggi dei deck, 6 della
  derivazione, il 2h due volte. Un controllo ha trovato un commento di deck
  sbagliato di mille volte: 4 pV contro 4,2 nV.
- **Fuori**: nessun modello del costruttore del gruppo B; T8 del gruppo B non
  verificato; solo 27 °C.

Suite **10 passed / 0 failed**. **14 voci aperte, 2 bloccanti.** Prossimo:
**L37**.

### L13 — E4 sulle tre uscite e a manopola che gira (2026-09-15)

**Chiude NC-008, apre NC-033.** Report: `reports/2026-09-15-L13-e4-tre-uscite.md`.
Dati: `data/2026-09-15/L13/`. Nessun valore del circuito cambia, nessuna ADR.

- **La baseline, rifatta sui file.**
  - Era coperta solo la fissa 1 (L17, Re(Z) 53,13 Ω).
  - La fissa 2 non aveva dati.
  - La principale aveva una sola `RSRC`, niente trim né attenuatore.
- **Un difetto vecchio di una settimana, trovato leggendo i log.** La sezione Zout
  di `tb_zout_psrr_noise.cir` lasciava `VSRC` a 1 V AC.
  - La firma: al nodo del blocco `za1k` = 1,0355 / 1,4704 / 3,2621 Ω, cioè il
    guadagno del modo.
  - Rieseguito identico a L27 e corretto: al jack 1 kHz **57,945** Ω invece di
    58,76; al nodo **0,0386** Ω. PSRR e rumore identici byte per byte.
  - Il dossier pubblica le cifre vecchie: **NC-033**, lotto **L37**.
    Limitazione **#28**.
- **Il deck: nuovo, non esteso.** `tb_e4_uscite.cir` porta la catena intera in
  subckt: A, F1, F2, trim, attenuatore, B. Il flat ospita un blocco solo (#24), e
  il volume è una resistenza di sorgente vera, non una `RSRC`.
  - Matrice: 45 celle (trim × attenuatore × modo) × 3 uscite, un jack per volta
    a sorgente spenta.
  - Più il controllo positivo del guadagno in ogni cella.
- **Il verdetto su E4: conforme su tutte e tre le uscite.**
  - Re(Z) max 20 Hz–20 kHz **60,05 / 60,07 / 60,13 Ω** sulla principale e
    **53,13 Ω** sulle fisse, a 20 Hz, dove pesa lo scarico.
  - Dispersione su trim × attenuatore **≤ 1e-4 Ω**, contro la soglia di 1 Ω
    scritta come lettura del lotto.
  - FIX1 riproduce L17 a tutte le cifre.
- **Otto sabotaggi, 8 su 8 rifiutati come attesi**, guardando quale controllo
  cade.
  - Il primo «attenuatore scollegato» era stato rifiutato per la ragione
    sbagliata: segnale zero, `vdb(0)` → `Error`, celle vuote. Il controllo
    positivo non era mai stato esercitato.
  - Rifatto come «attenuatore scavalcato», cade sul controllo positivo soltanto.
    La sua tabella Zout è identica a quella vera.

Suite **9 passed / 0 failed**. **15 voci aperte, 2 bloccanti.** Prossimo:
**L20**.

### L34 — le decisioni del 2026-09-15 diventano requisiti (2026-09-15)

**Apre NC-032, aggiorna NC-028.** ADR nuove: **ADR-028**, **ADR-029**,
**ADR-030**. Report: `reports/2026-09-15-L34-decisioni-comandi-guadagno-telaio.md`.
Nessun file di `circuits/`, `spice/` o `scripts/` toccato; nessun numero
simulato.

Nasce da una sessione di domande dell'utente, in sola lettura. Le decisioni,
con le sue parole:
- **Uscite**: nessun jack, solo sbilanciate RCA. F3 ora lo dice, e «jack» nei
  documenti vuol dire la presa d'uscita (nota in `REQUIREMENTS.md`).
- **Comandi** (ADR-028, F10, F11): «il guadagno é rotativo a 3 posizioni sul
  frontale», «il mute ha un comando sul pannello (switch)», un LED «rosso per il
  mute», «i LED li colleghiamo con fili».
- **Guadagno** (ADR-030):
  - «vorrei evitare bump sulle casse, mettiamo il cambio gudagno condizionato
    al mute, prendiamo la strada B»;
  - «ovviamente servono i LED anche per il guadagno ora»;
  - ma «si serve una misura perchè altrimenti rischiamo di aggiungere relè e
    LED senza motivo, introducendo un bump per togliere un bump». Quindi **L36
    si fa solo se L29 lo giustifica**.
- **Trim**: resta bistabile, «seguo il tuo consiglio». La strada B si rivaluta
  dopo L36.
- **Telaio** (ADR-029, P8): «3U», profondità «come il technics», «il limite di
  ingombro e un paio di modelli come esempio». Risultato: L ≤ 450 · A ≤ 130 ·
  P ≤ 367 mm.

**Cosa è emerso, e non era scritto:**
- **Il comando del guadagno e quello del mute non esistono nel sorgente**: ci
  sono solo le net. E i LED del trim hanno footprint sulla scheda. Apre
  **NC-032**, la chiude **L35**.
- **Il cambio di guadagno a caldo** porta sul jack un gradino **calcolato** di
  ~6–114 mV, e nessuna misura esiste: `tb_switch_v2` guarda `v(OUT)` per 70 ms.
  Quindi **L29 si estende**.
- **Il LED del trim legge il relè gemello** K9/K10, non K7/K8: un guasto di uno
  solo dei due li fa divergere. Messo in «Domande aperte».
- **Corretta un'affermazione fatta in sessione**: la caduta di `VRELAY`
  inserisce il mute, quindi non distingue i bistabili dalla strada B. La
  differenza vera è il guasto di una sola bobina.

**L'ordine dei lotti cambia solo in coda**: L13 → L20 → L28 → **L29 esteso** →
**L36**, se giustificato → **L35** → **L30 e l'alimentatore**. Questi ultimi
ereditano il budget delle bobine e il mute combinato con l'interruttore. Il
contenitore si sceglie entro G2.

Suite **9 passed / 0 failed**. **15 voci aperte, 2 bloccanti.** Prossimo:
**L13**.

### L33 — le etichette di provenienza dell'LSK489 (2026-09-15)

**Chiude NC-031.** Report: `reports/2026-09-15-L33-provenienza-lsk489.md`. Dati:
`data/2026-09-15/L33/`. Nessun valore del circuito, nessun modello e nessuna ADR
toccati; nessun numero rieseguito; dossier non rigenerato.

- **Il conto rifatto non era quello di NC-031** (`esplorazione/conta.py`):
  - **15 deck**, non 13: anche `tb_blockA_carichi.cir:40` e
    `tb_mute_corto.cir:54` («tutto tranne LS352 e LSK489 e' segnaposto»);
  - **5 README datati espliciti**, non 3 (anche L17 e `2026-09-10`), più **2
    impliciti** (`2026-09-13`, `2026-09-14`);
  - fuori conto e non toccata, perché datata:
    `L16/esplorazione/deck/tb_blockA_carichi_trim.cir`.
- **Il guardiano c'è: blocco 2h**, `scripts/check_deck_provenance.py`.
  - Il criterio è la `provenance()` di `build_dossier.py`, **importata**, non
    riscritta. Le affermazioni le legge dai commenti, nelle forme trovate.
  - **Fatto cadere prima di correggere**: sui deck di `main` rc 1,
    **esattamente 15**; suite 8 / 1 sul 2h. Sui 16 deck di `6748fbc`, 14.
  - **11 sabotaggi su 11**, fra cui una frase negata e una vera, che non
    devono scattare.
  - **Cosa non vede**: un modo nuovo di dire «vendor». È una rete tessuta sulle
    frasi trovate, non un lettore.
- **Solo commenti, provato**: `solo_commenti.py` contro i deck di `main`. 15
  cambiati, ogni riga `*`, righe di codice identiche. Caduto su `VPP … DC 16`.
- **README** annotati in coda, testo intatto: il diff ha solo righe aggiunte.
- **Il dossier diceva già il vero**: 16 righe di provenienza su 16, «del
  costruttore: LS352», LSK489 fra i segnaposto.
- **Trovato**: il README del `2026-09-10` dice anche «il contributo del JFET qui
  è conservativo» (NC-013). Non si applica, perché il modello d'angolo non era
  simulato: annotato, non riscritto.
- **Precisato**: «solo l'LSK489 ha rumore 1/f», in NC-004 e qui sotto, è vero di
  `models/`, non delle simulazioni.
- **Il mandato di L33 contava male anche i lotti**: L13 e L20 sono «da fare»
  e non aspettano nessuno, ma non comparivano fra gli aperti.
- Suite **9 passed / 0 failed**. **14 voci aperte, 2 bloccanti.** Prossimo:
  **L13**.

### L31 — i vettori di rumore di `tb_noise_vectors.cir` (2026-09-15)

**Chiude NC-030.** Report: `reports/2026-09-15-L31-vettori-di-rumore.md`. Dati:
`data/2026-09-15/L31/`. Nessun valore del circuito toccato, dossier non
rigenerato.

- **Baseline**: il deck di `main` rieseguito dà una riga
  `Error: no such vector onoise_q123`, rc 0, JSON a 0 righe.
- **Prima il guardiano.** `check_deck_refs.py` controlla ogni
  `onoise_<x>`/`inoise_<x>` fuori da commenti e virgolette: circuito
  (`spectrum`, `total`), `let`, dispositivo, o dispositivo più sotto-sorgente.
  - I suffissi sono letti con un **deck sonda**: nel log i nomi sono troncati a
    15 caratteri (`d102_ids` è `d102_idsw`).
  - Sul deck di allora **rc 1, esattamente 4 MISSING**; `run_tests.sh` 7 / 1 sul
    2g.
  - Nessun falso allarme sugli altri 16 deck, né sui 16 di `6748fbc`
    (pre-L27).
  - **13 sabotaggi su 13** come attesi.
- **Trovato: tre nomi vivi erano già sbagliati** (#22, secondo modo). La
  mappa per **nodi** dall'include di L4 a quello di oggi dà:
  - q123 → Q121B, q122 → Q121A;
  - r121 → R120, r120 → R119, r138 → R136;
  - jq110/jq111 → JQ110A/B.

  `onoise_q122`, `r120` e `r138` avrebbero scritto il VAS, l'altra
  degenerazione e R_g. Il suggerimento «VAS Q122» del mandato portava lì.
- **I dati**: 0 righe `Error`, CSV di 2 righe. A 1 kHz, **pavimento senza
  1/f**:
  - quadratura dei 42 totali 8,605323e-09 = `onoise_spectrum`;
  - gli 8 scritti sono i primi 8, 85,21 % della potenza (R_f da sola 33,51 %);
  - spettro identico a `tb_noise_breakdown` B di L27.
- **Il riscontro fatto cadere** sul deck di `main`: 7 colonne su 10 rifiutate.
  Coi nomi vecchi, `onoise_r138` avrebbe scritto 1,09e-12 invece di 4,98e-09.
- **Una premessa del mandato non era vera**: `tb_noise_breakdown.cir` non stampa
  la ripartizione per dispositivo (log: `No. of Data Rows : 2`). Anche «Perché
  minore» di NC-030 lo dava per fatto.
- **Osservato, fuori lotto**: `testbenches/01_op.cir` ha un `wrdata` con
  percorso assoluto, quindi il 2b lanciato da un worktree scrive e legge in
  `/Users/roberto/EDA/results/`.
- **15 voci aperte, 2 bloccanti.** Prossimo: **L33**.

### L32b — gli schemi del dossier si vedono (2026-09-15)

Nessun numero toccato. Una segnalazione dell'utente dopo la chiusura di L32:
«nel nuovo dossier le immagini dello schema a blocchi e dello schema di guadagno
mancano».

- **La causa.**
  - `index.html` collegava i due schemi come `../schematic/…`, fuori dalla
    propria cartella. Le figure `fig_*.svg`, che stanno accanto alla pagina, si
    vedevano.
  - I due SVG sono XML valido, con `xmlns`, e si renderizzano da soli: il
    visualizzatore dell'utente non serve file fuori dalla cartella della pagina.
  - Il difetto c'era anche prima di L32. Non si notava perché l'Artifact del
    2026-09-09 era stato pubblicato con `--standalone`, che incorpora gli SVG.
- **Il rimedio.**
  - `build_dossier.py` copia `gain_block.svg` e `preamp_blocks.svg` accanto a
    `index.html` e li collega da lì.
  - Rifiuta se uno dei due manca, prima di scrivere qualsiasi file.
  - Con `--standalone` li incorpora ancora da `docs/preamp/schematic/`.
- **È un'ipotesi sul visualizzatore**, confermata solo dal sintomo: le figure
  accanto alla pagina si vedono. Nessun browser headless per provarla qui.
- L'Artifact del dossier è ancora quello del **2026-09-09**.

### L32 — il dossier rigenerato sui dati di L27 e L16 (2026-09-15)

**Chiude la metà «dossier» di NC-009** (criterio 2), apre **NC-031**. Report:
`reports/2026-09-15-L32-dossier.md`. Nessun dato nuovo: il dossier impagina
`data/2026-09-14/L27/dopo/` e `data/2026-09-14/L16/dopo/`.

- **Il builder riscritto.**
  - Legge solo le due radici vigenti; un percorso del 2026-09-09 lo fa rifiutare.
  - Tre modi ovunque, 15 sezioni; nuove quelle su trim ed E3, E5, V2, V3 e P7.
  - Le tabelle `echo` si confrontano **riga per riga** con le `print` o le `meas`
    del log; una cella vuota o una riga mancante è un rifiuto.
  - La cifra di NC-009 si confronta con `headroom_nc009.py`, lanciato sugli
    stessi CSV.
  - La **provenienza dei modelli** è letta dagli `.include` di ogni deck, non
    dichiarata.
- **V1 come la vuole ADR-024**: minimo della spazzata al jack, blocco A col
  cablaggio ≤ 1 nF, KPI riferita a 60°. Figura nuova: margine contro capacità
  del cavo.
  - Blocco B 61,803 / 69,773 / 102,980°, agli spigoli 61,422 / 68,644°;
  - blocco A col trim 63,495°;
  - **il minimo del prodotto è il buffer delle fisse, 61,632°**, non il blocco B.
- **NC-009**: **M1 +6,58 dB** (+10 dB, trim −6 dB), +0,58 dB a trim 0; M2 e M3
  solo etichettate.
- **Le altre cifre**:
  - E3 121,068 kΩ con 68 pF, identica nelle tre posizioni;
  - E5 della catena ≤ 4,918 µV, pavimento senza 1/f;
  - P7: Tj massima 81,8 °C, 0 righe ascoltabili su 398 fuori classe A;
  - V2: 10 finestre su 10 nell'inviluppo del +10 dB.
- **Verificato da fuori**: `v1_trim.py`, `toll_L16.py` e `headroom_nc009.py`
  rieseguiti danno le stesse cifre che la pagina stampa.
- **Nove controlli fatti fallire** su copie di scratch: valore alterato, cella
  vuota, riga tolta, `att1k` alterato, metrica M1 alterata, spettro scalato del
  5 %, percorso del 2026-09-09, include dei segnaposto tolto. Tutti rc 1, nessun
  file scritto; il caso intatto passa.
  - **Il primo sabotaggio di M1 non ha fatto cadere niente**, e non per un buco
    del controllo: alterava il bordo inferiore della finestra, e M1 prende il
    bordo di modulo minore, che in tutti e tre i modi è il superiore. Rifatto sul
    bordo superiore: rifiutato.
- **Trovato, NC-031** (minore). I README di L12, L27 e L16 e tredici deck dicono
  che l'LSK489 simulato è quello del costruttore. I deck istanziano invece
  `LSK489X`, segnaposto con `KF=0`, e nessuno include `models/jfet/lsk489.lib`.
  - Nei dati di oggi l'unico modello del costruttore è l'**LS352**;
  - **nessun dispositivo simulato ha rumore 1/f**.
  - Lotto **L33**.
- **Ambiente**: a metà sessione `/usr/bin/python3` e `git` hanno cominciato a
  uscire 69 per la licenza Xcode non accettata. Il builder, che usa solo la
  stdlib, è stato eseguito col Python del venv.
- **16 voci aperte, 2 bloccanti.** Prossimo: **L31**.

### L16 — il trim entra nel progetto (2026-09-14)

**Chiude NC-005 e NC-023**; NC-009 resta aperta per il dossier (L32) e il
pannello. Report: `reports/2026-09-14-L16-trim.md`. Dati:
`data/2026-09-14/L16/`.

- **Tre decisioni dell'utente**, parole esatte in NC-023:
  - a relè;
  - **un trim comune con LED** invece di uno per ingresso;
  - dopo le prime misure, **il trim solo sull'uscita variabile**, con le fisse
    come copia fedele della sorgente.
- **Perché non all'ingresso del blocco A**: nessun partitore rispetta E3 ed E5
  insieme. A +10 dB, attenuatore al massimo, trim −6 dB fa **10,12 µV** con la
  scala più piccola consentita, contro 9,90 µV.
- **ADR-027**: trim fra il blocco A e l'attenuatore, **845 / 464 / 464 Ω**,
  −6,003 / −11,939 dB.
  - Relè bistabili **G6KU-2F-Y**: K7 e K8 sul segnale (reset = 0 dB), K9 e K10
    per i LED.
  - **K6** sul comando del mute, due NC in serie, come permissivo.
  - Comando rotativo SW1. Stato all'accensione = posizione del comando.
- **Il relè**: pinout letto su tre gambe e due revisioni del datasheet. T8 sul
  catalogo Omron **K106-E1-16** (03/2026), congelato dall'utente in
  `vendor/relays/omron/G6K-K106-E1-16/`. **La pagina degli avvisi di fine
  produzione non è stata letta.**
- **Misure, tutte conformi**:
  - **E3**: 121,1 kΩ con 68 pF, identica nelle tre posizioni;
  - **E5**: ≤ 4,92 µV;
  - **V1 blocco B** con la sorgente 2,611 k: 0 dB **61,80°**, agli spigoli
    **61,42°**;
  - **V1 blocco A**: 63,50°;
  - classe A del blocco A col partitore: 13,28 mA.
- **NC-009, una cifra**: metrica **M1**, **+6,58 dB** a +10 dB col trim a
  −6 dB; +0,58 dB a 0 dB.
- **Guardiani**:
  - il 2e prova l'interblocco sulla netlist ed è stato fatto fallire da sei
    varianti generate;
  - il 2f asserisce le attenuazioni ed è caduto sulla scala fuori finestra.
- **Budget bobine**: 126,6 mA a 5 V in mute e fuori. Vincolo per
  `psu-engineer`: mute rilasciato ≥ 13 ms dopo `VRELAY`.
- **15 voci aperte, 2 bloccanti.** Prossimo: **L32**.

### Dopo L27 — il trim: a relè, per ingresso, bistabili se possibile (2026-09-14)

Nessun lotto: l'utente ha chiesto di spiegare il primo punto del mandato di L16
(F2 contro F8, «per ingresso», trim dopo il selettore) e ha deciso.

- **Le parole dell'utente**: «1. rele 2. trim per ingresso (meglio se possibile
  coi bistabili)».
- **Il trim è a relè.** L'interlock elettrico di ADR-019 resta. F2 («a
  ponticello») si allinea a relè **senza ADR**: F8 escludeva già il ponticello,
  quindi l'insieme dei progetti conformi non cambia (criterio di L15).
- **Un trim per ingresso**, come ADR-011: niente trim unico dopo il selettore,
  che avrebbe voluto una ADR nuova. Una disposizione plausibile fa 8 relè,
  ancora da contare davvero.
- **Bistabili, se possibile.** Spiegando è emerso un punto che il mandato non
  diceva:
  - F8 vuole anche che **il valore del trim resti all'uscita dal mute**;
  - monostabili alimentati attraverso il contatto del mute lo perderebbero;
  - coi bistabili (G6KU-2F-Y, nel datasheet in `vendor/`) il mute abilita solo
    gli impulsi, e il valore resta senza corrente.
  È un ragionamento, non una simulazione.
- **Dove sta scritto**: `NEXT-SESSION.md` (mandato di L16) e la «Decisione
  dell'utente» di NC-023. **L16 registra la ADR del trim** (ADR-027) come primo
  passo.

### Dopo L27 — il dossier diventa un lotto (2026-09-14)

Nessun lotto: una domanda dell'utente, «ha senso rifare il dossier?».

- **Lo stato.** `build_dossier.py` legge ancora `data/2026-09-09` (THAT320, C_f
  22 pF, due guadagni) e conosce solo `0db`/`10db`. Schema a blocchi e disegno
  del blocco invece sono aggiornati a L27.
- **La decisione dell'utente.** Il dossier si rifà in un **lotto S subito dopo
  L16**, non adesso: L16 cambia la stabilità del blocco A e la cifra di headroom
  di NC-009. Diventa **L32**.
- **Nessun avviso di obsolescenza** nel dossier nel frattempo: «lo leggo solo
  io».
- **Cosa cambia per L16.** Sceglie la cifra di margine di NC-009 e la sua
  metrica; la pubblicazione nel dossier è di L32.

### L27 — il terzo livello di guadagno (2026-09-14)

**Chiude NC-022**, apre **NC-030**. Report:
`reports/2026-09-14-L27-terzo-livello-di-guadagno.md`. Dati:
`data/2026-09-14/L27/`.

- **La rete (ADR-026)**: due rami di R_g **in parallelo** verso massa.
  - **3,57 kΩ su K1** → +3,047 dB;
  - **866 Ω su K5**, chiuso solo con K1 → +9,972 dB. Con 698 Ω era +9,963.
  - In parallelo **nessuno stato dei contatti supera il +10 dB**; due rami
    esclusivi, con un contatto saldato, darebbero +11,03 dB.
- **I relè**: K5 è un secondo G6K-2F-Y. Bobine, cinque eccitate: **105,5 mA a
  5 V**, 45,5 a 12 V, 23,0 a 24 V. `VRELAY` non è decisa → `psu-engineer`.
- **Baseline verificata**: `tb_loop` di `main` byte-identico a L12.
- **V1 al minimo della spazzata**, carichi 100 k e 10 k:

  | Blocco B | Minimo | Agli spigoli |
  |---|---|---|
  | 0 dB | **61,83°** (era 61,21°) | 61,45° |
  | +3 dB | **69,79°** (griglia fitta) | 68,67° |
  | +10 dB | 102,99° | — |

  Nessun rimedio serve: a 0 dB i due rami appesi a FB pesano meno di uno.
- **Il resto a +3 dB**, tutto conforme:
  - V2 dentro l'inviluppo del +10 dB, con due relè che rimbalzano;
  - P7: MJE peggiore 339,6 mW, Tj 81,2 °C;
  - 0 righe ascoltabili fuori dalla classe A;
  - E5 2,01 µV; PSRR+ a 10 kHz 36,73 dB.
- **Una trappola nuova, limitazione #27**: un nodo di contatto non terminato non
  dà errore. Il deck `tb_ac` di `main` sull'include nuovo stampava **+3,04 dB
  nel modo che chiama 10db**, rc 0.
  - Il blocco **2g** ora rifiuta nodi pendenti e porte mancanti;
  - fatto fallire sui 16 deck di `main`, e senza falsi allarmi sullo stato
    pre-L27.
- **Guardiani estesi e fatti fallire**:
  - 2e con K5 su NC;
  - 2f con +3 dB fuori finestra e con R242 su K1.
- **Netlist**: 360 componenti, partizione dei nodi identica a meno di K5, R242
  e R442. Disegno del blocco a 45 dispositivi.
- **Trovato, NC-030** (minore): `tb_noise_vectors.cir` non scrive dati da
  tempo, per quattro nomi di vettore morti. Lotto **L31**.
- **17 voci aperte, 2 bloccanti.** Prossimo: **L16**.

### L12 — ogni istanza del blocco sopra i 60° (2026-09-14)

**Chiude NC-002 e NC-021** (bloccanti). Report:
`reports/2026-09-14-L12-margine-di-fase.md`. Dati: `data/2026-09-14/L12/`.

- **La domanda all'utente, prima di progettare**: dove si applica la sonda da
  4,7 nF. Presentati i numeri di nodo e jack. L'utente ha chiesto cosa fosse
  («per me é il cavo di collegamento tra il pre e il finale oppure tra il pre e
  gli ampli cuffia») e ha deciso: «ogni cavo fino a 4,7 nF, blocco A con
  capacità realistica». Diventa **ADR-024**.
- **Il caso peggiore vero era peggiore.** Al jack il margine non è monotono, e
  con l'attenuatore a metà corsa — cella di V1 mai misurata — il blocco B a
  0 dB stava a **54,97°** (2,7 nF), non 56,46°. Il blocco A col cablaggio
  ≤ 1 nF e i buffer al jack passavano già.
- **Il rimedio, scelto coi numeri fra quattro strade** (**ADR-025**): **C137
  da 22 a 330 pF C0G**, in tutte le otto istanze.
  - Blocco B **61,21°**, blocco A **63,36°**, buffer **61,63°**.
  - Agli spigoli di tolleranza: 60,73 / 62,69 / 61,16°.
- **Scartati con misura:**
  - più Miller: va in slew a 20 kHz fondo scala e toglie 6,5 dB di PSRR;
  - Miller più 68 Ω: ancora in slew, E4 a 82 Ω;
  - C_f più 56 Ω: più guardia, ma tre reti d'uscita e i loro deck.
- **Il costo**: banda a +10 dB da 333 a 183 kHz, −0,053 dB a 20 kHz. Nessun
  requisito lo vieta.
- **Non regressione:**
  - punto di lavoro 79 valori su 79 identici;
  - netlist: 357 componenti, 8 valori cambiati, connettività identica;
  - `tb_mute_corto`: 0 righe con lo stato di classe A cambiato, P7 invariata;
  - E4, E5, PSRR, V2 e V3 invariati.
- **I deck:**
  - `tb_loop.cir`: sonda al jack e sul nodo, sorgenti dell'attenuatore. Fatto
    fallire;
  - `tb_loop_blockA.cir`: sorgente phono;
  - `tb_loop_bufferfissa.cir`: griglia fitta. Il minimo del buffer stava fra i
    punti: 61,85° sulla griglia rada contro 61,63°.
- **Una trappola nuova**: `meas tran` su una `tran` con `tstart` fallisce in
  silenzio → limitazione **#26**.
- **17 voci aperte, 2 bloccanti** (NC-004, NC-017). Prossimo: **L27**.

### L17 — un buffer per ogni uscita fissa (2026-09-14)

**Chiude NC-010** (bloccante). Report:
`reports/2026-09-14-L17-buffer-uscite-fisse.md`. Dati: `data/2026-09-14/L17/`.

- **La decisione dell'utente**, che ha corretto la domanda. Fra «ADR che
  estende l'eccezione» e «buffer», ha indicato il punto mancato: un corto o un
  apparecchio spento su una fissa toglieva la classe A a **tutto l'ascolto
  primario**, e questo non è accettabile; un blocco che nessuno ascolta può
  uscirne, se la termica regge. Diventa **ADR-023**: la classe A si giudica
  sui **percorsi ascoltabili**.
- **La topologia.** Un `GAINBLOCK` a guadagno unitario per ogni fissa, R_IN
  non montata. La netlist passa da 197 a 357 componenti. ADR-008 superata;
  ADR-006 e ADR-021 precisate; T1, T3, T5, F3, V1 e la Nota su P7
  aggiornate.
- **Le misure**, cinque deck:
  - `tb_blockA_carichi`: blocco A a **14,356 mA** e l'altra fissa a
    **14,509 mA** da 470 kΩ a 0,01 Ω. Lo stesso deck col cablaggio vecchio
    ritrova la classe B;
  - `tb_mute_corto` a quattro blocchi: **0 righe ascoltabili fuori dalla
    classe A** su 294. P7 conforme: buffer 298,1 mW, più caldo Q125 a
    96,4 °C. L'apparecchio spento a 10 Ω scalda meno del corto;
  - `tb_loop_blockA`, ai valori veri: **40,96°** a 4,7 nF sul nodo. Il
    controllo col carico canonico dà 41,02°;
  - `tb_loop_bufferfissa`: **40,98°** sul nodo, **62,27°** al jack;
  - `tb_uscite_fisse`: E4, Re(Z) ≤ 53,1 Ω; E5, 1,67 µV.
- **Guardiani fatti fallire:**
  - 2e su una netlist sabotata;
  - la nuova asserzione ADR-023 del blocco 2f sulla netlist di `main`.
- **Due errori di deck trovati prima di registrare numeri**, ora limitazioni
  #24 e #25:
  - un nodo `SRC` che collideva con `_flat.inc`, e dava 106° finti;
  - una tabella `echo` sovrascritta dalla conversione di un `wrdata` omonimo.
- **Trovato: NC-029** (maggiore). A riposo la scheda audio dissipa **6,45 W**
  (0,806 W per blocco), contro i 3-4 W che P5 prevede per l'apparecchio
  intero. Lotto **L30**.
- **19 voci aperte, 4 bloccanti.** Prossimo: **L12**, che parte dalla domanda
  su dove si applica la sonda da 4,7 nF.

### Dopo L11 — dove mettere il contatto di mute (2026-09-14)

Nessun lotto: una domanda dell'utente su NC-028, «perché non mettere a massa
prima del condensatore?», studiata in simulazioni di scratch. I numeri sono in
NC-028.

- **Toglie il gradino della musica**: da −3,6 V a −72 mV, rilasciando sul
  picco.
- **Ne mette uno pari all'offset in continua del blocco.** A mute inserito il
  condensatore non segue più l'uscita e si scarica sul carico: +104 mV
  all'inserzione e −154 mV al rilascio dopo un mute di 2 s a +10 dB, **anche
  all'accensione**, che oggi è pulita a pV.
- **Il contatto su entrambi i lati non aiuta sull'offset.**
- **L'offset** vale −14/−45 mV coi modelli vendor (0/+10 dB), più fino a
  20 mV × 3,15 di dispersione LSK489.
- **Stima d'udibilità**, calcolata: 76-94 dB SPL di picco a 1 m sulle Heresy,
  per 14-104 mV. Il volume non la riduce.
- **Quindi non è una vittoria netta**: è un rimedio che vale solo insieme a un
  offset basso, o a un rilascio lento. **L29** confronta le strade con un
  deck versionato.

### L11 — mute tenuto e corto sulle uscite (2026-09-14)

**Chiude NC-001** (bloccante). Report:
`reports/2026-09-14-L11-mute-e-corto.md`.

- **Le decisioni registrate.** **ADR-021**: mute a tempo indefinito; ogni
  uscita regge un corto, requisito come esito (**P7**); classe B ammessa solo
  lì. **ADR-022**: operazionali e microcontrollore fuori dal percorso del
  segnale, con una definizione verificabile di percorso e tre condizioni.
  Aggiornati F6, F7 e T1, e il campo `Stato:` di ADR-003, ADR-009 e ADR-012.
  L'indice delle ADR aveva perso le righe 017-019: rimesse.
- **Due numeri che il repo non aveva, chiesti all'utente:** **60 °C** di
  ambiente nel telaio, **Tj ≤ 125 °C**. Le RθJA vengono dai datasheet in
  `vendor/`.
- **La baseline.** `tb_mute_corto.cir` è un canale intero, con cinque casi,
  due modalità, due frequenze, ampiezza e manopola spazzate. **Conforme senza
  protezione e senza dissipatore:**
  - MJE peggiore 484 mW, Tj 90,2 °C, contro 1,04 W ammessi;
  - dispositivo più caldo: Q125, Tj 96,5 °C.
- **Il caso peggiore non era quello di G0.** Il mute mette a massa **entrambe**
  le fisse, e il blocco A vede 47 ∥ 47 Ω. Le cifre di G0 (THAT320) sono
  riprodotte entro lo 0,1 % nella loro configurazione.
- **Provato su tre gambe:**
  - il deck fatto fallire togliendo i contatti di mute (0 righe su 36
    diverse);
  - la potenza ricalcolata da tensioni e correnti (≤ 0,23 %);
  - il riposo a 14,557 mA come `tb_op-LS352`.
- **Consegna tre vincoli di distinta:** la 47 Ω dell'uscita principale
  dissipa **1,10 W** in un corto a +10 dB e va dimensionata di conseguenza (P7).
- **Trovato: NC-028** (maggiore). Al rilascio del mute con segnale presente il
  jack riceve un gradino, **5,37 V** a +10 dB, che decade in 0,32 s. È il
  condensatore caricato durante il mute. V2 non ha soglia, quindi serve una
  decisione dell'utente. Lotto **L29**.
- **Sensibilità**: coi modelli vendor il riposo sale a 20,1 mA (R128 è tarata
  sui segnaposto), e il verdetto non cambia.
- **«Classe A garantita» corretta** in `gain_block.py` (AST identico) e su
  `gain_block.svg`.
- **NC-010 aggiornata:** `tb_blockA_carichi` rieseguito, identico. Il corto su
  una fissa è conforme a P7; resta l'apparecchio **spento**, che è T1 → L17.
- **19 voci aperte, 5 bloccanti.**

### Dopo L18 — protezione neutra sulla tecnica, e operazionali e microcontrollore fuori dal percorso (2026-09-13)

Nessun lotto: altre due decisioni dell'utente, messe nell'handoff.

- **La protezione dal corto non prescrive la tecnica.** L'utente non voleva
  che «venisse esclusa la possibilità di staccare o mutare le uscite in
  maniera attiva». Il mandato di prima diceva «limitare la corrente su ogni
  via», e chiedeva una verifica solo a regime.
- **Il requisito diventa un risultato.** Con un corto su una qualsiasi uscita,
  a tempo indefinito e con segnale presente, nessun dispositivo esce dai propri
  limiti termici e SOA. Il vincolo vale **anche nel transitorio prima
  dell'intervento**.
- **Le tecniche ammesse**, da scegliere coi numeri: limitazione di corrente,
  distacco attivo, mute attivo.
- **Operazionali e microcontrollore** sono esclusi dal percorso del segnale ma
  **ammessi nel circuito** (l'utente: «si procedi come hai detto»). Diventa
  **ADR-022**, da registrare in L11:
  - supera la clausola «nessun microcontrollore in tutto il progetto» di
    ADR-009 e aggiorna F7;
  - dà a T1 una definizione verificabile di percorso del segnale;
  - pone tre condizioni al microcontrollore: stato sicuro senza firmware,
    protezione dal corto non affidata solo al firmware, budget di rumore
    digitale misurato come ADR-020.
- **Tre vincoli scritti nel mandato**, perché non si scoprano dopo:
  - il mute di oggi è in derivazione e **non protegge** dal corto;
  - un distacco in serie **ridefinisce lo stato sicuro** dei relè;
  - ricollegamento automatico o blocco dopo il corto è una **scelta
    dell'utente**.

### Dopo L18 — la protezione dal corto sulle uscite (2026-09-13)

Nessun lotto: un requisito nuovo dell'utente, messo nell'handoff.

- **Il requisito.** «Non possiamo essere certi che le uscite non vengano messe
  in corto»: ciascuna delle tre uscite deve reggere un corto al connettore **a
  tempo indefinito**, con segnale presente, senza mettere a rischio la termica.
- **Dove si registra.** Nella stessa **ADR-021** del mute, al primo passo di
  L11. L'utente l'ha confermato («OK procedi»).
- **Perché insieme al mute.** Il contatto NC del mute mette a massa lo stesso
  nodo del jack su cui arriva un corto esterno: è la stessa fisica, già
  annotata fra NC-001 e NC-010. Un solo criterio termico a regime copre
  entrambi.
- **Cosa cambia per L11.** Il deck misura anche il corto su ciascuna uscita, e
  una resistenza in serie al contatto del mute non basta più come rimedio.
- **Cosa cambia per L17.** Il vincolo di impedenza minima a valle non chiude
  più NC-010, e L17 progetta contro il criterio di ADR-021.

### Dopo L18 — il mandato di L11 corretto dall'utente (2026-09-13)

Nessun lotto: si corregge l'handoff scritto alla chiusura di L18.

- **Cosa diceva.** Il mandato di L11 offriva come seconda strada un'ADR che
  accettasse la classe B «per la durata del temporizzatore».
- **Perché era sbagliato.** L'ipotesi veniva da ADR-012 («qualche secondo»),
  ma **contraddiceva già ADR-019**: il mute è il permissivo del trim, e chi lo
  regola lo tiene inserito quanto vuole. L18 non l'aveva visto.
- **La decisione dell'utente.** Mute **tenibile a tempo indefinito**; **classe
  B ammessa** a mute inserito; **termica sicura a regime**, a costo di cambiare
  la topologia.
- **Dove è scritta.** `NEXT-SESSION.md` e la «Decisione dell'utente» di NC-001,
  per ora. **L11 la registra per prima come ADR-021.**

### L18 — il vincolo PSRR scritto dove verrà letto (2026-09-13)

Nessun valore del circuito toccato. Un commento di `gain_block.py` è
aggiornato, con AST identico.

- **Le cifre rilette dalla topologia di oggi.** `tb_zout_psrr_noise.cir`
  rieseguito:
  - rail +: si muove di ≤ 0,107 dB (a 10 kHz, +10 dB: **29,82 dB**);
  - rail −: **peggiora fino a 4,74 dB** (a 100 Hz, da 79,02 a 74,37).
  - Il deck ha letto l'LS352: il rumore di caso peggiore è 4,231 µV. Dati in
    `data/2026-09-13/`.
- **Qualcuno aveva già deciso, a mezza voce.** `gain_block.py` e il report di
  Fase 2 davano a `psu-engineer` «≤ 1 mV pk a 100 Hz, cioè < 1 µV in uscita».
  Ora è **ADR-020**: **1 µV RMS** in uscita per ripple e rumore dei due rail,
  20 Hz–20 kHz, col PSRR minimo fra le modalità.
- **Sostanziale, quindi ADR** (criterio di L15): 5 µV di rumore più 5 µV di
  ripple passavano E5, con la quota no. La tabella per tono sta nella «Nota su
  E5 — la quota del ripple d'alimentazione»: sul rail + a 10 kHz il limite è
  ≤ 31,0 µV RMS.
- **Il verbo è stato fatto fallire.** Il controllo ha fermato anche un caso di
  prova mal dimensionato, che passava in entrambe le modalità.
- **NC-011 resta aperta** per rimedio e verifica, che sono
  dell'alimentatore. **19 voci, 6 bloccanti.**
- **Visto e non toccato.** Il dossier legge ancora `data/2026-09-09`, cioè il
  PSRR del THAT320. `gain_block_draw.py:468` scrive «59,5 dB a 1 kHz», oggi
  59,57.

### L15 — il vincolo su E3 scritto accanto a E3 (2026-09-13)

Nessun numero del circuito, nessun codice, nessuna misura.

- **Il vincolo** sta in `REQUIREMENTS.md`, «Nota su E3»: Zin al connettore,
  blocco A collegato, **≥ 100 kΩ in ciascuna delle tre posizioni del trim**,
  decisa sul minimo di |Zin| in 20 Hz–20 kHz.
- **Non in ADR-011.** Delle quattro aggiunte in coda alle ADR, due (ADR-007,
  ADR-008) **superano un valore** senza ADR nuova, e sono tutte del
  2026-09-08. Il precedente dopo le regole è ADR-019, una ADR nuova.
- **Nessuna ADR**: la nota non cambia l'insieme dei progetti conformi. E3 nasce
  dal condensatore del phono, che vede il connettore, trim compreso.
- **NC-005 resta aperta** per la misura (L16). **19 voci, 6 bloccanti.**
- Trovato: F2 dice «ponticello», F8 presuppone **relè** → a L16. Una frase di
  NC-009 diceva il contrario del vero, corretta. E **R1 + R2 = 100 kΩ non
  basta**: con `R_IN` in parallelo, 50 k / 50 k fa 97,62 kΩ.

### L14 — le tre correzioni di testo (2026-09-13)

Nessun numero del circuito toccato.

- **NC-006** — i commenti del cascode in `gain_block.py` citano ora
  `v(ncasc) = 9.887 V` e i drain a 9,21 V, dal log della topologia di
  **oggi** (`data/2026-09-10/tb_op-LS352.log`), non da quello col THAT320 che
  la voce citava.
  - `tb_op` rieseguito: 81 valori su 81 identici.
  - L'AST del file è identico a HEAD; il controllo è stato fatto fallire.
- **NC-007** — il dossier distingue lo scarto ADR-014 **riferito a 1 kHz**,
  che è la claim (4,35·10⁻⁵ dB a 0 dB, 1,37·10⁻⁴ a +10 dB; il KPI cita il
  peggiore), dallo scarto **assoluto** (−0,0217 dB a ogni frequenza), che è il
  partitore con la Zin.
- **NC-003** — il KPI dice «blocco B, peggiore dei 4 casi pubblicati».
- Tutto verificato sull'`index.html` generato. **19 voci, 6 bloccanti.**

### L10 — il simbolo dell'LSK489 (2026-09-13)

- L'LSK489 è **una** Part a due unità: simbolo in
  `library/preamp.kicad_sym`, pinout **letto** dal datasheet congelato
  (pag. 1, SOIC-A): 1=S1 2=D1 3=SS 4=G1 5=S2 6=D2 7=SS 8=G2.
- Sulla netlist i componenti su SOIC-8 scendono da **3 a 2**
  (`preamp_audio.net`: 12 → 8).
- **La trappola della lettura:** i JFET dentro il package sono disegnati
  **ruotati**, e letti come JFET verticali sembrano scambiare D e G.
- **SS** è disegnato ma mai definito dal datasheet dell'LSK489. L'unica
  definizione («substrate, leave floating») è stampata per l'LSK389 →
  **NC-027** (minore). I pin restano scollegati come prima.
- Mappa ricavata dai nodi; `.inc` rinominato **identico** al nuovo; `tb_op`
  81 valori su 81 identici.
- **Due deck rotti da L22 in silenzio**, emersi facendo la baseline:
  - il controfattuale di V2 apriva un `r138` inesistente (ngspice esce 0;
    anello «aperto» a −0,0522 V → riparato, −13,773 V);
  - lo sweep del bias spazzava l'altro ramo (I_q 5,2 mA → riparato,
    14,714 mA, uguale a `tb_op`).
- **NC-026 chiusa:** il disegno a blocchi gira e lo esegue il nuovo blocco
  **2f**. Il blocco **2g** (`check_deck_refs.py`) ferma i nomi morti nei deck,
  non quelli vivi sbagliati (#22). Entrambi i blocchi fatti fallire prima.
- Scoperto che SKiDL nomina le net fuse in modo non riproducibile (#23).
- Suite **8 passed / 0 failed**. **22 voci, 6 bloccanti.**

### L21 — il polo 2 del relè (2026-09-11)

- Il polo 2 del G6K-2F-Y era cablato con **NO e NC invertiti**. Sul **canale
  destro** il mute falliva nel verso sbagliato: all'accensione quel canale
  **non veniva messo a massa** e il transitorio passava, sul ramo che ADR-012
  protegge.
- Riga 79 corretta, netlist rigenerata. Il **diff normalizzato tocca
  esattamente quattro numeri di pin**: `GND` porta ora K1 4+5 e K2/K3/K4 2+7.
- Pinout **riletto alla fonte** e non ereditato da L8, su tre gambe
  concordi: nel PDF l'armatura passa a **0,44 pt** dal proprio NC e a 3,39 dal
  NO su *entrambi* i poli; nel simbolo KiCad ha la **stessa x esatta** del NC.
- **La trappola, ora scritta nel codice:** entrambe le armature riposano sul
  pad immediatamente **a sinistra** del proprio COM, ma le due righe sono
  numerate in **versi opposti** — «NO = COM+1» vale per il polo 1 e non per il
  polo 2.
- **A chiudere la voce è il guardiano, non la correzione.**
  `scripts/check_relay_safe_state.py` asserisce l'**intento delle ADR** sulla
  netlist generata (mute diseccitato ⇒ uscita a massa; guadagno ⇒ `R_g`
  flottante) e gira nel blocco **2e**: la suite passa da 5 a **6 blocchi**.
  Fatto fallire sulla netlist di prima (12 rilevazioni, tutte e sole sul
  polo 2) e su quattro casi sintetici.
- Scrivendolo sono emersi due difetti della famiglia «passa sempre»: un parser
  che perdeva l'**ultima net del file** (cioè tutte le bobine), e un blocco di
  suite che, scritto come pipeline verso `sed`, avrebbe restituito lo stato
  d'uscita di `sed`.
- Verificando è emersa **NC-026**: il disegno a blocchi **non girava da L22**
  (quattro riferimenti obsoleti dopo lo scarto di −1). Misurato, non stimato:
  coi rinomini gira pulito, e l'unica cifra che cambia sull'SVG è
  `205 componenti` contro **201**.
- **Una bloccante in meno.** **22 voci, 6 bloccanti.**

### L25 — i cinque modelli entrano in `models/` (2026-09-10)

- I cinque modelli congelati da L24 sono in `models/`, ognuno con la propria
  `.provenance.json` e una ricetta che lo **rimisura** alle condizioni del suo
  datasheet.
- Libreria da 28 a **38 check**, tutti verdi; i lucchetti **provati a
  fallire** sei volte su sei.
- Il testo `.MODEL` promosso è **byte per byte** quello del costruttore:
  nessuno dei cinque portava `mfg=`, quindi zero rimozioni.
- **Tutti e sette i dispositivi attivi hanno ora un modello del costruttore in
  `models/`** — prima volta da G0. Di **NC-017** resta il solo passo di Fase 4,
  la sostituzione in `circuits/preamp/`, quindi la voce **resta bloccante**.
- Rimisurando sono cadute **due cifre di L24**:
  - la f_T del MMBT5401 era presa a I_C = 12,68 mA invece dei 10 mA del
    datasheet: 169,5 → **160,1 MHz**, verdetto invariato;
  - le f_T dei due MJE erano lette come attraversamento a guadagno unitario
    invece che come la **Nota 2** del datasheet le definisce
    (`fT = hfe · ftest`, ftest = 1 MHz). Lette così **nessuno dei due
    raggiunge il proprio minimo di 30 MHz** (27,667 e 29,286 MHz) → **NC-025**.
- In più **NC-024**: l'h_FE del MJE15032 sotto il proprio minimo, che L24
  aveva misurato ma mai messo a registro.
- **22 voci, 7 bloccanti.**

### L26 — i tre requisiti nuovi dell'utente, ADR-019 (2026-09-10)

Nessuna riga di topologia scritta: il lotto registrava e apriva lavoro.

1. **Margine di fase minimo 60°**, su **ogni** combinazione della matrice V1 —
   blocco A e caso peggiore capacitivo da 4,7 nF compresi.
   - Chiude **NC-012**, che quella soglia la chiedeva.
   - Rende **decidibili in negativo** due misure che esistevano già:
     **NC-002 sale a bloccante** (blocco A a 41,98°, mancano 18°) e nasce
     **NC-021** (blocco B a 0 dB con cavo, 56,46°, mancano 3,5°).
   - Nessuno dei due è instabile: 60° è un margine di progetto.
2. **Il trim funziona solo a mute inserito**, con interlock **elettrico** sui
   suoi relè — l'unica delle tre forme proposte che un banco possa provare a
   fallire → **NC-023**, che va con **L16**.
3. **I guadagni diventano tre — 0 / +3 / +10 dB — con riposo a 0 dB**, così
   nessun guasto di bobina alza il guadagno. Il principio di ADR-004 (si
   commuta R_g, mai R_f) si conserva → **NC-022**, lotto **L27**, che deve
   estendere anche i dodici deck da due modalità a tre.

### L22 + L23 — lo specchio d'ingresso senza THAT320 (2026-09-10)

- Il THAT320 fine-vita è sostituito da un **Linear Systems LS352**, dual PNP
  monolitico in SOIC-8 (**ADR-018**).
- Degenerazione portata da 47 a **220 Ω**; lo stadio d'ingresso è **25,7% più
  silenzioso** di prima.
- NC-015 e NC-016 chiuse, NC-020 aperta.

---

## Come si lavora da qui: a lotti piccoli e pushati

Il vincolo che governa il lavoro non è tecnico, è il **cap di token del
piano**. Un lotto che non arriva in fondo non lascia lavoro a metà:
lascia un repo in uno stato che la sessione dopo deve prima capire e poi
riparare. Quindi il lavoro è ordinato per **dimensione**, non per
importanza.

### Le regole

1. **Un lotto per volta.** Mai due agenti in parallelo: i loro resoconti
   tornano insieme, e il ritorno è la parte che consuma.
2. **Ogni lotto finisce con `main` aggiornato e il checkout dell'utente
   riallineato.** Non basta il push: un push rende il lavoro *durevole*,
   non *raggiungibile*. L'ordine di `CLAUDE.md` è
   `push → STATE.md → merge e riallineo → il resto`, e non si fa a mano:

   ```sh
   /bin/zsh scripts/chunk_close.sh <lotto>
   ```

   Rifiuta se il tree è sporco, se ci sono commit non pushati, se il ramo
   non ha toccato `STATE.md`, se la tabella non segna il lotto **fatto**,
   se `NEXT-SESSION.md` **nomina ancora il lotto appena finito**, o se
   `run_tests.sh` fallisce. Poi merghia, riallinea, e **rilegge dal
   checkout dell'utente** per provarlo invece di dichiararlo.
3. **Questo file nomina sempre il lotto successivo.** È ciò che rende
   economica una ripartenza a freddo: la sessione dopo non ricostruisce
   il contesto, lo legge.
4. **Il messaggio di commit dice quale lotto chiude**, così `git log` da
   solo racconta a che punto è il progetto.
5. **Nessun lotto si inizia sopra l'80% del cap.** Sopra l'80% si chiude
   quello in corso e si aggiorna lo stato, punto.
6. **Gli agenti scrivono su file, non nel discorso.** Un subagente che
   torna con quattromila parole di resoconto costa quanto il lavoro:
   deve lasciare un report in `reports/` e restituire dieci righe.
   L'orchestratore riesegue i numeri prima di riferirli all'utente.

Nota onesta sul punto 5: **l'orchestratore non vede la quota a 5 ore.**
Vede solo un contatore della sessione corrente, che è un'altra cosa. Il
numero vero lo legge l'utente con `/status`. Per questo il lavoro a lotti
conta più del protocollo di avviso: se ogni lotto finisce pushato, il
momento in cui il cap arriva smette di essere importante.

### I lotti

Dimensioni relative, non promesse: **XS** = pochi minuti, **S** = una
manciata di file, **M** = riempie una sessione da solo.

| # | Lotto | Dim. | Stato |
|---|---|---|---|
| L0 | Riallineare questo file e depositarci il piano | XS | **fatto** |
| L1 | Diagramma a blocchi del preamp intero | S/M | **fatto** |
| L2 | Collaudare la convenzione di percorso su un deck solo (`.include` **e** `wrdata`) | S | **fatto** |
| L3 | Applicare la convenzione agli altri 11 deck (26 righe cablate rimaste) | S | **fatto** |
| L3b | `REPO` cablato in `circuits/preamp/gain_block.py` | XS/S | **fatto** |
| L3c | Chiusura di lotto che rifiuta, gate agganciato ai dati, dati del dossier versionati | S | **fatto** |
| L3d | Annotare il difetto `setplot`/plot stale di `tb_zout_psrr_noise.cir` (warning per L5) | XS | **fatto** |
| L4 | `wrdata` sui deck muti **senza** cicli | S | **fatto** |
| L5 | `wrdata` sui deck muti **con** cicli + correzione del caso peggiore | S/M | **fatto** |
| L5b | Prima bozza del dossier, generata dai dati + correzione di `za100k`/`p100k` | S/M | **fatto** |
| L5c | Definire **G0**, la prima revisione del prodotto | XS/S | **fatto** |
| L5d | **Eseguire G0**: report datato + non conformità | S | **fatto** |
| L5e | La revisione umana del dossier diventa registro: 4 voci nuove | S | **fatto** |
| L6 | LSK489: passi 1-3 di ADR-013 (congela, trascrivi, provenance) | S | **fatto** |
| L7 | LSK489: passo 4, il controllo incrociato | S | **fatto** |
| L8 | Fase 3a — le parti nuove, fatti verificabili | M | **fatto** |
| L8b | Le due regole dell'utente diventano ADR-016 e requisiti T7/T8 | XS/S | **fatto** |
| L9 | Fase 3b — la rosa dei componenti di segnale | M | **rinviata** — passa dopo i sostituti, vedi sotto |
| L10 | Simbolo KiCad dell'LSK489 — più NC-026 e due deck rotti da L22 | S | **fatto** |

**I lotti che le revisioni hanno generato.** È il meccanismo per cui una
non conformità produce lavoro invece di fermarlo: ogni voce aperta in
`NONCOMPLIANCE.md` arriva qui con il proprio lotto. I primi cinque vengono
da G0 (L5d), i quattro seguenti dalla revisione umana del dossier (L5e), e
l'ultimo — **L20** — dal controllo incrociato di L7, che è la prima voce a
nascere non da una revisione ma da un **controllo prescritto da una ADR**.

| # | Lotto | Dim. | Chiude | Stato |
|---|---|---|---|---|
| L11 | **Mute e corto sulle uscite: misurare e rimediare.** Prima le ADR delle decisioni dell'utente del 2026-09-13. **ADR-021**: mute tenibile **a tempo indefinito**; ciascuna uscita regge un corto al connettore a tempo indefinito, requisito scritto **come risultato** (limiti termici e SOA, a regime e sul transitorio d'intervento, tecnica libera); classe B ammessa. **ADR-022**: operazionali e microcontrollore fuori dal percorso del segnale ma ammessi nel circuito, con tre condizioni. Poi la baseline sulla topologia di oggi; se non regge, la tecnica si sceglie coi numeri. Divisibile in L11a/L11b | M | **NC-001** (bloccante) | **fatto** — conforme senza protezione; apre NC-028 |
| L12 | **Portare blocco A e blocco B sopra i 60°.** Cambia natura con **ADR-019**: non più solo «misura coi valori veri», ma **rimedio** — il blocco A sta a 41,98° e il blocco B a 0 dB con cavo a 56,46°, contro una soglia di 60°. Le strade (più compensazione, meno guadagno d'anello, rete d'isolamento diversa) costano tutte a un altro requisito e vanno confrontate coi numeri | M | **NC-002**, **NC-021** (bloccanti) | **fatto** — ADR-024 (la sonda è il cavo al jack), ADR-025 (C_f 330 pF) |
| L13 | **E4 sulle tre uscite e a manopola che gira.** Estendere `tb_zout_psrr_noise.cir` alle due uscite fisse e a tre posizioni dell'attenuatore | S | NC-008, apre **NC-033** | **fatto** — deck nuovo `tb_e4_uscite.cir` (catena intera, 45 celle × 3 uscite) invece dell'estensione: Re(Z) ≤ 60,13 Ω, dispersione ≤ 1e-4 Ω; la Zout di `tb_zout_psrr_noise.cir` misurata dal 2026-09-09 con la sorgente accesa, corretta; 8 sabotaggi su 8 |
| L14 | **Le tre correzioni di testo.** KPI del margine di fase qualificato, i due commenti di cascode allineati, lo scarto ADR-014 riferito a 1 kHz | XS | NC-003, NC-006, NC-007 | **fatto** |
| L15 | **Il vincolo su E3 scritto dove verrà letto** — in `REQUIREMENTS.md`, «Nota su E3», non in ADR-011 | XS | NC-005 (metà: il vincolo; la misura è L16) | **fatto** |
| L16 | **Il trim entra nel progetto.** Dimensionarlo in `circuits/preamp/` coi due vincoli insieme — attenuazione richiesta da ADR-015 e la «Nota su E3» (min \|Zin\| 20 Hz–20 kHz ≥ 100 kΩ in tutte e tre le posizioni; R1 + R2 = 100 kΩ non basta, `R_IN` sta in parallelo) — e misurarlo. Chiude anche NC-005. **Decisioni dell'utente del 2026-09-14: trim a relè, uno per ingresso, meglio coi bistabili se possibile.** Allineare F2 («a ponticello») a relè, senza ADR; la ADR del trim (ADR-027) è di L16. Il valore del trim deve restare all'uscita dal mute (F8). La cifra unica di margine di NC-009 si sceglie qui e si pubblica in L32 | S/M | **NC-009**, NC-005, **NC-023** | **fatto** — ADR-027 (un solo trim sul ramo variabile, bistabili G6KU-2F-Y, LED, permissivo K6); NC-005 e NC-023 chiuse, NC-009 aperta per L32 |
| L17 | **Buffer sulle uscite fisse.** Modifica di topologia in `preamp_audio.py` che disaccoppia le due fisse dal nodo del Blocco A, più la riesecuzione di `tb_blockA_carichi.cir` sulla topologia nuova. **Dopo L11**: progetta contro il criterio di corto di ADR-021 (risultato, tecnica libera) e nei limiti di ADR-022; il vincolo di impedenza minima a valle non basta più a chiudere NC-010 | M | **NC-010** (bloccante), apre **NC-029** | **fatto** — ADR-023 (classe A sui percorsi ascoltabili), un `GAINBLOCK` per fissa |
| L18 | **Il vincolo PSRR scritto dove verrà letto**: quanto ripple può lasciare l'alimentatore sui rail, ricavato da E5 — **ADR-020** e «Nota su E5 — la quota del ripple» | XS/S | **NC-011** (metà: il vincolo; rimedio e verifica vanno con l'alimentatore) | **fatto** |
| L19 | ~~**La soglia di margine di fase in V1**~~ — **ASSORBITA da L26**: la soglia l'ha data l'utente (60° ovunque, ADR-019) e NC-012 è chiusa. Resta solo la parte «KPI del dossier riferiti a quella», che va con la rigenerazione del dossier (**L32**) | XS | ~~NC-012~~ | **superata** |
| L20 | **Quanto il progetto dipende da I_DSS.** Rieseguire punto di lavoro e rumore del blocco di guadagno con `Vto` ai due estremi compatibili con la finestra A — il modello vendor com'è (2,59 mA) e un `Vto` che porti I_DSS al tipico (5,5 mA) — e scrivere in `REQUIREMENTS.md` o in una ADR quale dispersione il progetto tollera | S | **NC-013** | **fatto** — chiesto il gruppo all'utente: B (ADR-031, tolleranza 8,0–15,0 mA); blocco derivato con `LSK489A` (2i) e `Vto` via `altermod` con sonda; punto di lavoro, E5 e V1 non dipendono da I_DSS, margine di modo comune 2,4 V a 15 mA; 10 sabotaggi |
| L21 | **Il polo 2 del relè, corretto e riverificato.** Riga 79 di `preamp_audio.py` in `"6", "5", "7"`, rigenerazione, e verifica **sulla netlist** che il contatto verso massa di ogni mute cada su 2 e 7 e il ramo `R_g` su 4 e 5 | XS/S | **NC-014** (chiude, bloccante), apre **NC-026** | **fatto** |
| L22 | **Lo specchio d'ingresso senza THAT320.** Trovare e verificare una coppia PNP appaiata che soddisfi **T7 e T8 insieme**, poi rifare punto di lavoro e rumore dello stadio d'ingresso. La decisione *se* sostituire è presa (ADR-016): resta *con cosa* | M | **NC-015** (bloccante) | **fatto** |
| L23 | **Package e simbolo della parte che sostituisce il THAT320**, col pinout letto dal suo datasheet. Va fatto **insieme a L22**, non dopo: il footprint arriva con la parte. Copre anche il residuo `SOIC-8` che oggi non corrisponde a nessuna parte esistente | S | NC-016 | **fatto** |
| L24 | **T7 su tutti i dispositivi attivi.** Prima **verificare** MJE15032/33 e 1N4148 — è il passo che dice quanto è grande il resto — poi trovare i sostituti di 2N5401/2N5551, congelarli e promuoverli in `models/` col controllo incrociato di L6+L7 | M | **NC-017** (bloccante), **NC-004** | **fatto** |
| L25 | **Promuovere in `models/` i cinque modelli congelati in L24** (MMBT5401, MMBT5551, MJE15032, MJE15033, 1N4148), ognuno con la sua `.provenance.json` e una ricetta di regressione in `validate_models.py` sul modello di `tb_lsk489()`. Il controllo incrociato contro i datasheet **è già fatto** in L24: qui si tratta di bloccarne i numeri | S/M | **NC-017** (1° dei 3 passi), apre **NC-024** e **NC-025** | **fatto** |
| L26 | **I tre requisiti nuovi dell'utente diventano ADR-019**: margine di fase minimo **60° ovunque**, trim abilitato dal mute con **interlock elettrico**, guadagni **0 / +3 / +10 dB** con riposo a 0 dB | XS/S | **NC-012** (chiude), apre NC-021…NC-023 | **fatto** |
| L27 | **Il terzo livello di guadagno entra nel progetto.** Dimensionare il secondo ramo commutato verso massa (ADR-004 conservata: si commuta R_g, mai R_f; a relè diseccitati **0 dB**), decidere relè e poli col budget di corrente delle bobine, estendere i dodici deck da due modalità a tre e l'asserzione del diagramma a blocchi | M | **NC-022**, apre **NC-030** | **fatto** — ADR-026 (due rami di R_g in parallelo, K1 + K5) |
| L28 | **SS dell'LSK489 definito per l'LSK489.** Un documento del costruttore che dica cosa sono i pin 3 e 7 di *questa* parte — o una ADR che accetti l'istruzione dell'LSK389 in forza della compatibilità dichiarata. Prima di G2 | XS/S | NC-027 | da fare |
| L29 | **Il gradino al rilascio del mute.** Oggi il rilascio con segnale porta sul jack il condensatore caricato dalla musica: **5,37 V** a +10 dB, 1,79 V a 0 dB, 1,72 V sulle fisse, τ 0,32 s. **Il contatto prima del condensatore**, simulato in scratch dopo L11, toglie quel gradino ma ne mette uno **pari all'offset del blocco** (14-104 mV simulati, più fino a 63 mV di dispersione LSK489) **a ogni mute, accensione compresa**, e il volume non lo riduce (numeri e stima d'udibilità in NC-028). **Prima una soglia dell'utente su V2**; poi il confronto misurato, con un deck **versionato**, fra: contatto prima + offset abbassato (bilanciamento, coppie selezionate), rilascio lento, mute in serie, sequenza di rilascio. P7 va rimisurata per la posizione scelta. **Esteso da L34 (ADR-030)**: per ogni variante di mute, **cambio di guadagno a caldo contro cambio sotto mute seguito dal rilascio**, misurati sul jack e non su `v(OUT)`; transitorio ≥ 2 s (τ 0,32 s); passaggi 0↔+3, +3↔+10 e 0↔+10 dB, con e senza segnale, commutazione sul picco e sullo zero; dispersione LSK489 iniettata (±8 mV tipici, ±20 mV massimi) in più posizioni dell'attenuatore; rimbalzi dei contatti e break-before-make del rotativo; carichi 100 kΩ e 10 kΩ. **Dal confronto dipende L36** | M | NC-028 | da fare |
| L30 | **Il calore del telaio con otto blocchi.** A riposo la scheda audio dissipa 6,45 W (0,806 W per blocco, L17) contro i 3-4 W che P5 prevede per l'apparecchio intero. Stima termica del telaio con l'alimentatore; poi o P5 aggiornato al numero vero, o ventilazione e montaggio progettati con una ADR, o ADR-021 riaperta se i 60 °C non reggono. Va col lotto dell'alimentatore | S | NC-029 | da fare |
| L31 | **I vettori di rumore di `tb_noise_vectors.cir`.** Il deck cita `onoise_q123`, `onoise_r121`, `onoise_jq110`, `onoise_jq111`, dispositivi che non esistono più; il `wrdata` si ferma e non scrive niente, con rc 0. Rinominarli dall'include generato ed estendere `check_deck_refs.py` ai nomi `onoise_*`/`inoise_*`, facendolo fallire sul deck di oggi | XS | NC-030 | **fatto** — 2g esteso e fatto cadere (4 nomi morti), mappa per nodi (tre nomi vivi erano già sbagliati), quadratura = spettro |
| L32 | **Il dossier rigenerato sui dati di oggi. Subito dopo L16.** `build_dossier.py` legge ancora `data/2026-09-09`: THAT320, C_f 22 pF, due soli guadagni. Va esteso ai tre modi (0 / +3 / +10 dB) e puntato ai dati di L27 e L16, coi margini di V1 al minimo della spazzata (ADR-024), la cifra unica di headroom che L16 sceglie per NC-009 e la «KPI riferita a 60°» rimasta da L19. Accanto a ogni numero, la provenienza dei modelli ancora segnaposto (NC-004, NC-017). **Nessun avviso di obsolescenza**: il dossier lo legge solo l'utente (deciso il 2026-09-14) | S | NC-009 (la metà del dossier), apre **NC-031** | **fatto** — tre modi, V1 al minimo della spazzata, M1 +6,58 dB, provenienza letta dagli `.include`; nove controlli fatti fallire |
| L33 | **Le etichette di provenienza dell'LSK489.** I README di `data/2026-09-14/` (L12, L27, L16) e i commenti di tredici deck (dodici col commento di L22, più `tb_trim.cir`) dicono che l'LSK489 simulato è il modello del costruttore; i deck istanziano `LSK489X`, segnaposto con `KF=0`, e nessuno include `models/jfet/lsk489.lib`. Correggere le frasi dei deck (i README datati si precisano con una nota, non si riscrivono) e decidere se un guardiano debba confrontare la provenienza dichiarata con quella degli `.include` | XS | NC-031 | **fatto** — 15 deck (non 13) corretti solo nei commenti, 7 README (non 3) annotati, guardiano 2h fatto cadere su `main` e su 11 sabotaggi |
| L32b | **Gli schemi del dossier si vedono.** Segnalazione dell'utente dopo L32: schema a blocchi e schema del blocco mancavano, perché `index.html` li collegava da `../schematic/`. Il builder li copia accanto alla pagina e rifiuta se mancano | XS | — | **fatto** |
| L34 | **Le decisioni del 2026-09-15 diventano requisiti.** Da una sessione di domande dell'utente: **ADR-028** (comandi sul frontale, LED a pannello cablati), **ADR-029** (ingombro del telaio 450 × 130 × 367 mm), **ADR-030** (guadagno interbloccato dal mute con la strada B, subordinato a L29); in `REQUIREMENTS.md` F3 con «RCA», F10, F11, P8, note su F5 e su «jack», una riga in V2 | XS/S | apre **NC-032**, aggiorna NC-028 | **fatto** — nessun numero simulato; le cifre del bump a caldo sono calcolate ed etichettate |
| L35 | **Comandi e LED a pannello nel sorgente** (ADR-028). Header di cablaggio al posto dei LED del trim sulla scheda (`trim.py`); comando del guadagno sul rotativo a 3 posizioni, cablato perché K5 non sia mai comandato senza K1 (ADR-026); interruttore di mute combinato col temporizzatore d'accensione; LED rosso di mute, letto da un contatto che dica lo stato; `check_relay_safe_state.py` esteso. **Dopo L29 e L36**: il comando del guadagno si cabla una volta sola | S/M | **NC-032** | da fare |
| L36 | **Il guadagno interbloccato dal mute** (ADR-030, strada B). **Solo se L29 lo giustifica**, altrimenti «superata». Due relè ausiliari con autoritenuta su K1/K5; la corsa al rilascio del mute (scambio di K6 contro rilascio delle bobine) simulata e chiusa; il 2e esteso al guadagno; tre LED dello stato vero dai poli liberi degli ausiliari; budget delle bobine (~169 mA fuori mute a +10 dB, a 5 V) consegnato all'alimentatore. Se la corsa si chiude bene, rivalutare la stessa strada per il trim | M | parte di **NC-028** | da fare — **dipende da L29** |
| L37 | **E4 nel dossier.** `build_dossier.py` legge la Zout da `data/2026-09-14/L27/dopo/tb_zout_psrr_noise/`, misurata con la sorgente accesa (NC-033): KPI 58,76 Ω, tabella con 1,0355 Ω «al nodo OUT», nota E4/E8, riepilogo «≤ 60,5851 Ω». Puntarlo ai dati di L13 (`tb_e4_uscite` sulle tre uscite e `tb_zout_psrr_noise` corretto), pubblicare la costanza col volume e le fisse, rifiutare la Zout di L27, annotare in coda `data/2026-09-09/README.md`. I report datati non si toccano | XS/S | NC-033 | da fare |

**NC-004** non ha un lotto proprio: la chiudono **L6-L7** più una
riesecuzione di `tb_noise_breakdown.cir` coi modelli veri. È il caso
previsto da `AGENTS.md` — una voce bloccante a G0 **non** blocca i lotti che
procurano i modelli vendor, perché quelli sono il rimedio, non un
avanzamento di fase. **L6 e L7 sono chiusi**, quindi di NC-004 resta solo
la riesecuzione con i dati versionati sotto `docs/preamp/data/<data>/` —
che ora però va letta insieme a **NC-013**: il modello vendor descrive un
esemplare d'angolo, quindi le cifre di rumore che ne usciranno saranno
conservative sul contributo del JFET, e questo va scritto accanto ai
numeri e non sottinteso.

Dopo, non pianificati in dettaglio perché dipendono dall'esito:
**alimentatore + sicurezza rete** (chiude l'altra metà di **NC-011**: rimedio
e verifica contro **ADR-020**, più il limite sopra 20 kHz; viene **dopo L35 e
L36**, da cui eredita il budget delle bobine, la tensione di `VRELAY` e il
temporizzatore di mute da combinare con l'interruttore di ADR-028), **Fase 4**
(revisione topologia coi componenti veri), **Fase 5** (misure), **dossier**,
**G1**.

**Entro G2** (da L34):
- la scelta del contenitore dentro l'ingombro di ADR-029, verificata sulle sue
  misure interne;
- le prese RCA vere al posto dei `Conn_01x02` generici di `preamp_audio.py`.

**L9**, quando riparte, deve includere relè ausiliari, commutatori e LED di
pannello.

### Cosa contiene ciascun lotto

**L1 — diagramma a blocchi. FATTO.**
`schematic/preamp_blocks_draw.py` → `preamp_blocks.svg`. Tre pannelli:
ingresso + blocco A + le due uscite fisse; attenuatore + blocco B +
uscita principale; relè condivisi, alimentazione e cosa sta su quale
scheda. Disegnato **un canale**: il secondo è identico per contratto
(T3/ADR-006), e ciò che i canali condividono — i quattro relè — sta nel
terzo pannello, dove conta.

Non produce manifesto e **non** è coperto da `check_schematic.py`: un
diagramma a blocchi omette i dispositivi di proposito. La garanzia che ha
è un'altra, ed è scritta in `../architecture.md`: **nessuna cifra sul
disegno è scritta a mano**. Tutte vengono lette da
`circuits/preamp/preamp_audio.net` e asserite — i sei condensatori
d'accoppiamento devono coincidere, i resistori di scarico non possono
divergere fra i canali, e il "+10 dB" è **calcolato** da R_f/R_g e deve
cadere nella finestra di E2. Collaudato facendolo fallire di proposito su
tutti e tre i casi.

Il valore reale è +9,96 dB (R_f 1,50 kΩ / R_g 698 Ω): dentro tolleranza,
ma vale saperlo prima che qualcuno lo scopra misurando.

**L2-L5 — i testbench diventano artefatti. CHIUSO.** Dopo L5 scrivono
file dati **12 deck su 12**: 9 file dai deck senza ciclo (L2-L4) più i
**48** dei sei deck con `foreach` (L5), ognuno convertito in CSV e JSON.
Ma aprendo i deck per L2 è emerso un problema **più grande di quello
registrato**, e va detto per intero — anche ora che è chiuso, perché è il
ragionamento che ha prodotto la convenzione.

**RISOLTO IN L3 — quello che segue è la diagnosi, non lo stato attuale.**
Tutti e 12 i deck leggevano il circuito dal worktree vecchio. Non erano
4 righe `wrdata`: erano **28 righe** con un percorso assoluto cablato
dentro `.claude/worktrees/preamp-fase1/`, e **24 di quelle erano
`.include`**:

```
.include /Users/roberto/EDA/.claude/worktrees/preamp-fase1/spice/preamp/gain_block_flat.inc
```

La metà pericolosa era la lettura, non la scrittura. Una modifica al
circuito su `main` **non avrebbe raggiunto le simulazioni**: avrebbero
continuato a includere la copia di settembre, senza errore da nessuna
parte. Le due copie erano identiche — verificato con `diff` su
`gain_block_flat.inc` e `placeholder_devices.lib`, e riverificato in L3 —
quindi **nessun risultato prodotto è sbagliato**. Ma il meccanismo era
armato, e cancellare quel worktree avrebbe rotto di colpo tutti e 12 i
deck.

**RISOLTO IN L3b — quello che segue è la diagnosi, non lo stato attuale.**
**Il worktree vecchio non era cancellabile, e la ragione era peggiore.**
Cercato su tutto il repo con `git grep preamp-fase1` invece di fidarsi
dei soli deck: `circuits/preamp/gain_block.py:63` contiene

```python
REPO = "/Users/roberto/EDA/.claude/worktrees/preamp-fase1"
```

e `REPO` lì non è un percorso di lettura, è quello di **scrittura**:
`gain_block.py` ci scrive `spice/preamp/gain_block_flat.inc` (riga 497) e
`circuits/preamp/gain_block.net` (riga 505), e `preamp_audio.py` lo usa
per `preamp_audio.net` (riga 258). È lo stesso guasto silenzioso di
prima, **riarmato dall'altro lato**: rigenerare il circuito oggi
depositerebbe l'`.inc` nuovo nel worktree vecchio, e i deck — ora
corretti — continuerebbero a leggere la copia non aggiornata del checkout
corrente, senza errore da nessuna parte.

Non è stato corretto in L3 perché sta in `circuits/preamp/`, che L3 aveva
il mandato esplicito di non toccare, e perché verificare la correzione
vuol dire **rieseguire `gain_block.py`** sul venv SKiDL e confrontare gli
artefatti rigenerati: è un lotto suo, non una riga in coda a questo. La
correzione è una riga (`REPO` derivato da `__file__`, come
`ROOT=${0:A:h:h}` negli script), la **verifica** non lo è. È stata fatta
in **L3b** — vedi sotto.

**Due vincoli scoperti leggendo `scripts/run_simulation.sh`**, che
decidono quale forma può avere il rimedio:

1. Lo script fa `cd "$OUTDIR"` prima di lanciare ngspice (riga 73).
   Quindi **un `.include` relativo non funziona**: si risolverebbe contro
   la directory dei risultati, non contro quella del deck. "Basta usare
   percorsi relativi" è la risposta sbagliata.
2. Lo stesso `cd` risolve però la metà `wrdata` quasi da sé: lo script
   **cerca già** il file che il deck ha scritto dentro `$OUTDIR` (righe
   80-90). Un `wrdata <nomefile>` **senza percorso** atterra nel posto
   giusto da solo.

**L2 ha collaudato entrambe le metà su `tb_op.cir`, e la convenzione è
decisa.** Il vincolo 1 non era un sospetto: è stato *misurato*. Due file
entrambi chiamati `../real.lib`, uno raggiungibile dalla directory del
deck (1 kΩ) e uno dal cwd (9 kΩ); `ngspice -b` ha letto **quello del
cwd** — `i(V1) = -1.111e-04`, non `-1.000e-03`. Il percorso relativo è
quindi falsificato, non scartato per prudenza.

La convenzione, scritta per esteso in un commento dentro `tb_op.cir`:

| Metà | Regola |
|---|---|
| lettura | `.include @REPO@/<percorso-dalla-radice>`, sostituito da `run_simulation.sh` |
| scrittura | `wrdata <nome-nudo>`, che il `cd` porta in `$OUTDIR` da solo |

Un `@REPO@` non sostituito **fallisce in modo rumoroso** (ngspice esce 1,
"Could not find include file"): non è un fallimento silenzioso.

`run_simulation.sh` ha preso tre correzioni della stessa famiglia:
`ROOT` non è più cablato (come già in `run_tests.sh`); `OUTDIR` viene
reso assoluto, perché un `outdir` relativo lasciava `$LOG` e `$CSV` a
puntare nel nulla dopo il `cd` — **trovato eseguendolo, non leggendolo**;
e un `.include` relativo ora emette un avviso, perché si risolve contro
`$OUTDIR` e può pescare in silenzio un file omonimo di passaggio.

**`ROOT` cablato: due script corretti, due ancora no.** `run_tests.sh` e
`run_simulation.sh` derivano ora `ROOT` dalla propria posizione
(`ROOT=${0:A:h:h}`); **`export_fab.sh` e `setup.sh` restano cablati** su
`/Users/roberto/EDA` (righe 28 e 24, riverificate il 2026-09-09).
Eseguiti da un worktree leggono e scrivono nel checkout principale, in
silenzio. Non è un lotto assegnato: è il prossimo esemplare della stessa
famiglia di difetti, da sistemare quando uno dei due verrà toccato.

**L3 ha applicato la convenzione a tutti i deck rimanenti. FATTO.**
22 `.include` diventati `@REPO@/<percorso-dalla-radice>` e 4 `wrdata`
diventati nomi nudi. `grep -c '\.claude/worktrees' spice/preamp/tb/*.cir`
dà **0 su tutti e 12**: il meccanismo armato è disinnescato **dal lato
della lettura**. Il lato della **scrittura** — `gain_block.py`, che
depositava gli artefatti nel worktree vecchio — è stato disinnescato in
**L3b**, che ha anche verificato la correzione rigenerando davvero.

I nomi dei `wrdata` seguono la precedenza di `tb_op`, cioè
`<basename>_wrdata.txt`, che è il nome che `run_simulation.sh` cerca per
**primo**. Il deck che ne scrive due non può usarlo per entrambi, quindi:

| File | Modalità |
|---|---|
| `tb_dc_headroom_wrdata.txt` | 0 dB (relè aperto, RRG = 1 GΩ) |
| `tb_dc_headroom_10db.txt` | +10 dB (relè chiuso, RRG = 0,1 Ω) |

La corrispondenza è scritta **dentro il deck**, perché i nomi nudi non la
dicono più da soli.

**La trappola dei due `wrdata` è stata corretta, non subita.**
`run_simulation.sh` ha ora un **secondo passaggio** che converte in
CSV/JSON *ogni* file `wrdata` prodotto da una run, non solo il primo: il
fallback precedente faceva `grep … | head -1` e il secondo file di
`tb_dc_headroom` non diventava mai un CSV. Il passaggio guarda i file
**prodotti** e non il testo del deck, ed è questa la parte che conta per
L5: un `wrdata` dentro un `foreach` ha il nome **parametrizzato**, quindi
nel deck c'è la stringa non espansa e nessun grep può ricavare il nome
vero. Quando `tb_ac.cir` scriverà le sue 8 curve, saranno 8 CSV.

Lo scoping è un file marker depositato prima di lanciare ngspice, così i
detriti `.txt` di una run precedente non vengono mai riconvertiti.
Misurato e non assunto: gli mtime su APFS sono in nanosecondi e
`find -newer` ha separato due file creati a **126 µs** di distanza.
Il comportamento vecchio è intatto — `<basename>.csv`/`.json` esistono
come prima, e `run_tests.sh` blocco 2b passa senza modifiche.

**I numeri non sono cambiati, ed è stato verificato con una baseline.**
Prima di toccare i deck sono state eseguite tutte e 11 le versioni
committate (il worktree vecchio esisteva ancora) e conservati i log.
L'output `wrdata` è **byte-identico** attraverso la modifica: entrambe le
modalità di `tb_dc_headroom`, `tb_switch_v2` (3,9 MB) e `tb_v3_overload`
(2,6 MB). 9 log su 11 sono identici riga per riga. Le due differenze sono
state inseguite e nessuna è un numero:

- `tb_noise_vectors` — solo i timestamp che ngspice stampa nelle
  intestazioni dei grafici.
- `tb_v3_overload` — **il `Reference value` della `fourier` di ngspice non
  è riproducibile fra run.** Quattro esecuzioni dello *stesso* file hanno
  dato 1,82433e-02 / 1,97093e-02 / 1,89413e-02 / 1,95823e-02. Tutto il
  resto di quel log — tabella delle armoniche, ampiezze, fasi e la cifra
  di THD — è identico fra le run, e il transitorio è byte-identico. È una
  proprietà di ngspice, non della modifica, ed è **una ragione in più,
  indipendente dai modelli segnaposto, per non fidarsi di un THD preso da
  quel deck**.

### Il rumore di caso peggiore — CORRETTO IN L5

**Era sbagliato di un fattore 3,4, e lo era in silenzio.** Trovato il
2026-09-09 rispondendo a una domanda sullo stato delle misure, non
cercandolo; corretto lo stesso giorno in L5. Quel che segue è la diagnosi,
non lo stato attuale.

La riga finale del deck, `RRG=0.1 RSRC=2500 ... WORST CASE`, stampa
**1,676 µV** — che è *identico* al valore "intrinsic" della riga
precedente — invece di **5,697 µV**.

**Causa**: in coda a quel deck mancano i `destroy all` che invece ci sono
dentro i `foreach`. Ogni analisi crea plot numerati, quindi la seconda
`noise` produce `noise3`/`noise4` e il `setplot noise2` continua a
selezionare il plot della **prima**. Vedi `docs/limitations.md` #10.

**Provato su tre gambe, non dedotto:**

1. `alter` funziona in quel deck — il `foreach` sopra dà 1,718 µV e
   5,070 µV per le due modalità, quindi non è `alter` a non avere effetto;
2. `tb_noise_breakdown.cir` misura la **stessa** configurazione con
   `destroy all` e dà **5,696897e-06**;
3. aggiungendo `destroy all` a una copia di scratch dello stesso deck la
   riga diventa **5,696896e-06** — coincide a sette cifre. Il rimedio è
   verificato.

**Come è stato chiuso in L5.** I due `destroy all` mancanti sono ora in
coda al deck, e la riga stampa **5,696896e-06**. La prova non è che il
numero sia cambiato, ma **quanto poco altro è cambiato**: il diff fra il
log della baseline (presa prima della modifica) e quello dopo tocca
**esattamente due righe**, ed è la coppia `onoise_total`/`inoise_total` del
caso peggiore. Le due righe finali del deck sono ora diverse fra loro —
1,676 µV l'intrinseco, 5,697 µV il caso peggiore — che era il sintomo da
cui il difetto era stato notato.

Una **quarta gamba** di conferma è arrivata dai dati che L5 ha iniziato a
scrivere: lo spettro di rumore della configurazione D di
`tb_noise_breakdown` è piatto a 4,03e-08 V/√Hz, e 4,03e-08 × √19980 ≈
**5,70e-06**. Il totale integrato si ricostruisce dallo spettro, quindi ora
il numero ha una verifica che non passa da `onoise_total`.

**L3b — il `REPO` cablato in `gain_block.py`. FATTO.** Chiusa fuori
ordine, prima di L5, su richiesta dell'utente e per una ragione precisa:
**oggi la rigenerazione doveva dare un output identico a quello
committato**, quindi qualsiasi differenza era segnale puro. In Fase 4 il
circuito cambia insieme al percorso, i due effetti si mescolano e quel
controllo pulito non esiste più.

La correzione è una riga: `REPO` derivato da `__file__` (due directory
sopra `circuits/preamp/gain_block.py`), l'equivalente Python di
`ROOT=${0:A:h:h}`. Il file **calcolava già** la propria posizione tre
righe sopra, per il `sys.path`, e poi cablava `REPO`.

**La verifica, che è la parte che costava.** Rieseguiti davvero
`gain_block.py` e `preamp_audio.py` sul venv SKiDL — ed è la prima volta
che il progetto rigenera il circuito da quando gli artefatti esistono:

| Artefatto | Esito |
|---|---|
| `spice/preamp/gain_block_flat.inc` | **byte-identico** (stesso SHA-256) |
| `spice/preamp/gain_block.subckt` | **byte-identico** |
| `circuits/preamp/gain_block.net` | elettricamente identico, 1447 righe |
| `circuits/preamp/preamp_audio.net` | elettricamente identico, 6567 righe |

I due file che le simulazioni **leggono** sono byte-identici, ed è il
risultato che conta: nessun deck cambia numero.

**Scoperta: un `.net` di SKiDL non è riproducibile byte a byte.** I due
`.net` differiscono, e la differenza è tutta metadato: il campo `(date)`,
i **tag casuali** che SKiDL genera per ogni parte senza tag esplicito
(«Random tag ... generated»), gli UUID `(tstamps)` che ne derivano, e i
riferimenti `SKiDL Line`, che si spostano appena il sorgente cambia di
qualche riga. Conseguenza operativa: **un `git diff` su un `.net`
rigenerato non dice se la topologia è cambiata.** La verifica è il
confronto normalizzato — si tolgono `(date`, `SKiDL Tag`, `SKiDL Line` e
`(tstamps`, e si confronta il resto; con quel filtro il diff è **vuoto**
su entrambi i file. È la stessa famiglia del `Reference value` della
`fourier` di ngspice trovato in L3: un campo non riproducibile dentro un
artefatto per il resto deterministico.

**Provato che il worktree vecchio non viene più scritto**, non dedotto:
gli mtime dei quattro artefatti dentro `.claude/worktrees/preamp-fase1/`
sono ancora quelli dell'8 settembre dopo entrambe le rigenerazioni.

**Il worktree `preamp-fase1` è ora eliminabile**, e non lo era prima: non
lo legge più nessuno (da L3) e non ci scrive più nessuno (da L3b), e il
suo ramo ha **0 commit** che non siano già su `main`. Non è stato
eliminato in L3b perché è roba di una sessione dell'utente e la decisione
è sua; `worktree remove` rifiuta da solo se ci sono modifiche non
committate, quindi il comando è già sicuro di suo.

**Cosa resta di questa famiglia di difetti.** `export_fab.sh` e
`setup.sh` hanno ancora `ROOT` cablato su `/Users/roberto/EDA` (righe 28
e 24): eseguiti da un worktree leggono e scrivono nel checkout
principale, in silenzio. Non è un lotto assegnato — si sistemano quando
uno dei due verrà toccato. E il guardiano che renderebbe impossibile una
ricaduta (un controllo in `run_tests.sh` che rifiuti qualsiasi percorso
cablato verso `.claude/worktrees/` nei sorgenti) **non è stato aggiunto**:
cambierebbe il conteggio della suite, che tutta la documentazione cita
come «5 passed». È un candidato dichiarato, non una dimenticanza.

**L21 ha tolto a quell'argomento la sua metà pratica.** Aggiungendo il
blocco 2e la suite è passata a **6 blocchi**, e il costo si è visto per
intero: il conteggio in `run_tests.sh` è **dinamico**, e le righe di
documentazione da riallineare erano **tre**. Quindi il guardiano sui
percorsi cablati resta un candidato, ma non più per il motivo scritto
qui sopra.

**L4 — i due deck muti senza cicli. FATTO.** Additivo per costruzione:
solo righe `wrdata` e commenti, nessun `.include`, nessuna analisi,
nessun valore toccato. Verificato eseguendo i due deck **prima** della
modifica e confrontando i log: identici riga per riga a timestamp
normalizzati, quindi nessun numero è cambiato.

| Deck | File scritti |
|---|---|
| `tb_switch_v2_counterfactual` | 3 — uno per stato del contatto (A chiuso, B aperto, C richiuso) |
| `tb_noise_vectors` | 1 — 2 righe (1000 e 1001 Hz) × 10 vettori scelti |

I tre file del controfattuale hanno una **verifica incorporata**: i loro
`v(OUT)` devono coincidere con quelli che il deck già stampa, e
coincidono — A e C a −0,0372229 V, B a **−13,676851 V**. Se leggessero il
plot sbagliato, A, B e C non sarebbero diversi in quel modo.

**Prima decisione di L4: `tb_bias_sweep` cade in L5, non in L4.** Ha un
`foreach` su 7 valori di R130 con un `op` per iterazione e **nessun
`destroy all`**, quindi sembrava di confine. Non lo è: ogni `op` crea un
plot nuovo (`op1…op7`), quindi un `wrdata` fuori dal ciclo scriverebbe
solo la settima iterazione e la curva Iq(R130) — il senso del deck —
andrebbe persa. Serve un file per iterazione col nome parametrizzato
dentro il ciclo, cioè la forma di L5, più uno snapshot `let iq = @r136[i]`
perché un parametro di dispositivo non è un vettore del plot. Ragione
decisiva: **la convenzione di nome per gli output parametrizzati va
decisa una volta sola** per tutti e 6 i deck con ciclo.

**Due cose imparate, che valgono come regola per L5:**

1. **Un `wrdata` da un `.op` è utile ma non ovvio.** Scrive **una riga**
   e, per ogni vettore richiesto, una **coppia** di colonne
   `(scale, valore)`. Lo *scale* di un plot `op` è un vettore arbitrario
   del plot e **non significa niente**: in `tb_op.csv` vale −13,7002041
   ripetuto sei volte mentre `v(out)` è −0,0118. I dati sono le colonne
   **dispari**, nell'ordine richiesto.
2. **L'identità delle colonne esiste solo nel deck.**
   `run_simulation.sh` intesta i CSV `col0…colN`. Quindi ogni `wrdata`
   non banale vuole sopra di sé un commento con l'ordine delle colonne —
   ed è anche la ragione per cui `tb_noise_vectors` scrive 10 vettori
   scelti e non i **172** che `print all` elenca: 344 colonne intestate
   `colN` sono un file che nessuno può più interpretare. Si scrivono i due
   totali più i contributori dominanti, e **solo i totali per
   dispositivo** — mettere `onoise_q123_rb` accanto a `onoise_q123`
   conterebbe due volte. (I dominanti sommano in quadratura a
   `onoise_spectrum`: √Σ = 1,16e-08 contro 1,215e-08.)

**Nel dossier versionato è finito solo il controfattuale**, in
`data/2026-09-09/` con un `README.md` che porta la legenda delle colonne.
Il −13,68 V è già fra i contenuti previsti del dossier ed è un risultato
**in continua**, la parte che il progetto dichiara credibile anche con i
segnaposto. **`tb_noise_vectors` no, deliberatamente**: due punti a 1 kHz
non disegnano un grafico rumore-vs-frequenza, e i contributi per
dispositivo escono da modelli segnaposto, quindi non sono una cifra di
rumore credibile — lo diventeranno dopo L6-L7. Non riempire la directory
per abitudine è un esito, non una mancanza.

I **6 deck muti rimasti**, tutti con `foreach`, sono stati chiusi in L5 —
vedi sotto.

**L5 — i sei deck con ciclo, e la coda corretta. FATTO.**
I sei deck scrivono ora **48 file**, e con essi il progetto ha per la prima
volta i dati che il dossier deve impaginare: risposta in frequenza,
guadagno d'anello, PSRR e Z_out.

| Deck | File | Righe/file | Contenuto |
|---|---|---|---|
| `tb_bias_sweep` | 7 | 1 | Iq per valore di R130 (la curva Iq(R130)) |
| `tb_noise_breakdown` | 4 | 301 | spettro di rumore per configurazione |
| `tb_ac` | 8 + 1 | 1636 / 801 | risposta, 2 modalità × 4 Z sorgente, + corner LF |
| `tb_loop` | 12 | 801 | guadagno d'anello, 2 modalità × 6 C di cavo |
| `tb_loop_blockA` | 6 | 801 | guadagno d'anello del blocco A |
| `tb_zout_psrr_noise` | 10 | 74 / 151 | Z_out, PSRR dei due rail, rumore |

**La prima decisione del lotto era la convenzione di nome, ed è stata presa
misurando.** Un `$var` dentro un nome di file `wrdata` **non si chiude da
solo**: ngspice fa entrare nel nome della variabile anche `.`, `-` e `_`,
quindi `wrdata tb_ac_$rs.txt` cerca una variabile chiamata `rs.txt`, non la
trova, e scrive un file chiamato **`tb_ac_`** — senza errore e con exit
code 0. Le graffe non sono supportate. La forma che funziona è quella di
**due variabili adiacenti**, perché `$` invece termina il nome:

```
set t = .txt
wrdata tb_ac_$gm$u$rs$t G Gph      ->  tb_ac_0db_2500.txt
```

È finita in `docs/limitations.md` #10, perché è un fallimento **silenzioso**
e vale per qualunque deck futuro. Insieme a due sue conseguenze: `set`
converte in numero ciò che sembra un numero (`set gm = 0db` memorizza `0`,
`set mode = 1G` memorizza `1000000000`), quindi un'etichetta **va quotata**.

**I nomi portano l'etichetta, non il valore del componente** (deciso
dall'utente): `tb_ac_0db_2500.txt`, non `tb_ac_1G_2500.txt`. Chi apre la
directory dei risultati non deve ricordare che RRG = 1 GΩ significa "relè
aperto, guadagno unitario". Il `foreach` è però rimasto **quello di prima** e
l'etichetta si ricava con un `if $mode = 1G`: così `alter` e gli `echo`
usano ancora i valori originali, e **il log resta confrontabile riga per
riga** con quello di prima della modifica. Sdoppiare il ciclo avrebbe dato
lo stesso risultato al costo di ~120 righe duplicate.

**La verifica è stata la baseline, e ha tenuto.** I sei deck sono stati
eseguiti **prima** della modifica e i log conservati fuori dall'albero. Dopo
la modifica: **cinque log su sei byte-identici**. L'unico diverso è
`tb_zout_psrr_noise`, e il suo diff tocca **esattamente due righe** — la
coppia del caso peggiore, che è il punto della correzione. Nessun altro
numero si è mosso, che è ciò che "additivo" deve voler dire.

Controprove incrociate, non solo conteggi di file: il CSV di `tb_bias_sweep`
a R130 = 1690 Ω riporta le stesse quattro cifre che il deck stampa; il CSV
di `tb_ac` a 1 kHz vale 9,927404 dB contro `g1k = 9.927404e+00`; il CSV di
Z_out a 20 Hz vale 1693,4 Ω contro `z20 = 1.69341e+03`.

**Una cosa da sapere sui 4 deck senza sezione fuori ciclo**
(`tb_bias_sweep`, `tb_noise_breakdown`, `tb_loop`, `tb_loop_blockA`):
`run_simulation.sh` cerca per primo `<basename>_wrdata.txt`, che lì non
esiste, quindi **avvisa su stderr e scrive un `<basename>.json` con
`rows: 0`**. È atteso, non un guasto: i file veri li converte il secondo
passaggio, quello costruito in L3 apposta per i nomi parametrizzati. Sta
scritto nel commento di ciascuno di quei deck perché nessuno lo insegua.

**Nel dossier sono finiti 15 file** in `data/2026-09-09/`, con il `README.md`
esteso a portare la legenda delle colonne e i numeri chiave: le 4 curve che
provano la claim di ADR-014 più il corner LF, 4 curve di guadagno d'anello
ai due estremi di capacità, Z_out ×2 e PSRR ×4. Tre `.log` come evidenza.
**Il rumore no**, deliberatamente, per la stessa ragione per cui L4 aveva
tenuto fuori `tb_noise_vectors`: `KF = 0` su ogni segnaposto, quindi non c'è
rumore 1/f e la cifra è un pavimento, non una previsione.

**Tre numeri che ora esistono e prima no** — provvisori sui modelli
segnaposto, ma non più assenti:

- **ADR-014 regge**: fra manopola a 0 Ω e manopola a 2500 Ω la risposta a
  20 kHz si muove di **0,022 dB**, in entrambe le modalità.
- **Margine di fase**: 63,5° a vuoto e **56,9° con 4,7 nF di cavo** in
  modalità 0 dB; 86,2° e 80,6° in +10 dB. Il relè cambia la rete di
  controreazione, quindi il margine è diverso nelle due modalità — è
  esattamente perché `REQUIREMENTS.md` chiede la matrice V1.
- **PSRR**: il rail **positivo** è il lato debole, e in +10 dB scende a
  **29,8 dB a 10 kHz**. Da tenere in mano quando si progetta l'alimentatore.

Serve al dossier **e** a `design-reviewer` per rieseguire le misure a G1:
non era lavoro anticipato.

**L3c — la consegna diventa affidabile. FATTO.**
Nasce da una cosa che l'utente ha dovuto far notare: alla chiusura di L3
il lavoro era pushato, committato e in PR, e il suo checkout conteneva
ancora il prompt di ripresa di L3 — cioè il passo successivo documentato
gli consegnava **il file sbagliato**, senza che niente lo segnalasse. Il
difetto era strutturale e non un caso isolato: L2 aveva lo stesso buco, e
non ha morso solo perché la PR era stata mergiata subito.

La diagnosi in una riga: **un push rende il lavoro durevole, non
raggiungibile.** Sono due requisiti diversi e ne era soddisfatto uno solo.

Da qui **un lotto non è chiuso quando la sua PR è aperta: è chiuso quando
`main` contiene il lavoro e il checkout dell'utente nomina il lotto
successivo.** `scripts/chunk_close.sh` lo verifica invece di ricordarlo, e
rifiuta come fa `export_fab.sh` sulla DRC — senza flag di bypass, perché
i controlli che contiene sono esattamente quelli che erano "da ricordare"
e sono stati dimenticati. Mergiare la propria PR è **autorizzato
dall'utente**, sempre via `gh pr merge --squash --delete-branch`.

**Il gate si stacca dalla PR e si attacca ai dati.** Un diff è
l'artefatto sbagliato su cui giudicare un progetto analogico: le righe
modificate di `gain_block.py` non dicono niente sul margine di fase, e
quando la PR è aperta le misure che risponderebbero non esistono ancora.
Il gate gira quindi **offline, dopo il merge, su `main`**, e produce
**non conformità** — requisito, evidenza, severità, stato — invece di un
veto. Registro vivo in `NONCOMPLIANCE.md`, report datati in `reports/`.
Il **BLOCK non è sparito, si è spostato**: una non conformità bloccante
non ferma un merge, ferma l'**avanzamento di fase**, e l'assenza di
analisi di sicurezza su un progetto collegato alla rete resta bloccante
automatica a G3.

Il vantaggio non è solo di processo: una non conformità **genera lavoro**
invece di fermarlo, perché le voci aperte alimentano da sole la tabella
dei lotti qui sopra.

**I dati del dossier sono versionati** (deciso dall'utente il
2026-09-09). Conseguenza diretta: un gate che gira offline su `main`
deve poter *aprire* i numeri, e `results/` è scratch e gitignorato,
quindi su un checkout fresco è vuoto. I dati curati vanno in
`data/<YYYY-MM-DD>/` — datati come i report, perché una misura è vera di
una versione specifica del circuito. Curati e non grezzi: ciò che il
dossier impagina e ciò che una non conformità cita, non l'output di ogni
run.

Una trappola trovata mentre lo si faceva, e verificata in entrambe le
direzioni: `.gitignore` ha regole **globali** `*.log`, `*_out.txt`,
`*.raw`, che avrebbero mangiato in silenzio proprio i file di evidenza.
Serve la negazione `!docs/preamp/data/**`, che ora c'è — controllato con
`git check-ignore` sia dentro la directory (non ignorato) sia fuori
(ignorato).

**Nota di onestà su cosa questo costa a me.** Con il merge non
condizionato l'utente perde il momento "guardo il diff prima che atterri".
È il prezzo giusto — la revisione che conta è quella sui dati — ma sposta
il peso: la disciplina di verifica per lotto (baseline prima della
modifica, confronto byte a byte, `run_tests.sh`) smette di essere buona
pratica e diventa **l'unica rete** fra un errore e `main`.

**L6 — il primo modello vendor del repo. FATTO.** Report:
`reports/2026-09-09-L6-trascrizione-lsk489.md`. Fino a ieri `vendor/` non
conteneva **nessun** PDF e `models/jfet/` aveva solo `generic_njf.lib`:
il passo 1 di ADR-013 non era iniziato. Ora
`vendor/jfet/linear_systems/LSK489/` porta il datasheet (530 957 byte) e
il PDF del modello (27 178 byte), congelati a 0444 con sha256 e URL
registrati, e `models/jfet/lsk489.lib` esiste con la sua provenance.
*(L6 aveva registrato il datasheet come «RevA38», dal nome del file. **È
la RevA40**: L7 ha letto il footer di tutte e 7 le pagine. Il nome è
obsoleto alla sorgente — vedi la sezione L7 e
`PROVENANCE-L7-addendum.json`.)*

**Il metodo è la parte che conta**, perché è ciò che ADR-013 compra con
la trascrizione a mano: **due letture indipendenti che devono
coincidere**, una visiva (`qlmanage`) e una meccanica
(`scripts/pdf_glyphs.py`, solo stdlib). Sono uscite **byte-identiche**,
stesso sha256; una terza con `pdftotext` concorda a meno del form-feed di
pagina. Il confronto l'ha fatto `diff`, non l'occhio.

Una cosa imparata sul PDF: è un font CID con stringhe esadecimali, quindi
i codici nel content stream **non sono codici di carattere** (scarto
`+0x1D`). Lo scarto **non è indovinato** — il PDF porta la propria
`/ToUnicode` CMap, 52 voci, e lo script la legge; che si riduca a una
costante è un risultato verificato, non un'ipotesi.

**Una differenza sola dal testo vendor**: tolto `Mfg=Linear_Systems`, che
rende ngspice fatale (`Undefined parameter [linear_systems]`, exit 1 —
rumoroso, quindi innocuo). I quattro parametri che ngspice accetta e
ignora (`isr`, `alpha`, `vk`, `mj`) **restano nella riga** per scelta
dell'utente: diff minimo, e i loro warning sono output atteso. **`Kf`,
`Af`, `Nlev`, `Gdsnoi` sono accettati**, ed è il punto — questo modello
ha il 1/f che i segnaposto non hanno.

Libreria da **24 a 26 check** (`tb_lsk489()`, **fumo dichiarato**: 2,500 mA
a `Vgs = 0`, 8,0e-12 A a `Vgs = −3 V`). Il confronto coi limiti I_DSS/V_P
è L7: mescolarlo qui cancellerebbe la ragione per cui i due lotti sono
separati. Finché L7 non chiude, il modello è **trascritto e verificato
sintatticamente, non validato contro i limiti pubblicati della parte**.

**Il difetto trovato eseguendo.** `scripts/validate_models.py` aveva
`ROOT` **cablato** su `/Users/roberto/EDA` (riga 36): eseguito da un
worktree validava i modelli del **checkout principale**, non quelli del
ramo. Non è stato dedotto — la prima `--check-provenance` da qui ha
stampato 12 PASS e `lsk489.lib` **non compariva**, pur essendo sul disco.
È peggio dei fratelli già noti: `chunk_close.sh` esegue `run_tests.sh`
dal ramo, quindi la suite poteva passare **verde su un ramo di cui non
aveva guardato i modelli**. Corretto derivando `ROOT` da `__file__`.

Corretto nello stesso lotto `scripts/freeze_vendor.sh`, che aveva
`VENDOR_DIR` cablato allo stesso modo — congelava il checkout principale
e non i file nuovi. **Restano** `export_fab.sh` (riga 28) e `setup.sh`
(riga 24): non toccati da L6, quindi non corretti.

**L7 — il controllo incrociato. FATTO.** Report:
`reports/2026-09-09-L7-controllo-incrociato-lsk489.md`. Il passo 4 di
ADR-013 è eseguito, e **il verdetto è misto**.

Prima di tutto: **la trascrizione regge**, rieseguita e non ereditata.
`pdf_glyphs.py` riproduce gli stessi 223 byte e lo stesso sha256 di L6, i
due PDF hanno gli hash congelati intatti, e il `diff` fra la riga del
`.lib` e il testo vendor meno `Mfg` è **vuoto**.

Misurato **alle condizioni del datasheet** — che è la metà del controllo
che L6 aveva lasciato aperta — RevA40 pagina 2, gruppo **A**, **25 °C**:

| Grandezza | Misurata | Finestra LSK489A | Verdetto |
|---|---|---|---|
| I_DSS (V_DG = 15 V, V_GS = 0) | **2,59283 mA** | 2,5 … 8,5 mA | **dentro** — 3,7% sopra il minimo, 52,9% sotto il tipico |
| V_GS(off) (V_DS = 15 V, I_D = 1 nA) | **−1,124355 V** | −1,5 … −3,5 V | **FUORI**, 0,376 V sotto il minimo in modulo |
| V_GS (V_DS = 15 V, I_D = 500 µA) | −0,650211 V | −0,5 … −3,5 V | dentro |

**Tre condizioni che decidono la validità della misura**, e due erano
sbagliate nel modo in cui il compito era stato scritto: `V_DG = 15 V` con
`V_GS = 0` significa `V_DS = 15 V` **ai terminali** (`Rd` e `Rs` sono
interni al modello), non i 5 V arbitrari di L6; e il datasheet è
specificato **@ 25 °C** mentre ngspice gira a 27 °C, il che con
`Vtotc=-2.5m` vale esattamente 5,0 mV su V_P. Il numero di L6 è comunque
riprodotto — **2,50019 mA** a V_DS = 5 V — quindi la differenza viene
dalle condizioni e non da altro.

V_P è misurato su **tre strade indipendenti** concordi entro 1,0 mV:
soglia a 1 nA, estrapolazione di √I_D → 0 su 6315 campioni, e
`Vto + Vtotc·(T − Tnom)` letto dal modello.

**Il numero fuori finestra NON è un errore di trascrizione, ed è
misurato.** Dentro il modello I_DSS e V_P sono legati da `Beta`: tenendo
`Beta = 2.2m` e portando `Vto` al minimo V_GS(off) del datasheet
(−1,50 V), I_DSS sale a **4,392 mA**, dentro la finestra A. Le due
finestre del datasheet sono compatibili fra loro e il modello sta sotto
**entrambe in modo coerente** — **uno scarto solo, non due**. Un `Vto`
sbagliato avrebbe mosso le due grandezze in direzioni scorrelate. La
discrepanza è fra il modello SPICE del costruttore e il **datasheet dello
stesso costruttore**.

Quindi **il lavoro non è tornare su L6**, e **ADR-013 non è stata
riaperta**: la sua clausola vale per una parte sbagliata o una
trascrizione sbagliata, e qui non è né l'una né l'altra. È aperta
**NC-013** (maggiore, non bloccante), che il lotto **L20** chiude
quantificando quanto il progetto dipenda da I_DSS.

**La questione della revisione non si è risolta: si è dissolta.** Non
esistono due revisioni. Il PDF congelato si *chiama*
`LSK489DSRevA38.pdf` perché è il nome che il server manda nel
`content-disposition`, ma il suo footer dichiara **`Rev# A40,
04/12/2022`** su tutte e 7 le pagine — la stessa revisione che L6 aveva
attribuito alla copia Mouser. Rieseguita la richiesta all'URL registrato,
il costruttore serve **oggi** un file byte-identico sotto lo stesso nome
obsoleto: la discrepanza è **alla sorgente**. Mouser risponde 403, ma non
serve. Il `PROVENANCE.json` congelato **non è stato riscritto**: la
correzione sta accanto, in `PROVENANCE-L7-addendum.json`.

**`tb_lsk489()` non è più fumo dichiarato.** Misura alle condizioni del
datasheet e **blocca** i tre numeri, senza dichiarare una conformità che
per V_GS(off) non c'è. Conteggio invariato — **26/26** — cambia cosa
asserisce. Collaudato facendolo fallire: spostando `Vto` di soli 70 mV la
I_DSS resta **dentro** la finestra del datasheet, quindi la finestra da
sola non l'avrebbe visto; il lucchetto sì, con exit 1.

**Una cosa notata sul congelamento.** I file di `vendor/` sono 0444 nel
checkout principale ma arrivano **0644** in un worktree: git non versiona
il bit di sola lettura, quindi `freeze_vendor.sh` protegge il filesystem
su cui è girato, non il contenuto dentro il repo. La protezione che
attraversa un clone è l'**sha256**, e tiene.

Nota d'ambiente che resta vera: il datasheet ha 7 pagine e la tabella sta
oltre la prima, quindi `sips`/`qlmanage` non bastano — **poppler è stato
installato in L6** apposta (`/opt/homebrew/bin/pdftotext`, 26.09.0,
arm64). Nessuno script lo richiede, quindi `verify_env.sh` non lo
verifica.

**L8 prima di L9** perché le parti nuove sono fatti chiudibili mentre la
rosa è un giudizio aperto: se il cap arriva, è meglio che tagli la
seconda. **È stata la scelta giusta per una ragione che non era quella**:
L8 ha trovato una scadenza esterna a venti giorni. Se l'ordine fosse stato
invertito, la si sarebbe scoperta dopo.

**L8 — le parti nuove come fatti verificabili. FATTO.** Report:
`reports/2026-09-10-L8-parti-nuove.md`. Quattro parti verificate alla
fonte, e **tre portano una sorpresa**. Cinque documenti nuovi congelati in
`vendor/` con sha256, URL e provenance; **nessun file già presente in
`vendor/` è stato toccato** e tutti e 10 gli hash del repo verificano,
compresi i due dell'LSK489.

**1. Il THAT320 è fine vita, e c'è una scadenza.** È la cosa più urgente
che il progetto abbia adesso. Memo di THAT Corporation firmato dal
presidente, **1 settembre 2026**, congelato in `vendor/`: «Effective
immediately, the following products are on EOL status: … **300-series
transistor arrays**». Con **last-time buy fino al 2026-09-30**, via
`sales@thatcorp.com`.

Il memo è del 1° settembre e **ADR-013 è dell'8**: era già pubblico quando
la topologia è stata disegnata e quando la Fase 1 scrisse «Stock esatto non
verificato». Non era assente, è stato mancato — la lezione di L6-L7
spostata di un passo: **un dato di ciclo di vita non è un dato di
datasheet, e nessuno dei due è un dato di catalogo**.

Il quadro distributivo è coerente: **DigiKey non tratta THAT Corporation**
(zero risultati, il costruttore non compare fra i fornitori); Mouser,
Farnell/Newark e TME rifiutano le richieste automatiche e restano **non
verificati**; l'unica pagina di vendita davvero letta, un negozio tedesco,
dà €8,50 ed è **esaurito**. Aperta **NC-015**, bloccante, e chiude L22 —
la sola voce del registro con una scadenza esterna al progetto.

**2. Il polo 2 del relè Omron è invertito nel codice.** Il datasheet dà
**polo 1: COM 3, NC 2, NO 4** e **polo 2: COM 6, NC 7, NO 5**.
`preamp_audio.py:79` dichiara `K_NO2="7", K_NC2="5"`: scambiati. Il polo 1
è corretto.

La trappola è che le due lame **pendono dalla stessa parte**, ma la riga
alta è numerata 8-7-6-5 e quella bassa 1-2-3-4: la regola implicita
«NO = COM+1» è giusta per un polo e sbagliata per l'altro.

Poiché il polo 2 serve il **canale destro**: a bobina diseccitata — cioè
all'accensione — quel canale **non viene messo a massa**, e il transitorio
passa. È il guasto silenzioso, ed è esattamente quello contro cui ADR-012
è stata scritta, col ramo cuffie che finisce in un paio di
elettrostatiche. (A bobina eccitata il canale destro è invece
cortocircuitato: quello è rumoroso e si troverebbe al primo collaudo.) Il
relè di guadagno ha lo stesso difetto: canale destro a **+10 dB** da
diseccitato, il contrario di ADR-004. Aperta **NC-014**, bloccante → L21.

Il diagramma è grafica vettoriale, quindi è stato letto **tre volte in modo
indipendente** e le tre coincidono: raster a 2400 dpi; coordinate
vettoriali via `pdftocairo -svg` (la lama tocca il contatto di sinistra a
0,445 pt e dista 3,387 pt da quello di destra, **7,6:1**); e le polilinee
del simbolo KiCad, **19:1**. Quest'ultima è la parte che vale la pena
ricordare: **l'informazione era già nel repo**, disegnata nel simbolo. Ciò
che era stato letto erano solo le posizioni dei pin, non il disegno.

**3. Per 2N5401 e 2N5551 non esiste un modello SPICE del costruttore
raggiungibile.** La pagina modelli di onsemi carica l'elenco via
JavaScript; l'indice di Central Semiconductor pure; Diodes risponde 403.
Non è nemmeno un caso da trascrizione come l'LSK489: **nessun PDF del
costruttore contiene il testo `.MODEL`**. Mirror GitHub esistono e **non
sono stati usati** — un mirror non è provenienza vendor, che è la regola di
ADR-013. Aperta **NC-017**, maggiore → L24, che chiude anche la metà di
NC-004 riguardante VAS e cascode.

**4. BVceo ≥ 35 V: confermata**, e il bar stesso è stato controllato. Il
datasheet ha **due** tabelle e contano in modo diverso: gli *Absolute
Maximum Ratings* danno −36 V come soglia di **stress**, le *Electrical
Characteristics* danno **min −36 V, tip −40 V a I_C = −10 µA, I_B = 0** —
ed è il secondo il limite a cui si progetta. I 35 V venivano dalla consegna
della Fase 2, non da un requisito; la V_CE reale dei due THAT320 è
**0,72 / 1,17 V** a riposo, con limite strutturale 30 V. Margine ≈30× al
punto di lavoro.

**5. Il footprint del THAT320 nel codice è sbagliato.** Le uniche varianti
ordinabili sono `320P14-U` (DIP14) e `320S14-U` (SO14): **non esiste una
versione a 8 pin**, e `gain_block.py:303-304` assegna `SOIC-8`. Aperta
**NC-016**, maggiore → L23.

**Il modello SPICE del THAT320 invece c'è, è nativo, e ngspice lo carica.**
`300 Series_Macro_01.lib`, **5 366 byte** — esattamente la dimensione che
la Fase 1 aveva riportato, quindi quel dato è **confermato** e non
ripetuto. Provato alle condizioni del datasheet (V_CB = −10 V, I_C = −1 mA,
1 kHz, `set temp = 25`): **exit 0 e nemmeno un warning**, a differenza
dell'LSK489 che ne dava quattro.

**E qui la scoperta che vale oltre questo lotto: THAT pubblica DUE modelli
della stessa parte.** `QPNP_THAT_NS` (`RB = 25`, ottimizzato per il rumore)
e `QPNP_THAT_HF` (`RB = 103,345`, ottimizzato per l'alta frequenza), per il
resto identici. Rumore riferito all'ingresso a 1 kHz: **0,768 nV/√Hz**
contro **1,314 nV/√Hz**, il **71%** di distanza. Il datasheet dichiara
0,75 nV/√Hz tipici, quindi **il modello NS riproduce la cifra del
costruttore al 2,4%** e l'altro no. Verificato anche a mano — termico di
25 Ω più shot di collettore danno 0,791 nV/√Hz, entro il 3% del simulato.

Conseguenza: **una cifra di rumore e una di stabilità prese dallo stesso
modello non possono essere entrambe giuste**, e quale modello si è usato va
scritto accanto al numero. Finita in `docs/limitations.md` **#17**.

**Nessuno dei due ha `KF`/`AF`.** Provato empiricamente e non con un
`grep`: lo spettro simulato è **piatto alla nona cifra significativa** da
100 Hz a 100 kHz. Vincola NC-004: l'analisi coi segnaposto dice che i
contributori dominanti stanno **nello specchio**, e il modello vendor dello
specchio non ha 1/f, esattamente come i segnaposto. Solo l'LSK489 ce l'ha.

**Due segnaposto che sbagliano in direzioni opposte**, il che significa che
i margini di fase attuali non sono conservativi in modo noto: `PTHAT320` ha
`TF = 1,5 ns` («~100 MHz») contro **325 MHz** tipici del vero — **3×
lento**; `NSS2N5551` ha `TF = 0,5 ns` («~300 MHz») contro un minimo di
datasheet di **100 MHz**, per giunta misurato a 10 mA mentre il circuito
lavora a 2-6 mA dove f_T è più bassa — **3× veloce**.

**Una nota per la Fase 4**: le varianti del 2N5551 **selezionate per beta**
sono state dismesse (`2N5551YTA`, `2N5551YBU`, `2N5551CTA`; il suffisso -Y
significa h_FE 180~240). Resta la dispersione piena **50…250**, il che
riguarda la coerenza di beta nella coppia di cascode e nei generatori.

**Seconda trappola registrata, `docs/limitations.md` #18**: su
`www.onsemi.com` **HTTP 200 non prova che il file esista** — risponde 200
con la stessa pagina HTML da 303 722 byte per qualunque percorso
inesistente, e la prima richiesta di datasheet del lotto è caduta proprio
lì. È la regola «un modello è verificato se ngspice lo carica» spinta fino
al trasporto. Effetto collaterale: **falsificare lo user-agent peggiora le
cose**, onsemi risponde 403 a un UA Safari plausibile e 200 a quello di
curl.

**Cosa L8 non ha toccato, verificato e non dichiarato**: il diff del ramo
non nomina `circuits/`, `spice/preamp/` né `docs/preamp/data/`;
`validate_models.py` dà **26/26** e `--check-provenance` **13/13**,
conteggio invariato, che è la prova che `models/` è intatto. La promozione
dei modelli vendor dentro `models/` è **fuori da L8 per decisione
dell'utente**: porta con sé il controllo incrociato contro il datasheet,
cioè il lavoro di L7 moltiplicato per parte, ed è un lotto suo (L24).

**Cosa L8 non ha verificato, dichiarato e non riempito**: le **quantità di
stock**, per nessuna parte — DigiKey non le rende a un client non-browser e
gli altri distributori rifiutano; se un modello di 2N5401/2N5551 esista
dietro una sessione browser o un account; il modello THAT320 contro il
datasheet oltre alla sola cifra di rumore; il **pinout** del THAT320, che
servirà a L23; e MJE15032/33, fuori mandato.

## L8b — le due regole dell'utente diventano una ADR. FATTO.

Poche ore dopo L8, letto il quadro delle nuove non conformità, l'utente ha
risposto con due decisioni. Non erano due verdetti su tre parti: erano due
**regole di progetto**, ed è così che sono state registrate — **ADR-016**,
più i requisiti **T7** e **T8** in `REQUIREMENTS.md`.

> «non possiamo approvvigionare il THAT320 entro il 30.09 e non voglio un
> componente a fine vita in un progetto nuovo, va sostituito, allo stesso
> modo non accetto parti che non abbiano un modello vendor, anche loro da
> sostituire»

**Le due regole:**

1. **Nessun componente a fine vita entra nel progetto** (**T8**). Un EOL
   già annunciato squalifica la parte anche se c'è una finestra di
   last-time buy. Il controllo si rifà **a ogni gate**, non una volta sola.
2. **Ogni dispositivo attivo del percorso di segnale ha un modello SPICE
   del costruttore** (**T7**). Un modello pubblicato come PDF conta — è il
   caso dell'LSK489 — ma un mirror di terze parti no.

**L'estensione è stata chiesta e confermata, non assunta.** La seconda
regola nominava 2N5401 e 2N5551, ma il progetto ha **sette** dispositivi
attivi e tre non erano mai stati verificati. Alla domanda se la regola
valesse anche per MJE15032/33 e 1N4148, l'utente ha risposto **sì, a tutti
i dispositivi attivi**. È la ragione per cui NC-017 ha cambiato dimensione
invece di restare una voce su due parti.

**Lo stato di partenza è uno su sette:**

| Dispositivo | Modello vendor | Esito |
|---|---|---|
| LSK489 | **sì** — PDF, trascritto in L6, validato in L7 | **resta** |
| THAT320 | sì, nativo — ma fine vita | **fuori per T8** |
| 2N5551, 2N5401 | **no**, in nessuna forma | **fuori per T7** |
| MJE15032/33 | **non confermato** (Fase 1) | **da verificare** |
| 1N4148 | mai verificato | **da verificare** |

I due MJE sono i **dispositivi d'uscita**: se cadono, non è un cambio di
package, è una **modifica di topologia**.

**Cosa è cambiato nel registro.** NC-015 non ha più una scadenza — il
last-time buy è stato scartato, quindi la voce ora dice *con cosa*
sostituire e non *se*. NC-017 è passata da **maggiore a bloccante**,
perché da oggi misura la distanza da un requisito e non da una preferenza,
e copre tutti e sette i dispositivi. NC-016 non si chiude più correggendo
il footprint del THAT320: si chiude quando arriva la parte sostitutiva col
proprio footprint — resta però il residuo reale che `gain_block.py:303-304`
dichiara oggi un `SOIC-8` che non corrisponde a **nessuna parte
esistente**. Le bloccanti passano da 5 a **6**.

**Una nota di metodo che vale oltre questo lotto.** ADR-013 nomina il
THAT320 **una volta sola, di passaggio**, dentro la discussione di
un'alternativa scartata; la parte è entrata nella topologia come scelta
implementativa in `gain_block.py` che citava quella parentesi. Non c'era
quindi una decisione da superare. **Una parte che entra citando una
parentesi non ha mai avuto un'istruttoria** — ed è precisamente il motivo
per cui nessuno aveva controllato il suo stato di ciclo di vita, mentre
per il JFET ADR-013 la clausola giusta («oppure l'LSK489 esce di
produzione») l'aveva già scritta.

**Cosa costa, dichiarato in ADR-016 e non nascosto.** Lo specchio va
riprogettato e non ri-approvvigionato; se i due MJE cadono, si apre lo
stadio d'uscita; e **tutte le cifre attuali di polarizzazione, margine di
fase, PSRR e Z_out sono da rifare** dopo le sostituzioni. Erano già
provvisorie — vengono da segnaposto — ma smettono di essere anche solo
indicative. Il guadagno che paga il costo è che **NC-004 diventa
chiudibile davvero**.

**L8b non ha toccato nulla oltre la documentazione**: nessun file in
`circuits/`, `spice/preamp/`, `models/`, `vendor/` o `docs/preamp/data/`.

## L24 — T7 su tutti i dispositivi attivi. FATTO.

Report: `reports/2026-09-10-L24-t7-dispositivi-attivi.md`. Decisione:
**ADR-017**. Nove file congelati in `vendor/`, nessun file preesistente
toccato, **19 sha256 su 19 verificano**.

**1. Lo stadio d'uscita regge, ed è la risposta che dimensionava tutto il
resto.** ADR-016 aveva scritto che se i due MJE fossero caduti la
sostituzione sarebbe stata una modifica di topologia. Non cadono:
**MJE15032, MJE15033 e 1N4148 hanno un modello del costruttore**, e ngspice
lo carica ed esegue. La frase della Fase 1 — «pagina models esiste, file
finale non confermato» — era un'ipotesi ereditata, ed è stata risolta alla
fonte invece che creduta.

**Il pattern che L8 non aveva trovato**:
`https://www.onsemi.com/download/models/lib/<parte minuscola>.lib`. Il
conteggio di byte resta l'unico test onesto su quell'host (#18): un modello
vero torna `application/octet-stream`, un soft 404 torna 303 722 byte di
HTML.

**2. Per 2N5401/2N5551 non si sostituisce il dispositivo: si cambia
costruttore e package.** L8 aveva registrato «Diodes Incorporated risponde
403». È vero delle pagine HTML sotto `/design/` e `/part/`; **non** dei file
di modello, che stanno su `/spice/download/` e rispondono `200 text/plain` a
un `curl` nudo. Diodes pubblica lo stesso die come **MMBT5401** e
**MMBT5551**, in SOT-23.

Tenere il die non è pigrizia: il 2N5401 è il **VAS**, e con il Miller da
470 pF fissa il polo dominante di tutto l'amplificatore. Un transistor
davvero diverso lì sposta una cifra su cui la topologia è costruita.

*(La metà onsemi della conclusione di L8 **tiene**: `2n5401.lib` e
`2n5551.lib` danno il soft 404 anche col pattern che ha funzionato per i
MJE. È stata rifalsificata, non ereditata.)*

**3. Il controllo incrociato, e per la prima volta un verdetto pulito.**
Misurato alle condizioni dei datasheet, 25 °C:

| | MMBT5401 | finestra | MMBT5551 | finestra |
|---|---|---|---|---|
| hFE @ 10 mA | **124,9** | 60…240 | **107,2** | 80…250 |
| f_T @ 10 mA | **169,5 MHz** | 100 min / 300 tip | **173,1 MHz** | idem |
| C_obo @ 10 V, 1 MHz | **3,706 pF** | ≤ 6 pF | **2,221 pF** | ≤ 6 pF |

**Sei su sei dentro** — l'unico modello del repo che non produca un verdetto
misto. L'LSK489 ha NC-013, e il **MJE15032 sta sotto il minimo del proprio
datasheet**: hFE **66,4** a I_C = 0,5 A contro un minimo di **70**, fuori del
5,1%. Non è un errore di trascrizione (non si è trascritto nulla) e la
direzione è pessimistica, quindi la più sicura — ma il modello non descrive
una parte conforme. Il PNP MJE15033 invece è dentro a tutti e tre i punti.

**4. Quanto sbagliano i segnaposto, finalmente con i numeri.** ADR-016
diceva «in direzioni opposte» senza poterlo quantificare:

| Segnaposto | f_T implicita | reale al punto di lavoro | errore |
|---|---|---|---|
| `NSS2N5551` | ~318 MHz | **88,8 MHz** a 2 mA (cascode) | **3,6× veloce** |
| `PSS2N5401` | ~265 MHz | **137,0 MHz** a 6 mA (VAS) | **1,9× veloce** |
| `NMJE15032` | ~30 MHz | **11,2 MHz** a 15 mA | **2,8× veloce** |
| `PMJE15033` | ~25 MHz | **12,6 MHz** a 15 mA | **2,0× veloce** |

E la C_ob di `PSS2N5401` è 6 pF contro **3,71 pF** reali, cioè 1,6× **alta**:
sul polo di Miller spinge nella direzione **opposta** all'errore sulla f_T.
Non si compensano in modo noto. È il senso preciso di «non conservativo in
modo noto» di NC-002 e NC-012.

**5. La rosa alternativa è stata cercata prima, e T8 l'ha quasi azzerata.**
Sedici candidati provati per modello, i superstiti letti per ciclo di vita
**dal costruttore**:

- **KSA992** (PNP audio basso rumore) — **Last Shipments**, cioè il
  last-time buy che T8 squalifica. Con KSC1845 è **la coppia audio
  classica**, quella che sarebbe entrata «per reputazione»: **è il THAT320
  evitato in anticipo**, e solo perché ora il controllo di T8 è obbligatorio
  invece che implicito;
- **2N3904 / 2N3906** — i due transistor più diffusi al mondo, **tutti gli
  OPN Obsolete** presso onsemi. I cataloghi dei distributori ne sono pieni,
  ma di *altri* costruttori, e T7 chiederebbe allora il modello di *quello*;
- MPSA06/56/92, KSA733 — tutti Obsolete;
- **BC550C** — unico superstite attivo, ma è NPN senza complementare
  conforme, e il suo file dichiara «MODEL PARAMETERS FROM MEASURED DATA:
  **BC549**», cioè è adattato alla parte sorella.

**6. Il 1N4148 non si sostituisce: si attribuisce.** È un codice generico di
industria, quindi T7 si soddisfa nominando il costruttore di cui il progetto
usa modello e ciclo di vita. Scelto **onsemi**: sei OPN tutti **Active** dal
suo JSON-LD, e un modello. Vishay ha un datasheet recente ma nessun modello
SPICE a un client non-browser. Misurato: V_F **0,766 V** a 10 mA contro un
massimo di 1,0 V, C_T **0,869 pF** contro 4,0 pF max — **conforme**.

**7. Due trappole nuove, `docs/limitations.md` #19 e #20.**

**#19 — il prefisso micro non sopravvive all'estrazione dai PDF onsemi.**
`pdftotext` rende µ come **m**: un limite di corrente letto meccanicamente è
sbagliato di **mille volte**, exit 0 e nessun avviso. Provato con le due
letture di ADR-013: il render mostra «1.0 **μ**s», l'estrazione dà «1.0
**m**s». È della toolchain onsemi, non di poppler — 0 glifi µ estratti dai
tre PDF onsemi, **11** dall'LSK489 di Linear Systems. E il prefisso *nano*
sopravvive, il che è ciò che lo rende pericoloso.

**Tocca un documento già congelato in L8**, quindi le cifre di L8 sono state
ricontrollate a vista: tre righe del 2N5551 sono storpiate (V(BR)CBO,
V(BR)EBO, I_CBO a 100 °C), **nessuna delle tre è fra quelle che L8 aveva
registrato**, e la riga che L8 *ha* registrato — V(BR)CEO a I_C = 1,0 mA — è
**corretta**. Il `PROVENANCE.json` congelato non è stato toccato.

**#20 — il nome di un file non è la sua parte.**
`https://www.onsemi.com/download/models/lib/1n4148.lib` restituisce un file
**vero**, e dentro c'è `.SUBCKT 1N4148WT` — la variante **SOD-323**, non il
DO-35 che il progetto usa. ngspice lo carica senza una parola e simula un
altro dispositivo. Il modello giusto è in `1n914.lib`, che dichiara
«Product: … / **4148** / 4448 · Package: **DO-35**». **La conferma era sul
sito del costruttore**: la pagina prodotto 1N4148 di onsemi linka un solo
datasheet, ed è `1n914-d.pdf`. È la lezione di L7 spostata di un livello — là
il nome non era la revisione, qui non è la parte.

**8. Cosa costa la decisione, dichiarato in ADR-017.** Sei istanze per blocco
passano da TO-92 a SOT-23. La dissipazione ammessa scende da 625 a **310 mW**
sul pad minimo; il caso peggiore del progetto è il VAS a **86,3 mW**
(`gain_block.py:434`: 6,443 mA, V_CE 13,4 V), quindi margine **3,6×** — ma
letto dal punto di lavoro vero, non stimato. La BVceo del VAS scende da 160 a
150 V, restando 5× i 30 V di caso peggiore.

E **il moltiplicatore di Vbe perde il proprio metodo di accoppiamento
termico**: `gain_block.py:350` prescrive «thermal compound + cable tie» al
tab del TO-220, e **un SOT-23 non si fascetta**. Aperta **NC-019**
(maggiore), da risolvere prima del G2.

**9. Nessuno dei cinque modelli ha rumore 1/f.** Né i due Diodes, né i due
MJE, né il 1N4148 — come i segnaposto e come i modelli THAT (#17). **Nel repo
solo l'LSK489 ha `KF`/`AF`.** Quindi **NC-004 non si chiude «quando arrivano
i modelli veri»**: le cifre di rumore della Fase 4 restano un pavimento senza
flicker, proprio dove l'analisi dice che il rumore è dominante. Va scritto
accanto a ogni numero.

**10. Cosa L24 non ha toccato, verificato e non dichiarato.** Il diff del
ramo non nomina `circuits/`, `spice/preamp/` né `docs/preamp/data/`; sotto
`vendor/` tutte le righe di `git diff --name-status` sono `A`, nessuna `M`.

**Una nota sui sidecar di `vendor/`.** Ce ne sono **due formati**: 16 in
formato `<hash>  <nome>`, che `shasum -c` legge, e **3 in formato hash nudo**
(i due dell'LSK489 e la fixture demo), che `shasum -c` **rifiuta e segnala
come falliti**. Non è corruzione — verificano per confronto diretto — ma una
verifica ingenua dell'intero albero produce tre falsi allarmi.

## L22 + L23 — Lo specchio d'ingresso senza THAT320. FATTO.

Report: `reports/2026-09-10-L22-L23-specchio-ingresso.md`. Decisione:
**ADR-018**. Chiudono **NC-015** (bloccante) e **NC-016**, aprono **NC-020**.

**1. La parte è un Linear Systems LS352**, dual PNP monolitico in SOIC-8,
|V_BE1−V_BE2| **0,2 mV tip / 0,5 max**, BV_CEO 60 V. Stesso costruttore
dell'LSK489, e come per l'LSK489 il modello è pubblicato **come PDF**: vale la
procedura vincolante di ADR-013, e le due letture indipendenti sono uscite
**byte-identiche** (stesso sha256; una terza, visiva, concorda). Una sola
rimozione, `mfg=Linear_Systems`, fatale in ngspice — **riverificata
eseguendola**, non ereditata da L6.

**2. Il risultato che ha deciso la ADR: il dispositivo è più rumoroso e lo
stadio non lo è.** Un deck, due modelli, stesso punto di lavoro:

| Modello | rumore riferito all'ingresso |
|---|---|
| THAT320 `QPNP_THAT_NS` | **0,758 nV/√Hz** |
| LS350 | **1,685 nV/√Hz** — 2,22× peggio |

Il deck non valida sé stesso: il numero del THAT riproduce lo 0,768 nV/√Hz
già registrato in `limitations.md` #17. La causa è nel modello — `RB = 200`
con `IRB = 1e-05` e `BF = 500`, quindi a 1 mA la resistenza di base sta vicino
a RB e non a `RBM = 10`; il THAT320 portava `RB = 25` piatto, ed erano quei
25 Ω a farne una parte a basso rumore.

**Ma il contributo di uno specchio è fissato dalla sua transconduttanza**, e
la degenerazione la compra indietro più in fretta di quanto rbb la costi.
ADR-016 chiedeva di **riprogettare** lo specchio: il riprogetto è uno sweep,
non un ragionamento.

| R_deg | rumore, caso peggiore | V_BC interno della metà d'uscita |
|---|---|---|
| 22 Ω | — | −53,1 mV — **satura** |
| 47 Ω (ereditato) | 6,988 µV | −0,4 mV — sul ginocchio |
| 100 Ω | 5,149 µV | +112,5 mV |
| 150 Ω | 4,580 µV | +219,4 mV |
| **220 Ω** | **4,231 µV** ← minimo | **+369,1 mV** ← scelto |
| 330 Ω | 4,515 µV — **risale** | +590,8 mV, ma il clipping negativo perde 0,77 V |

Il minimo esiste davvero e a 330 Ω il degrado si vede su **due assi
indipendenti**. Contro il THAT320 a 47 Ω (5,697 µV), lo stadio finisce
**25,7% più silenzioso** — con un dispositivo il cui rumore proprio è 2,2×
peggiore. Dentro **E5** con più margine di prima.

**Il ginocchio esiste per via di `RC = 231,4`** nel modello, contro i 18 Ω del
THAT320: a 2,1 mA sono **0,49 V persi dentro il dispositivo** su ~1,2 V di
V_CE che la topologia concede. Non è un artefatto — il datasheet dichiara
V_CE(sat) ≤ 0,5 V a 1 mA, che implica esattamente quello. E il rimedio è
**controintuitivo**: aumentare la degenerazione *aumenta* il margine invece
di consumarlo. La prima intuizione è stata provata a 22 Ω e **falsificata**.

**3. Il duale è UNA parte, non due, e NC-016 si chiude così.** Era il residuo
peggiore: due Part con un footprint SOIC-8 ciascuna, cioè **due package sul
PCB per un dispositivo solo**. `library/preamp.kicad_sym` è la **prima
libreria di simboli del repo** — verificata con `kicad-cli sym upgrade` e
`sym export svg`, che disegna tutte e tre le unità, e caricata da SKiDL.

| | prima | dopo |
|---|---|---|
| componenti totali | 44 | **43** |
| componenti su SOIC-8 | 4 | **3** (LS352 + i due LSK489) |

Il pinout è **guardato, non estratto** (è grafica): SOIC-8 = 1=C1 2=B1 3=E1
4=N/C 5=N/C 6=E2 7=B2 8=C2. PDIP-8 e DFN-8 sono elencati dal costruttore ma
il datasheet **non ne disegna il pinout**, quindi non sono stati usati — un
pinout non pubblicato è esattamente come il SOIC-8 fantasma è nato.

Una modifica di infrastruttura è servita: `spice_export.spice_dev()` ha ora un
parametro **`suffix`**, senza il quale le due metà emetterebbero due righe
SPICE con lo **stesso nome**. Diventano `Q122A` e `Q122B`.

**Fondere due componenti in uno slitta tutti i riferimenti successivi di −1.**
La mappa vecchio→nuovo è stata **ricavata confrontando i nodi** fra il `.inc`
vecchio e quello nuovo, non dedotta a mano, e applicata in una sola passata ai
tre deck che citano riferimenti espliciti e al disegno. **Il controllo dello
schematico ha fatto il suo mestiere**: alla prima esecuzione
`check_schematic.py` ha rifiutato con 15 discordanze.

**4. Verdetto misto sul modello, come per l'LSK489.** Alle condizioni del
datasheet, 25 °C: h_FE 441,2 / 483,2 / 490,6 a 10 µA / 100 µA / 1 mA (finestra
200…600, **dentro**), C_OBO 1,584 pF (≤ 2, dentro), NF 0,325 dB (≤ 3, dentro)
— ma **f_T 129,5 MHz contro un minimo di 200 MHz**, il 35% sotto, verificata
su tre gambe concordi. È **NC-020**, maggiore: il modello è più *lento* della
parte garantita, quindi le cifre in alta frequenza sono pessimistiche — la
direzione sicura, ma non di quantità nota.

I numeri sono **bloccati** da `tb_ls350()` in `validate_models.py`: la
libreria passa da 26 a **28 check**. La ricetta ha trovato subito un difetto,
ed era **nel controllo e non nel modello**: leggendo il campione che
attraversa la soglia invece di interpolare come fa `meas`, l'h_FE a 10 µA
usciva 438,2 invece di 441,2 — 0,7%, cioè il passo dello sweep.

**5. Due candidati scartati alla fonte.** **DMMT5401** (Diodes) partiva
avanti — stesso die del MMBT5401 già scelto in ADR-017, percorso del modello
già noto — e cade su due righe del suo datasheet: appaiato su **h_FE al 2% e
non su V_BE**, e NF **8 dB** contro 3. L'appaiamento di uno specchio *è* un
appaiamento di V_BE. **SSM2220** (Analog Devices), il sostituto naturale per
funzione e rumore, è **non verificabile da qui**: `analog.com` e la sua CDN
non rispondono a un client automatico (HTTP/2 INTERNAL_ERROR e timeout a 60 e
90 s, su due protocolli e due URL). Una ricerca lo dava *Obsolete* e **non è
stata usata** — è la stessa regola che in L24 ha impedito di credere a quattro
aggregatori sul 1N4148. Resta **dichiarato non verificato**.

**6. Trappola nuova, `limitations.md` #21.** Su `diodes.com` il percorso di un
modello è deciso **solo dall'id**: il nome del file nell'URL non è controllato.
`/spice/download/2587/DMMT5401.spice.txt` risponde 200 e serve **MMBT5401** —
la verità sta nel `name=` del `Content-Type`, non nell'URL che hai scritto. È
la #20 spostata di un passo indietro: là il costruttore serviva la parte
sbagliata sotto un nome giusto, qui è il richiedente a poter scrivere un nome
che nessuno verifica.

**7. Cosa NON è stato verificato, dichiarato e non riempito.** Lo stato di
ciclo di vita esplicito dell'LS352 (Linear Systems non ne pubblica: l'evidenza
è pagina viva, datasheet senza timbro e un modello **rilasciato il
2026-07-27**, due mesi fa — più debole di una stringa di stato, e senza il
controllo di silenzio che L24 poté fare su Diodes); l'SSM2220; le scorte
presso i distributori; se la parte reale rispetti la finestra di appaiamento
(il modello descrive il die, non il grado). E **PSRR, Z_out e risposta non
sono state rimisurate**: i dati in `data/2026-09-09/` descrivono la topologia
**col THAT320**, quelli nuovi stanno in `data/2026-09-10/`.

**8. Cosa non si è mosso, misurato.** Margine di fase 63,54° → 63,02° (0 dB, a
vuoto) e 56,94° → 56,46° (4,7 nF); guadagno d'anello DC 72,32 → 72,38 dB;
clipping +13,017 → +13,002 V, cioè **0,01 dB**; guadagno a piccolo segnale
invariato a 3,1460. Offset d'uscita −11,8 → −16,6 mV.

**9. NC-004 non si muove**, e la ragione è la stessa di L24: **l'LS350 non ha
`KF`/`AF`**. Nel repo solo l'LSK489 ha rumore 1/f, quindi le cifre qui sopra
restano un **pavimento senza flicker** proprio dove l'analisi dice che il
rumore domina.

**10. L10 costa molto meno adesso.** Il simbolo dell'LSK489 ha ora la libreria
dove andare, il meccanismo multi-unit collaudato e il `suffix` di `spice_dev`
già pronto. I due LSK489 restano le ultime due Part che dichiarano un package
ciascuna per un solo dispositivo.

## L26 — I tre requisiti nuovi dell'utente. FATTO.

Report: `reports/2026-09-10-L26-requisiti-utente.md`. Decisione: **ADR-019**.
Chiude **NC-012**, apre **NC-021** (bloccante), **NC-022**, **NC-023**, e alza
**NC-002** a bloccante.

**Perché è un lotto e non una nota.** I tre requisiti sono arrivati in
conversazione, e un requisito che vive solo in una chat non fa fallire niente:
è il modo in cui un progetto scopre a valle di aver misurato la cosa sbagliata.
Il precedente è **L8b**, dove due regole dell'utente diventarono ADR-016 e i
requisiti T7/T8.

**1. Margine di fase minimo 60°, ovunque.** Chiude NC-012 — che quella soglia
la chiedeva — e con essa **due voci diventano decidibili, in negativo**:

| Configurazione | Margine | Contro 60° |
|---|---|---|
| Blocco B, 0 dB, a vuoto | 63,02° | conforme |
| Blocco B, +10 dB, a vuoto | 86,09° | conforme |
| **Blocco B, 0 dB, 4,7 nF** | **56,46°** | **−3,5°** → NC-021 |
| **Blocco A, carico canonico** | **41,98°** | **−18°** → NC-002, ora bloccante |

I due numeri **esistevano già** (L22 il primo, il gate G0 il secondo): il
requisito non ha scoperto niente, ha dato un confine a ciò che era sul tavolo.
Ed è ciò che NC-012 aveva previsto scrivendo che senza soglia «nessuna misura
di margine di fase può passare o fallire».

**La domanda è stata posta prima di scrivere**, perché NC-012 avvertiva che
una soglia senza il carico a cui si riferisce non sarebbe stata un requisito
migliore: fra «al carico reale» (oggi conforme), «anche a 4,7 nF» e «ovunque»,
la risposta è stata la più severa, scelta sapendo cosa comporta.

**Diciotto gradi non sono un ritocco.** Più compensazione costa banda e slew
rate; meno guadagno d'anello costa distorsione, che è metà della ragione per
cui ADR-003 ha scelto i discreti; una rete d'isolamento diversa dai 47 Ω tocca
E4 e ADR-008. **L12 cambia natura**: non più «misura coi valori veri» ma
«porta sopra soglia», e conviene farlo una volta sola per entrambi i blocchi.

Da leggere insieme a **NC-020**: il modello LS352 è più *lento* della parte
garantita, quindi questi margini sono pessimistici — ma di quantità ignota,
quindi non se ne può concludere che la parte reale passi.

**2. Il trim funziona solo a mute inserito, con interlock elettrico.** Due
comandi distinti, il mute abilita il trim; fuori mute agire sul trim non
cambia nulla, e il valore impostato resta applicato all'uscita dal mute.
Diventa il requisito **F8**.

Delle tre forme proposte è l'unica **falsificabile**: si applica il comando a
mute rilasciato e si verifica che non succeda nulla. Un vincolo di pannello
non si può provare, e un mute automatico avrebbe voluto temporizzazione, che
ADR-009 rende sgradevole.

Il trim di ADR-011 **non esiste ancora** — è **L16** — quindi l'interlock è
tutto da fare, ed è **NC-023**. Il punto delicato non è il permissivo: è
**quale contatto**. I relè di mute sono a riposo in mute (ADR-012), quindi
l'alimentazione delle bobine del trim va presa dal contatto chiuso **in** mute.
È lo stesso tipo di errore che **NC-014** ha già prodotto sullo stesso relè,
per questo NC-023 prescrive la verifica **sulla netlist**.

**3. Tre livelli di guadagno: 0 / +3 / +10 dB, riposo a 0 dB.** Il salto
0 → +10 dB è grosso e il gradino intermedio serve. **Il principio di ADR-004
non cambia**: si commuta R_g verso massa, mai R_f, quindi l'anello non passa
per il relè e non si apre mai; con due rami verso massa il principio si
conserva per costruzione, e «riposo = 0 dB» lo rende esplicito — nessun guasto
di bobina può alzare il guadagno.

**Cosa costa, ed è la parte che non si vede dalla riga di requisito**: la
matrice V1 passa da tre a quattro configurazioni di blocco; **i dodici deck
spazzano due modalità e ne vogliono tre**, con la trappola di
`limitations.md` #10 che aspetta chi tocca i nomi `wrdata`; servono più relè o
più poli, quindi cambia il budget di corrente delle bobine per `psu-engineer`
e cambia il pannello; il diagramma a blocchi **calcola** il guadagno da
R_f/R_g e lo asserisce, quindi `check_schematic.py` va esteso. Le cifre
pubblicate a +10 dB restano valide — quel livello non cambia — ma nessuna
copre il livello nuovo. È **NC-022**, lotto **L27**.

**4. Cosa questo lotto NON ha fatto.** Nessuna riga di topologia:
`circuits/preamp/` non è stata toccata, ed è una proprietà del diff. Nessuna
misura nuova: ogni numero citato viene da misure già nel repo. Non ha deciso
come si recuperano i 18°, non ha dimensionato il gradino intermedio, non ha
scelto i relè. E **non ha toccato il dossier**, che pubblica ancora 56,945°
come caso peggiore — un numero della topologia col THAT320. Il dossier si
rigenera **una volta**, dopo la Fase 4.

## L25 — I cinque modelli entrano in `models/`. FATTO.

Report: `reports/2026-09-10-L25-promozione-modelli.md`. Chiude il **primo dei
tre passi di NC-017** (bloccante) e apre **NC-024** e **NC-025** (maggiori).

**1. La libreria passa da 28 a 38 check, e i lucchetti sono stati provati a
fallire.** MMBT5401, MMBT5551, MJE15032, MJE15033 e 1N4148 sono in `models/`
con la propria `.provenance.json`; cinque ricette nuove in
`validate_models.py` li **rimisurano** alle condizioni dei rispettivi
datasheet. 38 PASS, 0 FAIL, 0 SKIP; `run_tests.sh` 5/5.

La prova che conta non è il verde: è il **rosso ottenuto apposta**. Sei
falsificazioni su copie di scratch — `TF` +1,5%, `CJC` +3,3%, `BF` +1,3%,
`TF` +1,4%, `CJO` +2,5% e `BF` +23% — danno **sei FAIL su sei**, ognuno col
messaggio giusto. Un lucchetto mai fatto fallire non è un lucchetto.

**2. Promozione a rimozioni zero, che è più stretto di L6 e L22.** L'LSK489 e
l'LS350 erano trascrizioni a mano da PDF e avevano richiesto di togliere
`mfg=`. **Nessuno di questi cinque contiene `mfg=`**: il testo `.MODEL` è
byte per byte quello del costruttore, blocchi di commento e disclaimer di
licenza compresi. Verificato con `diff` sulle righe non-commento, cinque
file su cinque vuoto.

**3. La trappola nuova, e ha morso dentro il lotto: il tool di editing
normalizza CRLF → LF.** I cinque file vendor usano CRLF. Tre modifiche di
*sola prosa* alle intestazioni hanno riscritto ogni file per intero e tolto il
CR da **ogni riga del testo vendor**. ngspice non se ne accorge, `git diff`
mostra righe che a occhio coincidono, e l'unica cosa che l'ha detto è stato il
`diff` — `1,7c1,7` con sette righe apparentemente identiche.

Rimedio: le intestazioni si modificano **fuori** dal file e l'artefatto si
ricompone sempre con `cat intestazione vendor > modello`. Sta scritto in
ognuna delle cinque intestazioni, perché il file ha davvero due convenzioni di
fine riga dentro ed è deliberato. È la famiglia del `Reference value` di
`fourier` (L3) e dei tag casuali di SKiDL (L3b) — un campo che si muove dentro
un artefatto per il resto deterministico — con la differenza che qui **non è
il generatore a non essere riproducibile, è lo strumento con cui lo si edita**.

**4. L'armatura ha imparato a leggere più di un file per modello.** f_T, C_obo
e C_T sono grandezze in alternata, h_FE e V_F in continua, e `wrdata` scrive
un plot per volta. Un builder può ora restituire una **lista** di output; le
quattordici ricette vecchie non sono state toccate e il conteggio resta di un
check elettrico per modello. Più una correzione indipendente: **gli output si
cancellano prima di lanciare ngspice**, altrimenti un deck che non scrive un
file lascia in piedi quello della run precedente — un verde per una run che
non è avvenuta.

E una guardia che nessuna ricetta precedente aveva: **la polarizzazione della
f_T si autoverifica**. La corrente di base è fissa, quindi smette di produrre
la corrente di collettore giusta appena un parametro cambia; ogni ricetta
scrive perciò la I_C che l'`op` produce davvero e **rifiuta** se non è quella
del datasheet. Non è cerimonia — è esattamente ciò che è andato storto in L24.

**5. Due cifre di L24 non riproducono, e la causa è il metodo.** Delle sedici
cifre rimisurate, undici tornano; quattro f_T no, e un «non raggiunto» si
raggiunge.

**La f_T del MMBT5401 era presa alla corrente sbagliata.** L24 e ADR-017 danno
169,5 MHz; con I_C **verificata** a 10,000 mA la risposta è **160,1 MHz** su
tre gambe concordi. Il numero di L24 si riproduce *esattamente* pilotando una
corrente di base tonda di 100 µA — che questo modello trasforma in I_C =
12,68 mA, il **27% sopra** la corrente del datasheet. Verdetto invariato
(minimo 100 MHz), numero spostato del 5,5% — ed è il numero su cui poggia la
discussione del polo dominante, perché il MMBT5401 è il VAS.

**6. La f_T dei due MJE cambia verdetto, non decimale → NC-025.** La **Nota 2**
del datasheet MJE15032/D dice `fT = hfe · ftest` e la riga di prova dà
**ftest = 1,0 MHz**: la f_T garantita è il prodotto guadagno-banda misurato a
1 MHz, non l'attraversamento a |hfe| = 1. A 1 MHz questi dispositivi stanno
solo ~2,6 ottave sopra il proprio polo di beta, quindi le due letture non
coincidono:

| | a ftest = 1 MHz (il datasheet) | attraversamento \|hfe\| = 1 |
|---|---|---|
| MJE15032 | **27,667 MHz** — 7,8% sotto i 30 min | 30,713 MHz — dentro |
| MJE15033 | **29,286 MHz** — 2,4% sotto i 30 min | 30,719 MHz — dentro |

Letta come il costruttore la definisce, **nessuno dei due raggiunge il proprio
minimo**. L24 aveva registrato 31,04 e 31,38 MHz e li aveva letti come dentro.
Direzione **pessimistica** — il modello è più lento della parte garantita —
quindi le cifre in alta frequenza sono conservative, ma di quantità non nota.
Da leggere insieme a NC-020: **tre dispositivi su sette** portano ora un
modello più lento del proprio minimo pubblicato.

Le due correzioni insieme dicono una cosa sola: **le condizioni di prova sono
metà del numero, e la definizione della grandezza è l'altra metà.**

**7. NC-024 — l'h_FE del MJE15032, che era misurato ma non a registro.**
66,389 a I_C = 0,5 A contro un minimo di 70, fuori del 5,1%. È di L24, e
riprodotto qui alla terza cifra; quello che mancava era la **voce nel
registro**, cioè il posto in cui una discrepanza genera lavoro invece di
restare in una ADR. NC-013 e NC-020 sono la stessa forma e ce l'hanno.

Con la voce va una correzione: l'h_FE a **2,0 A**, che L24 dichiarava «non
raggiunto», si raggiunge — era l'estensione del suo sweep di base, non una
proprietà del modello, che spazzato fino a V_b = 1,6 V arriva a I_C = 6,8 A in
modo liscio. Vale **53,488** contro un minimo di 10: dentro.

**8. NC-004 non si muove, e il perché è ora esatto.** Nessuno dei cinque ha
`KF`/`AF` — i due MJE lo scrivono esplicitamente (`KF=0 AF=1`), gli altri tre
non li nominano. **Nel repo solo `models/jfet/lsk489.lib` ha rumore 1/f**,
cioè sei modelli vendor su sette non ce l'hanno.

**9. Il punto raggiunto, e non è lusinghiero.** Tutti e sette i dispositivi
attivi del percorso di segnale hanno ora un modello del costruttore in
`models/` — prima volta da G0. Ma su sette modelli, **quattro portano una
deviazione dal proprio datasheet** (LSK489/NC-013, LS352/NC-020,
MJE15032/NC-024 e NC-025, MJE15033/NC-025) e i tre puliti sono MMBT5401,
MMBT5551 e 1N4148. Le deviazioni vanno tutte nella direzione sicura, di
quantità non nota.

**10. Cosa il lotto non ha toccato, verificato sul diff.** Niente
`circuits/`, niente `spice/preamp/`, niente `docs/preamp/data/`; nessun file
di `vendor/` modificato. La sostituzione in topologia è **Fase 4**, ed è
l'unico passo che tiene aperta NC-017.

## L21 — Il polo 2 del relè, corretto e riverificato. FATTO.

Report: `reports/2026-09-11-L21-polo-2-rele.md`. Chiude **NC-014**
(bloccante), apre **NC-026** (maggiore).

**1. La correzione è una riga, e il diff lo dimostra.**
`circuits/preamp/preamp_audio.py:79` diventa
`K_COM2, K_NO2, K_NC2 = "6", "5", "7"`. Rigenerata la netlist, il **diff
normalizzato** (tolti `(date`, `SKiDL Tag`, `SKiDL Line`, `(tstamps` — L3b)
tocca **quattro numeri di pin e nient'altro**. Sulla netlist, che è dove la
verifica conta:

| Relè | Ruolo | Pin a massa | Prima |
|---|---|---|---|
| K1 | guadagno | **4, 5** (i due NO) | 4, 7 |
| K2, K3, K4 | mute | **2, 7** (i due NC) | 2, 5 |

**2. Il pinout riletto alla fonte, tre gambe concordi.** Non ereditato da L8,
perché L25 aveva appena mostrato cosa costa fidarsi di una cifra del lotto
precedente. Render della pagina a 1200 dpi; coordinate vettoriali via
`pdftocairo -svg`, dove alla quota delle punte l'armatura passa a **0,44 pt**
dal proprio contatto NC e a **3,39 pt** dal NO — rapporto 7,6:1, su
**entrambi** i poli; e le polilinee del simbolo KiCad `G6K-2`, dove la punta
dell'armatura ha la **x esatta** del contatto NC e dista 3,81 mm dall'altro.
La misura riproduce quella di L8 alla terza cifra.

Un passo falso vale la pena registrarlo: il primo ritaglio era la riga
**G6K-2G-Y**, non la nostra. Le cinque varianti hanno diagrammi identici a
occhio e il nome sta fuori dal ritaglio.

**3. La trappola, detta bene.** Entrambe le armature riposano sul pad
immediatamente **a sinistra** del proprio COM — il disegno è geometricamente
simmetrico. Ma la riga alta è numerata **8-7-6-5** e quella bassa **1-2-3-4**,
in versi opposti: «il vicino di sinistra» è il 7 in alto e il 2 in basso. La
simmetria che l'occhio vede è reale; è la **numerazione** a non essere
simmetrica, ed è per questo che «NO = COM+1» è giusta per un polo e sbagliata
per l'altro. Ora è scritta per esteso sopra la riga che l'errore ha prodotto.

**4. A chiudere la voce è il guardiano, non la correzione.** Un difetto che
fallisce in silenzio nel verso che manda il transitorio d'accensione sulle
cuffie non è chiuso da una verifica una tantum.
`scripts/check_relay_safe_state.py` legge **solo la netlist generata** e
asserisce l'**intento delle ADR** — mute diseccitato ⇒ uscita a massa
(ADR-012), guadagno diseccitato ⇒ `R_g` flottante (ADR-004), e i due poli
cablati nello stesso modo (T3/ADR-006). Il pinout del datasheet ci sta come
**dato citato**: scrivere le regole come «il pin 7 sia a massa» avrebbe solo
spostato l'ipotesi altrove, e scritte così l'inversione fa scattare **tutte e
tre** le famiglie invece di una.

Gira nel blocco **2e** di `run_tests.sh`: la suite passa da 5 a **6 blocchi**,
6 passed / 0 failed.

**5. Il guardiano è stato fatto fallire**, e la falsificazione più autentica
era già sul disco: la **netlist di prima**. Dà 12 rilevazioni, **tutte e sole
sul polo 2**. Più quattro casi sintetici — un relè senza ruolo nel valore,
nessun relè noto (che **non passa**, perché un controllo che esce 0 quando non
ha trovato niente è decorativo), una bobina scollegata. E la suite intera,
puntata sulla netlist di prima, dà **5 passed / 1 failed**.

**6. Due difetti trovati scrivendolo, entrambi della famiglia «passa
sempre».** Il parser spezzava le net con un look-ahead sulla successiva e
perdeva quindi **l'ultima net del file** — che è `VRELAY`, cioè *tutte le
bobine*. L'ha detto solo l'asserzione che le bobine siano collegate: senza,
avrebbe riportato un pass pulito su una netlist che non aveva finito di
leggere. E il blocco 2e, scritto come `checker | sed` per indentare l'output,
avrebbe restituito lo stato d'uscita di **`sed`**: verde qualunque cosa
dicesse il controllo. Entrambi corretti e annotati sul posto.

**7. NC-026 — il disegno a blocchi non gira da L22.** Il piano prevedeva di
rieseguire `schematic/preamp_blocks_draw.py` come controllo indiretto. Non
gira: `KeyError: 'R237'`. Quattro riferimenti sono rimasti a prima dello
scarto di **−1** che L22 ha prodotto fondendo le due Part dell'LS352 —
`R237`/`R437` e `R239`/`R439` sono oggi `R236`/`R436` e `R238`/`R438`.

**Non è un difetto di L21**: verificato sulla netlist di *prima*. È rimasto
invisibile perché il diagramma a blocchi **non ha manifesto** — per scelta
dichiarata al §L1 — quindi il blocco 2d non lo copre e **nulla lo esegue**.

L'estensione è stata **misurata**: coi quattro rinomini su una copia di
scratch lo script gira pulito, tutte le sue asserzioni passano (guadagno
ricalcolato **+9,963 dB**, dentro E2), e l'SVG che ne esce differisce dal
committato per **una sola cifra** — `205 componenti` contro **201**. Quindi il
disegno non è sbagliato sul circuito: è fermo all'8 settembre e sbaglia il
conteggio. Il danno è che **la garanzia dichiarata in `architecture.md` non è
più in vigore**. Non corretto qui: è un artefatto di disegno dentro un lotto
sui relè, e il mandato aveva fenced fuori le altre voci.

**8. Una bloccante in meno, ed è la seconda volta da G0.** Restano NC-001
(L11), NC-002 e NC-021 (L12), NC-004, NC-010 (L17), NC-017 (Fase 4). La prima
volta fu L22, per una parte trovata; questa è la prima per una **correzione di
topologia**.

## L10 — Il simbolo dell'LSK489, e due deck rotti da L22. FATTO.

Report: `reports/2026-09-13-L10-simbolo-lsk489.md`. Chiude **NC-026**, apre
**NC-027** (minore). Dati: `data/2026-09-13/`.

**1. Il pinout, letto e non dedotto.** Datasheet congelato (Rev A40), pag. 1,
«SOIC-A Top View»: **1=S1 2=D1 3=SS 4=G1 5=S2 6=D2 7=SS 8=G2**. È un raster a
96 ppi: guardato a 600 e 1200 dpi. **La trappola:** i JFET dentro il package
sono disegnati **ruotati** — la barra orizzontale è il canale, D e S la
raggiungono dallo stesso lato e il gate dall'altro — e letti come JFET
verticali sembrano scambiare D e G. Il datasheet LSK389, che l'LSK489 dichiara
«pin compatible», disegna lo stesso simbolo in vettoriale: usato per
controllare la lettura, **mai** come fonte. URL e sha256 nel report.

**2. SS non è definito per l'LSK489 → NC-027.** L'unica definizione trovata,
«SS: SUBSTRATE, LEAVE THESE PINS FLOATING (N/C)», è stampata per l'**LSK389**
(datasheet Rev A27 pag. 7; Data Book pag. 15). I pin 3 e 7 restano
scollegati, come erano di fatto; nel simbolo sono `passive`, non `no_connect`.

**3. Una Part, verificata sulla netlist.** `library/preamp.kicad_sym` ha il
simbolo LSK489 a tre unità (A, B, SS); `kicad-cli sym upgrade` exit 0, `sym
export svg` disegna le 3 unità. Due `spice_dev(..., suffix=)` danno `JQ110A` e
`JQ110B`.

| | prima | dopo |
|---|---|---|
| `gain_block.net` su SOIC-8 | 3 | **2** |
| `preamp_audio.net` componenti / su SOIC-8 | 201 / 12 | **197 / 8** |

**4. La mappa, ricavata.** `.inc` 44 → 44, e l'insieme delle righe vecchie
rinominate è **identico** al nuovo. `tb_op.cir` **81 valori su 81 identici**,
`tb_blockA_carichi.cir` 8 CSV su 8 identici byte per byte. Sulla netlist
completa la mappa è fallita la prima volta per una ragione nuova: **SKiDL
nomina le net fuse in modo non riproducibile** (`limitations.md` #23) — stesso
codice, due rigenerazioni, nomi diversi, membri identici. Ancorata ai
componenti di canale, dà la stessa mappa su entrambe.

**5. Due deck rotti da L22, in silenzio.** Trovati facendo la baseline
*prima* di toccare niente:

| deck | guasto | prima | dopo |
|---|---|---|---|
| `tb_switch_v2_counterfactual.cir` | `alter r138`: R138 non esiste da L22, ngspice esce 0 | anello «aperto» −0,0522 V, identico al chiuso | **−13,773 V** |
| `tb_bias_sweep.cir` | `alter r130`: da L22 è l'**altro** ramo dello spreader | I_q 5,207 mA a 1690 Ω, e scende con R | **14,714 mA**, = `tb_op`, e sale con R |

Correzione in **due passate**: prima i nomi vecchi portati a quelli di oggi,
poi la mappa di L10. Alla cieca, la mappa di L10 avrebbe trasformato `r138` in
**R_g** — un nome vivo sbagliato, invisibile a ogni controllo.

**6. Due blocchi di suite, fatti fallire prima.** **2f** esegue il disegno a
blocchi (NC-026: *chi lo esegue?*) — sui file di prima `KeyError: 'R237'`.
**2g**, `scripts/check_deck_refs.py`, pretende che ogni dispositivo citato da
un deck esista — sui deck di prima 2 rilevazioni, entrambe `r138`. Suite prima
della rimappatura **6 passed / 2 failed**, a lavoro finito **8 passed / 0
failed**. **Il 2g non vede il caso di `tb_bias_sweep`**: un nome esistente ma
sbagliato. Scritto in `limitations.md` #22, non sottinteso.

**7. Cosa NON è stato verificato.** Le quote del SOIC-A (non sono nel
datasheet congelato); SS (NC-027); nessun'altra cifra del blocco.

## L14 — Le tre correzioni di testo. FATTO.

Report: `reports/2026-09-13-L14-correzioni-di-testo.md`. Chiude **NC-003**,
**NC-006** e **NC-007**, tutte minori. Nessun numero del circuito toccato,
nessuna misura nuova: il dossier legge ancora `data/2026-09-09/`.

**1. Baseline prima di toccare.** Il dossier rigenerato **senza modifiche**
lascia `git status` vuoto. La rigenerazione è quindi riproducibile, e il diff
successivo contiene solo il lotto. `run_tests.sh` dà 8 passed / 0 failed.

**2. NC-006: la cifra riletta, non copiata.** La voce citava
`data/2026-09-09/tb_op.log`, che è la topologia col THAT320. `tb_op.cir`
**rieseguito oggi** dà 81 valori su 81 identici a
`data/2026-09-10/tb_op-LS352.log`; cambiano solo i nomi di 47 righe, per la
rinumerazione di L10. Quel log descrive dunque il codice di oggi, e i commenti
di `gain_block.py` 314-315 e 320-321 lo citano insieme ad ADR-014:
`v(ncasc) = 9.887 V`, drain a 9,21 V. La riga 153 resta. **Che nessuna riga di
codice sia cambiata lo prova l'AST**: `ast.dump` identico fra HEAD e il file
nuovo, stesse 648 righe, e il controllo fatto fallire su una copia con
10.0k → 10.1k. Con le stesse righe i `SKiDL Line` delle netlist committate
restano veri, quindi non c'era niente da rigenerare.

**3. NC-007: due cifre, ognuna col suo nome.** Dai `print` di `tb_ac.log`, e
ricalcolate in modo indipendente dai CSV:

| Modalità | scarto assoluto 1 kHz | scarto assoluto 20 kHz | **20 kHz rif. 1 kHz (la claim)** |
|---|---|---|---|
| 0 dB | −0,02167 dB | −0,02163 dB | **4,35·10⁻⁵ dB** |
| +10 dB | −0,02167 dB | −0,02154 dB | **1,37·10⁻⁴ dB** |

Lo scarto assoluto è il partitore con la Zin: uguale a ogni frequenza, e ci
sarebbe anche senza cascode. Il KPI cita ora il **peggiore delle due
modalità**, 1,37·10⁻⁴ a +10 dB, e dice che è il peggiore: la lezione di NC-003
applicata alla voce accanto. `build_dossier.py` ha una funzione `adr014()` che
produce entrambe le cifre dai valori già passati da `check()`. La seconda copia
della cifra, nella tabella di `data/2026-09-09/README.md`, ha preso una **nota
datata** e non una riscrittura.

**4. NC-003.** Il KPI dice «Margine di fase, blocco B — 56,945 gradi · peggiore
dei 4 casi pubblicati». La sezione 6 si apre dicendo che i dati d'anello sono
tutti del blocco B e che il blocco A non è pubblicato (NC-002). La riga V1 e il
titolo di `fig_loop.svg` sono qualificati. Che `tb_loop.cir` sia il blocco B è
stato **letto nel deck**, non dedotto.

**5. Letto il prodotto, non il sorgente.** Il diff di `index.html` tocca il
KPI, la sottosezione ADR-014, l'apertura e la chiusura della sezione 6 e la
riga V1, e **nessun altro numero**. `fig_loop.svg` cambia solo nel titolo.
`dossier.summary.json` ha le chiavi rinominate secondo ciò che misurano, e nel
repo nessuno lo legge. Suite a lavoro finito: **8 passed / 0 failed**.

**6. Cosa resta com'è, deliberatamente.** La sezione storica L5 di questo file
dice ancora «ADR-014 regge: 0,022 dB»: è storia. Il riepilogo in coda a
`gain_block.py` («0.0001 dB», riga ~551) è arrotondato ed è compatibile con
entrambe le cifre.

**7. Un esemplare in più della famiglia dei percorsi cablati, visto e non
toccato.** `testbenches/01_op.cir:10` fa `wrdata /Users/roberto/EDA/results/01_op.csv`.
Quindi il blocco **2b** di `run_tests.sh`, eseguito da un worktree, trova il
proprio wrdata nel **checkout principale**: lo stampa, «found wrdata output:
/Users/roberto/EDA/results/01_op.csv». Passa lo stesso, perché il CSV della run
viene riscritto nella directory giusta. Non era di questo lotto.

## L15 — Il vincolo su E3 scritto accanto a E3. FATTO.

Report: `reports/2026-09-13-L15-vincolo-e3.md`. Tocca **NC-005** (minore) per
la metà che le compete: il vincolo scritto. **La voce resta aperta** per la
misura AC, che è di L16. Nessun numero del circuito, nessun codice, nessuna
misura.

**1. Il vincolo e dove sta.** `REQUIREMENTS.md`, riga E3 qualificata e
**«Nota su E3»** sotto la tabella elettrica, nella forma della nota su E5:
Zin al connettore d'ingresso, blocco A collegato, **≥ 100 kΩ in ciascuna delle
tre posizioni del trim**, deciso sul minimo di |Zin| in 20 Hz–20 kHz. La nota
porta i due fatti che L16 dovrà conciliare: l'attenuazione portante di ADR-015,
e la resistenza di Thévenin del partitore (≥ 25,0 kΩ a −6 dB, ≥ 18,8 kΩ a
−12 dB, a Zin minima), che è rumore contro E5 e sorgente a monte in V1.

**2. Perché non in ADR-011.** Letti col loro commit, i quattro addendum hanno
tutti 0 righe rimosse e sono tutti del 2026-09-08. **Due su quattro superano un
valore deciso**: ADR-007 da 2,2 a 4,7 µF, ADR-008 da ~100 a 47 Ω. È il caso
che la regola 2 manda a una ADR nuova. Il precedente **dopo** le regole è
ADR-019, una ADR nuova che aggiunge una condizione ad ADR-011. I precedenti
provano quindi che la forma è stata usata, non che sia ammessa.

**3. Perché nessuna ADR.** Criterio scritto: una modifica ai requisiti è
sostanziale se **cambia l'insieme dei progetti conformi**. E3 nasce dal
condensatore del phono, che vede il connettore, trim compreso: un trim da
13 kΩ violava già E3. La nota dice dove si misura, non cosa si chiede.

**4. Trovato leggendo.** F2 e ADR-011 dicono «a ponticello», F8/ADR-019
presuppongono **relè**: il vincolo è scritto indipendente dal meccanismo, e
l'allineamento di F2 è nella riga di L16. Una clausola di NC-009 diceva che le
resistenze alte «caricano la sorgente», cioè il contrario: corretta.

**5. Le cifre rieseguite, e il controllo fatto fallire.** Controesempio
10 k / 3,3 k con `R_IN`: **13 289 Ω**, −12,13 dB. La Zin di oggi è `R_IN`: una
sorgente da 2500 Ω su 1 MΩ dà −0,02169 dB, contro il −0,02167 di L14. Il verbo
del vincolo applicato in python passa la sola `R_IN` e **rifiuta** il
controesempio; con l'aspettativa invertita segnala l'errore. Un caso in più,
utile a L16: **50 k / 50 k con `R_IN` fa 97,62 kΩ e fallisce**, quindi
R1 + R2 = 100 kΩ non basta.

**6. Visto e non toccato.** L'indice di `decisions/README.md` si ferma ad
ADR-016. Il diagramma in `REQUIREMENTS.md` dice ancora «0/+10 dB».

## L18 — Il vincolo PSRR scritto dove verrà letto. FATTO.

Report: `reports/2026-09-13-L18-vincolo-psrr.md`. Tocca **NC-011** (maggiore)
per la metà che le compete, il vincolo scritto. **La voce resta aperta** per
il rimedio e la verifica, che sono del lotto dell'alimentatore.

**1. Chi aveva già deciso.** `gain_block.py:571-572` e
`reports/2026-09-08-fase2-bozza-topologia.md:170-174` (commit `d9ca07f`)
consegnavano a `psu-engineer` una quota di **1 µV in uscita**: «≤ 1 mV pk a
100 Hz su V+». Stava in un commento, con cifre del THAT320, e mescolava picco
e RMS. L18 la rende vincolo senza cambiarne l'ordine di grandezza.

**2. Le cifre rilette.** `tb_zout_psrr_noise.cir` rieseguito dal worktree.
- Due prove che ha letto la topologia di oggi: le `.include` risolte e il
  rumore WORST CASE a **4,230582 µV** (LS352, non 5,697).
- Rail +: si muove al più di **0,107 dB**.
- Rail −: perde fino a **4,74 dB** in bassa frequenza (a 100 Hz, +10 dB:
  79,02 → 74,37). La causa non è stata inseguita.
- La modalità +10 dB è la peggiore su tutti gli 81 punti di entrambi i rail.
- Log e 4 CSV versionati in `data/2026-09-13/`, con lo scarto nel README.

**3. Dove.** Col criterio di L15 la quota è **sostanziale**: un progetto con
5 + 5 µV passava E5 e ora non passa più. Quindi **ADR-020** (sola riga 020
nell'indice), più la **«Nota su E5 — la quota del ripple d'alimentazione»** in
`REQUIREMENTS.md` e il rimando nelle righe E5 ed E7, dove guarda chi progetta
l'alimentatore. Nessuna aggiunta in coda ad ADR-010 o ADR-015.

**4. Il verbo.** √(Σ_rail Σ_k [V_rail,k · 10^(−PSRR(f_k)/20)]²) ≤ 1 µV su
20 Hz–20 kHz, col PSRR minimo fra le modalità. Rail + a +10 dB, tutta la
quota su un tono: **1,28 mV** RMS a 100 Hz, **0,303 mV** a 1 kHz, **31,0 µV**
a 10 kHz, **15,5 µV** a 20 kHz; rumore bianco ≤ 190 nV/√Hz.

Fatto fallire su casi noti:
- 1 mV a 10 kHz sul rail + fallisce (32,3 µV);
- lo stesso tono sul rail − passa;
- 0,5 mV a 1 kHz fallisce col PSRR minimo e passa, a torto, con quello della
  modalità 0 dB;
- con l'aspettativa invertita, lo script segnala l'errore.
- Il precedente di Fase 2 dà 0,551 µV.
- Un primo caso (d) mal dimensionato è stato fermato dal controllo stesso.

**5. La metà non di L18.** La scelta fra regolatore a bassissimo rumore e
moltiplicatore di capacità vuole dropout, calore e spettro di un alimentatore
che non esiste, e il mandato lo esclude. Lo stesso vale per il limite sopra
20 kHz: a 100 kHz il PSRR+ vale 10,20 dB, e E5 non può dare quel numero.

**6. `gain_block.py`.** Il commento PSRR riporta le cifre LS352 con la fonte, e
il rimando a `psu-engineer` punta ad ADR-020. `ast.dump` è identico a HEAD, 648
righe su 648, e il controllo è stato fatto fallire con 6.81k → 6.82k.

**7. Visto e non toccato.**
- `build_dossier.py:32` ha `DATA_DATE = "2026-09-09"`: il dossier pubblica il
  PSRR del THAT320.
- `gain_block_draw.py:468` scrive «59,5 dB a 1 kHz».
- In NC-001 le righe citate di `preamp_audio.py` e il nome `q134` non
  corrispondono più al codice di oggi; è annotato nel mandato di L11.

## Il dossier: prima bozza consegnata in L5b

**Riassunto per l'utente, 2026-09-11**:
`dossier/2026-09-11-executive-summary.md` — una pagina, in parole povere, su
cosa manca per dire finito il progetto. Datato come i report: è vero della
data che porta, non si aggiorna in luogo. Richiesto dall'utente dopo L21.

**Il dossier non è negoziabile, e non si taglia per arrivare prima a G1.**
Detto dall'utente il 2026-09-08 («il dossier per me è estremamente
importante»), in risposta a una stima in giornate uomo in cui era stato
proposto un percorso corto che saltava L3-L5. La proposta era razionale
sul tempo e sbagliava l'obiettivo: **L3-L5 sono l'infrastruttura del
dossier**, quindi stanno nel percorso, non fra gli extra.

Se il cap di token stringe si rallenta l'ordine dei lotti — non si toglie
il dossier. Questa nota esiste perché la proposta di tagliarlo è già
stata fatta una volta, e senza un divieto scritto verrebbe rifatta.

L'utente vuole poter **guardare** il progetto. Formato **deciso con lui**,
da non riproporre in altre forme:

- **SVG dentro il repository** come formato primario — è testo, quindi
  versiona e si confronta con `git diff`, e si apre in ogni browser
- **più una pagina** con schema e grafici impaginati insieme, da aprire
  da qualsiasi dispositivo
- **niente PDF**: se lo vuole su carta lo stampa dal browser. Detto
  esplicitamente

Contenuto previsto: lo schematico, i grafici delle misure (risposta nelle
due modalità, guadagno d'anello con il margine di fase segnato, PSRR dei
due rail, Z_out in frequenza, il transitorio del relè **affiancato al
controfattuale a −13,68 V**, recupero da sovraccarico), la tabella dei
punti di lavoro e le previsioni dichiarate.

La pagina ha senso **dopo** che ci sono grafici veri da impaginare: viene
dopo le misure, non prima. Il lavoro preliminare che la rende possibile è
L2-L5, ed è finito: **la prima bozza esiste da L5b.**

**L5b — la bozza del dossier. FATTO.** Sta in `dossier/`, si rigenera con

```sh
/usr/bin/python3 docs/preamp/dossier/build_dossier.py
```

e produce sei tavole SVG più `index.html`, che le impagina insieme allo
schema del blocco di guadagno e al diagramma a blocchi di L1. Dodici
sezioni numerate perché il revisore possa citarle.

**La regola che governa il generatore è quella di L1, più una rete in
più.** Nessuna cifra della pagina è scritta a mano: sono tutte lette dai
CSV versionati. E ogni quantità calcolata dal CSV viene **confrontata con
quella che ngspice ha stampato da sé** nel `.log` versionato accanto — due
strade indipendenti verso lo stesso numero, la mia interpolazione sui
campioni e il `meas`/`print` del simulatore. Se divergono oltre la
tolleranza dichiarata lo script **rifiuta e non scrive niente**, come
`export_fab.sh` sulla DRC, e non ha flag di bypass. Collaudato facendolo
fallire di proposito: spostando di 0,5 dB un punto vicino a 1 kHz dentro
`tb_ac_0db_1.5.csv`, il generatore rifiuta e nomina lo scarto.

**Il difetto trovato costruendola, ed è il motivo per cui costruirla
serviva.** `za100k` e `p100k` chiedevano `find … at=100000` su una
spazzata che *finiva* a 100 kHz: `meas … find at=` interpola fra due
punti, quindi sul bordo ngspice rispondeva «out of interval», il `print`
che segue falliva a sua volta, e **sei misure su sei sezioni non venivano
prodotte** — con il deck che proseguiva e usciva 0, quindi dal codice di
uscita il buco non si vedeva. Non era stato notato in L5 perché L5
guardava i file prodotti e il numero di righe, non il contenuto delle
tabelle. La spazzata arriva ora a **200 kHz**.

Effetto collaterale **misurato, non assunto**: con `dec 20 20 100k` la
spazzata copre 3,699 decadi e ngspice distribuisce 74 punti fra gli
estremi, quindi il passo reale era 0,0507 decadi, non 1/20. Con 200 kHz le
decadi sono 4 esatte, i punti 81, il passo esattamente 0,05. Si è mosso
solo `z1k` (58,84 → 58,76 Ω, −0,14%), e **non perché il circuito sia
cambiato**: 1 kHz non cade su un punto della griglia in nessuno dei due
casi, quindi `find at=1000` interpola fra vicini diversi. È la misura
dell'errore di interpolazione di `find at=` su 20 punti/decade: circa
0,1%. Tutto il resto varia in quarta cifra, quindi **nessuna cifra già
scritta altrove diventa falsa**.

**Un risultato di topologia che prima non era stato letto.** Le due
modalità non saturano allo stesso livello: a guadagno unitario v(FB)
insegue v(OUT), quindi il modo comune della coppia d'ingresso sale
*insieme* all'uscita ed è lui a fermarsi per primo, a **+9,37 V**; a
+10 dB v(FB) vale un terzo di v(OUT), il modo comune resta basso e
l'uscita arriva a **+13,2 V**. Il ramo negativo è invece limitato dallo
stadio d'uscita e coincide quasi nelle due modalità. È una proprietà della
topologia; i valori esatti dipendono dal modello del JFET, che è
segnaposto.

Nota di riconciliazione, perché due cifre diverse circolano: il dossier
riporta un margine E6×E2 di **0,55 dB** contro gli 0,75 dB registrati più
sotto. Non è il circuito che è cambiato, è la **metrica**: il dossier
prende il punto in cui il guadagno si scosta dell'1%, che arriva prima del
punto in cui la forma d'onda visibilmente tosa. È la lettura conservativa
delle due, e vanno riconciliate quando arriveranno i modelli vendor.

**Cosa manca ancora alla bozza**, scritto dentro la pagina stessa nella
sezione «Cosa questo dossier non dice»: i due transitori (commutazione del
relè e recupero da sovraccarico), perché i dati grezzi sono 2,8 e 1,9 MB e
non è deciso come versionarli; la distorsione, che senza modelli vendor
sarebbe priva di significato; il rumore, escluso per la stessa ragione di
L4; e la matrice V1, coperta in quattro casi su una matrice molto più
grande.

**Nota di scoping dell'utente**: non serve un disegno da 205 componenti.
Servono **il blocco di guadagno** (44 componenti, l'oggetto da giudicare,
usato quattro volte) — che esiste — e un **diagramma a blocchi** del
preamp intero, che è L1.

## L5d — G0 eseguito. FATTO.

Il primo gate del progetto è stato eseguito il 2026-09-09. Report in
`reports/2026-09-09-gate-G0.md` (830 righe), voci in `NONCOMPLIANCE.md`.
`design-reviewer` è partito **a freddo**, come agente nuovo e non come fork
dell'orchestratore, offline su `main` al commit `54ba2ae`.

**Esito: accesso a G1 non concesso.** Otto voci aperte — 2 bloccanti, 1
maggiore, 5 minori.

**La voce che vale il gate è NC-001**, e non era nota a nessuno prima. I
contatti NC dei relè di mute cortocircuitano a massa il nodo **jack**, cioè
a valle dei 47 Ω e del 4,7 µF. A mute inserito lo stadio d'uscita non vede
i 100 kΩ del carico ma **58,6 Ω**, e con i 2,7 V RMS di E6 la corrente nel
dispositivo d'uscita sale a **65,07 mA a 0 dB** e **203,2 mA a +10 dB**,
contro 14,56 mA di riposo: i due dispositivi si interdicono a turno e lo
stadio **esce dalla Classe A**, che è T1. E F6 impone il mute proprio
durante la commutazione del guadagno, cioè col segnale presente. La frase
in rosso su `gain_block.svg` — «14,71 mA di riposo: Classe A garantita» —
è falsa in quella condizione.

È il tipo di errore per cui G0 è stato inventato: il rimedio plausibile è
una **modifica di topologia**, e trovarlo dopo G1 sarebbe costato molto di
più.

**La seconda bloccante, NC-004**, è il rumore senza evidenza — attesa, ed è
il meccanismo che funziona come previsto: non blocca L6-L7, che sono il suo
rimedio.

**Tutti i numeri del revisore sono stati rieseguiti dall'orchestratore**
prima di essere riferiti: NC-001 riprodotta con un deck indipendente
(65,0677 / 203,210 mA), NC-002 riprodotta (41,982° contro 41,98°), NC-007
ricalcolata, il margine E6×E2 (+0,547 dB) reimplementato dalla definizione,
e tutte le tabelle del dossier riverificate contro i `meas` che ngspice ha
stampato da sé. La sezione «Verifica dell'orchestratore» in coda al report
la documenta. Nessuna divergenza sostanziale.

### La calibrazione: G0 **non** ha trovato l'errore del diagramma a blocchi

Va scritto per intero, perché è un risultato su G0 e non un incidente da
nascondere.

Il lotto conteneva un **controllo cieco**. L'utente aveva trovato un errore
nel diagramma a blocchi guardando il dossier e aveva chiesto esplicitamente
che non fosse l'orchestratore a cercarlo: doveva trovarlo il revisore, a
freddo. Con l'utente che conosce l'errore, l'orchestratore che non l'ha
visto e il revisore che parte senza contesto, quella voce era una misura
della **sensibilità reale** del gate.

**Il revisore non l'ha trovato.** Alla domanda 6 ha risposto «il diagramma a
blocchi non mente», dopo aver confrontato il disegno riga per riga con
`preamp_audio.py` e aver trovato corrispondenti tutti gli elementi che ha
elencato. Ha registrato un solo scostamento, sotto soglia (+9,96 dB sul
diagramma contro +9,97 dB nel codice, troncamento).

**E non è per non aver guardato.** Ha rasterizzato entrambi gli SVG con
`qlmanage`, e trovando che le miniature sono quadrate e tagliano il lato
lungo si è ritagliato il `viewBox` in copie temporanee per vedere i disegni
per intero. Sull'altro disegno la stessa procedura ha funzionato: ha
confrontato sette annotazioni numeriche di `gain_block.svg` con `tb_op.log`
una per una, e ha trovato **falsa** l'affermazione in rosso sulla Classe A,
che è diventata NC-001. Quindi il metodo trova errori nei disegni; su questo
disegno non ha trovato *quello*.

**Cosa impariamo.** G0 è sensibile a ciò che può **incrociare con una
sorgente**: un'etichetta numerica contro un `.log`, una connessione contro
la netlist. L'errore che l'utente ha visto è sopravvissuto a un confronto
riga per riga col codice, quindi delle due l'una: o sta in qualcosa che il
revisore ha verificato e ha giudicato corrispondente, o sta in una classe di
proprietà che nessuna sorgente del repo può falsificare.

**CHIUSO IN L5e: era la seconda.** L'utente ha detto qual è l'errore, ed è
che il diagramma mostra il **Blocco A che pilota tre carichi in parallelo**
— le due uscite fisse e l'attenuatore — senza isolamento reciproco, e
niente nel disegno o nel codice dice che quel parallelo è un problema.
Nessuna etichetta è falsa, nessuna connessione è sbagliata: il disegno è
**fedele** a `preamp_audio.py`. Non c'era niente da falsificare, ed è per
questo che il metodo di G0 non poteva arrivarci.

Il controllo cieco ha quindi misurato quello che doveva misurare: **G0 vede
le affermazioni false, non le omissioni di giudizio.** Da qui due cose
concrete, non due propositi: `AGENTS.md` ha ora una **settima domanda** che
chiede cosa il progetto presenta come normale e nessuna sorgente
contraddice; e l'omissione è diventata **NC-010**, bloccante, con la sua
evidenza misurata (vedi sotto).

## L5e — la revisione umana del dossier. FATTO.

Poche ore dopo G0 l'utente ha riletto il dossier per conto proprio e ha
prodotto **quattro osservazioni**. L5e le ha trasformate da messaggio in
registro: report datato
(`reports/2026-09-09-revisione-utente-dossier.md`), quattro voci in
`NONCOMPLIANCE.md`, quattro lotti qui sopra, e — per la sola che non aveva
evidenza — un banco nuovo coi suoi dati versionati.

**È l'altra metà della revisione, e ora si sa perché serve.** G0 confronta
affermazioni con sorgenti; la revisione umana vede ciò che il progetto
presenta come normale. Le due non si sovrappongono: G0 aveva prodotto otto
voci e nessuna di queste quattro.

**NC-010, la voce che vale il lotto.** Il Blocco A pilota tre carichi in
parallelo senza isolamento reciproco. Se l'apparecchio a valle di una
uscita fissa si spegne e la sua impedenza d'ingresso crolla — il caso che
**V1 elencava già** come «Singxer (Zin ignota)» e che nessuna misura
copriva — quel ramo diventa un carico da qualche decina di ohm sul nodo
d'uscita. Misurato con `spice/preamp/tb/tb_blockA_carichi.cir`, a 2,7 V RMS
e guadagno unitario:

| Impedenza a valle | I_C(Q134) max | I_C(Q134) **min** | Regime |
|---|---|---|---|
| 470 kΩ (normale) | 14,759 mA | **14,352 mA** | **Classe A** |
| 1 kΩ | 16,552 mA | 12,524 mA | Classe A |
| 100 Ω | 27,956 mA | **2,396 mA** | Classe A, margine quasi finito |
| 10 Ω | 57,258 mA | **−0,23 µA** | **Classe B** |
| 0,01 Ω | 65,456 mA | **−0,34 µA** | **Classe B** |

I due dispositivi si interdicono a turno: fuori dalla Classe A, che è T1.
**La soglia sta fra 100 Ω e 10 Ω** di impedenza a valle — fra ~147 Ω e
~57 Ω di carico totale contando i 47 Ω di separazione — ed è il numero che
dimensiona la decisione fra buffer dedicati e vincolo scritto.

Il picco a impedenza nulla, **65,46 mA**, è lo stesso ordine dei 65,07 mA
che NC-001 misura per il mute. Stessa fisica, **vie d'ingresso diverse**, e
questo decide il rimedio: una resistenza in serie al contatto del mute non
fa niente contro un apparecchio spento. Chi chiuderà NC-001 deve saperlo.

**Una metà dell'osservazione non è stata confermata, ed è scritta com'è.**
La modulazione reciproca del livello fra i rami vale **0,0034 dB a 1 kHz**
e 0,0056 dB a 20 kHz: l'anello chiuso tiene il nodo. Il danno non è sul
livello, è sul regime di lavoro — e una spazzata AC di piccolo segnale non
può vederlo. Registrare solo la metà che torna sarebbe la forma più comoda
di errore.

**Le altre tre voci non hanno richiesto misure nuove**, solo di rileggere i
dati già versionati con la domanda giusta:

- **NC-009**, headroom — ed è la voce che ha cambiato forma cercando prima
  se qualcuno avesse già deciso. **ADR-015 l'aveva deciso il 2026-09-08**:
  si resta a ±15 V e il margine si recupera col trim di ADR-011. Quindi il
  margine in sé **non è** una non conformità. Restano scoperte due cose:
  circolano **tre cifre** per la stessa quantità (0,75 dB clipping in
  ADR-015, 0,55 dB al limite dell'1% nel dossier, 0,59 dB con il guadagno
  misurato invece che nominale — 36% di differenza fra gli estremi), e
  soprattutto **il rimedio non esiste nel progetto**: il trim non è in
  `circuits/`, non è dimensionato, e porta ora due vincoli portanti che
  tirano in direzioni opposte — attenuare abbastanza (ADR-015) e lasciare
  la Zin ≥ 100 kΩ (NC-005).
- **NC-011**, PSRR: il rail positivo dà 29,76 dB a 10 kHz contro gli
  86,93 dB del negativo, **57 dB di divario**. Il numero era già
  pubblicato; quello che manca è che **non vincola nessuno**, e
  l'alimentatore non è ancora progettato.
- **NC-012**, margine di fase: cercata una soglia di accettazione in
  `REQUIREMENTS.md`, nelle quattordici ADR e in `AGENTS.md`. **Non
  esiste.** V1 enumera i casi da coprire e non dice quale valore sia
  accettabile: finché è così, nessuna misura di margine può passare o
  fallire, e NC-002 e NC-003 discutono di un confine che nessuno ha
  tracciato.

**Verifica del banco nuovo, perché è la parte che conta.** Ogni numero
della tabella è stato **ricalcolato dal CSV versionato** e confrontato col
`meas` che ngspice ha stampato da sé nel `.log`: coincidono su tutte le
cifre stampate. Il passo del transitorio è 5 µs, e il confronto con una run
a 2 µs dà differenze in quinta-sesta cifra. Inoltre l'osservazione
d'apertura dell'utente — il banco `tb_loop_blockA.cir` coi valori superati
— è stata **rieseguita per la seconda volta in modo indipendente**: 69,83°
/ 64,05° / 56,59° / **41,85°**, che coincide con NC-002.

## Dove siamo

**Fase 2 consegnata, e la pausa è finita.** Il progetto si era fermato —
non per un difetto, ma perché mancava all'ambiente una capacità che serve
a tutti i progetti: produrre qualcosa che un umano possa guardare. Quella
capacità ora esiste ed è verificata (`scripts/check_schematic.py`, blocco
2d di `run_tests.sh`), quindi il lavoro riprende dalla lista dei lotti.

Verificato all'apertura della sessione del piano a lotti, non assunto:
`check_schematic.py` esce 0 con 44 dispositivi nella netlist e 44 nel
disegno; `run_tests.sh` dà 5 passed / 0 failed; `main` è pulito e allineato
a `origin`. **Le tre azioni "da fare" della vecchia sezione in volo (PR →
merge → pull) erano già state fatte**: la PR #8 è dentro `main`.

### Perché c'era stata la pausa

**Non si può rivedere un progetto che nessuno può guardare.** La
simulazione verifica i numeri; non verifica se il percorso del segnale è
corto, dove passa il ritorno di massa, o se una scelta di polarizzazione
convince chi conosce il dominio. Quel giudizio è dell'utente, e richiede
di *vedere* il circuito.

Finora l'ambiente non produceva nulla di guardabile: `generate_schematic()`
non è mai stato chiamato, e comunque darebbe un file illeggibile
(limitazione #5). E **non esiste alcuno strumento che pianifichi
automaticamente uno schematico analogico leggibile** — ricercato e
provato su ASG, lcapy e netlistsvg, vedi limitazione #16.

Non è un problema del preamp: si ripresenta identico con
l'**alimentatore**, il **phono** e il **finale**. Per questo è stato
risolto a livello di ambiente e non dentro `docs/preamp/`.

### Cosa è stato costruito

- `scripts/check_schematic.py` — confronta un disegno con la netlist
  **nelle due direzioni**: niente inventato, niente omesso. Collaudato
  facendolo fallire di proposito su dispositivo inventato, dispositivo
  omesso e pin cablato male.
- `scripts/run_tests.sh` blocco **2d** — scopre da solo ogni manifesto
  sotto `docs/*/schematic/` e lo verifica.
- Convenzione documentata in `../architecture.md`, sezione **"Revisione
  umana dello schematico"**.
- **La revisione umana dello schematico è ora precondizione di G1 e G2**
  (`../../AGENTS.md`).

Due difetti latenti di `run_tests.sh` sono emersi e sono stati corretti:
`ROOT` era cablato, quindi la suite eseguita da una copia isolata testava
**silenziosamente un altro albero**; e il controllo degli artefatti smoke
pretendeva file gitignorati, quindi la suite **non poteva passare su un
clone fresco**.

### Stato precedente

**Fase 2: bozza di topologia consegnata. In attesa della Fase 3.**

Le Fasi 0 e 1 sono chiuse. **Quattordici** decisioni sono in
`decisions/`.

`circuits/preamp/` **esiste ed è la fonte di verità**:

| File | Cosa |
|---|---|
| `gain_block.py` | il blocco di guadagno (ADR-006), 44 componenti |
| `preamp_audio.py` | due canali, quattro blocchi, relè condivisi (205 comp.) |
| `spice_export.py` | esportatore SKiDL -> ngspice |

I banchi di prova stanno in `spice/preamp/tb/` (11 deck) e i modelli
segnaposto in `spice/preamp/placeholder_devices.lib` — **deliberatamente
fuori da `models/`**, che resta a 24/24.

**Tutte le cifre prodotte in Fase 2 sono PREVISIONI da modelli
segnaposto scritti a mano.** Nessuna cifra di distorsione esiste: il
`.four` gira ma il suo risultato è privo di significato. La verifica
indipendente è la Fase 5.

**Esito Fase 1: la topologia regge — le parti esistono.** Il punto debole
non è l'approvvigionamento ma la **provenienza dei modelli SPICE**, cioè
l'opposto di quanto temuto. Vedi
`reports/2026-09-08-fase1-parti-critiche.md`.

**Il finale è stato identificato**: il cj Evolution 250 è un **MV50
riconfigurato in triodo**, 30 W, Zin 100 kΩ confermata dal manuale
ufficiale. La diagnosi di ADR-001 regge su tutto l'intervallo plausibile
di sensibilità. Vedi `reports/2026-09-08-identificazione-cj-ev250.md`.

## Il progetto in una frase

Preamplificatore di linea a **guadagno unitario**, Classe A pura a
componenti discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è stata identificata come causa misurabile della mancanza di
dinamica lamentata.

## Il piano

| Fase | Cosa | Owner | Stato |
|---|---|---|---|
| 0 | Requisiti | orchestratore + utente | **fatto** |
| 1 | Verifica parti critiche (JFET, BJT, modelli SPICE vendor) | `bom-component-manager` | **fatto** |
| 2 | Bozza di topologia in `circuits/preamp/` | `analog-topology-designer` | **fatto** |
| 3 | Giro componenti completo | `bom-component-manager` | da fare |
| 4 | Revisione della topologia alla luce dei componenti | `analog-topology-designer` | da fare |
| 5 | Misure (stabilità per prima) | `measurement-analyst` | da fare |
| 6 | Alimentatore + **sicurezza rete** — parte in parallelo dalla Fase 2 | `psu-engineer` | da fare |
| **G0** | Prima revisione del prodotto | `design-reviewer` | **fatto** — 8 voci, 2 bloccanti |
| **G0b** | Revisione umana del dossier | **utente** | **fatto** (L5e) — 4 voci, 1 bloccante |
| **G1** | Congelamento topologia | `design-reviewer` | **non accessibile** finché NC-001, NC-004 e NC-010 sono aperte |
| — | Layout → **G2** → fabbricazione → **G3** | | da fare |

**Perché la Fase 1 viene prima della bozza**: se i JFET complementari non
esistono, l'intero stadio d'ingresso cambia forma. Meglio saperlo prima
di disegnare tutto attorno a loro.

**Perché G1 viene dopo il giro componenti**: congela una topologia che
sappiamo costruibile con parti che esistono davvero, non una disegnata
sulla carta.

## Prossimo passo concreto

**L37 — E4 nel dossier.** Chiude **NC-033** (minore). Lotto **XS/S**. Il
mandato completo è in `NEXT-SESSION.md`.

**Perché adesso.**
- Non aspetta nessuno. Gli altri sì: L28 un documento del costruttore o una ADR
  (prima di G2), L29 una soglia dell'utente su V2, L36 e L35 aspettano L29, L30
  l'alimentatore.
- Il dossier pubblica oggi una Zout che contiene il segnale: KPI 58,76 Ω e
  1,0355 Ω «al nodo OUT», contro 57,945 e 0,0386 Ω veri.

**Dove parte.**
- `build_dossier.py` legge la Zout da
  `data/2026-09-14/L27/dopo/tb_zout_psrr_noise/`, misurata con la sorgente
  accesa (NC-033, limitazione #28).
- I dati giusti ci sono già: `data/2026-09-15/L13/dopo/`, cioè `tb_e4_uscite`
  sulle tre uscite e `tb_zout_psrr_noise` corretto.
- **Il dossier non pubblica niente di L20**, e L37 non lo aggiunge: resta un
  lotto su E4.

### Quello che il repo ti consegna già

- **Il dossier è rigenerato** (L32). `build_dossier.py` legge
  `data/2026-09-14/L27/dopo/` e `L16/dopo/` e rifiuta ogni percorso del
  2026-09-09. Confronta le tabelle `echo` riga per riga con le `print` o le `meas`
  del log, e la cifra di NC-009 con `headroom_nc009.py`. La provenienza dei
  modelli la legge dagli `.include`. Nove sabotaggi, tutti rifiutati. Rigenerarlo
  dopo un lotto che cambia i dati è un lotto a sé.

- **La suite è a 10 blocchi**, 10 passed a fine L20.
  - Il **2e** conosce MUTE, GAIN, PERMIT, TRIM e SPIA, e prova sulla netlist
    l'interblocco del trim (F8);
  - il **2f** asserisce tre guadagni, i rami in parallelo e le attenuazioni del
    trim;
  - il **2g** rifiuta i nodi di contatto non terminati (#27) e i vettori di
    rumore morti (L31);
  - il **2h** rifiuta un commento di deck che dichiara una provenienza diversa
    da quella dei suoi `.include` (L33). Un deck nuovo che copia un'intestazione
    la eredita: se la frase è sbagliata, il 2h cade;
  - il **2i** rifiuta un blocco derivato che non coincide con la derivazione
    fresca del blocco generato (L20).
- **L'LSK489 del costruttore si può simulare nel blocco** (L20).
  - `spice/preamp/derived/gain_block_flat_lsk489a.inc` è derivato da
    `scripts/derive_jfet_variant.py`.
  - `tb_idss_op_noise.cir` e `tb_idss_loop.cir` spostano `Vto` con `altermod`, e
    una JFET sonda misura la I_DSS simulata.
  - I deck di prima istanziano ancora `LSK489X`: la sostituzione è Fase 4
    (NC-017).
  - Il JFET è del **gruppo B**, con tolleranza 8,0–15,0 mA (ADR-031, «Nota su
    T4»).
- **Dieci relè** sulla scheda audio:
  - K1, K5 guadagno; K2–K4 mute; K6 permissivo;
  - K7, K8 trim; K9, K10 spie.

  Budget delle bobine: 126,6 mA a 5 V, in mute e fuori (ADR-027).
- **I conteggi**: 14 voci aperte, 2 bloccanti. L20 ha chiuso NC-013.
- **E4 è misurata su tutto** (L13): `tb_e4_uscite.cir`, tre uscite × 45 celle,
  e `tb_zout_psrr_noise.cir` con la Zout a sorgente spenta. Il dossier pubblica
  ancora le cifre vecchie: L37.
- **Da L34, requisiti nuovi che il circuito non soddisfa ancora**: F10 e F11
  (comandi e LED a pannello, NC-032), P8 (ingombro del telaio). E ADR-030, che
  si realizza solo se L29 lo giustifica.

**Poi**, nell'ordine:
- **L28** (SS dell'LSK489, NC-027) va fatto prima di G2.
- **L29** (NC-028, **esteso da L34**, ora M) aspetta una soglia dell'utente su
  V2, che si può chiedere in qualsiasi momento. È **sul cammino critico**: dal
  suo confronto fra cambio di guadagno a caldo e cambio sotto mute dipende
  **L36**.
- **L36** (ADR-030), **solo se L29 lo giustifica**: interblocco del guadagno con
  gli ausiliari e i LED del guadagno. Se L29 dice di no, «superata».
- **L35** (NC-032): comandi e LED a pannello nel sorgente, dopo L36, perché il
  comando del guadagno si cabla una volta sola.
- **L30** (NC-029) va col lotto dell'alimentatore e del telaio, **dopo L35 e
  L36**.
- **L'alimentatore**, quando arriva, parte da **ADR-020** e da NC-029. Deve
  anche:
  - dare corrente ai corti di P7, fino a ~200 mA di picco per blocco;
  - alimentare separatamente la parte digitale, se entra (ADR-022);
  - alimentare le bobine col budget finale di L35/L36 (fino a ~169 mA fuori
    mute a +10 dB, a 5 V, se L36 si fa);
  - dare il temporizzatore d'accensione, da combinare con l'interruttore di mute
    (ADR-028).

### Cosa cercare, e cosa NON accettare

Le regole sono **T7** e **T8** in `REQUIREMENTS.md`, il ragionamento sta in
**ADR-016**, e **ADR-017** è il precedente di come si applicano. In pratica:

- **un mirror di terze parti non conta.** Si congela ciò che il
  **costruttore** ha servito, con il suo URL e il suo hash — la stessa
  regola che ADR-013 impone per l'LSK489, e accettare un mirror qui la
  svuoterebbe là;
- **un modello pubblicato come PDF conta.** È il caso dell'LSK489: la
  procedura di trascrizione a due letture indipendenti esiste apposta;
- **lo stato di ciclo di vita si legge dal costruttore**, non dal
  distributore. È la lezione che è costata il THAT320 — e L24 l'ha vista
  mordere di nuovo: per il 1N4148 una ricerca dava «Active» da quattro
  aggregatori, e non è stata usata;
- **un modello che il costruttore serve ma che un contrattista ha
  scritto** conta comunque: i due MJE dichiarano «Model Generated by
  MODPEX / Symmetry Design Systems». Registrare l'autore non indebolisce
  la provenienza, **fa parte di cosa la provenienza è**.

### Le trappole già pagate, che valgono per il prossimo lotto

Ognuna è costata una scoperta:

1. **Il nome di un file non è la sua revisione** (L7):
   `pdftotext -layout <pdf> - | grep -i 'rev'`.
2. **Il nome di un file non è nemmeno la sua parte** (L24, #20). Si apre il
   modello e si legge l'intestazione **prima** di congelarlo.
3. **Il prefisso micro non sopravvive ai PDF onsemi** (L24, #19). Un limite
   di corrente sotto il milliampere va **guardato**, non estratto.
4. **Le condizioni di prova sono metà del numero** (L6), e attenzione a
   *quale tabella*: un Absolute Maximum Rating è una soglia di stress, non
   una caratteristica garantita (L8). E attenzione a *quale corrente*: L24
   ha misurato f_T **88,8 MHz a 2 mA** su una parte il cui datasheet
   dichiara 100 MHz minimi — a 10 mA.
5. **Un codice di stato non è una verifica** (#18). E su diodes.com **il nome
   del file nell'URL di un modello non è verificato dal server**: decide solo
   l'id, e la verità sta nel `name=` del `Content-Type` (L22, #21).
6. **Un costruttore può pubblicare due modelli della stessa parte** (#17).
   Quale si è usato va scritto accanto a ogni numero.
7. **Guarda cosa il repo ha già in casa prima di andare fuori** (L8): la
   risposta su quale contatto del relè fosse NC era disegnata nelle
   polilinee del simbolo KiCad, già sul disco.
8. **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto**
   (L24). La conclusione di L8 su Diodes era vera dei percorsi che aveva
   provato e falsa come affermazione generale, e ha tenuto ferme due parti
   per un lotto intero.

### Cosa resta di NC-004 dopo tutto questo

NC-004 (rumore e distorsione senza evidenza, bloccante) **non si chiude coi
modelli veri**, e da L24 si sa perché con precisione: **nessuno dei cinque
modelli congelati ha `KF`/`AF`**. Nel repo **solo l'LSK489 ha rumore 1/f**
— nella libreria `models/`, non nelle simulazioni: l'LSK489 simulato è il
segnaposto `LSK489X` con `KF = 0`, e oggi nessun dispositivo simulato ha 1/f
(NC-031, L33).

Quindi le cifre della Fase 4 saranno un pavimento senza flicker, e il
pavimento cade proprio dove l'analisi dice che il rumore è dominante — lo
specchio di corrente e le sue degenerazioni da 47 Ω. Da leggere insieme a
**NC-013** (il modello LSK489 descrive un esemplare d'angolo a bassa I_DSS,
quindi le cifre saranno conservative sul JFET). **Va scritto accanto ai
numeri, non sottinteso.**

### Materiale già raccolto per il giro componenti

Da non ricercare di nuovo.

- ~~**2N5401** (VAS) e **2N5551** (cascode, generatori, moltiplicatore di
  Vbe)~~ — **CHIUSA in L24.** Non si sostituiscono: **MMBT5401** e
  **MMBT5551** di Diodes Incorporated sono lo stesso die in SOT-23, con
  modello del costruttore e sei controlli incrociati su sei dentro le
  finestre. **ADR-017.** Resta la promozione in `models/` (L25) e la
  sostituzione in Fase 4.
- ~~**MJE15032/33 e 1N4148**~~ — **CHIUSA in L24.** Tutti e tre hanno un
  modello onsemi che ngspice esegue. MJE15032G **Active**; MJE15033G
  ordinabile ma **senza pagina prodotto**, lacuna dichiarata; 1N4148
  **Active**, attribuito a onsemi, modello in `1n914.lib`. Il MJE15032 sta
  **sotto il minimo hFE del proprio datasheet** (66,4 contro 70).
- ~~**Modello SPICE LSK489**~~ — **CHIUSA in L6-L7**: verdetto misto,
  **NC-013** → L20.
- ~~**THAT320**: stock e BVceo~~ — **CHIUSA in L8, con una sorpresa** (fine
  vita dal 2026-09-01 → NC-015), e **RISOLTA in L22**: sostituito da un
  **Linear Systems LS352**, dual PNP monolitico in SOIC-8, con la
  degenerazione portata a 220 Ω. **ADR-018.**
- ~~**Omron G6K-2F-Y**~~ — **CHIUSA in L8**: polo 2 invertito nel codice →
  **NC-014**, lotto **L21**.
- ~~**Simbolo KiCad dell'LSK489** (L10)~~ — **CHIUSA in L10.** Una Part a due unità (più i due pin SS), pinout letto dal datasheet congelato; su SOIC-8 restano l'LS352 e l'LSK489. Residuo: **NC-027**, la definizione di SS per questa parte.
- **La rosa dei componenti di segnale** (L9): **rinviata**, non restituisce
  un vincitore — restringe su basi misurabili e la scelta finale fra parti
  tutte buone è dell'utente, all'ascolto. È la ragione per cui esiste P6.

### Due tensioni fra requisiti, segnalate e non aggirate

1. **E6 × E2 contro E7.** 2,7 V RMS a +10 dB vogliono 8,54 V RMS in
   uscita; con rail a ±15 V il blocco clippa a 9,31 V RMS simulati.
   Margine 0,75 dB. Il rimedio è il trim, che con ADR-015 **non è più
   opzionale**: da L16 è comune e sta sul ramo variabile (ADR-027), e a −6 dB
   il margine sale a **+6,58 dB** (metrica M1, NC-009).
2. **E4 contro E8 a 20 Hz.** Con accoppiamento capacitivo la |Zout| al
   jack a 20 Hz è ~1,7 kΩ (è la reattanza del 4,7 µF). A 1 kHz è
   **57,94 Ω** a 0 dB, misurata a sorgente spenta in L13. Il 58,8 Ω scritto qui
   fino a L13 conteneva 1 V di segnale (NC-033, limitations #28). E4 letta alla
   lettera non è soddisfacibile a 20 Hz da nessun circuito con condensatore
   d'uscita. Il requisito la risolve già: «misurata escludendo la reattanza del
   condensatore». L13 la legge come Re(Z) al jack: ≤ **60,13 Ω** sulla
   principale, a 20 Hz, dove pesa lo scarico da 220 kΩ, e ≤ **53,13 Ω** sulle
   fisse.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| Condensatore verso il Singxer: 2,2 o 4,7 µF | utente | No |
| ~~Trascrizione e validazione del modello LSK489~~ | — | **CHIUSA**: trascritta in L6 (due letture byte-identiche), **validata contro il datasheet in L7** — I_DSS dentro la finestra, V_GS(off) **fuori di 0,376 V**, e non per un errore di trascrizione. Aperta NC-013; ADR-013 non riaperta |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale ufficiale. Da L5e **non è più solo una curiosità**: è l'ipotesi su cui poggia NC-010, perché da spento può andare a zero |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio |
| ~~Quale JFET d'ingresso~~ | — | **CHIUSA**: LSK489 (ADR-013) |
| ~~Conferma specifiche cj EV250~~ | — | **CHIUSA**: email costruttore + manuale MV50 |
| Il LED del trim legge i relè spia K9/K10, non K7/K8 che portano il segnale: un guasto meccanico di uno solo dei due (contatto incollato, bobina aperta) fa divergere LED e segnale. ADR-027 non lo elenca fra i casi da riaprire. Da L34 | utente | No. Vale anche per i LED del guadagno di ADR-030, letti dagli ausiliari |
| Soglia su V2: quanto gradino al jack è accettabile. Serve a L29, e ora anche alla decisione di ADR-030 | utente, all'apertura di L29 | Sì, L29 |
| Disponibilità e ciclo di vita dell'**LSK489B** (T8): ADR-013 cita 921 pezzi su DigiKey senza gruppo, e L20 non l'ha verificato. E se il costruttore pubblica un modello del gruppo B. Da L20, ADR-031 | giro componenti (`bom-component-manager`) | No, ma prima di G2 |

## Decisioni chiuse il 2026-09-08

| Cosa | Esito |
|---|---|
| Rail ±15 V o ±18 V | **±15 V** — ADR-015. Il trim di ADR-011 in modalità +10 dB **non è più opzionale** |
| Condensatore verso il Singxer | **4,7 µF su tutte e tre le uscite** — ADR-007 addendum. Chiude la domanda sull'impedenza ignota del Singxer |
| Resistenze di isolamento ADR-008 | **47 Ω** invece di ~100 Ω — soddisfa E4 con margine |

**Nessuna decisione dell'utente è pendente.** L'unica che il progetto
abbia mai avuto con una scadenza esterna — il last-time buy del THAT320 al
2026-09-30 — è stata **presa il 2026-09-10** e registrata in **ADR-016**:
il last-time buy è **scartato**, la parte si sostituisce, e da lì sono
nate le due regole generali **T7** e **T8**.

Quel che resta non è una decisione, è **lavoro**: quali parti sostituiscono
THAT320, 2N5401 e 2N5551, e se MJE15032/33 e 1N4148 debbano seguirle. Lo
decidono i lotti **L24** e **L22** cercando candidati che soddisfino T7 e
T8, non una domanda all'utente.

## Attenzione per chi riprende

`REQUIREMENTS.md` contiene ora una sezione **Requisiti di verifica**
(V1–V5). Non è burocrazia: il relè del guadagno commuta la rete di
controreazione, quindi **il margine di fase è diverso nelle due
modalità**, e l'impedenza dell'attenuatore varia con la manopola, quindi
**varia anche con la posizione del volume**. Se non si verifica tutta la
matrice, si verifica solo il caso in cui il circuito passa.

## Come è organizzata la documentazione

Tre cicli di vita, tenuti separati di proposito:

- **Vivi** — `STATE.md`, `REQUIREMENTS.md`, `NONCOMPLIANCE.md`.
  Riscritti, sempre veri al presente.
- **Immutabili** — `decisions/ADR-*.md`, i verdetti dei gate. Scritti una
  volta, mai corretti, solo superati da documenti nuovi.
- **Datati** — `reports/`. Output di un'esecuzione. Una misura è vera di
  una versione specifica del circuito: senza data è inutile.

I report di fase sono **cronaca**, non il posto dove si cerca il
"perché". Il perché sta nelle ADR.

## Da leggere per riprendere

1. Questo file.
2. `REQUIREMENTS.md` — cosa deve fare.
3. `reports/2026-09-08-analisi-catena.md` — la base di evidenza: i
   numeri della catena dell'utente e perché il progetto esiste.
   Poi `2026-09-08-identificazione-cj-ev250.md` (il finale è un MV50 in
   triodo) e `2026-09-08-fase1-parti-critiche.md` (cosa esiste davvero).
4. `decisions/README.md` e le ADR — perché il circuito è così.
5. `../../CLAUDE.md` — l'ambiente EDA, se non lo conosci.
