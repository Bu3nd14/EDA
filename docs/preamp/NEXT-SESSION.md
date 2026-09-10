# Prompt per la sessione successiva — L9

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L9,
e si ferma. Non iniziarne un secondo.

## PRIMA DI TUTTO: una cosa che non è un lotto e ha una scadenza

Il **THAT320 è fine vita dal 2026-09-01** e il **last-time buy chiude il
2026-09-30**. Il memo del costruttore è congelato in
`vendor/bjt_array/that/THAT320/THAT-EOL-Memo.pdf`. È **NC-015**,
bloccante, e la decisione è **mia, non tua**: comprare adesso una scorta,
oppure riprogettare lo specchio d'ingresso su una coppia PNP ancora in
produzione.

**Se non te ne ho ancora parlato, ricordamelo all'inizio della sessione**
— una riga, non un'analisi. Poi procedi con L9: la decisione non blocca
questo lotto.

## Leggi PRIMA, in quest'ordine, e non saltare

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, la sezione **L8**, "Prossimo passo concreto" e
     **"Materiale già raccolto per L8-L10"**, che è il tuo punto di
     partenza e che NON va ricercato di nuovo
  3. `docs/preamp/reports/2026-09-10-L8-parti-nuove.md` — non per le
     parti, che sono chiuse, ma per **il metodo**: come si verifica una
     parte in modo che il fatto regga, e le tre trappole in cui L8 è
     caduto per primo
  4. `docs/limitations.md` — **da leggere prima di scrivere codice**, e
     in particolare le due voci nuove, **#17** e **#18**, che sono di L8
  5. `docs/preamp/decisions/ADR-014-cascode-ingresso.md` — perché
     l'impedenza dell'attenuatore è un vincolo di progetto e non un
     dettaglio

## IL LOTTO: L9 — Fase 3b, la rosa dei componenti di segnale

**Cambia natura rispetto a L8, e va tenuto presente dall'inizio.** L8
verificava **fatti chiudibili**: una parte è disponibile o non lo è, un
contatto è NO o è NC. L9 restringe un **giudizio aperto**.

**L9 non restituisce un vincitore.** Restringe su basi misurabili —
assorbimento dielettrico, rumore in eccesso, coefficiente di tensione — e
la scelta finale fra parti tutte buone è **mia, all'ascolto**. È la
ragione per cui esiste **P6**. Un lotto che torna con «ho scelto questo»
ha sbagliato il mandato; uno che torna con «questi tre, e questo è il
criterio che li separa, e questo è ciò che il criterio non copre» ha
fatto il suo lavoro.

Cosa coprire, dai vincoli che il progetto ha già scritto:

1. **Il Miller da 470 pF: C0G/NP0 obbligatorio.** Vincolo dichiarato in
   `circuits/preamp/gain_block.py`: vede ~13 V di continua e porta
   l'intero segnale di correzione, e un X7R lì modulerebbe la
   compensazione col segnale. Serve la parte reale, la tolleranza, e cosa
   costa in ingombro.
2. **I sei condensatori d'accoppiamento da 4,7 µF** (ADR-007 addendum:
   tre uscite × due canali, stesso valore su tutte e tre per togliere una
   riga di BOM e un errore di montaggio silenzioso). Polipropilene. La
   loro **dimensione fisica** è già un vincolo di layout su telaio unico
   (ADR-010): è parte della risposta, non una nota a margine.
3. **I resistori del percorso di segnale**, in particolare R_f/R_g che
   fissano il +9,96 dB reale e i 47 Ω di isolamento di ADR-008.
   Coefficiente di tensione e rumore in eccesso sono i criteri; la
   tolleranza da sola non lo è.
4. **L'attenuatore a scatti da 10 kΩ**, fuori scheda (F4/ADR-009). La sua
   impedenza culmina a **2,5 kΩ a metà corsa** ed è la ragione per cui
   ADR-014 esiste: qualunque parte si scelga, quel numero non deve
   crescere.

### Le tre lezioni di L8, che valgono per L9

Sono la cosa più utile che il lotto precedente lascia, e sono costate una
scoperta ciascuna.

- **Un dato di ciclo di vita non è un dato di datasheet, e nessuno dei due
  è un dato di catalogo.** Il THAT320 era fine vita da una settimana
  quando la topologia lo ha scelto, il memo era pubblico, e nessuno
  l'aveva guardato. Per ogni parte che entra in rosa, lo stato di ciclo di
  vita si legge **dal costruttore**.
- **Un codice di stato non è una verifica** (`docs/limitations.md` #18).
  Su `www.onsemi.com` un `200` è arrivato con dentro una pagina HTML: quel
  sito risponde 200 con la stessa pagina da 303 722 byte per qualunque
  percorso inesistente. Si controlla `Content-Type` **e** dimensione, e
  per un PDF si apre il file. E **falsificare lo user-agent peggiora le
  cose**: con un UA Safari plausibile lo stesso host risponde 403.
- **Un costruttore può pubblicare due modelli della stessa parte**
  (`docs/limitations.md` #17). THAT ne pubblica due del THAT320 che
  differiscono solo per `RB` e danno il **71%** di rumore in più o in
  meno. Se L9 tocca un componente con un modello SPICE, va scritto
  **quale** modello accanto a ogni numero.

E la lezione di L7 che non è scaduta: **il nome di un file non è la sua
revisione**. Si legge dal footer del documento —
`/opt/homebrew/bin/pdftotext -layout <pdf> - | grep -i 'rev'`.

### Cosa vale come "verificato"

- una disponibilità è verificata se **hai visto la pagina**, non se è
  plausibile — e se non ci sei riuscito, **si dichiara**, non si riempie.
  L8 non è riuscito a leggere le quantità di stock da nessun
  distributore, e l'ha scritto;
- un limite di datasheet è verificato se hai letto **la tabella con le
  sue condizioni**, non l'intestazione della pagina prodotto. E attenzione
  a **quale** tabella: un *Absolute Maximum Rating* è una soglia di
  stress, non una caratteristica garantita — sono due numeri diversi che
  spesso coincidono, e solo il secondo è un limite di progetto;
- se congeli un PDF, va in `vendor/` con sha256, URL e `PROVENANCE.json`,
  e la revisione letta dal footer.

## NON fa parte di L9

**Correggere le non conformità.** Hanno i loro lotti — L11-L24 nella
tabella di `STATE.md`. Le cinque bloccanti:

- **NC-001**, il mute che porta lo stadio d'uscita fuori dalla Classe A
  (L11);
- **NC-004**, rumore e distorsione senza evidenza. L6 e L7 ne erano una
  parte del rimedio ed è **fatta**; L8 ha scoperto che il modello vendor
  dello specchio **non ha rumore 1/f**, quindi resta la riesecuzione di
  `spice/preamp/tb/tb_noise_breakdown.cir` più i modelli mancanti di
  VAS e cascode (L24);
- **NC-010**, le uscite fisse non isolate (L17). Stessa fisica di NC-001
  ma **rimedio diverso**: chi chiude una non chiude l'altra;
- **NC-014**, il polo 2 del relè Omron invertito (L21);
- **NC-015**, il THAT320 fine vita (L22) — la decisione con la scadenza.

**Non toccare `circuits/` né `spice/preamp/`**: la sostituzione dei
segnaposto nella topologia è **Fase 4**. Nessun numero del dossier deve
cambiare, ed è una proprietà da verificare: il diff del ramo non deve
nominare `circuits/` né `docs/preamp/data/`.

**Non toccare i file già in `vendor/`**: sono la traccia di controllo. Se
serve correggere un `PROVENANCE.json` congelato, si **aggiunge accanto**
un addendum — è quello che ha fatto L7 con
`PROVENANCE-L7-addendum.json` — non si riscrive l'originale.

**Non promuovere modelli vendor dentro `models/`.** Deciso: la promozione
porta con sé il controllo incrociato contro il datasheet, cioè il lavoro
di L7 moltiplicato per parte, ed è un lotto suo (L24). Il conteggio della
suite deve restare **26/26**, ed è la prova che `models/` non è stato
toccato.

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito tre volte.
  - **Cerca se qualcuno ha già deciso, prima di aprire una voce.** In L5e
    NC-009 stava per essere aperta come «serve una decisione di progetto»:
    ADR-015 l'aveva presa il giorno prima.
  - **Verifica alla fonte anche ciò che il lotto precedente ti ha
    scritto.** L6 ha lasciato a L7 due affermazioni plausibili e nessuna
    delle due era vera. Un compito ereditato è un'ipotesi, non un dato.
  - **Guarda cosa il repo ha già in casa prima di andare fuori.** In L8 la
    risposta su quale contatto del relè fosse NC era **disegnata nelle
    polilinee del simbolo KiCad**, già sul disco: quello che era stato
    letto erano solo le posizioni dei pin.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - **Diffida degli script che dichiarano di aver verificato qualcosa.**
    `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT`
    cablato su `/Users/roberto/EDA`: eseguiti da un worktree leggono e
    scrivono nel checkout principale, in silenzio. Se il tuo lotto ne
    tocca uno, correggilo lì.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano.
  - Lavora in un worktree. I commit non pushati dentro
    `.claude/worktrees/` spariscono col worktree, ed è già successo.
  - CHIUSURA. Non è una lista da ricordare, è uno script che rifiuta.
    Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L9 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L9, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L9`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
