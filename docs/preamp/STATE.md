# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-10** (L8 e **L8b** chiusi. L8: le quattro parti nuove verificate alla fonte, **tre su quattro con una sorpresa** — THAT320 **fine vita**, polo 2 del relè Omron **invertito nel codice**, e nessun modello SPICE vendor per 2N5401/2N5551. L8b: l'utente ha risposto con **due regole di progetto**, registrate in **ADR-016** e come requisiti **T7** e **T8** — *niente parti a fine vita, niente dispositivi attivi senza modello del costruttore*. Il last-time buy del THAT320 è **scartato**: si sostituisce. NC-017 sale a **bloccante** e copre tutti e sette i dispositivi attivi, di cui **uno solo è conforme oggi**. 17 non conformità, **6 bloccanti** — l'accesso a G1 non è concesso. Prossimo lotto **L24**, T7 su tutti i dispositivi attivi; **L9 è rinviata** perché non sblocca niente)

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
| L10 | Simbolo KiCad dell'LSK489 | S | da fare |

**I lotti che le revisioni hanno generato.** È il meccanismo per cui una
non conformità produce lavoro invece di fermarlo: ogni voce aperta in
`NONCOMPLIANCE.md` arriva qui con il proprio lotto. I primi cinque vengono
da G0 (L5d), i quattro seguenti dalla revisione umana del dossier (L5e), e
l'ultimo — **L20** — dal controllo incrociato di L7, che è la prima voce a
nascere non da una revisione ma da un **controllo prescritto da una ADR**.

| # | Lotto | Dim. | Chiude | Stato |
|---|---|---|---|---|
| L11 | **Mute: misurare e rimediare.** Deck che misura I_C dei due dispositivi d'uscita a mute inserito + il transitorio di inserzione/rilascio; poi o la modifica di topologia o la ADR che accetta il regime | M | **NC-001** (bloccante) | da fare |
| L12 | **Blocco A: stabilità coi valori veri.** `tb_loop_blockA.cir` ai 47 Ω / 4,7 µF / 470 kΩ, capacità sul nodo OUT **e** sui jack, CSV versionati. Da fare insieme allo sweep d'impedenza di `tb_blockA_carichi.cir`: stesso blocco, stessi carichi | S | **NC-002** | da fare |
| L13 | **E4 sulle tre uscite e a manopola che gira.** Estendere `tb_zout_psrr_noise.cir` alle due uscite fisse e a tre posizioni dell'attenuatore | S | NC-008 | da fare |
| L14 | **Le tre correzioni di testo.** KPI del margine di fase qualificato, i due commenti di cascode allineati, lo scarto ADR-014 riferito a 1 kHz | XS | NC-003, NC-006, NC-007 | da fare |
| L15 | **Il vincolo su E3 scritto dove verrà letto** (nota di dimensionamento in ADR-011 o `REQUIREMENTS.md`) | XS | NC-005 | da fare |
| L16 | **Il trim entra nel progetto.** Dimensionarlo in `circuits/preamp/` coi due vincoli insieme — attenuazione richiesta da ADR-015 e Zin ≥ 100 kΩ — e misurarlo. Chiude anche NC-005. Più la riconciliazione delle tre cifre di margine nel dossier | S/M | **NC-009**, NC-005 | da fare |
| L17 | **Buffer sulle uscite fisse.** Modifica di topologia in `preamp_audio.py` che disaccoppia le due fisse dal nodo del Blocco A, più la riesecuzione di `tb_blockA_carichi.cir` sulla topologia nuova | M | **NC-010** (bloccante) | da fare |
| L18 | **Il vincolo PSRR scritto dove verrà letto**: quanto ripple può lasciare l'alimentatore sul rail positivo, ricavato da E5 | XS/S | **NC-011** | da fare |
| L19 | **La soglia di margine di fase in V1**, col carico di prova dichiarato accanto; poi i KPI del dossier riferiti a quella | XS | **NC-012** | da fare |
| L20 | **Quanto il progetto dipende da I_DSS.** Rieseguire punto di lavoro e rumore del blocco di guadagno con `Vto` ai due estremi compatibili con la finestra A — il modello vendor com'è (2,59 mA) e un `Vto` che porti I_DSS al tipico (5,5 mA) — e scrivere in `REQUIREMENTS.md` o in una ADR quale dispersione il progetto tollera | S | **NC-013** | da fare |
| L21 | **Il polo 2 del relè, corretto e riverificato.** Riga 79 di `preamp_audio.py` in `"6", "5", "7"`, rigenerazione, e verifica **sulla netlist** che il contatto verso massa di ogni mute cada su 2 e 7 e il ramo `R_g` su 4 e 5 | XS/S | **NC-014** (bloccante) | da fare |
| L22 | **Lo specchio d'ingresso senza THAT320.** Trovare e verificare una coppia PNP appaiata che soddisfi **T7 e T8 insieme**, poi rifare punto di lavoro e rumore dello stadio d'ingresso. La decisione *se* sostituire è presa (ADR-016): resta *con cosa* | M | **NC-015** (bloccante) | da fare |
| L23 | **Package e simbolo della parte che sostituisce il THAT320**, col pinout letto dal suo datasheet. Va fatto **insieme a L22**, non dopo: il footprint arriva con la parte. Copre anche il residuo `SOIC-8` che oggi non corrisponde a nessuna parte esistente | S | NC-016 | da fare |
| L24 | **T7 su tutti i dispositivi attivi.** Prima **verificare** MJE15032/33 e 1N4148 — è il passo che dice quanto è grande il resto — poi trovare i sostituti di 2N5401/2N5551, congelarli e promuoverli in `models/` col controllo incrociato di L6+L7 | M | **NC-017** (bloccante), **NC-004** | **prossimo** |

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
**alimentatore + sicurezza rete**, **Fase 4** (revisione topologia coi
componenti veri), **Fase 5** (misure), **dossier**, **G1**.

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

## Il dossier: prima bozza consegnata in L5b

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

**L24 — T7 su tutti i dispositivi attivi.**

L'ordine è cambiato dopo **ADR-016**, ed è cambiato per una ragione, non
per gusto: **L9 (la rosa dei componenti di segnale) è rinviata**, perché
non sblocca niente, mentre L22 e L24 stanno sul percorso critico verso
G1 — chiudono due bloccanti.

**Perché L24 prima di L22.** Il primo passo di L24 è **verificare se
MJE15032/33 e 1N4148 hanno un modello del costruttore**, ed è il passo che
dice **quanto è grande tutto il resto del lavoro**: i due MJE sono i
dispositivi d'uscita, e se cadono la sostituzione non è un cambio di
package ma una modifica di topologia dello stadio d'uscita. Sapere questo
prima di riprogettare lo specchio evita di riprogettarlo due volte.

Cosa L24 deve fare, in ordine:

1. **Verificare** MJE15032, MJE15033 e 1N4148 contro **T7** e **T8**:
   esiste un modello del costruttore, in quale forma, e la parte è in
   produzione? La Fase 1 aveva scritto sui due MJE «pagina models esiste,
   file finale non confermato» — è un'ipotesi ereditata, non un dato, e
   va verificata alla fonte.
2. **Trovare i sostituti** di 2N5401 e 2N5551 che soddisfino **T7 e T8
   insieme**. Sono VAS, cascode, generatori di corrente e moltiplicatore
   di Vbe: cinque istanze per blocco. La sostituzione del 2N5401 tocca il
   VAS, che con il Miller da 470 pF fissa il **polo dominante di tutto
   l'amplificatore** — le cifre di margine di fase andranno rifatte.
3. **Congelare** ogni modello trovato in `vendor/` con hash, URL e
   provenance, e **provare che ngspice lo carica** alle condizioni del
   datasheet.

Poi **L22 + L23 insieme** (lo specchio senza THAT320, col suo footprint e
il suo simbolo: il footprint arriva con la parte, non dopo), poi **L21**
(il polo 2 del relè, che è quasi gratis), poi il resto.

### Cosa cercare, e cosa NON accettare

Le regole sono **T7** e **T8** in `REQUIREMENTS.md`, e il ragionamento
dietro sta in **ADR-016**. In pratica:

- **un mirror di terze parti non conta.** Circolano copie GitHub di
  modelli attribuiti a Central Semiconductor: ADR-016 le scarta
  esplicitamente. Si congela ciò che il **costruttore** ha servito, con il
  suo URL e il suo hash — la stessa regola che ADR-013 impone per
  l'LSK489, e accettare un mirror qui la svuoterebbe là;
- **un modello pubblicato come PDF conta.** È il caso dell'LSK489: la
  procedura di trascrizione a due letture indipendenti di ADR-013 esiste
  apposta;
- **lo stato di ciclo di vita si legge dal costruttore**, non dal
  distributore. È la lezione che è costata il THAT320.

### Le trappole già pagate, che valgono per questo lotto

Tutte da L6, L7 e L8, e ognuna è costata una scoperta:

1. **Il nome di un file non è la sua revisione** (L7). Si legge dal footer
   del documento: `pdftotext -layout <pdf> - | grep -i 'rev'`.
2. **Le condizioni di prova sono metà del numero** (L6). E attenzione a
   *quale tabella*: un *Absolute Maximum Rating* è una soglia di stress,
   non una caratteristica garantita — spesso danno lo stesso numero e solo
   la seconda è un limite di progetto (L8, sul BVceo del THAT320).
3. **Un codice di stato non è una verifica** (`docs/limitations.md` #18).
   Su `www.onsemi.com` un `200` arriva con dentro una pagina HTML da
   303 722 byte per qualunque percorso inesistente. E **falsificare lo
   user-agent peggiora le cose**: lo stesso host risponde 403.
4. **Un costruttore può pubblicare due modelli della stessa parte**
   (`docs/limitations.md` #17). Vanno il 71% di rumore in più o in meno.
   Quale modello si è usato va scritto **accanto a ogni numero**.
5. **Guarda cosa il repo ha già in casa prima di andare fuori** (L8): la
   risposta su quale contatto del relè fosse NC era disegnata nelle
   polilinee del simbolo KiCad, già sul disco.

### Cosa resta di NC-004 dopo tutto questo

NC-004 (rumore e distorsione senza evidenza, bloccante) non si chiude con
una riesecuzione: si chiude quando **T7 è soddisfatto su tutti e sette i
dispositivi** e i deck girano coi modelli veri, con i dati versionati
sotto `docs/preamp/data/<data>/`. Da leggere insieme a **NC-013** (il
modello LSK489 descrive un esemplare d'angolo, quindi le cifre saranno
conservative sul JFET) e alla scoperta di L8 che **il modello vendor dello
specchio non ha rumore 1/f** — quindi il pavimento senza flicker resta
proprio dove l'analisi dice che il rumore è dominante. Va scritto accanto
ai numeri, non sottinteso.

### Materiale già raccolto per L8-L10 (il giro componenti)

Da non ricercare di nuovo: sono le domande che la Fase 1 non copriva e
che la bozza di Fase 2 ha lasciato aperte. **Quattro delle cinque sono
chiuse**, e vanno lette per quello che hanno restituito, non riaperte.

- ~~**2N5401** (VAS) e **2N5551** (cascode, generatori, moltiplicatore di
  Vbe)~~ — **CHIUSA in L8.** Disponibili e a tre centesimi da sei
  costruttori su DigiKey; datasheet onsemi congelati con i limiti letti
  con le loro condizioni. Ma **nessun modello SPICE del costruttore è
  raggiungibile** → **NC-017**, lotto **L24**. Le varianti selezionate per
  beta del 2N5551 sono state dismesse: resta la dispersione 50…250.
- ~~**Modello SPICE LSK489**~~ — **CHIUSA in L6-L7**: trascritto,
  validato contro il datasheet, verdetto misto, **NC-013** → L20.
- ~~**THAT320**: stock e BVceo~~ — **CHIUSA in L8, con una sorpresa.**
  BVceo confermata (min −36 V a I_C = −10 µA, contro un bar di 35 V). Ma
  **la parte è fine vita dal 2026-09-01, con last-time buy che chiude il
  2026-09-30** → **NC-015**, bloccante, lotto **L22**. Lo stock non è
  fissato e non lo sarà: DigiKey non tratta il costruttore. In più il
  **footprint nel codice è a 8 pin e la parte esiste solo a 14** →
  **NC-016**, lotto **L23**. Il modello SPICE invece c'è, è nativo e
  ngspice lo carica — ma sono **due modelli della stessa parte**, vedi
  `docs/limitations.md` #17.
- ~~**Omron G6K-2F-Y**: quale contatto è NO e quale NC~~ — **CHIUSA in
  L8**, con tre letture indipendenti concordi: **polo 1 COM 3 / NC 2 /
  NO 4**, **polo 2 COM 6 / NC 7 / NO 5**. Il codice ha il **polo 2
  invertito** → **NC-014**, bloccante, lotto **L21**.
- **Simbolo KiCad dell'LSK489** (L10): **ancora aperta**. Non esiste.
  Oggi il duale è disegnato come due JFET separati. Serve un simbolo a 2
  unità col pinout letto dal datasheet **prima del G2**, o il PCB
  piazzerà due package. Da fare **insieme a L23**, che ha lo stesso
  problema sul THAT320: stessa procedura, due parti.

La rosa dei componenti di segnale (L9) **non restituisce un vincitore**:
restringe su basi misurabili — assorbimento dielettrico, rumore in
eccesso, coefficiente di tensione — e la scelta finale fra parti tutte
buone è dell'utente, all'ascolto. È la ragione per cui esiste P6.

### Due tensioni fra requisiti, segnalate e non aggirate

1. **E6 × E2 contro E7.** 2,7 V RMS a +10 dB vogliono 8,54 V RMS in
   uscita; con rail a ±15 V il blocco clippa a 9,31 V RMS simulati.
   Margine 0,75 dB. Il rimedio è il trim di ADR-011 (−6 dB sull'ingresso
   del K11), che con ADR-015 **non è più opzionale**.
2. **E4 contro E8 a 20 Hz.** Con accoppiamento capacitivo la |Zout| al
   jack a 20 Hz è ~1,7 kΩ (è la reattanza del 4,7 µF). A 1 kHz è
   58,8 Ω. E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun
   circuito con condensatore d'uscita.

## Domande aperte

| Cosa | Chi risponde | Blocca? |
|---|---|---|
| Condensatore verso il Singxer: 2,2 o 4,7 µF | utente | No |
| ~~Trascrizione e validazione del modello LSK489~~ | — | **CHIUSA**: trascritta in L6 (due letture byte-identiche), **validata contro il datasheet in L7** — I_DSS dentro la finestra, V_GS(off) **fuori di 0,376 V**, e non per un errore di trascrizione. Aperta NC-013; ADR-013 non riaperta |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale ufficiale. Da L5e **non è più solo una curiosità**: è l'ipotesi su cui poggia NC-010, perché da spento può andare a zero |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio |
| ~~Quale JFET d'ingresso~~ | — | **CHIUSA**: LSK489 (ADR-013) |
| ~~Conferma specifiche cj EV250~~ | — | **CHIUSA**: email costruttore + manuale MV50 |

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
