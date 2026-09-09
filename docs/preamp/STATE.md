# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-09** (L5c chiuso: **G0 definito**, la prima revisione del prodotto; prossimo lotto **L5d**, che lo esegue)

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
| L5d | **Eseguire G0**: report datato + non conformità | S | **prossimo** |
| L6 | LSK489: passi 1-3 di ADR-013 (congela, trascrivi, provenance) | S | da fare |
| L7 | LSK489: passo 4, il controllo incrociato | S | da fare |
| L8 | Fase 3a — le parti nuove, fatti verificabili | M | da fare |
| L9 | Fase 3b — la rosa dei componenti di segnale | M | da fare |
| L10 | Simbolo KiCad dell'LSK489 | S | da fare |

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

**L6-L7 — i modelli veri.** `vendor/` non contiene **nessun** PDF (13
sottodirectory, zero datasheet congelati) e `models/jfet/` ha solo
`generic_njf.lib`: il passo 1 di ADR-013 non è iniziato. Finché i modelli
sono segnaposto, **ogni cifra di distorsione è priva di significato** —
ed è l'intera ragione per cui si è andati a discreti. I due lotti sono
separati perché il passo 4 è il punto in cui la trascrizione può
risultare sbagliata: in quel caso il lavoro è tornare su L6, non andare
avanti.

**L8 prima di L9** perché le parti nuove sono fatti chiudibili mentre la
rosa è un giudizio aperto: se il cap arriva, è meglio che tagli la
seconda.

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
| **G1** | Congelamento topologia | `design-reviewer` | da fare |
| — | Layout → **G2** → fabbricazione → **G3** | | da fare |

**Perché la Fase 1 viene prima della bozza**: se i JFET complementari non
esistono, l'intero stadio d'ingresso cambia forma. Meglio saperlo prima
di disegnare tutto attorno a loro.

**Perché G1 viene dopo il giro componenti**: congela una topologia che
sappiamo costruibile con parti che esistono davvero, non una disegnata
sulla carta.

## Prossimo passo concreto

**L5d — eseguire G0.**

`design-reviewer` gira **a freddo**, offline su `main`, sul dossier e sui
dati versionati, con il mandato scritto in `../../AGENTS.md` sezione **G0**.
Produce un report datato in `reports/` e apre le non conformità in
`NONCOMPLIANCE.md`.

**C'è un controllo cieco dentro questo gate, ed è la ragione per cui va
eseguito così.** L'utente ha trovato un errore **nel diagramma a blocchi**
guardando il dossier, e ha chiesto esplicitamente che **non sia
l'orchestratore a cercarlo**: lo deve trovare il revisore. Quindi
l'orchestratore non ha aperto il corpo di `preamp_blocks_draw.py` né le
etichette del disegno, e non deve farlo. Con l'utente che conosce l'errore,
l'orchestratore che non l'ha visto e il revisore che parte a freddo, quella
voce diventa una **calibrazione del gate**: se il revisore la trova, G0 ha
dimostrato sensibilità invece che dichiararla; se non la trova, sappiamo che
il gate è più debole di quanto avremmo assunto, ed è un'informazione che
vale quanto la voce stessa.

**Ostacolo pratico già risolto**: i due SVG sotto `schematic/` hanno il
testo convertito in tracciati da matplotlib, quindi leggere il file non
mostra nessuna etichetta. Si rasterizzano con

```sh
qlmanage -t -s 2400 -o <outdir> docs/preamp/schematic/preamp_blocks.svg
```

oppure si legge lo script che li genera, che è la loro vera fonte. Sta in
`AGENTS.md` perché un revisore che si limitasse a `cat` sull'SVG
concluderebbe di non poter giudicare il disegno, e sbaglierebbe.

**Poi L6 — LSK489: i passi 1-3 di ADR-013 (congela il datasheet, trascrivi
il modello, registra la provenance).**

È il lotto che rende credibili le cifre che oggi non lo sono. Stato di
partenza, verificato e non assunto: `vendor/` non contiene **nessun** PDF
(13 sottodirectory, zero datasheet congelati) e `models/jfet/` ha solo
`generic_njf.lib`. Il passo 1 di ADR-013 non è iniziato.

Perché viene ora: l'infrastruttura di misura è finita. Dopo L5 tutti e 12 i
deck scrivono dati, quindi il giorno in cui i modelli veri entrano nel repo
**basta rieseguire i deck** per avere numeri nuovi e confrontabili con
quelli di oggi, senza toccare nessun banco di prova.

**L7 è separato di proposito**: il passo 4 di ADR-013 è il controllo
incrociato, ed è il punto in cui la trascrizione può risultare sbagliata. Se
succede, il lavoro è tornare su L6, non andare avanti.

Attenzione a `docs/limitations.md` #13 mentre si trascrive: `"1M"` in KiCad
è 1 MΩ, in SPICE è 1 mΩ. Sei ordini di grandezza senza alcun errore da
nessuna delle due parti.

**La Fase 4 non ha più il preliminare che aveva.** L3b è chiusa: il
circuito si rigenera nel checkout corrente, verificato rieseguendo
davvero i due generatori. Chi apre la Fase 4 la apre dalla topologia, non
da una correzione di percorso.

### Materiale già raccolto per L8-L10 (il giro componenti)

Da non ricercare di nuovo: sono le domande che la Fase 1 non copriva e
che la bozza di Fase 2 ha lasciato aperte.

- **2N5401** (VAS) e **2N5551** (cascode, generatori, moltiplicatore di
  Vbe): parti nuove, non verificate in Fase 1.
- **Modello SPICE LSK489**: procedura obbligatoria di ADR-013 — è L6-L7,
  precede il resto perché la credibilità della distorsione ci poggia
  sopra.
- **THAT320**: stock non ancora fissato, e va confermata la BVceo ≥ 35 V.
- **Omron G6K-2F-Y**: confermare quale contatto è NO e quale NC. Il
  progetto fallisce in sicurezza solo se sono quelli giusti.
- **Simbolo KiCad dell'LSK489** (L10): non esiste. Oggi il duale è
  disegnato come due JFET separati. Serve un simbolo a 2 unità col
  pinout letto dal datasheet **prima del G2**, o il PCB piazzerà due
  package.

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
| Trascrizione del modello LSK489 da PDF | Fase 2 | No, ma **la credibilità della distorsione ci poggia sopra** |
| Impedenza d'ingresso Singxer SA-1 V2 | — | **Non pubblicata**, verificato sul manuale ufficiale |
| Valore del cap d'uscita del phono a valvole | utente | **Rinviata** — non ha accesso agli schematici né può aprire agevolmente il telaio |
| ~~Quale JFET d'ingresso~~ | — | **CHIUSA**: LSK489 (ADR-013) |
| ~~Conferma specifiche cj EV250~~ | — | **CHIUSA**: email costruttore + manuale MV50 |

## Decisioni chiuse il 2026-09-08

| Cosa | Esito |
|---|---|
| Rail ±15 V o ±18 V | **±15 V** — ADR-015. Il trim di ADR-011 in modalità +10 dB **non è più opzionale** |
| Condensatore verso il Singxer | **4,7 µF su tutte e tre le uscite** — ADR-007 addendum. Chiude la domanda sull'impedenza ignota del Singxer |
| Resistenze di isolamento ADR-008 | **47 Ω** invece di ~100 Ω — soddisfa E4 con margine |

Nessuna decisione dell'utente è pendente.

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
