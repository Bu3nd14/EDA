# Prompt per la sessione successiva — L11

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L11** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è una bloccante

I tre lotti precedenti — **L14, L15, L18** — erano di testo: correzioni e
vincoli scritti, nessun valore del circuito toccato. **L11 è il primo di quelli
che toccano davvero il prodotto**: la voce che chiude è bloccante.

Dopo la chiusura di L18, **l'utente ha preso tre decisioni** che cambiano il
mandato di questo lotto. Sono riportate per esteso qui sotto e non sono
ancora in nessuna ADR: **registrarle è il primo passo**.

Tre cose di L18 ti riguardano:

1. **Le cifre delle voci vanno rilette dalla topologia di oggi.** L18 ha
   rieseguito `tb_zout_psrr_noise.cir`. Il rail + si è mosso di 0,1 dB, ma il
   rail − di **4,74 dB**, e nessuno lo sapeva. Le cifre di NC-001 sono di G0,
   cioè della topologia **col THAT320**.
2. **Come si prova che un deck ha letto il circuito giusto.** Con un numero
   indipendente che può fallire: L18 ha controllato che il rumore di caso
   peggiore desse 4,231 µV (LS352) e non 5,697 (THAT320).
3. **ADR-020** riserva 1 µV RMS dei 10 µV di E5 al ripple d'alimentazione. Se
   entra un microcontrollore, anche il suo rumore consuma lo stesso budget.

Voci: **19 aperte, 6 bloccanti**. Le bloccanti sono NC-001 (L11), NC-002 e
NC-021 (L12), NC-004, NC-010 (L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto).
2. **`docs/preamp/STATE.md`**: «Come si lavora da qui», la tabella dei lotti,
   le tre voci di diario «Dopo L18» e **«Prossimo passo concreto»**.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-001**, quella che chiudi, e
   **NC-010**, che ha la stessa fisica. Poi **NC-024** / **NC-025**: i modelli
   MJE stanno sotto i minimi del datasheet e pesano su qualsiasi calcolo
   termico.
4. **`docs/preamp/decisions/`**, le ADR che le tre decisioni toccano:
   - **ADR-003**: Classe A, nessun operazionale nel percorso del segnale;
   - **ADR-007**: nessun servo di continua;
   - **ADR-009**: nessun microcontrollore in tutto il progetto;
   - **ADR-012**: relè di mute «per qualche secondo»;
   - **ADR-019**: il contatto del mute è il permissivo del trim.
5. **`docs/preamp/reports/2026-09-09-gate-G0.md`**: come G0 ha simulato il
   mute, e la verifica dell'orchestratore in fondo.
6. **`circuits/preamp/preamp_audio.py`**: il cablaggio del mute e il commento
   di L21 sui due poli del G6K-2F-Y.

## IL LOTTO: L11 — mute e corto sulle uscite

**Il difetto.** A mute inserito i contatti NC mettono a massa i jack, a valle
di 47 Ω e 4,7 µF. Lo stadio d'uscita vede ≈ 58,6 Ω a 1 kHz invece di 100 kΩ.
G0 ha simulato I_C del dispositivo d'uscita a **65,07 mA** (0 dB) e
**203,2 mA** (+10 dB), contro circa 14,6 mA di riposo: **classe B**. È una
condizione che F6 fa attraversare a ogni commutazione di guadagno, contraddice
T1, e **non esiste nessun deck versionato** per il mute.

### Le tre decisioni dell'utente (2026-09-13)

Parole dell'utente, refusi corretti.

**1. Il mute a tempo indefinito.**

> «il mute deve potersi tenere a tempo indefinito a costo di cambiare la
> topologia»
>
> «la classe B può essere accettata in mute, ma il mute non deve mettere a
> rischio la termica»

Il mandato di L18 proponeva un'ADR che accettasse la classe B «per la durata
del temporizzatore». Quella strada **contraddiceva già ADR-019**: il mute è il
permissivo del trim, e chi regola il trim lo tiene inserito quanto vuole.

**2. La protezione dal corto sulle uscite, come risultato e non come tecnica.**

> «dovremo inserire la protezione per il corto sulle uscite, non possiamo
> essere certi che le uscite non vengano messe in corto»
>
> «il requisito non dice come proteggersi dal corto vero? non vorrei al
> momento dell'implementazione che venisse esclusa la possibilità di staccare
> o mutare le uscite in maniera attiva»

Il requisito **descrive l'esito e non prescrive la tecnica**:
- **Il requisito.** Con un corto al connettore di **una qualsiasi delle tre
  uscite**, per un tempo indefinito e con segnale presente, **nessun
  dispositivo esce dai propri limiti termici e di area di lavoro sicura
  (SOA)**.
- **Il transitorio conta.** Il vincolo vale anche nel tempo che passa fra
  l'inizio del corto e l'intervento di un'eventuale protezione.
- **Le tecniche ammesse**, da confrontare coi numeri:
  - limitazione di corrente;
  - distacco attivo dell'uscita;
  - mute attivo.
- **La classe B** è ammessa a mute inserito e durante un corto: con un corto al
  connettore è inevitabile.
- **Il mute è un caso particolare del corto.** Il contatto NC mette a massa lo
  stesso nodo del jack su cui arriva un corto esterno.

**3. Operazionali e microcontrollore: fuori dal percorso del segnale, ammessi
nel circuito.**

> «e se decidessimo che operazionali e micro non devono essere sul percorso
> segnale ma possono essere nel circuito?»
>
> «si procedi come hai detto»

- **Operazionali.** ADR-003 e T1 li vietano già **solo** nel percorso del
  segnale. Manca una **definizione verificabile di percorso del segnale**:
  - nessun integrato **attraversato dal segnale** o che **chiuda un anello sul
    segnale**. Il servo di continua resta escluso (T2, ADR-007) perché chiude
    l'anello, anche se non sta in serie;
  - un ingresso **di sola rilevazione** su un nodo di segnale è ammesso, se il
    suo effetto su E4, E5 e sulla risposta è **misurato** e sta sotto soglie
    scritte con numeri.
- **Microcontrollore.** ADR-009 lo esclude «in tutto il progetto». Per
  ammetterlo fuori dal percorso serve un'ADR nuova che superi **quella
  clausola** e aggiorni F7. L'attenuatore a scatti di ADR-009 resta com'è.
  Valgono tre condizioni:
  1. **stato sicuro senza firmware.** Microcontrollore spento, in reset,
     bloccato o in brown-out ⇒ relè a riposo ⇒ uscite nello stato sicuro. Il
     guardiano `check_relay_safe_state.py` si estende, non si rilassa;
  2. **la protezione dal corto non dipende solo dal firmware.** Rilevamento e
     distacco funzionano anche a microcontrollore bloccato: può coordinare e
     decidere il ricollegamento, ma non essere l'unica barriera;
  3. **il rumore digitale ha un budget misurato**, come ADR-020 per il ripple:
     un contributo massimo in uscita dentro E5, verificato, e un'alimentazione
     separata per la parte digitale.

### Cosa fare

1. **Registrare le decisioni, per prima**, in due ADR nuove, secondo TEMPLATE e
   con le righe nell'indice di `decisions/README.md`:
   - **ADR-021 — mute e corto sulle uscite.**
     - Supera la durata «qualche secondo» di ADR-012 e aggiorna F6.
     - Aggiunge in `REQUIREMENTS.md` il requisito di protezione dal corto,
       scritto come **risultato**, e dichiara l'eccezione a T1 / ADR-003 a
       mute inserito e in corto.
     - Fissa il criterio con un **verbo verificabile**, **a regime** e **sul
       transitorio d'intervento**.
     - I numeri (temperatura di giunzione massima, declassamento, curve SOA,
       temperatura nel telaio chiuso di P5) si ricavano da datasheet e
       ADR-010, **non si inventano**.
   - **ADR-022 — operazionali e microcontrollore fuori dal percorso del
     segnale.**
     - Supera la clausola di ADR-009, aggiorna F7, e dà a T1 la definizione
       verificabile di percorso del segnale.
     - Le tre condizioni del microcontrollore, con i numeri: il budget di
       rumore digitale è **una ripartizione di E5**, come ADR-020.

   Tutte e due sono sostanziali col criterio di L15, perché cambiano l'insieme
   dei progetti conformi. Se una scelta richiede una decisione di prodotto, è
   dell'utente.
2. **La misura, sulla topologia di oggi**, che non ha alcuna protezione. Un deck
   in `spice/preamp/tb/` (convenzione `@REPO@`, `wrdata` con nome nudo) misura,
   per i due dispositivi d'uscita:
   - I_C e **dissipazione a regime**, sia a mute inserito sia **con ciascuna
     delle tre uscite in corto al connettore** (le fisse caricano il blocco A,
     la principale il blocco B);
   - il transitorio di inserzione e di rilascio del mute.

   Va eseguito nelle modalità di guadagno che la topologia ha, **con segnale
   presente** (il mute non spegne la sorgente, e il trim si regola a mute
   inserito). Dati in `docs/preamp/data/<data>/`. Confronta con G0 e registra
   lo scarto. È la **baseline**: dice se oggi serve una protezione, e contro
   quali correnti.
3. **I riferimenti della voce non valgono più: verificali, non ricopiarli.**
   - NC-001 cita le righe 132-141 e 242-243 di `preamp_audio.py`: oggi il
     contatto NC verso massa è alla **riga 264** (`k[nc] += GND`) e le liste
     dei jack alle 162-168 e 205-206.
   - `@q134[ic]` è **+14,557 mA** in `data/2026-09-09/tb_op.log` e
     **−14,557 mA** in `data/2026-09-10/tb_op-LS352.log`: dopo le
     rinumerazioni di L22 e L10 quel nome indica con ogni probabilità l'altro
     dispositivo. Ricava i nomi dalla netlist di oggi.
4. **Il rimedio: scegliere la tecnica coi numeri, poi verificarla sulle due
   finestre.**
   - **Se la topologia di oggi regge in tutti i casi**, NC-001 si chiude con:
     - le ADR del passo 1;
     - il calcolo termico e SOA su MJE15032/33, coi modelli e tenendo conto di
       NC-024 e NC-025;
     - la correzione di «Classe A garantita» dovunque sia scritta, perché a
       mute e in corto non è più vera.
   - **Se non regge**, si confrontano le tecniche ammesse, ciascuna con i suoi
     costi misurati:
     - **limitazione di corrente**: una resistenza in serie si somma ai 47 Ω
       contro E4 (< 100 Ω; oggi al jack ≈ 59-61 Ω a 1 kHz, da
       `data/2026-09-13/tb_zout_psrr_noise-LS352.log`), mentre un limitatore
       attivo nello stadio d'uscita tocca il percorso del segnale;
     - **distacco attivo**: un contatto in serie nel percorso del segnale, un
       tempo di reazione, e una scelta fra ricollegamento automatico e blocco;
     - **mute attivo**: vedi i vincoli qui sotto.
   - **Verificare la tecnica scelta** a regime e sul transitorio d'intervento,
     su ogni via da cui il corto può arrivare.
   - **Il blocco A in corto su una fissa.** Se non regge, lo si registra in
     **NC-010** e lo si lascia a L17.

**Se il lotto non sta in una sessione, si divide.** L11a: le due ADR più la
baseline. L11b: il rimedio. È la regola dei lotti per dimensione.

### I vincoli che una protezione attiva incontra

1. **Il mute di oggi non protegge dal corto.** È in derivazione: mette a massa
   il jack, quindi durante un corto ne aggiungerebbe un secondo invece di
   togliere il primo. Una protezione «a mute» funziona solo con un mute **in
   serie**, che apre l'uscita. Toglierebbe anche il problema termico del mute
   tenuto a lungo, ma cambia ADR-012.
2. **Lo stato sicuro dei relè cambia.** Oggi `check_relay_safe_state.py`
   verifica che a bobine diseccitate il mute metta le uscite a massa, e
   ADR-019 usa quel contatto come permissivo del trim. Un distacco in serie
   ridefinisce quale sia lo stato sicuro. Va **deciso esplicitamente**, e il
   guardiano va riscritto e fatto fallire di nuovo, non aggirato.
3. **Ricollegamento automatico o blocco dopo il corto.** È una scelta
   dell'utente, e va chiesta.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **La suite è a 8 blocchi**, 8 passed a fine L18.
- **Il guardiano del mute**: `scripts/check_relay_safe_state.py` asserisce
  sulla netlist «mute diseccitato ⇒ uscita a massa». Se tocchi il contatto,
  fallo fallire di nuovo prima di fidarti.
- **Il pinout del G6K-2F-Y è letto dal datasheet** (L21): «NO = COM+1» vale
  per il polo 1 e **non** per il polo 2.
- **La convenzione dei deck** (L2-L3) e la trappola dei `$var` nei nomi
  `wrdata` (`docs/limitations.md` #10).
- **Il corto su una fissa è già spazzato**: `tb_blockA_carichi.cir` scende
  fino a 0,01 Ω a valle della fissa. I dati del 2026-09-09 sono però della
  topologia col THAT320, quindi va rieseguito.
- **Il simbolo degli op-amp audio e dei comparatori**: la libreria KiCad ha già
  `Amplifier_Operational.kicad_sym` (vedi `CLAUDE.md`), se la protezione ne
  usa uno fuori dal percorso.

## Cosa NON accettare

- **Una cifra di G0 usata senza dire che è della topologia col THAT320.**
- **Un nome di dispositivo copiato da un log vecchio.**
- **Una verifica termica limitata alla durata di un temporizzatore.** Il mute
  si tiene a tempo indefinito.
- **Un requisito o un'ADR che prescriva la tecnica di protezione.** Il
  requisito dice l'esito; la tecnica si sceglie coi numeri.
- **Una verifica solo a regime per una protezione attiva.** Il rischio sta nel
  transitorio prima dell'intervento.
- **Un mute in derivazione presentato come protezione dal corto.**
- **Una protezione che regge solo se il firmware funziona.**
- **Un rimedio che protegge una via sola.** Il corto può arrivare dal mute o
  dal connettore di ciascuna uscita.
- **Un deck che esce 0 e che nessuno ha provato a far fallire**: L10 ne ha
  trovati due rotti in silenzio.
- **Un'ADR riscritta**, o un'aggiunta in coda a una ADR esistente (ADR-003,
  ADR-009 e ADR-012 si superano con ADR nuove).
- **Una netlist o uno schematico modificati a mano**: la topologia sta solo in
  `circuits/preamp/*.py`.

## NON fa parte di questo lotto

- **Il buffer sulle uscite fisse (L17, NC-010).** Il criterio di corto di
  ADR-021 vale anche per le fisse, ma il loro rimedio è di L17.
- **Il margine di fase (L12)**, il trim (L16), il terzo guadagno (L27).
- **L'alimentatore** (ADR-020 e la metà aperta di NC-011). Se entra un
  microcontrollore, l'alimentazione separata della parte digitale è un
  requisito da consegnare a quel lotto, non da progettare qui.
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
