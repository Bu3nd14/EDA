# Prompt per la sessione successiva — L20

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L20** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L13 ha chiuso NC-008**: E4 è misurata sulle tre uscite, nei tre modi, a ogni
posizione di trim e attenuatore. Il deck è `spice/preamp/tb/tb_e4_uscite.cir`,
i dati stanno in `data/2026-09-15/L13/`.
- **Re(Z) al jack ≤ 60,13 Ω** sulla principale e **≤ 53,13 Ω** sulle fisse. Il
  massimo cade a 20 Hz, dove pesa lo scarico.
- La dispersione su trim × attenuatore è **≤ 1e-4 Ω**.

**E ha trovato un difetto di misura vecchio di una settimana.**
- La sezione Zout di `tb_zout_psrr_noise.cir` lasciava `VSRC` a 1 V AC: le cifre
  di E4 pubblicate contenevano il segnale (58,76 / 59,11 / 60,59 Ω a 1 kHz invece
  di 57,94 / 57,95 / 57,99).
- Il deck è corretto; PSRR e rumore sono rimasti identici byte per byte.
- **NC-033** (minore) tiene aperto il dossier, che pubblica ancora le cifre
  vecchie. Lotto **L37**. Limitazione **#28**.

**Due lezioni che valgono anche per L20.**
1. **Un controllo che non riesce a esercitare il suo caso non è fallito, è muto.**
   Il primo sabotaggio «attenuatore scollegato» di L13 è stato rifiutato per la
   ragione sbagliata: segnale zero, `vdb(0)` dà `Error`, cella vuota. Il
   controllo positivo non era mai stato messo alla prova. Si guarda **quale**
   controllo cade, non solo che qualcosa cada.
2. **Un numero che scala con la cosa sbagliata è un segnale.** `za1k` seguiva il
   guadagno del modo: bastava leggerlo.

Voci: **15 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4). NC-008
chiusa, NC-033 aperta.

**Perché questo lotto viene adesso.** Non aspetta nessuno. Gli altri sì:
- L28 aspetta un documento del costruttore o una ADR, prima di G2;
- L29 aspetta una soglia dell'utente su V2;
- L36 e L35 aspettano L29;
- L30 aspetta l'alimentatore, che viene dopo L35 e L36.

Nemmeno L37 (NC-033, il dossier) aspetta nessuno, e viene dopo.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L13 e L33, «Prossimo passo
   concreto» e la riga L20 della tabella dei lotti.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-013** per intero, poi NC-004,
   NC-017 e la chiusura di NC-031. Dicono che cosa è davvero simulato oggi.
4. **`docs/preamp/decisions/ADR-013-jfet-ingresso-lsk489.md`** e il report di L7,
   `reports/2026-09-09-L7-controllo-incrociato-lsk489.md`: le condizioni di
   prova, 25 °C gruppo A, e le tre strade per V_P.
5. **`docs/preamp/REQUIREMENTS.md`**: **E5**, **V1**, **V4**, T7.
6. **Cosa c'è già**:
   - `models/jfet/lsk489.lib` (`LSK489A`, del costruttore, con `Kf`), la sua
     `.provenance.json` e la ricetta `tb_lsk489` in `scripts/validate_models.py`,
     che riesegue i tre numeri di L7 a ogni giro della suite;
   - `spice/preamp/placeholder_devices.lib`: `LSK489X`, il segnaposto che **ogni**
     deck istanzia oggi, con `KF = 0`;
   - `spice/preamp/tb/tb_op.cir`, `tb_noise_breakdown.cir`, `tb_loop.cir`;
   - i dati vigenti, `data/2026-09-14/L27/dopo/` e `L16/dopo/`.
7. **`docs/limitations.md`**: in particolare #17 (due modelli della stessa
   parte), #22 (un nome vivo ma sbagliato), #24 (nodi che collidono con
   `_flat.inc`), #27 (contatti non terminati) e #28 (sorgenti AC dimenticate e
   `vdb(0)`).

## IL LOTTO: L20 — quanto il progetto dipende da I_DSS

### Cosa fare

1. **Baseline: che JFET simula il progetto oggi, misurato e non ricordato.**
   - I_DSS e V_GS(off) di `LSK489X` alle condizioni di L7, accanto a quelli di
     `LSK489A`. È la prima volta che il segnaposto si misura contro la finestra
     del datasheet.
   - Quale dei due sta più vicino al tipico? La risposta dice quanto valgono
     tutte le cifre del progetto fino a oggi.
2. **Il blocco di guadagno con il modello del costruttore**, ai due estremi di
   NC-013:
   - `LSK489A` com'è, con I_DSS 2,59 mA;
   - `LSK489A` con `Vto` portato a una I_DSS di 5,5 mA (tipico), `Beta` invariato.
     Si dichiara il `Vto` usato e si misura la I_DSS che ne esce.
   - Misurare punto di lavoro (correnti di coda, cascode, VAS, uscita; offset in
     uscita) e rumore in uscita 20 Hz–20 kHz (E5), nei casi di
     `tb_noise_breakdown`.
   - Il JFET entra nel guadagno d'anello: dire coi numeri se V1 (60°) va
     rimisurato nel caso peggiore di L27, e se sì misurarlo.
3. **Come istanziare `LSK489A` senza toccare niente di generato.**
   `gain_block.subckt` e `_flat.inc` sono generati da `gain_block.py` (AGENTS.md
   regola 2), e i file di `models/` non si ritoccano. Decidere coi file, e
   scrivere perché.
4. **La tolleranza, scritta.** In `REQUIREMENTS.md` o in una ADR nuova: quale
   dispersione di I_DSS il progetto tollera, e con quale criterio. Se il
   progetto risulta sensibile, la scelta di ADR-013 si riapre con un numero in
   mano: con una ADR nuova, non riscrivendo la 013.
5. **Chiudere NC-013**, o lasciarla aperta con cosa manca.

### I vincoli

- **Nessun valore del circuito cambia.** Se un risultato chiede un rimedio, è una
  non conformità nuova o un lotto suo.
- **I dati si versionano** sotto `docs/preamp/data/<data>/L20/`, con un README
  che dichiara la provenienza.
- **Il 2h legge i commenti dei deck.** Un deck che include `models/jfet/lsk489.lib`
  ha l'LSK489 **del costruttore, con `Kf`**. Le intestazioni copiate dagli altri
  deck dicono il contrario, e il 2h deve cadere se restano: fallo cadere apposta
  una volta.
- **Il dossier non si rigenera** (è L37).
- **Un controllo mai fatto fallire non è un controllo**, e un controllo fatto
  fallire per la ragione sbagliata nemmeno.

## Cosa NON accettare

- **Un `Vto` ritoccato dentro `models/jfet/lsk489.lib`** o in un file di
  `vendor/`.
- **Una I_DSS dichiarata e non misurata** sul modello modificato.
- **Una cifra di rumore senza la frase** «pavimento senza flicker» dove vale. Coi
  segnaposto nessun dispositivo ha 1/f; con `LSK489A` il JFET ce l'ha, e il resto
  no.
- **Un deck che include due modelli con lo stesso nome** (#17), o un modello
  modificato che ombreggia quello del costruttore senza dirlo.
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.

## NON fa parte di questo lotto

- **L28** (NC-027), **L29** (NC-028, aspetta una soglia dell'utente su V2),
  **L30** (NC-029), **L35**, **L36**, **L37** (NC-033, il dossier).
- **La sostituzione dei modelli nel circuito** (Fase 4, NC-017): L20 misura una
  sensibilità, non adotta `LSK489A` nei deck di `main`.
- **Il selettore d'ingresso**, l'alimentatore, `VRELAY`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra: L33 e L13 hanno
  trovato sbagliate cose che il lotto precedente aveva scritto.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con
    `git archive -o <file>` e `tar -xf` separato;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`), un comando con
    valori calcolati in posizione di opzione (`sed -n "$(grep …),+45p"`) o con
    **variabili di shell** vengono rifiutati nel worktree: usa percorsi
    letterali, o uno script su file;
  - in zsh un argomento `--include=*.md` non quotato viene espanso come glob e
    il comando fallisce («no matches found»): quotalo;
  - `echo "===="` in zsh fallisce (`= not found`): usa `echo "---"`;
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
   ancora L20, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L20`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
