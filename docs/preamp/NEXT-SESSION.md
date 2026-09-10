# Prompt per la sessione successiva — L22 + L23

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO** —
**L22 insieme a L23** — e si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è lo specchio d'ingresso

Il lotto precedente, **L24**, ha eseguito il requisito **T7** su tutti e
sette i dispositivi attivi. Due risultati cambiano il quadro:

- **lo stadio d'uscita regge.** MJE15032, MJE15033 e 1N4148 hanno un
  modello del costruttore, quindi la modifica di topologia che ADR-016
  temeva non serve;
- **2N5401 e 2N5551 non si sostituiscono.** Diodes Incorporated pubblica
  il modello dello stesso die come **MMBT5401** e **MMBT5551**, in SOT-23.
  Deciso in **ADR-017**.

Conseguenza: **il THAT320 è l'unico dei sette dispositivi attivi senza una
risposta.** È fine vita (T8) e ADR-016 ha scartato il last-time buy, quindi
va sostituito. È **NC-015**, bloccante, e il suo lotto è **L22**.

**L23 va fatto insieme, non dopo**: il footprint arriva con la parte.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono
   in silenzio, e la regola di fine sessione (**push prima di tutto**)
2. **`docs/preamp/STATE.md`** — la sezione «Come si lavora da qui», la
   tabella dei lotti, la sezione **L24**, e «Prossimo passo concreto», che
   contiene il mandato di questo lotto per esteso
3. **`docs/preamp/decisions/ADR-016-modello-vendor-e-ciclo-di-vita.md`** —
   le due regole T7 e T8, il perché con i numeri, e cosa costano
4. **`docs/preamp/decisions/ADR-017-dispositivi-attivi-conformi-a-t7.md`**
   — **il precedente di come si applicano**: cosa si accetta come
   provenienza, cosa no, e come si dichiara una lacuna invece di riempirla
5. **`docs/preamp/reports/2026-09-10-L24-t7-dispositivi-attivi.md`** — non
   per le parti, che sono chiuse, ma per il **metodo**: gli URL che
   funzionano, quelli che mentono, e le due trappole nuove
6. **`docs/limitations.md`** — prima di scrivere codice, e in particolare
   **#17, #18, #19 e #20**

## IL LOTTO: L22 + L23 — lo specchio d'ingresso senza THAT320

Chiude **NC-015** (bloccante) e **NC-016**.

Nell'ordine:

1. **Trovare e verificare una coppia PNP appaiata** che soddisfi **T7 e T8
   insieme** per lo specchio di corrente dello stadio d'ingresso.

   Il THAT320 portava **appaiamento monolitico e rbb = 25 Ω**, ed è
   quest'ultimo che il modello `QPNP_THAT_NS` riproduceva al 2,4% della
   cifra di rumore dichiarata dal costruttore. Le strade sono un altro
   array monolitico — con lo stesso rischio di catalogo — oppure una coppia
   discreta appaiata, che costa rumore e deriva.

2. **Rifare punto di lavoro e rumore dello stadio d'ingresso** con la parte
   scelta. ADR-016 dichiara che lo specchio va **riprogettato e non
   ri-approvvigionato**: cambiano il punto di lavoro e le cifre di rumore.

3. **L23: package e simbolo** della parte scelta, col pinout letto dal suo
   datasheet. Copre anche il residuo reale che `gain_block.py:303-304`
   dichiara oggi un `SOIC-8` che **non corrisponde a nessuna parte
   esistente** — nemmeno al THAT320, che esiste solo a 14 pin.

4. **Congelare** in `vendor/` con hash, URL e `PROVENANCE.json`, e
   **provare che ngspice carica il modello** alle condizioni del datasheet.

## Cosa L24 ti consegna — usalo invece di riscoprirlo

Sono tutti fatti verificati, con il comando che li falsifica.

1. **Il pattern dei modelli onsemi**:
   `https://www.onsemi.com/download/models/lib/<parte minuscola>.lib`.
   Attenzione: la variante col suffisso `(spice model)` funziona su alcune
   parti e non su altre; il nome nudo è quello che ha funzionato in L24.
2. **I modelli Diodes stanno su `/spice/download/<id>/<PARTE>.spice.txt`**
   e rispondono `200 text/plain` a un `curl` nudo, mentre `/design/` e
   `/part/` danno **403**. È la scoperta che ha sbloccato L24, e smentisce
   la conclusione generale di L8 su quel costruttore.
3. **Il ciclo di vita si legge dal JSON-LD della pagina prodotto onsemi**,
   nel blocco `offers/itemProductList`: dà OPN → `itemCondition` →
   `availability` verbatim. È così che L24 ha scoperto che KSA992 è in
   *Last Shipments* e che 2N3904/2N3906 sono interamente Obsolete.
4. **T8 azzera la rosa molto più di quanto sembri.** Di sedici candidati
   piccoli segnale, **uno solo** è risultato attivo con modello. Aspettati
   lo stesso per una coppia appaiata, e pianifica di conseguenza.

## Cosa NON accettare

- **un mirror di terze parti non conta.** ADR-016 lo scarta esplicitamente:
  si congela ciò che il **costruttore** ha servito, con il suo URL e il suo
  hash. È la stessa regola che ADR-013 impone per l'LSK489, e accettarne
  uno qui la svuoterebbe là;
- **un modello pubblicato come PDF conta** — è il caso dell'LSK489, e la
  procedura di trascrizione a due letture indipendenti esiste apposta;
- **lo stato di ciclo di vita si legge dal costruttore**, mai dal
  distributore. È la lezione che è costata il THAT320, e in L24 ha morso di
  nuovo: per il 1N4148 una ricerca dava «Active» da quattro aggregatori, e
  non è stata usata;
- **un modello che il costruttore serve ma che un contrattista ha scritto
  conta comunque** (i due MJE dichiarano «Model Generated by MODPEX /
  Symmetry Design Systems»). Registrare l'autore non indebolisce la
  provenienza: fa parte di cosa la provenienza **è**.

## Cosa vale come «verificato»

- una **disponibilità** è verificata se hai visto la pagina del
  costruttore, non se è plausibile — e se non ci sei riuscito, **si
  dichiara**, non si riempie. L24 non è riuscito a leggere una pagina
  prodotto per MJE15033 né uno stato esplicito per i due Diodes, e l'ha
  scritto invece di pareggiare l'evidenza;
- un **limite di datasheet** è verificato se hai letto la tabella con le
  sue condizioni. Attenzione a *quale* tabella — un Absolute Maximum Rating
  è una soglia di stress, non una caratteristica garantita — e a *quale
  corrente*: L24 ha misurato f_T **88,8 MHz a 2 mA** su una parte il cui
  datasheet dichiara 100 MHz minimi, a 10 mA;
- un **modello SPICE** è verificato se ngspice lo carica **ed esegue** alle
  condizioni del datasheet, non se il link esiste. E a **25 °C**: il
  datasheet è a 25, ngspice gira a 27;
- se congeli un documento, va in `vendor/` con sha256, URL e
  `PROVENANCE.json`, e la revisione letta dal **footer**, mai dal nome del
  file.

## Le trappole già pagate

Ognuna è costata una scoperta a un lotto precedente.

1. **Il nome di un file non è la sua revisione** (L7):
   `pdftotext -layout <pdf> - | grep -i 'rev'`.
2. **Il nome di un file non è nemmeno la sua parte** (L24,
   `limitations.md` #20). onsemi serve `1n4148.lib` contenente
   `.SUBCKT 1N4148WT`, che è un'altra variante in un altro package.
   **Apri il modello e leggi l'intestazione prima di congelarlo.**
3. **Il prefisso micro non sopravvive all'estrazione dai PDF onsemi**
   (L24, `limitations.md` #19). `pdftotext` rende µ come **m**: errore
   ×1000, exit 0, nessun avviso — e il prefisso *nano* invece sopravvive,
   quindi un controllo a campione può ingannarti. Un limite di corrente
   sotto il milliampere va **guardato**, non estratto.
4. **Le condizioni di prova sono metà del numero** (L6).
5. **Un codice di stato non è una verifica** (`limitations.md` #18): su
   `www.onsemi.com` un 200 arriva con una pagina HTML da **303 722 byte**
   per qualunque percorso inesistente, e falsificare lo user-agent peggiora
   le cose — lo stesso host risponde 403.
6. **Un costruttore può pubblicare due modelli della stessa parte**
   (`limitations.md` #17). Vanno il 71% di rumore in più o in meno, ed è
   proprio sul THAT320. Quale modello hai usato va scritto **accanto a ogni
   numero**.
7. **Guarda cosa il repo ha già in casa prima di andare fuori** (L8): la
   risposta su quale contatto del relè fosse NC era disegnata nelle
   polilinee del simbolo KiCad, già sul disco. Vale doppio per L23, che
   deve produrre un simbolo.

## NON fa parte di questo lotto

- **Promuovere in `models/` i cinque modelli che L24 ha congelato.** È
  **L25**, e il controllo incrociato è già fatto: resta bloccarne i numeri
  con una ricetta di `validate_models.py` ciascuno.
- **Sostituire le parti nella topologia.** La sostituzione di
  MMBT5401/MMBT5551 in `circuits/preamp/` è **Fase 4**. Questo lotto tocca
  `circuits/preamp/` solo per lo **specchio d'ingresso**, se e quando la
  parte è scelta e verificata.
- **Correggere le altre non conformità.** Hanno i loro lotti. Le sei
  bloccanti: NC-001 (L11), NC-004, NC-010 (L17), NC-014 (L21), NC-015
  (questo lotto), NC-017 (L25 + Fase 4).
- **Non toccare i file già in `vendor/`**: sono la traccia di controllo.
  Una correzione a un `PROVENANCE.json` congelato si aggiunge accanto come
  addendum — è quello che ha fatto L7 — non si riscrive l'originale.

## Come lavoriamo

1. **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
   rieseguili tu prima di riferirmeli.
2. **Verifica alla fonte anche ciò che il lotto precedente ti ha
   scritto.** Un compito ereditato è un'ipotesi, non un dato — e L24 lo ha
   dimostrato di nuovo: la conclusione di L8 su Diodes era vera dei
   percorsi provati e falsa come affermazione generale, e ha tenuto ferme
   due parti per un lotto intero.
3. **Cerca se qualcuno ha già deciso, prima di aprire una voce.**
4. **Una parte che entra citando una parentesi non ha mai avuto
   un'istruttoria.** È come il THAT320 è entrato nel progetto.
5. **Niente cifre non eseguite.** Una simulazione descritta e non lanciata
   non è evidenza.
6. **Diffida degli script che dichiarano di aver verificato qualcosa.**
   `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT`
   cablato su `/Users/roberto/EDA`: eseguiti da un worktree leggono e
   scrivono nel checkout principale, in silenzio. Se il tuo lotto ne tocca
   uno, correggilo lì.
7. **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap
   di token del piano.
8. **Lavora in un worktree.** I commit non pushati dentro
   `.claude/worktrees/` spariscono col worktree, ed è già successo.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il
   successivo come prossimo (la tabella deve dire `**fatto**`)
2. **riscrivi QUESTO file per il lotto successivo** — se il titolo nomina
   ancora L22 o L23, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L22` — verifica tutto, merghia,
   riallinea il checkout dell'utente e **rilegge da lì** per provare il
   riallineo. Se rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
