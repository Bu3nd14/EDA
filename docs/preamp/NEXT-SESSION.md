# Prompt per la sessione successiva — L7

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L7,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, la sezione **L6** e "Prossimo passo concreto"
  3. `docs/preamp/decisions/ADR-013-jfet-ingresso-lsk489.md` — il
     mandato: questo lotto è il **passo 4**, e la ADR dice perché non è
     un di più
  4. `docs/preamp/reports/2026-09-09-L6-trascrizione-lsk489.md` — cosa
     L6 ha trascritto, come, e le due cose che ha lasciato a te
  5. `docs/limitations.md` **#13** — la trappola che morde proprio
     mentre si leggono valori da un datasheet

## IL LOTTO: L7 — il controllo incrociato di ADR-013, passo 4

L6 ha congelato i PDF vendor e trascritto il modello. **Nessuno ha ancora
verificato che i parametri trascritti descrivano la parte vera.** ADR-013
lo dice senza ammorbidire:

> Il punto 4 non è un di più: è ciò che rende accettabile il punto 2.

Finché L7 non chiude, `models/jfet/lsk489.lib` è **trascritto e verificato
sintatticamente, non validato contro i limiti pubblicati della parte** —
ed è scritto così nella sua intestazione, nella provenance e in STATE.md.
Se il controllo non torna, **il lavoro è tornare su L6**, non andare
avanti. È l'intera ragione per cui i due lotti sono separati.

### Cosa fare

1. **Leggere I_DSS e V_P dal datasheet congelato**
   (`vendor/jfet/linear_systems/LSK489/LSK489DSRevA38.pdf`, 7 pagine, la
   tabella sta **oltre la prima**). `sips` e `qlmanage` vedono solo la
   prima pagina: per questo L6 ha installato poppler —
   `/opt/homebrew/bin/pdftotext`, 26.09.0, arm64. Conta il **suffisso di
   selezione**: la parte è divisa in **due** gruppi, **A** (ΔIDSS = 6 mA) e
   **B** (ΔIDSS = 7 mA), con finestre diverse. Il modello si chiama
   `LSK489A`, quindi il confronto va fatto con la finestra **A**, non con
   l'intervallo complessivo.
2. **Ricavare le stesse due grandezze dal modello trascritto**, con
   ngspice e non a mano: I_DSS come I_D a `Vgs = 0` in saturazione, V_P
   dal `Vto` e da uno sweep che lo confermi. Il numero già misurato in L6
   è **2,500 mA** a `Vgs = 0`, `Vds = 5 V` — riverificalo, non fidartene.
3. **Confrontare, e scrivere il verdetto** in un report datato sotto
   `docs/preamp/reports/`. Un verdetto è "dentro la finestra" oppure
   "fuori, di tanto": non "plausibile".
4. **Rafforzare la ricetta in `scripts/validate_models.py`** se e solo se
   il confronto torna: `tb_lsk489()` oggi è **fumo dichiarato** (conduce a
   `Vgs = 0`, interdetto a `Vgs = -3 V`) e può diventare un controllo con
   la finestra del datasheet dentro. Se lo fai, il conteggio dei check
   **non** cambia (26/26): cambia cosa asserisce.

### Le due cose che L6 ti ha lasciato scritte

- **La revisione del datasheet.** Il costruttore serve **RevA38**; Mouser
  serve **RevA40 (04/12/2022)**. È congelata quella del costruttore, che
  è la fonte autorevole. **Conferma che i limiti I_DSS/V_P non siano
  cambiati fra le due revisioni prima di usarli.** Se sono cambiati, è la
  RevA40 a essere vera per una parte comprata oggi, e va congelata anche
  quella — `vendor/` è di sola lettura ma non è chiuso.
- **Il numero da spiegare, se non torna.** Se i 2,500 mA cadono fuori
  dalla finestra I_DSS del gruppo A, la risposta **non è ritoccare il
  modello**: è rileggere la trascrizione. Le tre letture di L6 sono
  rieseguibili — `scripts/pdf_glyphs.py` non ha dipendenze.

  **Un fatto visto di striscio in L6, che non è un verdetto.** Aprendo il
  datasheet solo per confermare che i gruppi fossero due, la riga del
  gruppo A si è vista: I_DSS **2,5 / 5,5 / 8,5 mA** (min/tip/max). I
  2,500 mA di L6 stanno sul **bordo inferiore** — ma **il confronto così
  com'è non è valido**, perché L6 ha misurato a `Vds = 5 V` senza
  guardare le condizioni di prova che il datasheet prescrive per I_DSS.
  È precisamente il lavoro di L7: rimisurare **alle condizioni del
  datasheet** e poi confrontare. Non ereditare questo numero come se
  fosse già un esito.

### Attenzione a `docs/limitations.md` #13

`"1M"` in KiCad è 1 MΩ, in SPICE è 1 mΩ: sei ordini di grandezza senza
alcun errore da nessuna delle due parti. Sul modello LSK489 **non morde**
— L6 ha controllato suffisso per suffisso: `2.2m`/`4.3m`/`-2.5m` sono
milli in entrambe le convenzioni, `3f`/`0.0009f` femto, `3.19p`/`2.92p`
pico, `30u` micro. È scritto proprio perché è il punto in cui qualcuno,
avendo letto #13, «correggerebbe» un valore giusto. **Non correggerlo.**

## NON fa parte di L7

**Correggere le non conformità.** Hanno i loro lotti — L11-L19 nella
tabella di `STATE.md`. Le tre bloccanti:

- **NC-001**, il mute che porta lo stadio d'uscita fuori dalla Classe A
  (L11);
- **NC-004**, rumore e distorsione senza evidenza. **L7 è metà del suo
  rimedio, non la sua chiusura**: dopo L7 serve ancora una riesecuzione di
  `spice/preamp/tb/tb_noise_breakdown.cir` coi modelli veri e i dati
  versionati sotto `docs/preamp/data/<data>/`;
- **NC-010**, le uscite fisse non isolate che portano il Blocco A in
  Classe B se un apparecchio a valle si spegne (L17). Stessa fisica di
  NC-001 ma **rimedio diverso**: chi chiude una non chiude l'altra.

**Non toccare `circuits/` né `spice/preamp/`**: il segnaposto `LSK489X`
resta dov'è, la sostituzione nella topologia è **Fase 4**. Nessun numero
del dossier deve cambiare, ed è una proprietà da verificare
(`git diff --stat` non deve nominare `circuits/` né `docs/preamp/data/`).

**Non toccare i file in `vendor/`**: sono di sola lettura (0444) e sono
la traccia di controllo. Se serve una revisione nuova del datasheet, si
**aggiunge** accanto, non si sostituisce.

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito tre volte.
  - **Cerca se qualcuno ha già deciso, prima di aprire una voce.** In L5e
    NC-009 stava per essere aperta come «serve una decisione di progetto»:
    ADR-015 l'aveva presa il giorno prima.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - **Diffida degli script che dichiarano di aver verificato qualcosa.**
    L6 ha trovato `ROOT` cablato dentro `validate_models.py`: eseguito da
    un worktree validava i modelli del **checkout principale** e stampava
    un PASS che non riguardava il ramo. È stato corretto, ma
    `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora lo
    stesso difetto: se il tuo lotto ne tocca uno, correggilo lì.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano.
  - Lavora in un worktree. I commit non pushati dentro
    `.claude/worktrees/` spariscono col worktree, ed è già successo.
  - CHIUSURA. Non è una lista da ricordare, è uno script che rifiuta.
    Nell'ordine:
      1. aggiorna `docs/preamp/STATE.md` segnando **L7 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L7, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L7`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
