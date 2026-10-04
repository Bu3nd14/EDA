# Prompt per la sessione successiva — L47b2b2 (il pilota vero col profilo v5, il firmware, VRELAY, S col pilota vero e le catene a valle)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47b2b2**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L47 è stato diviso più volte dall'utente: L47a la parte e il modello (ADR-058), L47b1 la
prova del JFET (ADR-059), L47b2a la cella nel sorgente e la cima del LED (ADR-060), **L47b2b**
diviso all'inizio in **L47b2b1** (fatto: il profilo, le misure con un pilota ideale, la scelta del
pilota, l'impronta; ADR-061) e **L47b2b2**: questo.

**Cosa ha fatto L47b2b1** (2026-10-03, `reports/2026-10-03-L47b2b1-profilo-v5.md`, ADR-061, dati
`data/2026-10-03/L47b2b1/`):
- **il profilo v5**, simmetrico, 3 s per verso, cima 7 mA, riposo 10 nA:
  - serie 7 mA (d = 0) → 10 nA (d = 0,6), log-lineare;
  - derivazione 10 nA (d = 0,155) → 7 mA (d = 1), log-lineare;
  - S 10,9 dB sul banco ridotto (v4 compresso 16,4); **sul preamp intero col pilota ideale S ≤
    13,52 dB** su A–E (`data/2026-10-03/L47b2b1/v2/*/verdetto.csv`);
- **perché**: la NSL-32SR3 sopra 100 kΩ si spegne a ~0,24 decadi/s, e il v4 compresso violava E3
  a 20 kHz al rilascio (88,7 kΩ). Scelta dell'utente: **«3 s e 3 s, impedenza ai bassi»**:
  durante la sfumatura E3 si giudica a 20 Hz (≥ 154,9 kΩ), a 20 kHz si dichiara (88,1 kΩ per
  ~2 s). Nota nuova in `REQUIREMENTS.md` (E3), limitations **#43**;
- **il pilota resta quello di oggi** (ADR-049/050), scelta dell'utente: «Tenere il pilota di
  oggi». La semplificazione di NC-045 è scartata coi numeri (RC + generatore lineare 44,5 dB; un
  NPN senza calibrazione 17,8 dB e mute −68 dB agli angoli);
- **l'impronta propria** `library/preamp.pretty/NSL-32SR3_LED3.30` (LED a 3,30 mm), la prima
  libreria di impronte del repo; `preamp_audio.py` la usa;
- i generatori V2 e i deck `tb_v2_casopeggiore.cir` / `tb_v2_mute_ldr.cir` sono sul v5 (pilota
  ideale), e il contratto di J3 in `preamp_audio.py` lo dice;
- **B con musica a 20 Hz subito dopo il relè non regge** (100,5–241,2 µV): la musica che la
  NSL-32SR3 lascia passare nei 0,5 s fra d = 1 e il relè. Rimedio noto e quantificato (il relè
  ≥ 2,5 s dopo d = 1: B2 ≤ 81 µV); l'utente: **«0,5 s com'è»** → **NC-053** aperta (maggiore,
  proposta, da confermare);
- **il banco V2 è stato corretto** (scelta dell'utente): VOSA davanti a R113 faceva passare 20 nA
  nelle celle (click finto di 211 µV); `iosa()` nel generatore, limitations **#44**;
- le corse a 20 Hz delle curve C ed E corrono con `option trtol=1` (E anche `rshunt=1e12`),
  applicate alle `corsa_*.cir` da `v2/sonda_20hz/aggiungi_*.py` (#42); la guardia nuova
  `data/2026-10-03/L47b2b1/script/guardia_v2.py` va passata su ogni cartella di V2.

Le non conformità del lotto:
- **NC-043 (bloccante per G2)** e **NC-049 (maggiore)**: si chiudono con S sul preamp intero **col
  pilota vero** (le correnti dei LED da `psu.py`), sul v5;
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`. Chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`;
- **NC-053 (maggiore, proposta)**: B a 20 Hz subito dopo il relè; si chiude col relè ≥ 2,5 s dopo
  d = 1 (firmware `T_MUTE_HOLD_US`, contratto di J3, riverifica sul banco V2) o con un'ADR che
  accetti lo scostamento. Decide l'utente.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle; i livelli in **dB SPL** contro una stanza
silenziosa, non in mV. Le domande di partenza:
- **se dividere il lotto** (per esempio: pilota e firmware in uno, `VRELAY`, catena dei guasti e S
  col pilota vero nell'altro). Proporre, non decidere;
- **la severità di NC-053** (il silenzio a 20 Hz subito dopo il relè: ~39–41 dB SPL contro 33),
  proposta maggiore, e se l'utente vuole ora il rimedio (il relè 2,5 s dopo la fine della
  sfumatura invece di 0,5: tocca il firmware e il contratto di J3, che questo lotto tocca comunque).

### 2. Il pilota in `psu.py` (ADR-049, ADR-050, ADR-060, ADR-061)

- **La cima di 7 mA** e la tabella v5. La rete DAC → base di Q2 (`R_A`, `R_C`, `R_PD`, il commento
  alle righe ~168–188) è dimensionata sulla v4 a 20 mA: da 10 nA a 7 mA a 60 °C, il codice a
  piena scala, la risoluzione in dB per LSB.
- **La caduta di due LED NSL in serie** per stringa: 1,89 V l'uno a 7 mA nel modello (il commento
  alla riga ~182 cita la VTL5C4 a 20 mA e 2,0 V), il margine su V5 = 4,90 V.
- `R_LIM` (oggi limita a ~30 mA contro i 40 mA assoluti della VTL5C4): il massimo assoluto del LED
  della NSL-32SR3 è nel datasheet in `vendor/optocoupler/`.
- **Il rumore sul comando** sotto **613 nV/√Hz** (L47b2a).
- Il cablaggio J3 (`LDR_CMD`) non cambia se il pilota resta a correnti di LED: il 2j lo dice.

### 3. Il firmware `firmware/preamp_timer/`

- `LDR_I_TOP` in `timer_core.h` (oggi 12e-3, commento sulla VTL5C4) → 7e-3 (ADR-060).
- Le tabelle in `timer_core.c` (`timer_profile_series`, `timer_profile_shunt`) → il v5
  (ADR-061): serie {0: TOP, 0,6: IDLE, 1: IDLE}, derivazione {0: IDLE, 0,155: IDLE, 1: TOP}.
- `T_FADE_US` 6 s → **3 s** (ADR-059).
- **Il punto alto della calibrazione** (ADR-050 punto 2: 12 mA e 2 mA) e la calibrazione della
  serie in MUSICA (spec § 5, riga ~197: «200 ms a 2 mA, ~850 Ω contro R_IN»: rifare il conto con
  la NSL-32SR3).
- `spec/timer_spec.md` (§ 4, § 5: la tabella, la cima, i tempi), i test sull'host (blocco 2k:
  65 + 45 controlli, 21 falsi) e **i falsi nuovi**: la tabella v4, il tempo di 6 s, la cima a
  12 mA devono far fallire i test.

### 4. Le misure col pilota vero

- **S sul preamp intero col pilota vero**: la catena di L41c (l'alimentatore di `psu.py` col core
  del firmware al punto fisso, il ponte, la scheda audio), i comandi in
  `data/2026-10-01/L46b/README.md`. Il ponte porta le correnti delle stringhe nel banco V2
  (`--matrice l41c`). Chiude NC-049 e, con E3/E5 di L47b2b1, NC-043.
- **La catena dei guasti di L41c**, che L47b2a e L47b2b1 non hanno ricorso.
- Le cifre col pilota ideale sono in `data/2026-10-03/L47b2b1/` (report, sezione «Sul preamp
  intero»): il pilota vero deve ridarle entro la tolleranza della calibrazione.

### 5. Comunque

- **`psu.py`**: la tenuta di `VRELAY` a rete −10 %, ricorsa col carico nuovo (NC-050); il commento
  di `C_VRELAY` riscritto con le cifre di oggi (NC-051).
- **Le catene a valle**: i 21 deck veloci (`data/2026-10-03/L47b2b1/script/regressione.sh` e
  `confronta_regressione.py`, riferimento `data/2026-10-03/L47b2b1/regressione/dopo/`); il
  firmware sull'host (blocco 2k).
- **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta all'ADR o
  al lotto; `validate_models.py --check-provenance` pulito.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #23 i nomi delle reti fuse (SKiDL li sceglie a caso), #24 nodi del blocco,
    #29 `altermod` e i modelli rinominati;
  - #33/#38 il «transient op», e #40: con `abstol=1e-15` l'op di un modello a stato dipende dal
    percorso di Newton; «failed» nel log non vuol dire fallito;
  - #34 un `alter` che sopravvive a `destroy all`, #35 la `tran` abortita che scrive zeri, #36 la
    PWL lunga ignorata (il ponte di L41c la riduce), #37 le Note dentro le tabelle;
  - #41 due simboli che numerano anodo e catodo al contrario; #42 la NSL-32SR3 ferma in una `tran`;
  - **#43** (da L47b2b1): E3 lungo la sequenza si misura al connettore, non sul ramo della cella;
  - **#44** (da L47b2b1): un generatore d'offset davanti a una resistenza che sta dentro un
    sottocircuito fa passare corrente nella rete a monte.
- `docs/preamp/STATE.md`: «In breve» e le voci di diario di **L47b2b1**, L47b2a, L41b1, L41b2,
  L41c.
- `reports/2026-10-03-L47b2b1-profilo-v5.md` e `data/2026-10-03/L47b2b1/README.md`.
- `NONCOMPLIANCE.md`: **NC-043**, **NC-049**, **NC-050**, **NC-051**, **NC-053**; NC-045 è chiusa da
  L47b2b1.
- `decisions/ADR-049*`, `ADR-050*`, `ADR-058*`, `ADR-059*`, `ADR-060*`, **`ADR-061*`**;
  `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni). **Anche `cd … && script`**: gli script
    si lanciano col percorso assoluto;
  - **le variabili di shell nei percorsi**; `awk` con programmi, i cicli con variabili e i
    percorsi calcolati a runtime; gli heredoc; un `python3 -c` dentro un altro comando
    (`time`, per esempio);
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte**, mai con Edit
  (#39).
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto.
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): le forme d'onda grosse
  vanno in `.gitignore` prima del commit.
- Le matrici V2 sono lunghe: 135 corse in ~2,5 h con 8 processi (L47b2b1).

## NON fa parte di questo lotto

- il profilo (ADR-061) e la cima (ADR-060): decisi; si riaprono solo per le ragioni scritte lì;
- l'impronta (ADR-061): fatta; la tabella delle librerie del PCB che la nomini è di L49;
- un tetto del tempo di mute nel PRB (ADR-053);
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` dice ancora «solo l'LSK489A porta KF» e «niente distorsione»,
    superato da L44 e L46a;
  - il mute descritto è quello della VTL5C4 col profilo v4, la prova del JFET non c'è, la cella e
    il profilo sono cambiati (ADR-058…061);
  - le righe `Stato:` di ADR-038, ADR-039 (superate sulla parte da ADR-058), ADR-040 (superata
    sul profilo da ADR-061) e ADR-050 (superata sulla cima da ADR-060) non lo dicono; quelle di
    ADR-059 e ADR-060 nominano ADR più vecchie, che il controllo del punto 14 rifiuta. Si
    allineano con l'utente, toccando solo quella riga, come in L42d.

## CHIUSURA

1. `STATE.md` con L47b2b2 **fatto** (o il primo sotto-lotto, se l'utente lo divide) e il prossimo
   lotto nella tabella (L48, o il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47b2b2` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
