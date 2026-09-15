# Prompt per la sessione successiva — L29

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L29** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**V2 ha una soglia e un metodo di misura (L38, ADR-032), e NC-028 è bloccante.**
- **La soglia**: ≤ 100 µV di picco, filtrato 20 Hz–20 kHz, al jack di ognuna
  delle tre uscite, in ogni condizione, **accensione e spegnimento compresi**.
  - Sotto i 20 Hz nessun limite oltre il filtro.
  - Vale il caso peggiore, non l'uso reale.
- **Vale per tre grandezze**, scelte dall'utente:
  - **A**, il gradino;
  - **B**, il residuo di musica a mute inserito;
  - **C**, il taglio netto della musica sul contatto.
- **Il metodo è in `REQUIREMENTS.md`, V2**, e si segue alla lettera: nodo al
  jack, carichi 10 e 100 kΩ, Butterworth 2° ordine a 20 Hz e a 20 kHz, picco,
  passo ≤ 10 µs, contatti a 100 mΩ e ≤ 3 ms con fronte e rimbalzi, A come
  differenza da una corsa di riferimento, C col tono meno la sua ricostruzione su
  10 ms.
- **NC-028 è salita a bloccante.** Il CSV versionato di L11 porta 5,37 V sul jack,
  circa 54 000 volte la soglia.
- **Le altre decisioni di L38 non toccano L29**: ADR-033 (LED dai relè spia) e
  ADR-034 (moltiplicatore di Vbe accoppiato col rame).

**Tre cose trovate in L38 che valgono qui.**
- **I contatti dei banchi sono ideali.** `tb_mute_corto.cir:132` ha `RON=0.01`;
  il datasheet G6K (`vendor/relays/omron/G6K/en-g6k.pdf`) dà 100 mΩ massimi. Il
  residuo di 4 mV p-p di NC-028 è stato simulato con un contatto dieci volte
  migliore del peggiore.
- **I nomi dei nodi del jack cambiano da deck a deck.**
  - `tb_mute_corto.cir` usa `JM`, `J1` e `J2`;
  - `tb_e4_uscite.cir` usa `MAINJACK`, `FIXJACK1` e `FIXJACK2`;
  - `preamp_audio.py` ha `MAINJACK`.

  Il nome si legge nel deck prima di scrivere un marcatore.
- **Il metodo ha una scelta dentro.** C sottrae la musica ricostruita su 10 ms.
  A 20 Hz la finestra copre un quinto di periodo: il fit va controllato, e il
  risultato va dichiarato. **Se il metodo non separa i casi che L29 incontra, lo
  si dice all'utente, non lo si aggiusta in silenzio.**

Voci: **13 aperte, 3 bloccanti** (NC-004, NC-017, NC-028).

**Perché questo lotto viene adesso.** È sul cammino critico: **L36** e **L35**
aspettano il suo confronto, e NC-028 è bloccante.
- L28 aspetta una sessione interattiva con l'utente sui pin SS.
- L30 aspetta l'alimentatore.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: la riga **L29** della tabella dei lotti,
   «Prossimo passo concreto» e la voce di diario **L38**.
3. **`docs/preamp/REQUIREMENTS.md`**: **V2 per intero**, cioè soglia e metodo; la
   «Nota su F5»; F6; P7 e la «Nota su P7».
4. **`docs/preamp/decisions/`**:
   - **ADR-032**;
   - **ADR-030**, il criterio 3, da leggere nel caso peggiore;
   - **ADR-012**;
   - **ADR-021**, che lascia libera la tecnica del mute;
   - **ADR-027** §5, la sequenza d'accensione, 10 ms + 3 ms.
5. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-028 per intero**.
6. **I dati e i deck**:
   - `spice/preamp/tb/tb_mute_corto.cir` e `tb_switch_v2.cir`;
   - `docs/preamp/data/2026-09-14/tb_mute_corto_*`;
   - `reports/2026-09-14-L11-mute-e-corto.md`;
   - `data/2026-09-15/L38/calcolo_v2.py`, un filtro già scritto e controllato
     contro gradini e rampe.

## IL LOTTO: L29 — il gradino, il residuo e il taglio al jack, misurati col metodo di V2

### Cosa fare

1. **Un deck versionato** del mute sulla catena intera, col metodo di V2:
   - il jack delle tre uscite, con carichi 10 e 100 kΩ;
   - contatti a 100 mΩ, con fronte e rimbalzi modellati e dichiarati;
   - passo ≤ 10 µs.
2. **Uno script versionato** che applica il metodo: filtro, A come differenza dal
   riferimento, B, C col fit a frequenza nota su 10 ms, e il picco.
   **Va fatto fallire prima di usarlo**:
   - un gradino sintetico noto deve uscire con la sua ampiezza;
   - una dissolvenza lenta deve passare C;
   - un taglio netto deve cadere su C.
3. **Le varianti di mute da confrontare** (NC-028):
   - il contatto dopo il condensatore, com'è oggi;
   - il contatto prima, con l'offset abbassato;
   - il contatto su entrambi i lati;
   - il rilascio lento e il mute graduale;
   - il mute in serie;
   - la sequenza di rilascio.

   Per ciascuna: A, B e C sulle tre uscite, nel caso peggiore di V2.
4. **ADR-030.** Per la variante migliore, il cambio di guadagno a caldo contro il
   cambio sotto mute seguito dal rilascio, nel caso peggiore:
   - passaggi 0↔+3, +3↔+10 e 0↔+10 dB;
   - dispersione LSK489 ±8 mV tipici e ±20 mV massimi;
   - rimbalzi e break-before-make del rotativo.

   Da questo confronto dipende **L36**.
5. **Accensione e spegnimento**, con le rampe dei rail.
6. **P7 rimisurata** per la posizione del contatto scelta.
7. **L'esito**: la variante che rispetta A, B e C, oppure nessuna. Se nessuna, la
   scelta torna all'utente coi numeri («Da riaprire se» di ADR-032). **NC-028 si
   chiude quando il rimedio è nel sorgente e misurato.** Se L29 si ferma al
   confronto, la voce resta aperta e lo si scrive.

### I vincoli

- **Il mute nel sorgente cambia solo con una ADR nuova**, che precisa ADR-012 e
  ADR-021. ADR-012 e ADR-021 non si riscrivono.
- **Il metodo di V2 non si cambia in silenzio.** Una modifica è una domanda
  all'utente e una ADR.
- **L29 è M/L.** Se non entra in una sessione, dividilo in L29a e L29b nella
  tabella di `STATE.md`, e chiudine uno.
- **Se rigeneri il blocco**, il 2i cade finché il derivato non si rigenera
  (`scripts/derive_jfet_variant.py`).

## Cosa NON accettare

- **Una cifra misurata su `v(OUT)`**, o senza il metodo di V2.
- **Contatti a 0,01 Ω**, o un interruttore ideale senza fronte dichiarato.
- **Un verdetto preso da un deck scratch.**
- **Una variante «conforme»** su una sola uscita, una sola frequenza o un solo
  carico.
- **Una stima calcolata presentata come misurata.**
- **NC-028 chiusa** con un rimedio che esiste solo in un deck.

## NON fa parte di questo lotto

- **L36**: l'interblocco del guadagno. **L35**: comandi e LED a pannello.
- **L28** (NC-027), **L30** (NC-029).
- **Il dossier.**
- **La sostituzione dei modelli nel circuito** (Fase 4, NC-017).
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L33, L13, L20, L37
  e L38 hanno trovato sbagliate cose che il lotto precedente aveva scritto.
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
- **Scipy non c'è nel venv** (L38): i filtri si scrivono in stdlib, come
  `calcolo_v2.py`.
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
   ancora L29, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L29`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
