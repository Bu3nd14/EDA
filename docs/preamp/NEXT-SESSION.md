# Prompt per la sessione successiva — L15

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L15** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è un vincolo scritto

Il lotto precedente è **L14**, che ha chiuso tre voci minori di testo senza
toccare un numero del circuito. Tre cose di quel lotto ti riguardano:

1. **Il dossier ora dice cosa misura ogni cifra.** Lo scarto ADR-014 ha due
   cifre, ciascuna col suo nome: lo scarto **riferito a 1 kHz**, che è la
   claim (4,35·10⁻⁵ dB a 0 dB, 1,37·10⁻⁴ a +10 dB, e il KPI cita il peggiore),
   e lo scarto **assoluto**, che è il partitore con la Zin (−0,0217 dB a ogni
   frequenza). Il KPI del margine di fase dice «blocco B, peggiore dei 4 casi
   pubblicati». Se tocchi il dossier, verifica su `index.html`, non su
   `build_dossier.py`.
2. **Una cifra si rilegge dal log della topologia di oggi**, non dalla voce che
   la cita. NC-006 citava un log col THAT320, e quello giusto era
   `data/2026-09-10/tb_op-LS352.log`, riconfermato rieseguendo `tb_op`. Vale
   anche per te: NC-005 è stata scritta a G0, prima di L22 e L26.
3. **Un altro percorso cablato, visto e non corretto**:
   `testbenches/01_op.cir:10` scrive in `/Users/roberto/EDA/results/`, quindi il
   blocco 2b della suite, eseguito da un worktree, legge il wrdata dal checkout
   principale.

Voci: **19 aperte, 6 bloccanti** — NC-001 (L11), NC-002 e NC-021 (L12), NC-004,
NC-010 (L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. **`docs/preamp/STATE.md`** — «Come si lavora da qui», la tabella dei lotti,
   la sezione **L14**, e **«Prossimo passo concreto»**, che contiene il mandato
   di questo lotto per esteso
3. **`docs/preamp/NONCOMPLIANCE.md`**, voce **NC-005** — quella che chiudi — e
   **NC-009**, che porta lo stesso trim con l'altro vincolo, quello opposto
4. **`docs/preamp/REQUIREMENTS.md`** — E3, F2, F8 e la matrice V1, che elenca
   «le tre posizioni del trim»
5. **`docs/preamp/decisions/README.md`** (le regole delle ADR) e
   **`ADR-011-trim-per-ingresso.md`**, compreso il suo «Aggiornamento» in coda
6. **`docs/preamp/decisions/ADR-015-*.md`** e **`ADR-019-*.md`** — perché il
   trim è diventato portante (headroom) e interbloccato col mute

## IL LOTTO: L15 — il vincolo su E3 scritto dove verrà letto

**Il difetto.** E3 chiede Zin ≥ 100 kΩ. Il trim 0 / −6 / −12 dB di ADR-011 sta
**a monte** del blocco A, e nessun documento dice che anche il trim deve
rispettare E3. Un partitore dimensionato senza quel vincolo — 10 k / 3,3 k per
i −12 dB — porterebbe la Zin a ~13 kΩ, e niente nel repo lo segnalerebbe.

**Cosa fare:**

1. Scrivere il vincolo: «la resistenza vista all'ingresso, **in ogni posizione**
   del ponticello di trim, deve restare ≥ 100 kΩ». Va scritto accanto al
   requisito che lo impone, e con i due fatti che il dimensionamento dovrà
   conciliare: l'attenuazione chiesta da ADR-015 (NC-009) e il rumore di un
   partitore ad alta impedenza.
2. **Decidere dove, e scrivere perché.** Due vincoli di forma, trovati leggendo
   in L14:
   - **le ADR non si riscrivono** (`decisions/README.md`, regola 2), ma ADR-011
     porta già un «Aggiornamento 2026-09-08» in coda col testo sopra intatto,
     e anche ADR-001, ADR-007 e ADR-008 hanno aggiunte. Verifica se la forma
     «addendum datato» è coerente con la regola **prima** di usarla;
   - `REQUIREMENTS.md` è congelato, e **ogni modifica sostanziale vuole una
     ADR** (`CLAUDE.md`). Decidi se rendere esplicito un vincolo implicato da
     E3 sia sostanziale, e scrivi la risposta.
3. Chiudere NC-005 **per la metà che le compete**: il vincolo scritto. La
   misura AC che la voce chiede «quando la scheda sarà in `circuits/preamp/`» è
   di **L16**.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **`R_IN = "1M"`** in `circuits/preamp/gain_block.py:118` fissa la Zin del
  solo blocco A; `preamp_audio.py:23` dichiara selettore e trim fuori dal
  proprio perimetro.
- **La suite è a 8 blocchi**, 8 passed a fine L14.
- **Cerca se qualcuno ha già deciso**: la voce è di G0 (2026-09-09). Da allora
  ADR-015, ADR-019 e F8 hanno cambiato il ruolo del trim.

## Cosa NON accettare

- **Un'ADR riscritta.** Se scegli ADR-011, la forma è quella che le regole
  permettono, verificata, non «aggiungo una riga».
- **Un vincolo senza verbo verificabile.** «Deve restare ≥ 100 kΩ in ogni
  posizione» si può misurare; «va tenuta alta» no.
- **Un dimensionamento del trim.** È L16.

## NON fa parte di questo lotto

- **Dimensionare o simulare il trim**: **L16** (NC-009, NC-023, e NC-005 lato
  misura).
- **NC-011**, il vincolo PSRR per l'alimentatore: è **L18**, stessa forma ma
  lotto suo.
- **Rimisurare qualsiasi cosa.**
- **Il percorso cablato di `testbenches/01_op.cir`**: annotato, non tuo.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.**
  L14 l'ha rifatto: la voce citava il log di una topologia superata.
- **Un controllo mai fatto fallire non è un controllo.** L14 ha fatto fallire
  la prova AST su un valore alterato prima di fidarsene.
- **Cerca se qualcuno ha già deciso, prima di aprire una voce.**
- **Niente cifre non eseguite.**
- **Diffida degli script che dichiarano di aver verificato qualcosa.**
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`. Se il tuo lotto ne tocca uno, correggilo lì.
- **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo. Nel worktree, lancia gli script
  zsh **da soli**, non in comandi composti: il guardiano di isolamento li
  rifiuta.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo (la tabella deve dire **fatto**)
2. **riscrivi QUESTO file per il lotto successivo** — se il titolo nomina
   ancora L15, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L15` — verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
