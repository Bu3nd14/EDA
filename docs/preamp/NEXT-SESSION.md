# Prompt per la sessione successiva — L11

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L11** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è una bloccante

I tre lotti precedenti — **L14, L15, L18** — erano di testo: correzioni e
vincoli scritti, nessun valore del circuito toccato. **L11 è il primo di quelli
che toccano davvero il prodotto**: la voce che chiude è bloccante. Tre cose di
L18 ti riguardano:

1. **Le cifre delle voci vanno rilette dalla topologia di oggi.** L18 ha
   rieseguito `tb_zout_psrr_noise.cir`. Il rail + si è mosso di 0,1 dB, ma il
   rail − di **4,74 dB**, e nessuno lo sapeva. Le cifre di NC-001 sono di G0,
   cioè della topologia **col THAT320**.
2. **Come si prova che un deck ha letto il circuito giusto.** Con un numero
   indipendente che può fallire: L18 ha controllato che il rumore di caso
   peggiore desse 4,231 µV (LS352) e non 5,697 (THAT320).
3. **ADR-020** fissa la quota del ripple d'alimentazione (1 µV RMS in uscita).
   Non ti riguarda direttamente, ma è il primo vincolo che l'alimentatore
   dovrà rispettare.

Voci: **19 aperte, 6 bloccanti**. Le bloccanti sono NC-001 (L11), NC-002 e
NC-021 (L12), NC-004, NC-010 (L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto).
2. **`docs/preamp/STATE.md`**: «Come si lavora da qui», la tabella dei lotti,
   la sezione **L18** e **«Prossimo passo concreto»**, che contiene il mandato
   di questo lotto per esteso.
3. **`docs/preamp/NONCOMPLIANCE.md`**: la voce **NC-001**, quella che chiudi,
   e **NC-024** / **NC-025** (i modelli MJE sotto i minimi del datasheet), che
   pesano su qualsiasi calcolo termico.
4. **`docs/preamp/decisions/`**: **ADR-003** (Classe A), **ADR-012** (relè di
   mute), **ADR-019** (il contatto del mute è il permissivo del trim).
5. **`docs/preamp/reports/2026-09-09-gate-G0.md`**: come G0 ha simulato il
   mute, e la verifica dell'orchestratore in fondo.
6. **`circuits/preamp/preamp_audio.py`**: il cablaggio del mute e il commento
   di L21 sui due poli del G6K-2F-Y.

## IL LOTTO: L11 — mute: misurare e rimediare

**Il difetto.** A mute inserito i contatti NC mettono a massa i jack, a valle
di 47 Ω e 4,7 µF. Lo stadio d'uscita vede ≈ 58,6 Ω a 1 kHz invece di 100 kΩ.
G0 ha simulato I_C del dispositivo d'uscita a **65,07 mA** (0 dB) e
**203,2 mA** (+10 dB), contro circa 14,6 mA di riposo: **classe B**, in una
condizione che F6 fa attraversare a ogni commutazione di guadagno. Contraddice
T1, e **non esiste nessun deck versionato** per il mute.

**La decisione dell'utente (2026-09-13, dopo la chiusura di L18).** Il
mandato scritto da L18 proponeva come seconda strada un'ADR che accettasse la
classe B «per la durata del temporizzatore». L'utente l'ha corretta così (in
due messaggi, refusi corretti):

> «il mute deve potersi tenere a tempo indefinito a costo di cambiare la
> topologia»
>
> «la classe B può essere accettata in mute, ma il mute non deve mettere a
> rischio la termica»

Quindi:
- **il mute si può tenere inserito senza limite di tempo.** Era già implicito
  in ADR-019, perché il mute è il permissivo del trim e chi regola il trim lo
  tiene inserito quanto vuole. Ma ADR-012 parla ancora di «qualche secondo»;
- **a mute inserito la classe B è ammessa.** Fuori dal mute, T1 resta com'è;
- **il criterio è termico e a regime**: col mute tenuto indefinitamente,
  nella condizione peggiore che l'uso consente, nessun dispositivo esce dai
  propri limiti. Se la topologia di oggi non ci sta, la topologia cambia.

**Cosa fare:**

1. **Registrare la decisione, per prima.** Una ADR nuova (**ADR-021**, secondo
   TEMPLATE e con la sua riga nell'indice) che:
   - supera la durata di ADR-012 e aggiorna F6;
   - ammette la classe B a mute inserito come eccezione dichiarata a T1 e
     ADR-003;
   - fissa il criterio termico con un **verbo verificabile**.

   Col criterio di L15 la modifica è sostanziale. Un progetto
   termicamente sicuro solo per qualche secondo era conforme e ora non lo è
   più; uno in classe B a mute violava T1 e ora no. I numeri del criterio
   (temperatura di giunzione massima, declassamento, temperatura dentro il
   telaio chiuso di P5) si ricavano dai datasheet e da ADR-010, **non si
   inventano**. Se richiedono una scelta di prodotto, la scelta è dell'utente.
2. **La misura, sulla topologia di oggi.** Un deck in `spice/preamp/tb/`
   (convenzione `@REPO@`, `wrdata` con nome nudo) che misuri, per i **due**
   dispositivi d'uscita:
   - I_C e **dissipazione a regime** a mute inserito;
   - il transitorio di inserzione e di rilascio.

   Va fatto nelle modalità di guadagno che la topologia ha, **con segnale
   presente all'ingresso**: il mute non spegne la sorgente, e il trim si regola
   a mute inserito. Dati in `docs/preamp/data/<data>/`. Confronta con G0 e
   registra lo scarto.
3. **I riferimenti della voce non valgono più: verificali, non ricopiarli.**
   - NC-001 cita le righe 132-141 e 242-243 di `preamp_audio.py`: oggi il
     contatto NC verso massa è alla **riga 264** (`k[nc] += GND`) e le liste
     dei jack alle 162-168 e 205-206.
   - `@q134[ic]` è **+14,557 mA** in `data/2026-09-09/tb_op.log` e
     **−14,557 mA** in `data/2026-09-10/tb_op-LS352.log`: dopo le
     rinumerazioni di L22 e L10 quel nome indica con ogni probabilità l'altro
     dispositivo. Ricava i nomi dalla netlist di oggi.
4. **Il rimedio, deciso dal verdetto termico a regime.**
   - **Se a regime i dispositivi reggono**, NC-001 si chiude con:
     - l'ADR del passo 1;
     - il calcolo termico su MJE15032/33, fatto coi loro modelli e tenendo
       conto di NC-024 e NC-025, che stanno sotto i minimi del datasheet;
     - la correzione di «Classe A garantita» ovunque sia scritta (almeno
       `gain_block.svg`), perché a mute inserito non è più vera.
   - **Se non reggono, la topologia cambia.** Una modifica in
     `preamp_audio.py` (resistenza in serie al contatto, o punto di
     derivazione spostato), rigenerata, più il deck. Tocca il contatto che
     ADR-019 usa come permissivo del trim, e `check_relay_safe_state.py`
     (blocco 2e) deve continuare a passare.
   - **Un calcolo termico su una durata finita non chiude niente.**

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **La suite è a 8 blocchi**, 8 passed a fine L18.
- **Il guardiano del mute**: `scripts/check_relay_safe_state.py` asserisce
  sulla netlist «mute diseccitato ⇒ uscita a massa». Se tocchi il contatto,
  fallo fallire di nuovo prima di fidarti.
- **Il pinout del G6K-2F-Y è letto dal datasheet** (L21): «NO = COM+1» vale per
  il polo 1 e **non** per il polo 2.
- **La convenzione dei deck** (L2-L3) e la trappola dei `$var` nei nomi
  `wrdata` (`docs/limitations.md` #10).

## Cosa NON accettare

- **Una cifra di G0 usata senza dire che è della topologia col THAT320.**
- **Un nome di dispositivo copiato da un log vecchio.**
- **Una verifica termica limitata alla durata di un temporizzatore.** Il mute
  si tiene a tempo indefinito: è una decisione dell'utente del 2026-09-13.
- **Un deck che esce 0 e che nessuno ha provato a far fallire**: L10 ne ha
  trovati due rotti in silenzio.
- **Un'ADR riscritta**, o un'aggiunta in coda a una ADR esistente.
- **Una netlist o uno schematico modificati a mano**: la topologia sta solo in
  `circuits/preamp/*.py`.

## NON fa parte di questo lotto

- **Il buffer sulle uscite fisse (L17, NC-010)**, anche se tocca gli stessi
  nodi.
- **Il margine di fase (L12)**, il trim (L16), il terzo guadagno (L27).
- **L'alimentatore** (ADR-020 e la metà aperta di NC-011).
- **Il dossier**, che legge ancora `data/2026-09-09`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto**,
  compresi i numeri di riga qui sopra.
- **Un controllo mai fatto fallire non è un controllo.**
- **Cerca se qualcuno ha già deciso, prima di aprire una voce.** L18 ha
  trovato la quota del ripple in un commento di Fase 2.
- **Niente cifre non eseguite.**
- **Diffida degli script che dichiarano di aver verificato qualcosa.**
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`. Se il tuo lotto ne tocca uno, correggilo lì.
- **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo. Nel worktree lancia gli script
  zsh **da soli**, non in comandi composti: il guardiano di isolamento li
  rifiuta. Una simulazione rieseguita da un worktree legge il circuito del
  worktree **solo** se il deck usa la convenzione di percorso di L2-L3:
  verificalo sul deck prima di fidarti del confronto.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo (la tabella deve dire **fatto**);
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L11, lo script rifiuta, ed è il controllo che esiste apposta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L11`: verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia;
5. rimuovi il worktree con i due comandi che lo script stampa;
6. **fermati.** Non iniziare il lotto dopo.
