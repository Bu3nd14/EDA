# Prompt per la sessione successiva — L21

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L21** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è il polo del relè

Il lotto precedente è **L25**, che ha promosso in `models/` i cinque modelli
vendor congelati da L24. Tre cose di quel lotto ti riguardano prima di toccare
qualsiasi cosa:

1. **Tutti e sette i dispositivi attivi hanno ora un modello del costruttore
   in `models/`** — prima volta da G0. La libreria passa da 28 a **38 check**,
   tutti verdi. Di **NC-017** (bloccante) resta il solo passo di **Fase 4**: la
   sostituzione in `circuits/preamp/`. **Non è questo lotto.**
2. **Rimisurando sono cadute due cifre di L24**, e la seconda ha cambiato un
   verdetto. La f_T del MMBT5401 era presa a I_C = 12,68 mA invece dei 10 mA
   del datasheet (169,5 → **160,1 MHz**); le f_T dei due MJE erano lette come
   attraversamento a guadagno unitario invece che come la **Nota 2** del
   datasheet le definisce (`fT = hfe · ftest`, ftest = 1 MHz) — e letta così
   **nessuno dei due raggiunge il minimo di 30 MHz**. È **NC-025**. Più
   **NC-024**, l'h_FE del MJE15032 sotto il proprio minimo, che L24 aveva
   misurato ma mai messo a registro. **22 voci, 7 bloccanti.**
3. **Una trappola nuova che vale per chiunque tocchi un file con CRLF**: il
   tool di editing **normalizza le fini riga in silenzio**. In L25 tre
   modifiche di sola prosa hanno tolto il CR da ogni riga di testo vendor;
   ngspice non se ne accorge e `git diff` mostra righe che a occhio
   coincidono. L'unica cosa che l'ha detto è stato un `diff` esplicito.

Nessuno dei tre invalida L21, che non tocca né modelli né misure.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. **`docs/preamp/STATE.md`** — la sezione «Come si lavora da qui», la tabella
   dei lotti, la sezione **L25**, e **«Prossimo passo concreto»**, che contiene
   il mandato di questo lotto per esteso
3. **`docs/preamp/NONCOMPLIANCE.md`**, voce **NC-014** — il difetto, la sua
   evidenza e cosa serve per chiuderla
4. **`docs/preamp/decisions/ADR-012-*.md`** — la decisione sul mute che questo
   difetto rende inefficace su un canale
5. **`docs/preamp/reports/2026-09-10-L8-parti-nuove.md`**, la sezione sul relè
   Omron — è dove il pinout è stato letto dal datasheet
6. **`docs/limitations.md`** — prima di scrivere codice, in particolare #13,
   #14 e #16

## IL LOTTO: L21 — il polo 2 del relè, corretto e riverificato

Chiude **NC-014**, che è **bloccante**. È la voce più economica del registro.

**Il difetto.** Il datasheet del G6K dà **polo 1: COM 3, NC 2, NO 4** e
**polo 2: COM 6, NC 7, NO 5**. La riga **79** di
`circuits/preamp/preamp_audio.py` dichiara `K_NO2="7", K_NC2="5"`:
**scambiati**. Il polo 1 è corretto.

La trappola è che le due lame pendono dalla stessa parte del package, ma la
riga alta è numerata 8-7-6-5 e quella bassa 1-2-3-4: la regola implicita
«NO = COM+1» è giusta per un polo e sbagliata per l'altro.

**Perché è bloccante.** Il polo 2 serve il **canale destro**. A bobina
diseccitata — cioè **all'accensione** — quel canale **non viene messo a massa**
e il transitorio passa. È esattamente il guasto silenzioso contro cui ADR-012
è stata scritta, col ramo cuffie che finisce in un paio di elettrostatiche. (A
bobina eccitata il canale destro sarebbe cortocircuitato: rumoroso, e lo si
troverebbe al primo collaudo. È il caso *fortunato*.)

**Cosa fare, ed è tutto:**

1. riga 79 in `K_NO2="5", K_NC2="7"` — NO 5 e NC 7, come il datasheet;
2. **rigenerare** gli artefatti col venv SKiDL
   (`/Users/roberto/EDA/env/venv/bin/python3`);
3. **verificare sulla netlist, non sul sorgente**: il contatto verso massa di
   ogni mute deve cadere su **2 e 7**, e il ramo di `R_g` su **4 e 5**;
4. `check_schematic.py` deve continuare a passare, e `run_tests.sh` restare
   5/5.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **Un `.net` di SKiDL non è riproducibile byte a byte** (L3b). Il campo
  `(date)`, i tag casuali, gli UUID `(tstamps)` e i riferimenti `SKiDL Line`
  cambiano a ogni rigenerazione. **Il confronto è quello normalizzato**: si
  tolgono `(date`, `SKiDL Tag`, `SKiDL Line` e `(tstamps`, e si confronta il
  resto. Con quel filtro il diff di una rigenerazione a sorgente invariato è
  **vuoto** — provato in L3b su entrambi i file.
- **Fondere o spostare componenti slitta i riferimenti** (L22). Non dovrebbe
  succedere qui, ma se succede: la mappa vecchio→nuovo si **ricava
  confrontando i nodi** fra il `.inc` vecchio e quello nuovo, non si deduce a
  mano.
- **`check_schematic.py` fa il suo mestiere**: in L22 ha rifiutato alla prima
  esecuzione con 15 discordanze. Se rifiuta, ha ragione.
- **La verifica «sulla netlist» è la forma che conta.** Il sorgente dice cosa
  volevi, la netlist dice cosa hai fatto. NC-014 esiste proprio perché una
  regola implicita sembrava giusta guardando il sorgente.

## Cosa NON accettare

- **Una correzione dedotta dalla simmetria.** Il pinout va letto dal datasheet
  congelato, non ricavato dalla regola «NO = COM+1» — è la regola che ha
  prodotto il difetto.
- **Una verifica fatta sul sorgente.** Se la prova non passa dalla netlist
  generata, non è una prova.
- **Un `git diff` su un `.net` letto come prova che la topologia è cambiata (o
  non è cambiata).** Vedi sopra: serve il confronto normalizzato.
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
- **Le altre non conformità.** Hanno i loro lotti. Le bloccanti che restano
  dopo L21: NC-001 (L11), NC-002 e NC-021 (L12), NC-004, NC-010 (L17),
  NC-017 (Fase 4).
- **Non toccare i file già in `vendor/`**: sono la traccia di controllo. Una
  correzione si aggiunge accanto come addendum — è quello che ha fatto L7 —
  non si riscrive l'originale.

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.** Un
  compito ereditato è un'ipotesi, non un dato — L24 lo ha dimostrato sulla
  conclusione di L8, L22 su `mfg=`, e **L25 su quattro cifre di f_T di L24**,
  una delle quali cambiava un verdetto.
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
   ancora L21, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L21` — verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
