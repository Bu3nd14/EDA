# Prompt per la sessione successiva — L14

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L14** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto sono tre correzioni di testo

Il lotto precedente è **L10**, che ha fuso l'LSK489 in **una** Part a due
unità col pinout letto dal datasheet congelato, e ha chiuso **NC-026**. Tre
cose di quel lotto ti riguardano prima di toccare qualsiasi cosa:

1. **La suite è a 8 blocchi.** Il **2f** esegue il disegno a blocchi
   (`preamp_blocks_draw.py`) e pretende exit 0; il **2g**
   (`scripts/check_deck_refs.py`) pretende che ogni dispositivo citato da un
   deck esista. Se tocchi un deck o un disegno, devono restare verdi.
2. **Due deck erano rotti da L22, in silenzio, e ngspice usciva 0.** Il
   controfattuale di V2 apriva un resistore inesistente, e lo sweep del bias
   spazzava il ramo sbagliato. Riparati, dati in `data/2026-09-13/`. La
   lezione vale anche per un lotto di solo testo: **ngspice non fallisce su un
   nome di dispositivo che non trova**, e un nome che esiste ma è un altro non
   lo vede nessuno (`limitations.md` #22).
3. **Una voce nuova, minore: NC-027** — i pin SS (3, 7) dell'LSK489 sono
   disegnati dal suo datasheet e mai definiti. Ha il suo lotto, **L28**. Non è
   tuo.

Bloccanti invariate: **sei** — NC-001 (L11), NC-002 e NC-021 (L12), NC-004,
NC-010 (L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. **`docs/preamp/STATE.md`** — «Come si lavora da qui», la tabella dei lotti,
   la sezione **L10**, e **«Prossimo passo concreto»**, che contiene il mandato
   di questo lotto per esteso
3. **`docs/preamp/NONCOMPLIANCE.md`**, voci **NC-003**, **NC-006**, **NC-007**
   — le tre che chiudi — e **NC-002**, che NC-003 cita
4. **`docs/preamp/decisions/ADR-014-*.md`** — la claim che NC-007 dice
   misurata male
5. **`docs/preamp/dossier/build_dossier.py`** — l'intestazione, per sapere
   come si rigenera il dossier e da quali dati legge
6. **`docs/limitations.md`** — in particolare #10, #22 e #23

## IL LOTTO: L14 — le tre correzioni di testo

**Il difetto comune.** Tre punti in cui ciò che il repo **dice** non è ciò che
i suoi dati **misurano**. Nessuno cambia un numero del circuito; tutti e tre
cambiano ciò che un lettore porta via.

**Cosa fare:**

1. **NC-006** — `circuits/preamp/gain_block.py` righe **314** («Cascode base
   reference: 8.485 V») e **321** («the JFET drains at a fixed 7.8 V») sono la
   bozza abbandonata; il codice implementa il partitore 4,99k/10,0k. Allineali
   al valore implementato citando ADR-014 e il log che lo misura. La riga
   **153** («First draft used 8.485 V») è storia dichiarata: **resta**.
2. **NC-007** — `docs/preamp/dossier/build_dossier.py:782` pubblica lo
   «Scarto ADR-014» **a 20 kHz**. Quella cifra è il partitore 2500 Ω / 1 MΩ, a
   banda larga, e ci sarebbe identica senza cascode. Il dossier deve
   presentare lo scarto **riferito a 1 kHz** come misura della claim (o
   entrambe, dicendo cosa misura ciascuna), e il KPI in testa cita quello.
3. **NC-003** — `build_dossier.py:783`, KPI «Margine di fase, peggiore»: è il
   peggiore dei **quattro casi pubblicati del blocco B**, non del prodotto. Il
   KPI prende il qualificatore.
4. Rigenerare il dossier e **leggere l'`index.html` prodotto**.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **La diagnosi completa sta nelle tre voci**, con le cifre rieseguite da G0:
  0,02167 dB a tutte le frequenze per il partitore, 4,35·10⁻⁵ dB riferito a
  1 kHz, 41,98° per il blocco A.
- **Il dossier legge `data/2026-09-09/`**, cioè la topologia col THAT320. È
  dichiarato: L14 corregge *come* le cifre sono presentate, non le rimisura.
- **Un commento spostato in `gain_block.py` sposta i `SKiDL Line`** della
  netlist. Se rigeneri, il confronto è quello normalizzato (L3b), e i nomi
  delle net fuse possono cambiare da soli (#23): nessuno dei due è un cambio di
  topologia.

## Cosa NON accettare

- **Una cifra copiata dalla voce invece che riletta dal log.** NC-006 cita
  `data/2026-09-09/tb_op.log`, che è di prima di L22; da allora esiste
  `data/2026-09-10/tb_op-LS352.log`. Leggi quale descrive la topologia di oggi
  e cita quello.
- **Una verifica fatta sul sorgente del dossier.** `build_dossier.py` dice
  cosa volevi; `index.html` dice cosa hai pubblicato.
- **Un KPI che chiude la voce e lascia il corpo del dossier a dire l'altra
  cifra.** NC-007 lo dice: circolano due cifre per la stessa claim.

## NON fa parte di questo lotto

- **NC-002** (il blocco A sotto i 60°): è **L12**, ed è un rimedio, non una
  frase. NC-003 si chiude col qualificatore, non portando il blocco A nel KPI.
- **NC-005**, il vincolo su E3: è **L15**.
- **Rimisurare qualsiasi cosa.** PSRR, Z_out, risposta e margine di fase
  restano da rifare in Fase 4.
- **NC-027** e le altre voci: hanno i loro lotti.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.** L10
  lo ha appena rifatto: facendo la baseline dei deck *prima* di toccarli ha
  trovato due guasti che L22 aveva dichiarato sistemati.
- **Un controllo mai fatto fallire non è un controllo.** L10 ha fatto fallire
  i due blocchi nuovi sui file di prima, prima di dichiararli verdi.
- **Cerca se qualcuno ha già deciso, prima di aprire una voce.**
- **Niente cifre non eseguite.**
- **Diffida degli script che dichiarano di aver verificato qualcosa.**
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`. Se il tuo lotto ne tocca uno, correggilo lì.
- **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo (la tabella deve dire **fatto**)
2. **riscrivi QUESTO file per il lotto successivo** — se il titolo nomina
   ancora L14, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L14` — verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
