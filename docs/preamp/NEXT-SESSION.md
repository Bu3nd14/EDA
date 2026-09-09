# Prompt per la sessione successiva — L5d

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L5d,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `AGENTS.md`, sezione **Gates** e in particolare **G0** — è il
     mandato di questo lotto, comprese le sei domande e cosa blocca una
     voce bloccante
  3. `docs/preamp/NONCOMPLIANCE.md` — il registro vivo, oggi a zero voci,
     e il formato che una voce deve avere
  4. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, e "Prossimo passo concreto", che contiene il
     vincolo qui sotto
  5. `docs/preamp/dossier/index.html` — l'oggetto da far giudicare, e
     `docs/preamp/REQUIREMENTS.md`, contro cui va giudicato

IL LOTTO: L5d — eseguire G0, la prima revisione del prodotto

`design-reviewer` gira **a freddo**, offline su `main`, sul dossier e sui
dati versionati in `docs/preamp/data/2026-09-09/`. Non su un diff: il
gate è attaccato ai risultati, non alla PR (deciso il 2026-09-09).

Il suo prodotto **non è un verdetto che blocca un merge**: è un report
datato in `docs/preamp/reports/2026-09-09-gate-G0.md` più le non
conformità aperte in `docs/preamp/NONCOMPLIANCE.md`, ognuna con il
requisito, l'evidenza apribile, la severità e lo stato.

⚠ IL VINCOLO CHE GOVERNA QUESTO LOTTO — leggilo due volte

**L'utente ha trovato un errore nel DIAGRAMMA A BLOCCHI guardando il
dossier, e ha chiesto esplicitamente che non sia tu a cercarlo.** Lo deve
trovare il revisore.

Quindi:

  - **NON aprire** il corpo di `docs/preamp/schematic/preamp_blocks_draw.py`
    (le etichette, i collegamenti, il disegno), **non** rasterizzare il
    diagramma per guardarlo, **non** cercare l'errore in nessun modo.
  - Alla chiusura di L5c l'orchestratore aveva letto solo il blocco che
    legge la netlist e le asserzioni (righe 60-175) più un `grep` sulle
    righe che disegnano etichette. Non aveva visto il corpo del disegno.
    Parti da lì e non allargare.
  - Il revisore va lanciato come **agente nuovo**, non come fork del tuo
    contesto, così parte davvero a freddo.

**Perché.** Con l'utente che conosce l'errore, te che non l'hai visto e il
revisore che parte a freddo, quella voce è una **calibrazione di G0**: se
il revisore la trova, il gate ha *dimostrato* sensibilità invece di
dichiararla; se non la trova, sappiamo che è più debole di quanto
avremmo assunto — ed è un'informazione che vale quanto la voce stessa.
Se la cerchi tu, non impariamo né l'una né l'altra cosa.

COSA DARE AL REVISORE

Il mandato è la sezione **G0** di `AGENTS.md`: sei domande sul **prodotto**
— struttura di guadagno, requisiti elettrici con evidenza, stabilità e
copertura della matrice V1, ADR confermate o smentite, onestà sui «non lo
so», e **i disegni dicono la verità sul circuito**.

Fuori scope, e va detto al revisore in modo esplicito: banchi di prova,
`run_simulation.sh`, generatore del dossier, toolchain. È una correzione
dell'utente, non una sfumatura: G0 rivede **il prodotto, non l'ambiente**.
Se il revisore inciampa in un difetto della catena lo annota sotto
«osservazioni fuori scope» e non apre una non conformità di prodotto.

Digli anche il fatto pratico, o si blocca: i due SVG sotto
`docs/preamp/schematic/` hanno il testo convertito in tracciati da
matplotlib, quindi `cat` sull'SVG non mostra **nessuna** etichetta. Si
guardano rasterizzandoli,

```sh
qlmanage -t -s 2400 -o <outdir> docs/preamp/schematic/preamp_blocks.svg
```

oppure leggendo lo script che li genera, che è la loro vera fonte.

E ricordagli il limite di merito: i modelli sono **segnaposto**, `KF = 0`
ovunque, nessun modello vendor. Rumore e distorsione non hanno cifre
credibili; risposta, guadagno, impedenze e risultati in continua sì.

FATTO QUANDO

  - il report esiste in `docs/preamp/reports/2026-09-09-gate-G0.md`, con
    ogni voce che nomina il file di dati che la sostiene — «una non
    conformità senza evidenza apribile non è una non conformità, è
    un'opinione»
  - `NONCOMPLIANCE.md` elenca le voci aperte con severità e stato
  - le voci bloccanti, se ce ne sono, dicono cosa serve per chiuderle in
    modo concreto e verificabile
  - **hai rieseguito tu i numeri che il revisore riporta** prima di
    riferirli all'utente: è già servito, ed è la regola numero uno
  - `STATE.md` dice se G0 ha trovato l'errore del diagramma a blocchi
    oppure no. **Entrambi gli esiti vanno scritti**: il secondo è un
    risultato su G0, non un fallimento da nascondere
  - `/bin/zsh scripts/run_tests.sh` resta 5 passed, 0 failed

NON FA PARTE DI L5d: correggere ciò che il gate trova. Un gate che ripara
da sé non è un gate — le voci aperte alimentano la tabella dei lotti, ed è
il meccanismo per cui una non conformità **genera lavoro** invece di
fermarlo. La sola eccezione è se l'utente chiede esplicitamente il
contrario.

COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano, e i resoconti che tornano insieme sono la parte
    che consuma.
  - Lavora in un worktree. I commit non pushati dentro
    .claude/worktrees/ spariscono col worktree, ed è già successo.
  - CHIUSURA. Non è una lista da ricordare, è uno script che rifiuta.
    Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L5d fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L5d, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L5d`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
