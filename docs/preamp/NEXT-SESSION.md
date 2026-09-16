# Prompt per la sessione successiva — L29b

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L29b** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L29 è stato diviso, e la prima metà (L29a) ha misurato le varianti di mute col
metodo di V2.** Report: `reports/2026-09-16-L29a-metodo-v2-e-varianti.md`.

**Il metodo di V2 è cambiato due volte, con l'utente.**
- **ADR-035 — C.** C sottraeva la sola fondamentale e contava la distorsione del
  circuito (h2 = 887 µV senza nessun evento). Ora C è la **differenza dei residui
  del fit** fra la corsa con l'evento e il riferimento, con soglia **1 mV**. A e B
  restano a **100 µV**. Il pavimento di C2 sulla principale a 1 kHz vale
  0,57–0,80 mV; **a 20 kHz sulla principale 1,08 mV: quella cella non è
  decidibile.**
- **ADR-036 — A.** Con musica la differenza dal riferimento contiene la musica
  stessa (12,7 V per ogni variante e ogni rampa). **A si giudica solo senza
  segnale; con musica decide C.**
- `scripts/v2_metodo.py` applica tutto: `analizza`, `riassumi`, 23 controlli, 12
  sabotaggi (`autotest`, `sabotaggi`).

**Il risultato, e la scelta dell'utente (ADR-036).**
- Nessuna variante rispetta A, B e C. Nessun contatto netto rispetta C.
- **«Per ora» il mute di progetto è graduale e in serie, con rampa da 3 s**,
  accettato con C fuori soglia sulla principale: 2,93–3,05 mV; fisse 0,83–0,87 mV,
  gradino senza segnale a pV, residuo a µV.
- **Le attese uditive sono scritte in ADR-036**, e vanno lette.
- **È un elemento IDEALE in un deck** (`tb_v2_mute_graduale.cir`, posizione `g4`):
  una conduttanza log-lineare da 1e-12 a 10 S. Nessun circuito reale esiste.

**NC-028 resta aperta e bloccante**, aggiornata. Voci: **13 aperte, 3 bloccanti**
(NC-004, NC-017, NC-028).

**Una trappola pagata in L29a, già dentro i deck**: `vntol=1e-9` collassa il passo
nelle celle senza segnale a mute inserito (~41 ore per una cella). I tre deck
`tb_v2_mute_*.cir` usano `vntol=1e-6 abstol=1e-12`, verificato che non cambia le
cifre (`data/2026-09-16/L29a/tolleranze/`). **Un deck nuovo del mute deve fare lo
stesso**, e dichiararlo.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: la riga **L29b** della tabella dei lotti e la voce di
   diario **L29a**.
3. **`docs/preamp/REQUIREMENTS.md`**: **V2 per intero**; la «Nota su F5»; F6; P7 e la
   «Nota su P7».
4. **`docs/preamp/decisions/`**:
   - **ADR-036** per intero, attese uditive comprese;
   - **ADR-035**, **ADR-032**;
   - **ADR-030**, il criterio 3, nel caso peggiore;
   - **ADR-012** e **ADR-021**: il mute in serie cambia lo stato sicuro;
   - **ADR-027** §5, la sequenza d'accensione.
5. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-028 per intero**.
6. **Il lavoro di L29a**:
   - `scripts/v2_metodo.py` (la docstring elenca i sottocomandi);
   - `spice/preamp/tb/tb_v2_mute_graduale.cir` e gli altri due `tb_v2_mute_*`;
   - `data/2026-09-16/L29a/corse/serie_3s.csv`.

## IL LOTTO: L29b — il mute graduale in serie reale, e il resto di L29

### Cosa fare

1. **L'elemento graduale reale, in serie.** La tecnica è libera (ADR-021): JFET,
   fotoaccoppiatore o altro. Deve tenere, al jack, le cifre dell'elemento ideale
   o dire di quanto se ne allontana. Una scelta di tecnica è un'ADR nuova che
   **precisa ADR-012 e ADR-021**, che non si riscrivono.
2. **Misurarlo col metodo di V2**, con un deck versionato:
   - tre uscite, carichi 10 e 100 kΩ, contatti e fronti dichiarati;
   - **1 kHz, 20 Hz con la rampa da 3 s, e 20 kHz** — le due ultime mancano;
   - A senza segnale, B, C2; il pavimento accanto a ogni C2.
3. **Il caso peggiore di V2 che L29a non ha coperto**:
   - passaggi di guadagno 0↔+3, +3↔+10, 0↔+10 dB, e il **criterio 3 di ADR-030**
     (cambio a caldo contro cambio sotto mute seguito dal rilascio) — da cui dipende
     **L36**;
   - trim nelle tre posizioni; dispersione LSK489 fino a ±20 mV;
   - **accensione e spegnimento**, con le rampe dei rail.
4. **P7** per la posizione in serie.
5. **Lo stato sicuro**: ADR-012 vuole il jack a massa a macchina spenta. Col mute
   in serie va riletto, con `check_relay_safe_state.py`.
6. **L'esito.** NC-028 **si chiude solo quando il rimedio è nel sorgente e misurato.**
   Se L29b si ferma prima, la voce resta aperta e lo si scrive.

### I vincoli

- **Il metodo di V2 non si cambia in silenzio.** Una modifica è una domanda
  all'utente e un'ADR. Se il metodo non separa i casi che L29b incontra, lo si dice
  all'utente.
- **L29b è M/L.** Se non entra in una sessione, dividilo in L29b e L29c nella
  tabella di `STATE.md`, e chiudine uno.
- **Se rigeneri il blocco**, il 2i cade finché il derivato non si rigenera
  (`scripts/derive_jfet_variant.py`).
- **Le corse sono lunghe**: il graduale ha richiesto circa tre ore. Lanciale in
  background, con `save`, e **aspetta l'utente quando lo chiede**.

## Cosa NON accettare

- **Una cifra su `v(OUT)`**, o senza il metodo di V2.
- **A con musica usata come verdetto** (ADR-036).
- **Un C2 sotto il proprio pavimento presentato come misura**, o un verdetto di C a
  20 kHz sulla principale, dove il pavimento sta sopra la soglia.
- **Un elemento ideale** presentato come circuito reale.
- **Una variante «conforme»** su una sola uscita, frequenza o carico.
- **Una stima calcolata presentata come misurata.**
- **NC-028 chiusa** con un rimedio che esiste solo in un deck.

## NON fa parte di questo lotto

- **L36**: l'interblocco del guadagno. **L35**: comandi e LED a pannello.
- **L28** (NC-027), **L30** (NC-029).
- **Il dossier.**
- **La sostituzione dei modelli nel circuito** (Fase 4, NC-017).
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Fai quello che l'utente chiede, non di più.** Se dice di aspettare, si aspetta:
  niente commit, niente modifiche, niente chiusure non richieste.
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato; anche `python` con un heredoc e
    `awk` con un programma inline: scrivi lo script su file e lancialo;
  - comandi con **variabili di shell** vengono rifiutati nel worktree: usa percorsi
    letterali, `grep -A <n>` o uno script su file;
  - in zsh `--include=*.md` va quotato; `echo "===="` fallisce (usa `---`);
  - un `| tail` restituisce l'exit code di `tail`;
  - se il classificatore dei permessi va in timeout, il comando non è partito:
    rilancialo.
- **Scipy non c'è nel venv**: i filtri sono stdlib, con `/usr/bin/python3`.
- **Trappole di ngspice già pagate**: `pwl()` dentro una sorgente B accetta solo
  punti letterali; senza `save` una corsa da 7 s supera i GB; a 20 kHz serve TMAX
  ≈ 0,5 µs; `vntol=1e-9` blocca le celle senza segnale.
- **Se `/usr/bin/python3` o `git` escono 69** con «You have not agreed to the
  Xcode license agreements», serve `sudo xcodebuild -license` dall'utente.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina ancora
   L29b, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L29b`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
