# Prompt per la sessione successiva — L10

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L10** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è il simbolo dell'LSK489

Il lotto precedente è **L21**, che ha chiuso **NC-014** — il polo 2 del relè
G6K-2F-Y era cablato con NO e NC invertiti, quindi sul **canale destro** il
mute falliva nel verso sbagliato. Tre cose di quel lotto ti riguardano prima
di toccare qualsiasi cosa:

1. **La suite ha un blocco in più.** `run_tests.sh` è ora a **6 blocchi**: il
   2e esegue `scripts/check_relay_safe_state.py`, che legge la netlist
   generata e pretende che ogni relè si guasti nel verso che le ADR
   richiedono. Se il tuo lotto rinumera i riferimenti, **deve restare verde**.
2. **Una bloccante in meno: ne restano sei** — NC-001 (L11), NC-002 e NC-021
   (L12), NC-004, NC-010 (L17), NC-017 (Fase 4).
3. **È aperta NC-026, e sta proprio sulla tua strada.** Il disegno a blocchi
   `docs/preamp/schematic/preamp_blocks_draw.py` **non gira da L22**: cita
   quattro riferimenti che lo scarto di −1 di L22 ha spostato
   (`R237`/`R437`/`R239`/`R439` → `R236`/`R436`/`R238`/`R438`). Nessuno se ne
   è accorto perché quel disegno **non ha manifesto** e quindi nulla lo
   esegue. **L10 produrrà un altro scarto di −1**, quindi conviene chiudere
   NC-026 prima di rinumerare di nuovo, o insieme: la diagnosi è completa
   nella voce e il rimedio è quattro rinomini più la rigenerazione.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. **`docs/preamp/STATE.md`** — «Come si lavora da qui», la tabella dei lotti,
   la sezione **L21**, e **«Prossimo passo concreto»**, che contiene il
   mandato di questo lotto per esteso
3. **`docs/preamp/STATE.md` §L22 + L23** — è il precedente da copiare: la
   stessa fusione è già stata fatta una volta, per l'LS352
4. **`docs/preamp/decisions/ADR-013-*.md`** — la decisione sull'LSK489, e la
   procedura vincolante di provenienza
5. **`docs/preamp/NONCOMPLIANCE.md`**, voci **NC-016** (chiusa, è il modello di
   come si chiude questa) e **NC-026** (aperta, sulla tua strada)
6. **`docs/limitations.md`** — prima di scrivere codice, in particolare #13,
   #14 e #16

## IL LOTTO: L10 — il simbolo KiCad dell'LSK489

**Il difetto.** L'LSK489 è un **duale** — due JFET appaiati sullo stesso die,
SOIC-8 — ma `circuits/preamp/gain_block.py:287-288` lo istanzia come **due
Part**, ognuna col proprio footprint SOIC-8. Sul PCB sono **due package per un
dispositivo solo**. Il codice lo dichiara già come gap noto alle righe
279-286, e dice anche cosa serve: una libreria di simboli di progetto che
fornisca **un** simbolo LSK489 a **due unità**, col pinout **letto dal
datasheet**.

È esattamente il residuo che NC-016 aveva per il THAT320, e che **L23 ha già
chiuso una volta** per l'LS352: i componenti su SOIC-8 sono passati da quattro
a **tre**, e i tre sono l'LS352 più i **due LSK489**.

**Cosa costa molto meno di prima:** `library/preamp.kicad_sym` esiste — è la
prima libreria di simboli del repo — il meccanismo multi-unit è collaudato, e
`spice_dev(..., suffix=)` è già lì.

**Cosa fare:**

1. aggiungere il simbolo **LSK489 a due unità** a `library/preamp.kicad_sym`,
   col pinout **letto dal datasheet congelato** in
   `vendor/jfet/linear_systems/LSK489/` — mai dedotto;
2. verificarlo con `kicad-cli sym upgrade` e `sym export svg`, che disegna
   tutte le unità (è quello che L23 ha fatto per l'LS352);
3. fondere le due Part in una in `gain_block.py`, usando
   `spice_dev(..., suffix=)` — senza, le due metà emettono due righe SPICE
   **con lo stesso nome**;
4. rigenerare gli artefatti col venv SKiDL e verificare **sulla netlist** che
   i componenti su SOIC-8 scendano da tre a **due**.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **Fondere due Part in una slitta di −1 tutti i riferimenti successivi**
  (L22). La mappa vecchio→nuovo si **ricava confrontando i nodi** fra il
  `.inc` vecchio e quello nuovo, **non si deduce a mano**. Va applicata a
  tutto ciò che cita riferimenti espliciti: i deck, `gain_block_draw.py` e
  `preamp_blocks_draw.py` — che L22 ha mancato, ed è NC-026.
- **`gain_block.py` è coperto da un manifesto**, quindi il blocco 2d di
  `run_tests.sh` (`check_schematic.py`) confronterà disegno e netlist in
  entrambe le direzioni. In L22 ha rifiutato alla prima esecuzione con 15
  discordanze. Se rifiuta, ha ragione.
- **Un `.net` di SKiDL non è riproducibile byte a byte** (L3b): il confronto è
  quello normalizzato, tolti `(date`, `SKiDL Tag`, `SKiDL Line` e `(tstamps`.
- **Un pinout non pubblicato non si usa.** L23 ha scartato PDIP-8 e DFN-8
  dell'LS352 proprio per questo: il datasheet li elenca ma non ne disegna il
  pinout, ed è così che il SOIC-8 fantasma era nato.
- **Il blocco 2e esiste ora** e va tenuto verde.

## Cosa NON accettare

- **Un pinout dedotto**, dalla simmetria o da un altro package. L21 ha appena
  riletto alla fonte il pinout di un relè e ha trovato che la regola implicita
  «NO = COM+1» era giusta per un polo e sbagliata per l'altro. Si legge il
  datasheet congelato.
- **Una verifica fatta sul sorgente.** Il sorgente dice cosa volevi, la
  netlist dice cosa hai fatto.
- **Un `git diff` su un `.net`** letto come prova che la topologia è (o non è)
  cambiata. Serve il confronto normalizzato.
- **Una cifra non eseguita.** Se il lotto dichiara un numero, quel numero deve
  uscire da una run.

## NON fa parte di questo lotto

- **Sostituire i modelli nella topologia.** MMBT5401/MMBT5551 in
  `circuits/preamp/` è **Fase 4**, ed è l'unico passo che tiene aperta
  NC-017.
- **Rifare le misure del blocco.** PSRR, Z_out, risposta e margine di fase
  restano da rifare in Fase 4. I dati in `data/2026-09-09/` descrivono la
  topologia col THAT320, quelli in `data/2026-09-10/` lo stadio d'ingresso con
  l'LS352.
- **Le altre non conformità.** Hanno i loro lotti — con l'eccezione motivata
  di **NC-026**, che sta sulla strada di questo lotto (vedi sopra).
- **Non toccare i file già in `vendor/`**: sono la traccia di controllo. Una
  correzione si aggiunge accanto come addendum — è quello che ha fatto L7 —
  non si riscrive l'originale.

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.** Un
  compito ereditato è un'ipotesi, non un dato — L24 lo ha dimostrato sulla
  conclusione di L8, L25 su quattro cifre di f_T di L24 (una cambiava un
  verdetto), e L21 rileggendo il pinout del relè invece di ereditarlo.
- **Un controllo mai fatto fallire non è un controllo.** L21 ha trovato, nel
  guardiano che stava scrivendo, un parser che perdeva l'ultima net del file e
  un blocco di suite che sarebbe stato verde qualunque cosa. Entrambi sono
  emersi facendolo fallire di proposito.
- **Cerca se qualcuno ha già deciso, prima di aprire una voce.**
- **Niente cifre non eseguite.**
- **Diffida degli script che dichiarano di aver verificato qualcosa.**
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`: eseguiti da un worktree leggono e scrivono nel
  checkout principale, in silenzio. Se il tuo lotto ne tocca uno, correggilo lì.
- **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo (la tabella deve dire **fatto**)
2. **riscrivi QUESTO file per il lotto successivo** — se il titolo nomina
   ancora L10, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L10` — verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
