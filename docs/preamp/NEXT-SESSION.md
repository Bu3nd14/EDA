# Prompt per la sessione successiva — L45c2, i guasti della linea dei relè e del comando

Nome della sessione: **hi-fi preamp L45c2** (la convenzione è in `CLAUDE.md`).

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L45c2**, e si ferma. Non iniziarne un secondo, salvo che l'utente
lo chieda esplicitamente nella sessione.

## Perché questo lotto, e perché adesso

**NC-042** (maggiore, **prima di G1**): l'analisi dei guasti singoli. L45a il blocco di guadagno,
L45b i controlli, **L45c l'alimentatore**, L45d la decisione. L45c è **diviso in due** (scelta
dell'utente all'inizio di L45c, 2026-10-13: «Due parti», circa 250 modi): **L45c1 i rail audio
(fatto)**, **L45c2 la linea dei relè e del comando** (questo).

I criteri sono quelli di L45c1 (`data/2026-10-13/L45c1/script/tabella_l45c1.py`, intestazione):
- un rail dentro |13,5 V| → **PR-23 / P9 (b)**: il sorvegliante entro 1 ms, il jack aperto prima che
  un rail arrivi a 10,6 V (il criterio s di L41c), il picco filtrato al principale ≤ 0,87 V
  (obiettivo 2 mV);
- il corto franco di un rail → **P9 (c)**, caso accettato: i numeri, senza verdetto;
- i rail restano fuori da |13,5 V| → **P10**: ogni jack ≤ 100 ms sopra 0,87 V, grezzo e a vuoto;
- un guasto latente → il criterio del suo evento.

Cosa ha trovato L45c1, da tenere davanti (`reports/2026-10-13-L45c1-fmea-rail.md`):
- **il filo del rail + fra le due schede che si apre** (J1 pin 1): 13,3 V filtrati al jack principale,
  sopra il tetto 286 ms al principale e 910 ms sulle fisse, **e il mute non si inserisce**: il
  sorvegliante legge il rail dal lato dell'alimentatore. Il filo del − dà 4,2 mV;
- **il mute che non si inserisce** (NO di K2–K4 saldato, Q501 in corto D-S): allo spegnimento e alla
  perdita di rete 0,27 V filtrati (0,62 V grezzi); con U501 che poi si spegne 3,4 V (NO saldato) e
  2,8 V (Q501 in corto). Con Q501 in corto il jack si apre solo quando cade `VRELAY`: 682 ms dopo la
  perdita di rete, 193 ms dopo il guasto di un regolatore;
- le **sovratensioni** (U501 o U502 in corto ingresso-uscita, SENSE aperto, un pin ANY-OUT a massa,
  R501 aperta: fino a ±20,3 V) e le **ondulazioni** (C501/C502 aperti, la presa centrale aperta) non
  fanno intervenire niente, e al jack restano sotto 0,4 mV;
- dati per questo lotto: con Q501 in corto il jack si apre al cadere di `VRELAY`, cioè **dipende dalla
  tenuta di C520 e C523 e dall'interruttore Q505**: i guasti di quelle parti cambiano anche i latenti
  di L45c1.

## Il mandato

1. **L'elenco dei guasti singoli**, dal sorgente (`circuits/preamp/psu.py`), parte per parte:
   - la linea dei relè: T2 e J514, il ponte D503, D504, C520, U503, C521, C522, C523, D512, U504,
     C524, C525, la stella NT501, J2 (`RLY_RET`);
   - l'interruttore dello standby: Q505, Q506, R539, R540, C531;
   - i sorveglianti U505, U506, il riferimento U507 coi partitori (R503–R509, R522, R523) e i
     condensatori di filtro; il rivelatore di rete (Q504, R510–R512, C518);
   - il ritardo Δ in hardware: U508, C528, R534, C529, R536, D520, D521, D523, D524, R532, R533, R535,
     R524, R516, R537, R538;
   - i sink Q501, Q502, Q503 coi loro clamp (D506–D509), D505, R513, R514, C527, D522, R520, R521;
   - il relè di rete K501 (bobina aperta o in corto, contatto saldato o aperto) e F501;
   - i pull-down dei comandi del micro (R525–R528) e le letture (R541–R547).
   Per ognuno l'effetto **al jack principale e alle fisse**, coi criteri sopra.
2. **I casi che superano, simulati** sul banco di L45c1, che ha già tutto:
   `data/2026-10-13/L45c1/` (README). Si copia la cartella del lotto, si aggiungono i modi a
   `psu/modi.py` (le primitive `corto`, `aperto`, `vset`, `j1`; se ne serve una nuova la si aggiunge
   in `applica_guasto()` col suo `assert`), e si rifà la catena.
3. **Nessuna decisione**: i rimedi li sceglie l'utente in **L45d**. Se un caso chiede una scelta
   subito, la si chiede all'utente per nome e senza sigle.
4. **La tabella nella forma di ADR-070** (decisa dall'utente il 2026-10-14): per ogni modo, oltre
   all'effetto e al verdetto, la gravità 1–5, il tasso in FIT con la fonte (SN 29500 o IEC 61709 a
   60 °C d'aria, i modi da FMD-2016) e la classe di probabilità 1–4, la rilevabilità 1–3, la
   priorità dalla matrice, i rimedi candidati. Le tabelle di L45a–L45c1 **non** si toccano: le
   riporta L45d.
5. Report `docs/preamp/reports/<data>-L45c2-fmea-comando.md`, dati in `docs/preamp/data/<data>/L45c2/`.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (**58** voci; #33, #34, #35, #57, #58), `AGENTS.md`.
- `docs/preamp/STATE.md`: «In breve» e le voci di **L45c1**, L45b, L45a.
- `NONCOMPLIANCE.md`: NC-042, NC-054, NC-062.
- Il report di L45c1 e il README di `data/2026-10-13/L45c1/`; i report di L45a e L45b.
- ADR-043, ADR-045, ADR-046, ADR-048, ADR-049, ADR-051, ADR-069.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo);
  - `cd … && script`, le variabili di shell nei percorsi;
  - `xargs` sulla riga di comando (va dentro uno script: `psu/corri_lista.sh` di L45c1);
  - `awk` con programmi, i cicli con variabili, un heredoc insieme a un altro comando, un
    `python3 -c` dentro un altro comando, e un comando che contiene la parola «git» anche solo
    in un testo;
  - un titolo di PR con l'apostrofo: il corpo va su file, con `--body-file`.
- Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per i
  testi.
- **Non modificare uno script mentre zsh lo sta eseguendo** (zsh lo legge a pezzi).
- In `catena_l45c1.sh` la guardia di V2 non ferma più la catena: le corse rifiutate si rifanno col
  metodo gear (`rifai_gear.sh`) e quelle che si fermano ancora si leggono fino all'aborto
  (`fino_all_aborto.py`, che verifica che l'aborto cada dopo i rimbalzi del jack).
- Le forme d'onda vanno nel `.gitignore` (le righe di L45c1 sono un modello).
- I subagenti in una sessione isolata possono non poter eseguire comandi (L52): se servono
  simulazioni, falle dalla sessione principale.
- Uno strumento di misura nuovo si controlla su un caso noto prima di usarlo.

## NON fa parte di questo lotto

- La decisione sui rimedi (L45d), l'ingresso protetto (L57), il riesame del micro e dello standby
  (L54: `MUTE_REQ` bloccata alta, Q502 in corto all'accensione, D522), il dispositivo d'uscita
  (L55), il moltiplicatore di Vbe (NC-062), G1. Se un guasto tocca uno di questi, si dice e si
  lascia al suo lotto.

## CHIUSURA

1. `STATE.md` con L45c2 **fatto** nella tabella dei lotti, e il prossimo (L45d).
2. Riscrivi QUESTO file per il lotto successivo, con la riga «Nome della sessione: hi-fi preamp
   <lotto nuovo>» subito sotto il titolo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L45c2`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
