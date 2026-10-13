# Prompt per la sessione successiva — L45c, i guasti dell'alimentatore componente per componente

Nome della sessione: **hi-fi preamp L45c** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45c**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli, in **quattro parti** (scelta
dell'utente all'apertura di L45): L45a il blocco di guadagno (**fatto**), L45b i controlli
(**fatto**), **L45c l'alimentatore componente per componente** (questo), L45d la decisione.

Il criterio è **P10** (PR-30, ADR-069): un guasto singolo della scheda audio durante l'ascolto porta
su ogni uscita al più **100 ms sopra 0,87 V**, al jack senza filtro e a vuoto. Per la **rete e
l'alimentatore** vale ancora **PR-23 / P9 (b)**: le uscite si staccano prima che il circuito esca di
regolazione, ≤ 2 mV obiettivo, **≤ 0,87 V di picco** in ogni caso. Un guasto che porta un rail sotto
|13,5 V| ricade in P9 (b).

Cosa hanno trovato le due parti fatte, da tenere davanti:
- **L45a** (`reports/2026-10-13-L45a-fmea-blocco.md`): un guasto del blocco su due porta il jack al
  rail (~14,9 V); il rivelatore di continua non abbassa il picco ma accorcia la durata; la cella RC
  in corto e la resistenza del riferimento in corto portano un regolatore in limitazione (il
  sorvegliante muta). **I corti dei disaccoppiamenti dei rail (C139–C142) sono rimasti a L45c**: coi
  rail ideali del banco sarebbero migliaia di ampere.
- **L45b** (`reports/2026-10-13-L45b-fmea-controlli.md`): nessun guasto ordinario dei controlli si avvicina al tetto (≤ 9,5 mV
  al jack, ≤ 29,7 mV con la dispersione); lo supera solo l'isolamento fra bobina e contatti che cede
  (12 V in continua sul jack dal relè di mute, per sempre). I guasti del blocco di L45a a vuoto:
  **257 su 544 fuori da P10**; il rivelatore ideale li porta a 0,2–10,1 ms.
- **Dati per questo lotto, da L45b**: un NO di K2–K4 saldato o **Q501 in corto D-S** non fanno niente
  al guasto, ma da lì **il mute non si inserisce più**, nemmeno dal sorvegliante. Coi rail ideali in
  rampa lo spegnimento col jack collegato dà **1,6–10,5 V, 14–348 ms sopra 0,87 V**, secondo come
  scendono i due rail (`data/2026-10-13/L45b/analisi_latenti.csv`). **Il numero vero lo dà solo il
  banco dell'alimentatore**: spegnimento morbido, perdita di rete, guasto di un regolatore, col mute
  che non si apre.
- Ogni bobina in corto, e ogni ricircolo in corto, mette in corto la linea dei relè: la classe di
  **ADR-051** (≤ 29,7 mV, accettata). L45c deve dire se tutti i punti di `VRELAY` / `VRELAY_REG`
  ci stanno davvero, componente per componente.

## Il mandato

1. **L'elenco dei guasti singoli dell'alimentatore**, dal sorgente (`circuits/preamp/psu.py`), parte
   per parte: ponte e serbatoi, i due regolatori (TPS7A4701, TPS7A3301) in corto verso l'alto o
   aperti, la tenuta dopo i regolatori, i disaccoppiamenti dei rail sulla scheda audio (C139–C142),
   la linea dei relè (U503, C523, C524, U504, Q505, Q506), i sorveglianti (U505, U506) e il
   rivelatore di rete, il ritardo Δ in hardware (U508, PERMIT_T, VR_T), i sink Q501, Q502 e quello
   di K501, il relè di rete K501. Per ognuno l'effetto **al jack principale e alle fisse**, contro
   **PR-23 / P9 (b)** (picco) o **P10** (durata), secondo che il rail resti sopra |13,5 V| o no.
2. **I casi che superano, simulati** sul banco dell'alimentatore di L41c / L47c2b2 / L56 (il
   circuito vero, il firmware al punto fisso), e **il mute che non si inserisce** (NO saldato, Q501
   in corto) allo spegnimento morbido, alla perdita di rete e al guasto di un regolatore.
3. **Nessuna decisione**: i rimedi li sceglie l'utente in **L45d**, con i numeri di L45a, L45b e
   L45c davanti. Se un caso chiede una scelta subito, la si chiede all'utente per nome e senza sigle.
4. Report `docs/preamp/reports/<data>-L45c-fmea-alimentatore.md`, dati in `docs/preamp/data/<data>/L45c/`.

Il lotto è grande: se all'inizio sembra più di una sessione, proporre all'utente di dividerlo e
lasciar decidere lui.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci; #57 sugli `op`, #58 su `esegui.sh`), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di **L45a** e **L45b**.
- `NONCOMPLIANCE.md`: NC-042, NC-054, NC-062.
- I report di L45a e L45b, e i README di `data/2026-10-13/L45a/` e `data/2026-10-13/L45b/`.
- ADR-043, ADR-046, ADR-048, ADR-049, ADR-051, ADR-056, ADR-069.
- I banchi dell'alimentatore: L41c (`reports/2026-09-26-L41c-banco-l30-circuito-vero.md`), L47c2b2,
  L56 (la parte dell'alimentatore).

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi. Una modifica a uno script fatta con un programma Python va scritta su file e lanciata da
  sola (L45b).
- Le liste lunghe di deck con `xargs -P 8` (`data/2026-10-13/L45b/script/corri.sh`, che scrive in
  `run/` accanto a sé: si copia nel lotto), **non** con `esegui.sh` in background (#58); i processi
  si contano con `ps -eo args`, non con `pgrep -c`. `uno.sh` non ha un tempo massimo: i modi che si
  bloccano vanno tolti dalla lista e corsi a parte, accorciati (L45a, L45b).
- Un `pkill -f` con un percorso uccide anche le analisi che hanno quel percorso fra gli argomenti:
  il modello va ristretto a `ngspice -b <percorso>`.
- Le forme d'onda delle corse vanno nel `.gitignore` (L45a 31 GB, L45b 23 GB).
- I subagenti in una sessione isolata possono non poter eseguire comandi (L52): se servono
  simulazioni, falle dalla sessione principale.
- Un `op` va letto rifiutando «source stepping failed» e controllando un nodo noto (#57).
- Uno strumento di misura nuovo si controlla su un caso noto prima di usarlo (L45b: il seno a 1 kHz
  esatto dava un errore che una prova a 997 Hz mostra).

## NON fa parte di questo lotto

- La decisione sui rimedi (L45d), l'ingresso protetto (L57), il riesame del micro e dello standby
  (L54: `MUTE_REQ` bloccata alta, Q502 in corto all'accensione e D522 sono annotati lì da L45b), il
  dispositivo d'uscita (L55), il moltiplicatore di Vbe (NC-062), G1. Se un guasto tocca uno di
  questi, si dice e si lascia al suo lotto.

## CHIUSURA

1. `STATE.md` con L45c **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45c`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
