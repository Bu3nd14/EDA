# Prompt per la sessione successiva — L6

Copiare da qui in giù.

---

Riprendo il progetto del preamplificatore hi-fi in questo repository.
Il lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa UNO, L6,
e si ferma. Non iniziarne un secondo.

Leggi PRIMA, in quest'ordine, e non saltare:

  1. `CLAUDE.md` — ambiente, percorsi assoluti, trappole che falliscono
     in silenzio, e la regola di fine sessione (push PRIMA di tutto)
  2. `docs/preamp/STATE.md` — la sezione "Come si lavora da qui", la
     tabella dei lotti, e il paragrafo "L6-L7 — i modelli veri"
  3. `docs/preamp/decisions/ADR-013-jfet-ingresso-lsk489.md` — **è il
     mandato di questo lotto.** La sezione "Costo accettato
     consapevolmente" elenca i quattro passi obbligatori: L6 fa 1, 2 e 3
  4. `scripts/validate_models.py` e un `.provenance.json` già esistente
     sotto `models/` — la forma non va reinventata, va replicata
  5. `docs/limitations.md` — **#13 prima di tutto** (i suffissi di
     valore: `"1M"` in KiCad è 1 MΩ, in SPICE è 1 mΩ — sei ordini di
     grandezza senza errore da nessuna parte), poi #11 (la copertura di
     validate_models è disuguale: i check JFET sono solo di ordine di
     grandezza)

Contesto in due righe: preamplificatore di linea a guadagno unitario,
Classe A pura a discreti senza operazionali, per sostituire un Technics
SU-9070 la cui struttura di guadagno sbagliata (46 dB di attenuazione
richiesta) è la causa misurabile della mancanza di dinamica lamentata.
La topologia canonica è in `circuits/preamp/`, i banchi di prova in
`spice/preamp/tb/` (12 deck, tutti e 12 scrivono dati da L5).

IL RAMO NON È PIÙ UN PROBLEMA. Da L3c ogni lotto si chiude mergiando e
riallineando il checkout principale, quindi `main` è corrente e si
riparte sempre da lì. Se `git -C /Users/roberto/EDA log --oneline -1`
non mostra L5, qualcosa è andato storto nella chiusura precedente:
risolvi quello prima di iniziare L6.

IL LOTTO: L6 — il primo modello SPICE vendor vero (LSK489)

È il lotto che rende credibili le cifre che oggi non lo sono, ed è per
questo che viene subito dopo l'infrastruttura di misura.

STATO DI PARTENZA, da riverificare e non da assumere:

  - `vendor/` ha 13 sottodirectory e **nessun PDF**: zero datasheet
    congelati. Il passo 1 di ADR-013 non è mai iniziato.
  - `models/jfet/` contiene solo `generic_njf.lib`, un segnaposto.
  - `spice/preamp/placeholder_devices.lib` ha **KF = 0 su ogni
    dispositivo**: nelle simulazioni di oggi non esiste rumore 1/f, e il
    macro-modello dichiara nella propria intestazione di non avere
    clipping, né slew rate, né assorbimento dalle alimentazioni.
  - `validate_models.py` sta a 24/24 check. Non deve scendere.

I TRE PASSI, che sono di ADR-013 e non miei:

  1. **Congelare il PDF** in `vendor/` con sha256 e URL registrati. Il
     modello di Linear Systems è distribuito come PDF che *contiene* il
     testo `.MODEL`, non come `.lib`.
  2. **Trascrivere i parametri** in `models/jfet/`. È il punto in cui si
     introducono errori silenziosi, ed è il motivo per cui esiste il
     passo 4 (che è L7, non L6).
  3. Il `.provenance.json` deve dichiarare **esplicitamente**
     "trascritto manualmente da PDF vendor, non estratto
     meccanicamente". Non è una formula di cortesia: è ciò che dice al
     gate quanto fidarsi del numero.

NON FA PARTE DI L6: il passo 4, cioè il controllo incrociato di I_DSS e
V_P contro il datasheet. È L7, ed è separato di proposito — è il punto in
cui la trascrizione può risultare **sbagliata**, e in quel caso il lavoro
è tornare su L6, non andare avanti. Un lotto che contenga sia la
trascrizione sia il suo giudizio è un lotto che si giudica da solo.

NON FA PARTE DI L6: toccare il circuito o i banchi di prova. La topologia
sta solo in `circuits/preamp/*.py`, e i 12 deck sono finiti in L5.

SE IL PDF NON È RAGGIUNGIBILE — è l'unico rischio vero del lotto, ed è
esterno. Non inventare i parametri e non "ricostruirli da un modello
simile": fermati, dillo, e lascia il lotto aperto. Un modello inventato
che passa i check è peggio di nessun modello, perché il resto del
progetto poggia su quei numeri credendoli vendor.

FATTO QUANDO

  - il PDF è in `vendor/` con sha256 e URL registrati, e il file c'è
    davvero (verificato con `ls` e `shasum`, non dedotto)
  - `models/jfet/` contiene il modello trascritto, e ngspice lo carica
    davvero in una simulazione reale (exit code 0, nessun "unknown
    parameter")
  - il `.provenance.json` dichiara la trascrizione manuale a parole
    esplicite
  - `/usr/bin/python3 scripts/validate_models.py` resta a 24/24 (o sale,
    se hai aggiunto un check — mai scende)
  - `/bin/zsh scripts/run_tests.sh` resta 5 passed, 0 failed

UNA COSA CHE ORA È VERA E PRIMA NO: dopo L5 tutti e 12 i deck scrivono
CSV/JSON, e dopo L5b esiste **la prima bozza del dossier**, in
`docs/preamp/dossier/` — si rigenera con

```sh
/usr/bin/python3 docs/preamp/dossier/build_dossier.py
```

e ogni cifra che stampa è letta dai dati versionati e **ricontrollata
contro i `print` di ngspice**; se le due strade divergono, rifiuta di
scrivere. Quindi il giorno in cui i modelli veri entrano nel repo basta
rieseguire i deck e rigenerare la pagina per avere numeri nuovi
confrontabili con quelli di oggi, senza toccare nessun banco di prova.
Non farlo in L6 — è Fase 5 — ma sappi che il confronto esiste già.

DECISIONE APERTA, non tecnica: l'utente ha chiesto che la bozza venga
rivista da un **«Revisore Avversariale»**. Nel repo non esiste: il roster
ha 12 agenti e l'unico revisore è `design-reviewer`, che è legato ai gate
G1/G2/G3. Va deciso con lui se (a) usare `design-reviewer` fuori dal
contesto di gate per una revisione avversariale delle misure, (b) definire
un agente nuovo con un mandato diverso, o (c) chiedergli il verdetto G1
vero e proprio sapendo che darà non conformità bloccanti automatiche
(Fasi 3-4 non fatte, modelli segnaposto). **Non decidere da solo.**

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
      1. aggiorna `docs/preamp/STATE.md` segnando **L6 fatto** e il lotto
         successivo come prossimo (la tabella deve dire `**fatto**`)
      2. riscrivi QUESTO file per il lotto successivo — se il titolo
         nomina ancora L6, lo script rifiuta, ed è il controllo che
         esiste apposta
      3. committa, pusha, apri la PR
      4. `/bin/zsh scripts/chunk_close.sh L6`
         Verifica tutto, merghia, riallinea il checkout dell'utente e
         **rilegge da lì** per provare il riallineo. Se rifiuta, ha
         ragione: sistema e rilancia.
      5. rimuovi il worktree con i due comandi che lo script stampa
      6. fermati. Non iniziare il lotto dopo.
