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
     tabella dei lotti (ora con i lotti L11-L15 che G0 ha generato), la
     sezione **L5d** con l'esito del primo gate, e "Prossimo passo
     concreto"
  3. `docs/preamp/NONCOMPLIANCE.md` — **otto voci aperte, 2 bloccanti**.
     È il registro vivo, e da oggi non è più vuoto
  4. `docs/preamp/decisions/ADR-013-jfet-ingresso-lsk489.md` — è il
     mandato di questo lotto, passi 1-3
  5. `docs/limitations.md` **#13** — la trappola che morde proprio
     mentre si trascrive un modello

## Prima di cominciare: una domanda all'utente

**Qual è l'errore che hai visto nel diagramma a blocchi?**

G0 non l'ha trovato. Il revisore ha rasterizzato il disegno, l'ha guardato
per intero e l'ha confrontato riga per riga con `preamp_audio.py`,
concludendo che «il diagramma a blocchi non mente». Sullo *altro* disegno lo
stesso metodo ha trovato un'affermazione falsa (è diventata NC-001, la voce
bloccante), quindi il metodo funziona — su questo disegno non ha trovato
*quello*.

Finché l'errore è noto solo all'utente non c'è evidenza da scrivere, e una
non conformità senza evidenza apribile è un'opinione. **Non blocca L6**: è
una domanda da fare, non una dipendenza da aspettare. Se l'utente risponde,
si apre la voce e nasce il lotto che la chiude.

## IL LOTTO: L6 — LSK489, i passi 1-3 di ADR-013

È il lotto che rende credibili le cifre che oggi non lo sono, ed è ora il
**rimedio a una non conformità bloccante** (NC-004): rumore e distorsione
non hanno evidenza finché i modelli sono segnaposto, e i contributori
dominanti previsti stanno nello **specchio di corrente**, cioè nella
topologia. Non è un dettaglio di componente.

I tre passi, come ADR-013 li scrive:

  1. **Congela il datasheet.** Nessun PDF è oggi in `vendor/` — 13
     sottodirectory, zero datasheet. `vendor/` è di sola lettura
     (`scripts/freeze_vendor.sh`, mode 0444).
  2. **Trascrivi il modello** in `models/jfet/`, che oggi contiene solo
     `generic_njf.lib`.
  3. **Registra la provenance** nel sidecar `<file>.provenance.json` —
     convenzione in `models/PROVENANCE_CONVENTION.md`.

Poi `/usr/bin/python3 scripts/validate_models.py --check-provenance`, che
oggi dà 24/24.

**Attenzione a `docs/limitations.md` #13 mentre trascrivi**: `"1M"` in
KiCad è 1 MΩ, in SPICE è 1 mΩ. Sei ordini di grandezza senza alcun errore
da nessuna delle due parti. È già costato una volta.

**L7 è separato di proposito**: il passo 4 di ADR-013 è il controllo
incrociato, ed è il punto in cui la trascrizione può risultare sbagliata.
Se succede, il lavoro è tornare su L6, non andare avanti.

## NON fa parte di L6

**Correggere le non conformità di G0.** Hanno i loro lotti — L11-L15 nella
tabella di `STATE.md` — ed è il meccanismo per cui un gate genera lavoro
invece di fermarlo. La sola eccezione è se l'utente chiede esplicitamente
il contrario.

In particolare **NC-001** (il mute che porta lo stadio d'uscita fuori dalla
Classe A, 203 mA contro 14,56 mA di riposo) è L11 e vuole una decisione di
progetto: o una modifica di topologia o una ADR che accetti il regime. Non
è una riga da aggiungere in coda a L6.

## COME LAVORIAMO

  - Verifica invece di fidarti. Se un subagente riporta dei numeri,
    rieseguili tu prima di riferirmeli. È già servito due volte.
  - Niente cifre non eseguite. Una simulazione descritta e non lanciata
    non è evidenza.
  - Un lotto per volta, mai due agenti in parallelo: il vincolo è il cap
    di token del piano, e i resoconti che tornano insieme sono la parte
    che consuma.
  - Lavora in un worktree. I commit non pushati dentro
    `.claude/worktrees/` spariscono col worktree, ed è già successo.
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
