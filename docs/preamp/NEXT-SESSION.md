# Prompt per la sessione successiva — L47b2b (il mute con la NSL-32SR3: il profilo a 3 s con la cima di 7 mA, il pilota, il firmware, le misure sul preamp intero)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47b2b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L47 è stato diviso tre volte dall'utente: **L47a** la parte e il modello (ADR-058),
**L47b1** la prova del JFET e la decisione (ADR-059), **L47b2a** la cella nel sorgente e la cima
del LED (ADR-060), **L47b2b** il resto: questo.

**Cosa ha fatto L47b2a** (2026-10-03, `reports/2026-10-03-L47b2a-cella-nel-sorgente.md`, ADR-060):
- la NSL-32SR3 nel sorgente (`Isolator:NSL-32`, `OptoDevice:Luna_NSL-32`), i LED collegati **per
  nome**: il simbolo ha anodo e catodo opposti alla VTL5C, e la sola parte cambiata capovolgeva i
  LED senza un errore (limitations #41). I controlli 2e e 2j lo prendono;
- **nessun deck canonico resta sulla VTL5C4**. Ma i banchi V2 (`tb_v2_casopeggiore.cir`,
  `tb_v2_mute_ldr.cir`) hanno ancora **il profilo v4 a 6 s e la cima di 20 mA della VTL5C4**, e lo
  dicono nell'intestazione: le loro cifre di S e B non sono ancora verdetti;
- **la cima del LED è 7 mA**, ipotesi dichiarata (l'utente: «Solo ipotesi a 7 mA»; nessuna email
  al costruttore). La cella accesa vale 99,9 Ω sulla curva B, 115,5 Ω su C ed E;
- preliminari: E3 110,7 kΩ, E5 5,53 µV; il rumore ammesso sul comando dei LED scende a
  **613 nV/√Hz** (la derivazione spenta ora vale 25 MΩ);
- **l'impronta**: i terminali del LED sono a 3,81 mm nell'impronta KiCad contro 3,30 ± 0,13 del
  disegno. Non deciso: è per l'utente, prima di L49.

Le non conformità del lotto:
- **NC-043 (bloccante per G2)**: si chiude col profilo, il pilota e le misure sulla NSL-32SR3;
- **NC-045 (minore)**: il tempo è deciso (3 s); restano il profilo ricalibrato e, se si può, il
  pilota semplificato;
- **NC-049 (maggiore)**: S con la cima **a 7 mA**, sul preamp intero col pilota vero;
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`. Chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle («non ricordo sigle a memoria»); i livelli in
**dB SPL** contro una stanza silenziosa, non in mV.

- **Se dividere il lotto.** Resta grande: profilo, pilota, firmware, misure, catene a valle.
  Proporre, non decidere (per esempio: profilo e misure sul banco V2 con un pilota ideale in uno;
  pilota in `psu.py`, firmware e catene a valle nell'altro).
- **Se semplificare il pilota** (NC-045: un RC più un generatore di corrente al posto di DAC,
  convertitori esponenziali e calibrazione). Se sì, vuole un'ADR. Portare i numeri prima.
- **L'impronta del LED** (3,81 contro 3,30 mm), se c'è tempo: un'impronta propria nel repo o i
  terminali divaricati. Si può anche lasciare a L49, ma va chiesto.

### 2. Il profilo a 3 s

Ricalibrato sull'inviluppo A–E della NSL-32SR3 **con la cima di 7 mA**, non solo compresso. Il
banco di L47b1 (`data/2026-10-02/L47b1/banco/sfumatura.py`, opzioni `--cima12`) è il punto di
partenza: va portato a 7 mA (oggi ha `--cima12`). A 7 mA la serie accesa è più resistiva e la
derivazione ~2,3 dB meno profonda a pari serie: S e B cambiano.

Il profilo nuovo entra **insieme** in: il generatore V2 (`ION`, `SERIE`, `TD` in
`data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py` e `data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py`;
togliere le righe «L47b2a: PROFILO E CIMA SONO ANCORA QUELLI DELLA VTL5C4»), il commento del
contratto in `preamp_audio.py` (blocco J3, il paragrafo «STILL THE VTL5C4'S PROFILE»), il pilota e
il firmware.

### 3. Il pilota e il firmware

- **Il pilota** in `circuits/preamp/psu.py` (ADR-049, ADR-050): la cima di 7 mA; la caduta di
  **due LED NSL in serie** per stringa (1,89 V l'uno a 7 mA nel modello; il commento alla riga
  ~182 cita la VTL5C4); il rumore sul comando sotto 613 nV/√Hz; il profilo nuovo.
- **Il firmware** `firmware/preamp_timer/`: `LDR_I_TOP` in `timer_core.h` (oggi 12e-3, commento
  sulla VTL5C4), la tabella in `timer_core.c`, **il punto alto della calibrazione** (ADR-050 punto
  2: 12 mA e 2 mA), `spec/timer_spec.md` (riga ~223), i test sull'host (blocco 2k: 65 + 45
  controlli, 21 falsi) e i falsi nuovi per il tempo di 3 s.
- Il cablaggio J3 (`LDR_CMD`) non cambia se il pilota resta a correnti di LED: il 2j lo dice, ora
  anche per anodo e catodo.

### 4. Le misure, sul preamp intero

Col banco V2 (`tb_v2_casopeggiore.cir`, rigenerato col profilo nuovo), metodo di
`REQUIREMENTS.md`, V2; script in `data/2026-09-25/L29d2/` e `data/2026-09-26/L41c/`. La prova di
corsa di L47b2a (`data/2026-10-03/L47b2a/v2_prova/`, README) dice come si risolve, si divide e si
lancia, e che le corse scrivono i `.dat` nella cartella di lancio.

| Grandezza | Requisito | Note |
|---|---|---|
| **S** | ≤ 20 dB in 100 ms | 12,7–16,9 dB sul banco ridotto a 12 mA (L47b1); a 7 mA da rifare; chiude NC-049. Curva D compresa (`--curve`) |
| **B** | ≤ 100 µV, ~33 dB SPL | **a 20 kHz prima che chiuda il relè: 42–49 dB SPL sul banco ridotto**, dai 5 pF di cella ipotizzati. Quanto dura prima della chiusura del relè al jack (ADR-038), e se il verdetto di B lo prende |
| **E3** | ≥ 100 kΩ | 110,7 kΩ preliminare (L47b2a); lungo la sequenza, dal post di V2 |
| **E5** | 9,90 µV | 5,53 µV preliminare; il modello non ha rumore: la cella si conta come resistore |

Le cifre portano l'etichetta «modello comportamentale da dati pubblicati, una sola cella misurata
nella regione del mute». La distorsione della NSL-32SR3 **non è modellata**: dirlo accanto a ogni
cifra di distorsione.

### 5. Comunque

- **`psu.py`**: la tenuta di `VRELAY` a rete −10 %, ricorsa col carico nuovo (NC-050); il commento
  di `C_VRELAY` riscritto con le cifre di oggi (NC-051).
- **Le catene a valle**: i 21 deck veloci (`data/2026-10-03/L47b2a/script/regressione.sh` e
  `confronta_regressione.py`, riferimento in `data/2026-10-03/L47b2a/regressione/dopo/`); **la
  catena dei guasti di L41c** (i comandi in `data/2026-10-01/L46b/README.md`), che L47b2a non ha
  ricorso: il suo deck include le celle, ma le correnti dei LED vengono dal pilota; il firmware
  sull'host (blocco 2k).
- **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta all'ADR o
  al lotto; `validate_models.py --check-provenance` pulito.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #24 nodi del blocco, #29 `altermod` e i modelli rinominati;
  - #33/#38 il «transient op», e #40: con `abstol=1e-15` l'op di un modello a stato dipende dal
    percorso di Newton; «failed» nel log non vuol dire fallito. Leggere stdout e stderr;
  - #34 un `alter` che sopravvive a `destroy all`, #35 la `tran` abortita che scrive zeri, #36 la
    PWL lunga ignorata, #37 le Note dentro le tabelle;
  - **#41** (da L47b2a): due simboli che numerano anodo e catodo al contrario; collegare per nome;
  - **#42** (da L47b1 e L47b2a): la NSL-32SR3 ferma in una `tran` può far collassare il passo con
    rc 0, ma dipende dal banco; validare dal log e dall'ultima riga dei dati.
- `docs/preamp/STATE.md`: «In breve» e le voci di diario di **L47b2a**, L47b1, «Dopo L47a», L47a,
  L41b1, L41b2, L29b2.
- `reports/2026-10-03-L47b2a-cella-nel-sorgente.md` e `data/2026-10-03/L47b2a/README.md`;
  `reports/2026-10-02-L47b1-prova-mute.md` e `data/2026-10-02/L47b1/README.md`.
- `NONCOMPLIANCE.md`: **NC-043**, **NC-045**, **NC-049**, **NC-050**, **NC-051**, con gli
  avanzamenti di L47a, L47b1 e L47b2a.
- `decisions/ADR-038*`, `ADR-039*`, `ADR-040*`, `ADR-049*`, `ADR-050*`, `ADR-053*` (il PRB),
  `ADR-058*`, `ADR-059*`, **`ADR-060*`**; `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni). **Anche `cd … && script`**: gli script
    si lanciano col percorso assoluto;
  - **le variabili di shell nei percorsi** (`W=…; sed … $W/…`): si scrivono i percorsi per intero;
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
  `git show REV:file --output=…` stampa invece di scrivere: per copiare un file di `main` si usa
  l'output salvato o un piccolo script.
- I file di `models/` con un blocco del costruttore si modificano **sui byte**, mai con Edit
  (#39). Il `.lib` della NSL-32SR3 è generato: si corregge `genera_modello.py` e si rigenera.
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la
  corsa (#33, #38, #40).
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): le forme d'onda grosse
  vanno in `.gitignore` prima del commit (L47b2a ne ha escluse ~2,5 GB, L47b1 ~1,3 GB).

## NON fa parte di questo lotto

- il JFET e ogni altra alternativa alla fotoresistenza (ADR-059);
- la cima del LED: decisa in ADR-060. Si riapre solo per le ragioni scritte lì;
- un tetto del tempo di mute nel PRB: l'utente ha scelto un bersaglio. Se dopo le misure lo vuole,
  vuole un'ADR (ADR-053);
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- il blocco di guadagno (ADR-054, ADR-056) e il flicker (ADR-057): decisi;
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` dice ancora «solo l'LSK489A porta KF» e «niente distorsione»,
    superato da L44 e L46a;
  - il mute descritto è quello della VTL5C4, la prova del JFET non c'è, e la cella è cambiata;
  - le righe `Stato:` di ADR-038, ADR-039 (superate sulla parte da ADR-058) e ADR-050 (superata
    sulla cima da ADR-060) non lo dicono: il controllo del punto 14 lo segnalerà; si allineano
    con l'utente, toccando solo quella riga, come in L42d.

## CHIUSURA

1. `STATE.md` con L47b2b **fatto** (o il primo sotto-lotto, se l'utente lo divide) e il prossimo
   lotto nella tabella (L48, o il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47b2b` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
