# Prompt per la sessione successiva — L24

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L24,
e si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto non è L9

Il 2026-09-10 ho posto **due regole di progetto**, registrate in
**ADR-016** e come requisiti **T7** e **T8**:

1. **Nessun componente a fine vita entra nel progetto.**
2. **Ogni dispositivo attivo del percorso di segnale ha un modello SPICE
   del costruttore.**

Conseguenza immediata: il THAT320 esce (era fine vita), 2N5401 e 2N5551
escono (nessun modello vendor), e **MJE15032/33 e 1N4148 vanno
verificati** perché nessuno l'ha mai fatto. Dei sette dispositivi attivi
del progetto **uno solo è conforme oggi**: l'LSK489.

**L9 — la rosa dei componenti di segnale — è rinviata**: non sblocca
niente, mentre L24 e L22 chiudono due non conformità bloccanti.

## Leggi PRIMA, in quest'ordine, e non saltare

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, le sezioni **L8** e **L8b**, e "Prossimo passo
     concreto", che contiene il mandato di questo lotto per esteso
  3. `docs/preamp/decisions/ADR-016-modello-vendor-e-ciclo-di-vita.md` —
     le due regole, il perché **con i numeri**, e cosa la decisione costa
  4. `docs/preamp/reports/2026-09-10-L8-parti-nuove.md` — non per le parti,
     che sono chiuse, ma per **il metodo**: come si verifica una parte in
     modo che il fatto regga, e le trappole in cui L8 è caduto per primo
  5. `docs/limitations.md` — **da leggere prima di scrivere codice**, e in
     particolare **#17** e **#18**, che sono di L8

## IL LOTTO: L24 — T7 su tutti i dispositivi attivi

Chiude **NC-017** (bloccante) e sblocca la metà di **NC-004** che riguarda
VAS, cascode e stadio d'uscita.

**Nell'ordine, e l'ordine conta:**

1. **Verificare MJE15032, MJE15033 e 1N4148** contro T7 e T8: esiste un
   modello del costruttore, in quale forma, e la parte è in produzione?

   **È il primo passo perché dice quanto è grande tutto il resto.** I due
   MJE sono i **dispositivi d'uscita**: se cadono, la sostituzione non è
   un cambio di package, è una **modifica di topologia**. Saperlo prima
   evita di riprogettare due volte.

   La Fase 1 aveva scritto sui due MJE «pagina models esiste, file finale
   non confermato». **È un'ipotesi ereditata, non un dato** — e L7 ha
   dimostrato cosa succede a fidarsi di quelle: due affermazioni plausibili
   lasciate da L6, nessuna delle due vera.

2. **Trovare i sostituti di 2N5401 e 2N5551** che soddisfino **T7 e T8
   insieme**. Sono cinque istanze per blocco: VAS, due cascode, due
   generatori di corrente e il moltiplicatore di Vbe.

   Attenzione al VAS: con il Miller da 470 pF fissa il **polo dominante di
   tutto l'amplificatore**, quindi la sua f_T e la sua C_ob non sono
   dettagli di catalogo. Le cifre di margine di fase andranno rifatte
   comunque, ma serve sapere di quanto ci si muove.

3. **Congelare** ogni modello trovato in `vendor/` con hash, URL e
   `PROVENANCE.json`, e **provare che ngspice lo carica** alle condizioni
   del datasheet.

### Cosa NON accettare

- **un mirror di terze parti non conta.** ADR-016 lo scarta
  esplicitamente: si congela ciò che il **costruttore** ha servito, con il
  suo URL e il suo hash. È la stessa regola che ADR-013 impone per
  l'LSK489, e accettarne uno qui la svuoterebbe là;
- **un modello pubblicato come PDF invece conta** — è il caso
  dell'LSK489, e la procedura di trascrizione a due letture indipendenti
  di ADR-013 esiste apposta;
- **lo stato di ciclo di vita si legge dal costruttore**, non dal
  distributore. È la lezione che è costata il THAT320: il memo di EOL era
  pubblico da una settimana quando la topologia lo ha scelto.

### Cosa vale come "verificato"

- una disponibilità è verificata se **hai visto la pagina**, non se è
  plausibile — e se non ci sei riuscito, **si dichiara**, non si riempie.
  L8 non è riuscito a leggere le quantità di stock da nessun
  distributore, e l'ha scritto;
- un limite di datasheet è verificato se hai letto **la tabella con le sue
  condizioni**. E attenzione a **quale** tabella: un *Absolute Maximum
  Rating* è una soglia di stress, non una caratteristica garantita —
  spesso danno lo stesso numero e solo la seconda è un limite di progetto;
- un modello SPICE è verificato se **ngspice lo carica** ed esegue, non se
  il link esiste;
- se congeli un PDF, va in `vendor/` con sha256, URL e `PROVENANCE.json`,
  e **la revisione letta dal footer**, mai dal nome del file.

### Le trappole già pagate

Ognuna è costata una scoperta a un lotto precedente:

1. **Il nome di un file non è la sua revisione** (L7) —
   `pdftotext -layout <pdf> - | grep -i 'rev'`.
2. **Le condizioni di prova sono metà del numero** (L6): il datasheet è a
   25 °C, ngspice gira a 27.
3. **Un codice di stato non è una verifica** (`limitations.md` #18): su
   `www.onsemi.com` un `200` arriva con dentro una pagina HTML da 303 722
   byte per qualunque percorso inesistente, e **falsificare lo user-agent
   peggiora le cose** — lo stesso host risponde 403.
4. **Un costruttore può pubblicare due modelli della stessa parte**
   (`limitations.md` #17): vanno il 71% di rumore in più o in meno. Quale
   modello hai usato va scritto **accanto a ogni numero**.
5. **Guarda cosa il repo ha già in casa prima di andare fuori** (L8): la
   risposta su quale contatto del relè fosse NC era disegnata nelle
   polilinee del simbolo KiCad, già sul disco.

## NON fa parte di L24

**Sostituire le parti nella topologia.** L24 trova e verifica; la
sostituzione in `circuits/preamp/` è **Fase 4**. Nessun numero del dossier
deve cambiare, ed è una proprietà da verificare: il diff del ramo non deve
nominare `circuits/`, `spice/preamp/` né `docs/preamp/data/`.

**Lo specchio d'ingresso** (la parte che sostituisce il THAT320): è
**L22**, da fare insieme a **L23** perché il footprint arriva con la
parte. Viene dopo, non prima, per la ragione al punto 1.

**Promuovere i modelli in `models/`** oltre a quelli che questo lotto
riesce a incrociare col datasheet. La promozione porta con sé il controllo
incrociato di L6+L7 per ogni parte: se diventa troppo grande, si congela
in `vendor/` e la promozione è un lotto suo. Meglio un lotto chiuso che
due a metà.

**Correggere le altre non conformità.** Hanno i loro lotti — L11-L24. Le
sei bloccanti: NC-001 (L11), NC-004, NC-010 (L17), NC-014 (L21), NC-015
(L22), NC-017 (questo lotto).

**Non toccare i file già in `vendor/`**: sono la traccia di controllo. Una
correzione a un `PROVENANCE.json` congelato si **aggiunge accanto** come
addendum — è quello che ha fatto L7 — non si riscrive l'originale.

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito tre volte.
  - **Cerca se qualcuno ha già deciso, prima di aprire una voce.** In L5e
    NC-009 stava per essere aperta come «serve una decisione di progetto»:
    ADR-015 l'aveva presa il giorno prima.
  - **Verifica alla fonte anche ciò che il lotto precedente ti ha
    scritto.** Un compito ereditato è un'ipotesi, non un dato — e in
    questo lotto la frase della Fase 1 sui MJE è esattamente uno di quei
    compiti.
  - **Una parte che entra citando una parentesi non ha mai avuto
    un'istruttoria.** È come il THAT320 è entrato nel progetto, ed è il
    motivo per cui il suo fine vita non l'aveva controllato nessuno.
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
      1. aggiorna `docs/preamp/STATE.md` segnando **L24 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L24, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L24`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
