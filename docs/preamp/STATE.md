# STATE — Preamplificatore di linea

**Leggi questo per primo** riprendendo il progetto.

**Documento vivo**: ogni sessione che tocca il preamp lo aggiorna prima
di chiudere, e lo committa insieme al lavoro. Se è disallineato dalla
realtà, il progetto non è ripartibile.

Ultimo aggiornamento: **2026-09-09** (L4 chiuso: `wrdata` sui due deck muti senza cicli, `tb_bias_sweep` assegnato a L5; prossimo lotto L5)

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
| L3b | `REPO` cablato in `circuits/preamp/gain_block.py` — **obbligatorio prima della Fase 4** | XS/S | da fare |
| L3c | Chiusura di lotto che rifiuta, gate agganciato ai dati, dati del dossier versionati | S | **fatto** |
| L3d | Annotare il difetto `setplot`/plot stale di `tb_zout_psrr_noise.cir` (warning per L5) | XS | **fatto** |
| L4 | `wrdata` sui deck muti **senza** cicli | S | **fatto** |
| L5 | `wrdata` sui deck muti **con** cicli (`tb_bias_sweep` incluso) | S/M | **prossimo** |
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

**L2-L5 — i testbench diventano artefatti.** Dopo L4 scrivono file dati
**6 deck su 12** (`tb_op`, `tb_dc_headroom` con due file, `tb_switch_v2`,
`tb_v3_overload`, e i due di L4): 9 file in tutto. I **6 muti rimasti**
sono tutti L5, perche' hanno tutti un `foreach`. Ma aprendo i
deck per L2 è emerso un problema **più grande di quello registrato**, e
va detto per intero — anche ora che è chiuso, perché è il ragionamento
che ha prodotto la convenzione.

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

**Ma quel worktree NON è ancora cancellabile, e la ragione è peggiore.**
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
`ROOT=${0:A:h:h}` negli script), la **verifica** non lo è.

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
della lettura**. Non su tutto il repo: `circuits/preamp/gain_block.py`
scrive ancora nel worktree vecchio — vedi il riquadro sopra.

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

### ⚠ WARNING PER L5 — un numero già stampato oggi è sbagliato

**`tb_zout_psrr_noise.cir` riporta un rumore di caso peggiore sbagliato di
un fattore 3,4, e lo fa in silenzio.** Trovato il 2026-09-09 rispondendo a
una domanda sullo stato delle misure, non cercandolo.

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

**Cosa deve fare L5**: quel deck è già suo (è uno dei deck con `foreach` e
`destroy all`). Oltre ad aggiungerci i `wrdata`, deve **correggere questa
coda** e ricontrollare che le due righe finali tornino diverse. Attenzione
al caso generale: ogni `wrdata` piazzato dopo un'analisi ripetuta senza
`destroy all` scriverà i dati del plot **sbagliato** — che è lo stesso
guasto, ma dentro un file che poi finisce nel dossier.

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

Restano da aggiungere `wrdata` ai **6 deck muti rimasti**, tutti con
`foreach`, e sono L5. Non sono meccanici: `tb_ac.cir` ha un doppio ciclo
(2 modalità × 4 impedenze di sorgente = 8 curve) e chiude ogni iterazione
con `destroy all`, quindi il `wrdata` va **dentro il ciclo, prima del
`destroy all`**, col nome file parametrizzato.

Serve al dossier **e** a `design-reviewer` per rieseguire le misure a G1:
non è lavoro anticipato.

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

## Il dossier: formato deciso, non ancora iniziato

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
L2-L5.

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

**L5 — aggiungere `wrdata` ai 6 deck muti *con* cicli, e correggere la
coda di `tb_zout_psrr_noise.cir`.**

Sono i deck che restano dopo L4, e non sono meccanici: dove c'è un
`destroy all` dentro il ciclo, il `wrdata` va **dentro il ciclo, prima
del `destroy all`**, col nome file parametrizzato. Un `wrdata` piazzato
dopo un'analisi ripetuta **senza** `destroy all` scrive i dati del plot
sbagliato — che è lo stesso guasto del riquadro qui sopra, ma dentro un
file che poi finisce nel dossier.

| Deck muto | Forma | Nota |
|---|---|---|
| `tb_bias_sweep` | `foreach` (7 × `op`), **nessun** `destroy all` | assegnato a L5 in L4: serve un file per iterazione |
| `tb_noise_breakdown` | `foreach` + `destroy all` | |
| `tb_ac` | `foreach` doppio + `destroy all` | 2 modalità × 4 Z sorgente = 8 curve |
| `tb_loop` | `foreach` doppio + `destroy all` | |
| `tb_loop_blockA` | `foreach` + `destroy all` | |
| `tb_zout_psrr_noise` | quattro sezioni + `destroy all` | **porta anche la correzione del riquadro ⚠ qui sopra** |

La prima decisione di L5 è **la convenzione di nome per gli output
parametrizzati**, e va presa una volta sola per tutti e sei. Il secondo
passaggio di `run_simulation.sh` guarda i file **prodotti** e non il testo
del deck, proprio perché un nome dentro un `foreach` non è ricavabile con
un grep: quando `tb_ac.cir` scriverà le sue 8 curve, saranno 8 CSV.

Due regole ereditate da L4: ogni `wrdata` non banale porta sopra di sé un
commento con **l'ordine delle colonne** (i CSV sono intestati
`col0…colN`), e si scrivono i vettori **scelti**, non `all`.

Verifica: deck eseguito davvero, CSV/JSON non vuoti col numero di righe
atteso dal tipo di analisi, numeri dei deck esistenti invariati rispetto a
una baseline presa prima della modifica, e `run_tests.sh` a 5 passed.

**L3b resta obbligatorio prima della Fase 4** (il `REPO` cablato in
`gain_block.py`): se si rigenera il circuito con quel percorso, l'`.inc`
nuovo va nel worktree vecchio e le simulazioni continuano sulla copia
vecchia in silenzio. Chi apre la Fase 4 la apre da L3b.

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
