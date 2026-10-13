# Prompt per la sessione successiva — L45b, i guasti dei controlli della scheda audio

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45b**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. All'apertura di L45
(2026-10-13) l'utente l'ha allargata all'alimentatore e ai controlli e divisa in **quattro parti**:
L45a il blocco di guadagno (**fatto**), **L45b i controlli** (questo), L45c l'alimentatore componente
per componente, L45d la decisione.

Cosa ha trovato la prima parte (`reports/2026-10-13-L45a-fmea-blocco.md`), da tenere davanti:
- un guasto su due del blocco porta il jack oltre il tetto di non-danno (~14,9 V, 136,9 dB SPL col
  PRB, ~114 col finale), e il sorvegliante non interviene;
- **un rivelatore di continua che apra il mute non abbassa il picco**: il gradino arriva al jack
  insieme al guasto, e col mute a 0,1–10 ms dal guasto il picco resta 14,8–14,9 V; accorcia solo
  l'impulso;
- a mute inserito un guasto non arriva al rilascio (7,3 mV): la geometria iii regge;
- il banco del canale con guasto esiste: `data/2026-10-13/L45a/script/genera_canale.py`;
- dopo L45a l'utente ha aperto **NC-062** (bloccante per G1): quattro guasti del moltiplicatore di
  Vbe non si sentono al jack ma portano i finali a ~182 °C e le 22 Ω fino a 7,5 W. Il rimedio lo
  sceglie l'utente, con L45d o in un lotto proprio: non è di questo lotto;
- sempre dopo L45a l'utente ha scelto la strada del **criterio di durata** per i guasti della scheda
  audio (il tetto di 0,87 V resta per l'alimentatore) e lo sta definendo in conversazione, **per una
  catena generica** («potrei in futuro cambiare il finale»): se c'è già una ADR, L45b misura contro
  quella; se non c'è, misura la durata del colpo accanto al picco.

**L'utente sta leggendo il dossier in parallelo.** Se porta dei rilievi, si registrano come in
L43b e non si mescolano alle misure di questo lotto.

## Il mandato

1. **L'elenco dei guasti singoli dei controlli** della scheda audio, dal sorgente
   (`circuits/preamp/preamp_audio.py`, `gain_interlock.py`, `selector.py`, `trim.py`) e
   dall'alimentatore per i comandi (`psu.py`):
   - **i relè**: il selettore (K13–K16, G6K-2F-Y), il guadagno e il suo ritegno (K1, K5, K11, K12),
     il trim e il permesso (K7–K10 G6KU bistabili, K6), il mute (K2, K3, K4, la geometria iii).
     Per ognuno: bobina aperta o in corto, contatto saldato, contatto aperto, rimbalzo, un polo sì e
     l'altro no;
   - **i piloti delle bobine** e i commutatori del frontale (SW1, SW2, SW4), e il pilota di
     `MUTE_CMD` (Q501) e di `PERMIT_CMD` (Q502) con le loro ritenute;
   - **i LED** che per PR-17 e PR-18 devono dire lo stato vero, non la posizione del comando;
   - **i condensatori d'uscita** (4,7 µF) e **C_T** (10 µF) in corto o aperti, i bleed aperti;
   - **il firmware** (le LDR non ci sono più, ADR-062: dirlo), un'uscita del micro bloccata alta o
     bassa (PR-24).
   Per ognuno l'effetto **al jack principale e alle fisse**, in dB SPL a 1 m contro il tetto di
   non-danno (112,2 dB SPL, PR-23), e contro PR-17, PR-18, PR-22, PR-24 dove toccano.
2. **I casi che superano il tetto, simulati** sul banco di L45a (o sul suo generatore allargato ai
   contatti: i contatti come interruttori, come i deck di V2), coi controlli che devono fallire.
3. **Nessuna decisione**: i rimedi li sceglie l'utente in **L45d**, con i numeri di L45a, L45b e
   L45c davanti. Se un caso chiede una scelta subito (un rimedio che non dipende dagli altri), si
   chiede all'utente per nome e senza sigle.
4. Report `docs/preamp/reports/<data>-L45b-fmea-controlli.md`, dati in `docs/preamp/data/<data>/L45b/`.

Il lotto è grande: se all'inizio sembra più di una sessione, proporre all'utente di dividerlo e
lasciar decidere lui.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci; la #58 è di L45a: `esegui.sh` in background parte
  tutto insieme, si usa `corri.sh` di L45a), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e la voce di **L45a**.
- `NONCOMPLIANCE.md`: NC-042, NC-046, NC-054.
- `reports/2026-10-13-L45a-fmea-blocco.md` e il README di `data/2026-10-13/L45a/`.
- ADR-022, ADR-026, ADR-027 (il «Da riaprire se» sulla bobina di K6), ADR-030, ADR-033, ADR-041,
  ADR-043, ADR-044, ADR-045, ADR-049, ADR-051, ADR-062, ADR-064, ADR-065.
- I guasti già esaminati: L11 (mute e corto), L29c (il caso peggiore di V2), L41c / L47c2b2 / L56
  (i guasti dell'alimentatore al jack, il corto della linea dei relè di ADR-051).

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
  testi.
- Le liste lunghe di deck con `xargs -P 8` (`data/2026-10-13/L45a/script/corri.sh`), **non** con
  `esegui.sh` in background (#58); i processi si contano con `ps -eo args`, non con `pgrep -c`.
- Un `pkill -f` con un percorso uccide anche le analisi che hanno quel percorso fra gli argomenti
  (in L45a ha fermato due analisi): il modello va ristretto a `ngspice -b <percorso>`.
- Le forme d'onda delle corse vanno nel `.gitignore` (L45a ne ha fatte 31 GB).
- I subagenti in una sessione isolata possono non poter eseguire comandi (L52): se servono
  simulazioni, falle dalla sessione principale.
- Un `op` va letto rifiutando «source stepping failed» e controllando un nodo noto (#57).

## NON fa parte di questo lotto

- L'alimentatore componente per componente (L45c), la decisione sui rimedi (L45d), l'ingresso
  protetto (L57), il micro e lo standby (L54), il dispositivo d'uscita (L55), G1. Se un guasto tocca
  uno di questi, si dice e si lascia al suo lotto.

## CHIUSURA

1. `STATE.md` con L45b **fatto** nella tabella dei lotti, e il prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45b`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
