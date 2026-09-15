# Prompt per la sessione successiva — L38

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L38** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**Il dossier pubblica E4 dai dati di L13, e NC-033 è chiusa.**
- **`build_dossier.py` legge E4 da `data/2026-09-15/L13/dopo/`**: tre uscite,
  costanza su trim × attenuatore, Zout a sorgente spenta. Rifiuta un percorso
  Zout sotto `2026-09-14/L27`.
- **Pubblicato**: Re(Z) max al jack **60,13 Ω** sulla principale e 53,13 Ω sulle
  fisse, dispersione col volume ≤ 1,0·10⁻⁴ Ω.
- **Il resto del dossier è provato identico** da uno script di confronto, in
  `data/2026-09-15/L37/`.

**Una lezione che vale anche qui: un criterio scritto nel mandato può non
distinguere niente.**
- **Il mandato chiedeva** di rifiutare «una Zout al nodo che scala col guadagno».
- **Anche la Zout vera scala col guadagno**, perché il guadagno d'anello cala.
  Il criterio alla lettera avrebbe rifiutato i dati buoni.
- **Rifatti i conti prima di scrivere il controllo**, è stato sostituito con la
  grandezza più un incrocio fra due deck. La limitazione #28 è corretta in coda.
- **Per L38**: una soglia che diventa requisito va letta contro i numeri che ha
  già il repo, prima di scriverla. Se non separa i casi che deve separare, lo
  si dice all'utente, non lo si aggiusta in silenzio.

Voci: **13 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** **L29** è sul cammino critico e aspetta
la soglia di V2 che l'utente ha dato dopo L20. Finché non è scritta, L29 misura
contro niente.
- L36 e L35 aspettano L29.
- L28 aspetta una sessione interattiva con l'utente sui pin SS.
- L30 aspetta l'alimentatore.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**:
   - la voce di diario **«Dopo L20 — le risposte dell'utente alle domande
     aperte»**: sono **le parole dell'utente**, e L38 le trasforma, non le
     reinterpreta;
   - «Prossimo passo concreto»;
   - la riga **L38** della tabella dei lotti, e quella di **L29**.
3. **`docs/preamp/REQUIREMENTS.md`**: **V2** e la «Nota su F5»; F8, F10 e F11;
   la sezione **«Aperti»** (riga ~476).
4. **`docs/preamp/decisions/`**: **ADR-030** per intero (il criterio 3 e «l'uso
   reale»), **ADR-027** (i LED del trim da K9/K10), **ADR-007** con l'addendum
   (il Singxer), `TEMPLATE.md` e `README.md` della cartella.
5. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-028** per intero (con la stima
   d'udibilità e la formula in dB SPL), **NC-009** (punto 3), **NC-019**.
6. **`circuits/preamp/gain_block.py`**: dove sta oggi il commento sul
   moltiplicatore di Vbe e sull'accoppiamento termico (NC-019).

## IL LOTTO: L38 — le risposte del 2026-09-15 diventano requisiti

### Cosa fare

1. **ADR nuova per V2**, la prima libera: **ADR-032**, da verificare con `ls`.
   - **Soglia**: gradino all'uscita, filtrato 20 Hz–20 kHz, **≤ 100 µV di
     picco**, su **tutte e tre** le uscite, **accensione compresa**.
   - **Sotto i 20 Hz** il cono può muoversi in maniera non distruttiva: nessun
     limite infrasonico oltre questo.
   - **Il caso peggiore sostituisce «l'uso reale»**. Parole dell'utente: «non
     deve essere udibile come bump in nessuna condizione e su nessuna uscita
     [...] L'uso reale non conta».
   - **Come si misura**: quale filtro, quale finestra (il τ al jack è 0,32 s),
     su quale nodo (il jack, non `v(OUT)`), con quali carichi. Senza il metodo
     la soglia non è verificabile, e L29 la leggerà.
   - **I ~34 dB SPL** di picco a 1 m sono una stima calcolata e un limite
     superiore: così vanno scritti.
2. **`REQUIREMENTS.md`**:
   - V2 con la soglia e il rimando alla ADR;
   - la riga «Aperti» del Singxer allineata a ADR-007 addendum;
   - l'intestazione «Ultimo aggiornamento».
3. **Il criterio 3 di ADR-030 al caso peggiore**: con una ADR nuova o con la
   stessa ADR-032. **ADR-030 non si riscrive.**
4. **NC-028 aggiornata** con la soglia. La riga **L29** della tabella dei lotti
   aggiornata: il cambio a caldo calcolato (6–114 mV) non rispetta la soglia,
   e L29 lo deve confermare misurando, non assumere.
5. **NC-009, punto 3**: la conseguenza operativa del trim va nel **manuale
   d'uso**, non su una legenda di pannello. Decidi, dai file, se questo chiude
   la voce o la sposta: il manuale d'uso non esiste ancora.
6. **NC-019**: **ponte di rame** sul PCB fra la piazzola del SOT-23 e quella del
   tab del TO-220; T7 resta intatta.
   - Scritto in `gain_block.py` come commento che punta alla ADR (regola di
     tracciabilità di `CLAUDE.md`);
   - scritto nella consegna a `pcb-automation-engineer`: trova dove sta, o
     dillo se non esiste ancora.
7. **LED gemelli K9/K10 accettati**: nota in una ADR nuova (ADR-027 non si
   riscrive), col guasto di un solo relè come caso noto e accettato, anche per
   i LED di ADR-030.
8. **Il condensatore d'uscita del phono** resta **rimandato**: non scriverlo come
   deciso.

### I vincoli

- **Nessun valore del circuito cambia.** `gain_block.py` riceve solo un
  commento. Se rigeneri, il 2i cade finché il derivato non si rigenera
  (`scripts/derive_jfet_variant.py`).
- **Nessun numero simulato nuovo.** Le cifre che citi esistono già in un file
  del repo, e le citi da lì.
- **Le parole dell'utente si citano**, non si parafrasano in qualcosa di più
  forte o più debole.

## Cosa NON accettare

- **Una soglia di V2 senza metodo di misura.**
- **Una ADR esistente riscritta.**
- **Una voce chiusa perché «è stato deciso»**, quando il rimedio non esiste ancora.
  NC-028 resta aperta: la chiude la misura di L29.
- **Una stima calcolata presentata come misurata.**

## NON fa parte di questo lotto

- **L29**: la misura del gradino e il confronto fra le varianti di mute.
- **L28** (NC-027), **L30** (NC-029), **L35**, **L36**.
- **Pubblicare nel dossier i dati di L20.**
- **La sostituzione dei modelli nel circuito** (Fase 4, NC-017).
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L33, L13, L20 e
  L37 hanno trovato sbagliate cose che il lotto precedente aveva scritto.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con
    `git show HEAD:<file> > <copia>` o `git archive -o <file>` e `tar -xf`
    separato;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`), un comando con
    valori calcolati in posizione di opzione (`sed -n "$(grep …),+45p"`) o con
    **variabili di shell** vengono rifiutati nel worktree: usa percorsi
    letterali, `grep -A <n>` o uno script su file;
  - in zsh un argomento `--include=*.md` non quotato viene espanso come glob e
    il comando fallisce («no matches found»): quotalo;
  - `echo "===="` in zsh fallisce (`= not found`): usa `echo "---"`;
  - un `| tail` dopo un comando restituisce l'exit code di `tail`: per l'rc vero
    scrivi l'uscita su file e leggi `$?` subito dopo;
  - se il classificatore dei permessi va in timeout, il comando non è partito:
    rilancialo.
- **`testbenches/01_op.cir` ha un `wrdata` con percorso assoluto**: il 2b
  lanciato da un worktree scrive in `/Users/roberto/EDA/results/` (L31).
- **Se `/usr/bin/python3` o `git` escono 69** con «You have not agreed to the
  Xcode license agreements», serve `sudo xcodebuild -license` dall'utente in un
  terminale: è successo a metà di L32.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L38, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L38`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
