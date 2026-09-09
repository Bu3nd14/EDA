# Prompt per la sessione successiva — L8

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L8,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, la sezione **L7**, "Prossimo passo concreto" e
     **"Materiale già raccolto per L8-L10"**, che è il tuo punto di
     partenza e che NON va ricercato di nuovo
  3. `docs/preamp/reports/2026-09-09-L7-controllo-incrociato-lsk489.md` —
     non per l'LSK489, che è chiuso, ma per **il metodo**: come si legge
     un datasheet in modo che il numero regga
  4. `docs/preamp/decisions/ADR-003-classe-a-discreti.md` e
     `ADR-014-cascode-ingresso.md` — perché queste parti sono in lista
  5. `docs/limitations.md` — da leggere prima di scrivere codice

## IL LOTTO: L8 — Fase 3a, le parti nuove come fatti verificabili

Il giro componenti è diviso in tre lotti. **L8 viene prima di L9** perché
le parti nuove sono fatti chiudibili, mentre la rosa dei componenti di
segnale è un giudizio aperto: se il cap arriva, è meglio che tagli la
seconda.

Quattro cose da rendere verificabili, tutte già identificate — il lavoro
è **verificarle**, non riscoprirle:

1. **2N5401** (VAS) e **2N5551** (cascode, generatori di corrente,
   moltiplicatore di Vbe). Parti nuove, mai verificate in Fase 1.
   Servono: disponibilità e prezzo reali, e soprattutto **da dove viene
   il modello SPICE** e se esiste in forma macchina o va trascritto come
   l'LSK489.
2. **THAT320**: lo stock non è mai stato fissato, e va confermata la
   **BVceo ≥ 35 V** — **contro il datasheet del costruttore**, non
   contro la scheda di un distributore.
3. **Omron G6K-2F-Y**: confermare **quale contatto è NO e quale NC**. È
   un fatto di sicurezza travestito da dettaglio di catalogo: il progetto
   fallisce in sicurezza solo se sono quelli giusti (ADR-012).

### Cosa L6 e L7 hanno imparato, e che vale per questo lotto

Sono le due trappole in cui il giro componenti cade per prime, e sono
costate due lotti.

- **Il nome di un file non è la sua revisione.** L7 ha trovato che il PDF
  congelato come «RevA38» è in realtà la **RevA40**: l'unico posto dove
  compariva «A38» era il nome del file, che è quello che il server manda
  nel `content-disposition`, e nessuno l'aveva aperto per controllare. Se
  congeli un PDF vendor, la revisione si legge **dal footer del
  documento**. `/opt/homebrew/bin/pdftotext -layout <pdf> - | grep 'Rev#'`.
- **Le condizioni di prova sono metà del numero.** L6 aveva misurato
  I_DSS a `V_DS = 5 V` perché così faceva la ricetta accanto; il
  datasheet prescrive `V_DG = 15 V`, ed è specificato a **25 °C** mentre
  ngspice gira a **27 °C**. Nessuno dei due scarti dà errore. Un limite
  di datasheet senza le sue condizioni non è un limite.

Per congelare: `scripts/freeze_vendor.sh`. Per rileggere un PDF senza
dipendenze: `scripts/pdf_glyphs.py`. Entrambi hanno `ROOT`/`VENDOR_DIR`
già derivati dalla propria posizione (corretti in L6).

### Cosa vale come "verificato"

- una disponibilità è verificata se **hai visto la pagina**, non se è
  plausibile;
- un modello SPICE è verificato se **ngspice lo carica**, non se il link
  esiste;
- un limite di datasheet è verificato se hai letto **la tabella con le
  sue condizioni**, non l'intestazione della pagina prodotto;
- se congeli un PDF, va in `vendor/` con sha256, URL e
  `PROVENANCE.json` — e la revisione letta dal footer.

## NON fa parte di L8

**Correggere le non conformità.** Hanno i loro lotti — L11-L20 nella
tabella di `STATE.md`. Le tre bloccanti:

- **NC-001**, il mute che porta lo stadio d'uscita fuori dalla Classe A
  (L11);
- **NC-004**, rumore e distorsione senza evidenza. L6 e L7 ne erano metà
  del rimedio ed è **fatta**: resta la riesecuzione di
  `spice/preamp/tb/tb_noise_breakdown.cir` coi modelli veri e i dati
  versionati sotto `docs/preamp/data/<data>/`, da leggere insieme a
  **NC-013**;
- **NC-010**, le uscite fisse non isolate che portano il Blocco A in
  Classe B se un apparecchio a valle si spegne (L17). Stessa fisica di
  NC-001 ma **rimedio diverso**: chi chiude una non chiude l'altra.

**Non toccare `circuits/` né `spice/preamp/`**: la sostituzione dei
segnaposto nella topologia è **Fase 4**. Nessun numero del dossier deve
cambiare, ed è una proprietà da verificare (`git diff --stat` non deve
nominare `circuits/` né `docs/preamp/data/`).

**Non toccare i file già in `vendor/`**: sono la traccia di controllo. Se
serve correggere un `PROVENANCE.json` congelato, si **aggiunge accanto**
un addendum — è quello che ha fatto L7 con
`PROVENANCE-L7-addendum.json` — non si riscrive l'originale.

**Non riaprire ADR-013.** L7 ha chiuso il suo passo 4 con un verdetto
misto e ha aperto NC-013 invece di riaprire la ADR. Se pensi che vada
riaperta, è una decisione dell'utente, non un lavoro da fare di tua
iniziativa.

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito tre volte.
  - **Cerca se qualcuno ha già deciso, prima di aprire una voce.** In L5e
    NC-009 stava per essere aperta come «serve una decisione di progetto»:
    ADR-015 l'aveva presa il giorno prima.
  - **Verifica alla fonte anche ciò che il lotto precedente ti ha
    scritto.** L6 ha lasciato a L7 due affermazioni plausibili e nessuna
    delle due era vera. Un compito ereditato è un'ipotesi, non un dato.
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
      1. aggiorna `docs/preamp/STATE.md` segnando **L8 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L8, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L8`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
