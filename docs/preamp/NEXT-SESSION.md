# Prompt per la sessione successiva — L47b (il mute: la prova del JFET contro la fotoresistenza, la scelta, poi il resto)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. All'inizio di L47 l'utente l'ha diviso in due: **L47a la parte e il modello** (fatto il
2026-10-02, ADR-058), **L47b** il resto.

**Cosa è cambiato dopo la chiusura di L47a** (conversazione del 2026-10-02 con l'utente). L47a ha
scelto la **NSL-32SR3**, l'unica fotoresistenza sostituta della VTL5C4 acquistabile. Il suo modello
(`models/optocoupler/nsl32sr3_comportamentale.lib`) però si regge su **una sola cella misurata**
nella regione del mute, con una dispersione di ~5,5× fra i pezzi, e l'utente non può misurare dei
campioni. In più il pilota è la parte più complicata del mute, e il declassamento del LED non è
pubblicato.

Le alternative messe in tabella con l'utente, ora che il mute sta **a monte**, all'ingresso del
blocco A davanti a 1 MΩ e non più al jack:

| Strada | Esito |
|---|---|
| **JFET** in serie e verso massa (MMBFJ112, modello onsemi già in `models/jfet/mmbfj112.lib`) | **la preferita, da provare**: modello del costruttore, dispersione pubblicata, pilota RC, a massa senza alimentazione, pochi centesimi. Incognita principale: la distorsione durante la sfumatura |
| Fotoresistenza NSL-32SR3 (ADR-058) | **la riserva**, pronta: si misura accanto al JFET sullo stesso banco |
| Attenuatore a gradini a relè | scartato dall'utente: «costa molto» |
| MOSFET contrapposti col pilota fotovoltaico (ADR-037) | scartati: regione di lavoro non modellata, rampe di 7–10 s, banco che non converge; spostarli a monte non cambia nulla |
| Amplificatore controllato in tensione (THAT 2180) o integrato di volume (PGA2311) | scartati: un integrato attivo sempre nel percorso del segnale, contro ADR-022; il primo sfora anche E5. Cifre a memoria, non verificate |

Al jack (ADR-037) il JFET era escluso per i 50 Ω in serie e per un gate oltre −20 V. A monte i
50 Ω valgono una parte su 20 000 contro 1 MΩ, e il picco del segnale è ~3,8 V (2,7 V RMS alla
sorgente): col pinch-off fino a −5 V basta un gate a ~−9 V, e i −15 V dei rail ci arrivano.

L'utente, alla domanda «passeresti al JFET?»: **sì, con una prova prima** e la decisione sua sui
numeri. Questo lotto quindi **comincia con la prova**, e il resto dipende dall'esito.

Viene **prima del placement di prova (L49)** perché cambia una parte e il suo footprint, comunque
vada.

Le non conformità del lotto:
- **NC-043 (bloccante per G2)**: si chiude con le misure sulla cella scelta, qualunque sia;
- **NC-045 (minore)**: il pilota delle LDR e Td = 6 s. Col JFET il pilota diventa una rampa di
  tensione, e la voce si chiude da sola;
- **NC-049 (maggiore)**: S del mute col pilota vero, mai misurato;
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`. Chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle («non ricordo sigle a memoria»); i livelli in
**dB SPL** contro una stanza silenziosa, non in mV.

- **Se dividere il lotto.** Proporre, non decidere: **L47b1** la prova e la decisione (ADR),
  **L47b2** il sorgente, il pilota, il firmware e le catene a valle secondo l'esito. Col JFET L47b2
  è grande: pilota in `psu.py`, firmware, cablaggio J3.
- **Il tempo massimo del mute.** L'utente ha detto «decido dopo la tabella». Né il JFET né la
  NSL-32SR3 (100 kΩ in 10 ms) pongono un limite: la sfumatura la dà la rampa. Il limite che resta è
  S ≤ 20 dB in 100 ms: dal livello pieno a −70 dB servono almeno ~0,35 s. Se vuole un tetto, va
  nel PRB con un'ADR (ADR-053). La domanda si può fare dopo la tabella della prova.

### 2. La prova: JFET contro fotoresistenza, sullo stesso banco

**La parte.** Il `bom-component-manager` verifica la disponibilità di MMBFJ112 (SOT-23) e J112
(TO-92) da un distributore, e dei pari categoria (es. MMBFJ111/J113, altri costruttori), coi
datasheet in `vendor/` se mancano. Il modello onsemi c'è già, validato: `validate_models.py`,
ricetta `tb_mmbfj112`.

**Il circuito.** La stessa geometria di ADR-038: un JFET **in serie** fra il connettore selezionato
e l'ingresso del blocco A, uno **verso massa** sull'ingresso.
- **Il correttivo della distorsione**, su entrambi: metà della tensione drain-source riportata
  sul gate con due resistenze uguali, il comando iniettato attraverso una resistenza grande.
- **In gioco** il JFET in serie ha Vgs = 0 e quello verso massa è spento, col gate a −15 V
  attraverso la rampa.
- **In mute** il contrario.
- **Il comando**: una rampa RC, o il generatore che serve, dal temporizzatore. Lo stato senza
  firmware deve essere quello sicuro (ADR-022 condizione 1).

**Gli angoli.** Il pinch-off va da −1 a −5 V (datasheet): **copie rinominate** del modello onsemi
con VTO agli estremi, come il banco di L44 (`data/2026-10-01/L44/script/banco.py`, limitations
#29). Non `derive_jfet_variant.py`: è ritirato da L39 ed era per l'LSK489. Più IDSS ai suoi
estremi, se il datasheet li dà.

**Le misure**, per il JFET sui suoi angoli e per la NSL-32SR3 sulle curve A–E:

| Grandezza | Requisito | Note |
|---|---|---|
| **S**, il salto di livello in 100 ms | ≤ 20 dB (V2) | `tb_v2_casopeggiore.cir`; metodo in `REQUIREMENTS.md`, V2; script in `data/2026-09-25/L29d2/` e `data/2026-09-26/L41c/` |
| **B**, la musica a mute inserito | ≤ 100 µV, ~33 dB SPL (V2) | per la NSL-32SR3 dipende dalla coda dello spegnimento ipotizzata: dirlo |
| **La distorsione durante la sfumatura** | **nessuno** | finora data per buona. In % e in dB, accanto alla fotoresistenza; il giudizio è dell'utente (nessun agente giudica come suona) |
| **La distorsione a regime**, fuori mute | i tetti di V4 (ADR-055): THD a 20 kHz ≤ 0,001 % a 0,2 V RMS, ≤ 0,01 % a 2 V | per il JFET conta la capacità del JFET spento verso massa, che varia con la tensione |
| **E3**, l'impedenza d'ingresso | E3 | `tb_e3_e5_ldr.cir` |
| **E5**, il rumore | E5; il rumore del comando nella **quota ausiliaria di 1 µV RMS** (ADR-022 punto 4) | il gate tocca il segnale senza isolamento ottico: il filtro del comando sulla scheda audio fa parte della prova |
| Parti, costo, disponibilità | — | per canale e in tutto |

**La tabella all'utente**, per nome e in dB SPL, prima della domanda. La NSL-32SR3 col suo
modello di L47a: le cifre portano l'etichetta «modello comportamentale, una sola cella misurata».

### 3. La decisione dell'utente

- **Se sceglie il JFET**: un'ADR che **supera ADR-058**, e in parte ADR-038, ADR-039, ADR-049 e
  ADR-050 (il pilota delle LDR e la sua cima non servono più). Il modello della NSL-32SR3 resta in
  `models/`, come riserva documentata.
- **Se sceglie la NSL-32SR3**: ADR-058 resta; si decide la cima del LED (il declassamento non è
  pubblicato: ~7,2 mA a 60 °C se vale quello della cella, contro i 12 di ADR-050; ipotesi
  dichiarata o domanda scritta al costruttore, techsupport@advancedphotonix.com) e si rifà il
  profilo v4 sull'inviluppo A–E.

### 4. Il resto, secondo l'esito (in L47b2, se l'utente divide)

**Col JFET:**
- **Il sorgente** `circuits/preamp/preamp_audio.py`: i due JFET per canale al posto di `ls` e
  `lp`, con il correttivo e il filtro del comando, footprint SOT-23 (o TO-92).
  - Il controllo del mute in `scripts/check_relay_safe_state.py` (blocco 2e: «le LDR del mute
    graduale stanno dove ADR-038 le vuole») va esteso ai JFET e **fatto fallire prima di
    fidarsene**.
- **Il pilota** in `circuits/preamp/psu.py`: il pilota delle LDR di ADR-049/050 (DAC, convertitori,
  calibrazione) sostituito dalla rampa del gate.
  - Il cablaggio **J3** (`LDR_CMD`) porta una tensione invece di due correnti di LED: il controllo
    2j del cablaggio fra le schede si aggiorna e si fa fallire.
- **Il firmware** `firmware/preamp_timer/`: la legge delle LDR in `timer_core.c` e la sua tabella,
  la specifica `spec/timer_spec.md`, i test sull'host (blocco 2k, 65 + 45 controlli, 21 falsi) e i
  falsi nuovi.

**Con la NSL-32SR3:**
- **Il sorgente**: `ls` e `lp` con `Isolator:NSL-32` e `OptoDevice:Luna_NSL-32`. Il passo delle
  piazzole (3,81 / 2,53 mm) va confrontato col disegno Silonex (~3,3 / 2,54).
- **Il pilota** e la sua cima, e due LED in serie fino a 5,0 V (`psu.py` riga 182).

**Comunque vada:**
- **Le misure finali** sul circuito scelto: S, B, E3, E5, e la calibrazione se c'è.
- **`psu.py`**:
  - la tenuta di `VRELAY` a rete −10 %, ricorsa col carico nuovo (NC-050). Col JFET il carico
    scende: niente 12 mA di LED;
  - il commento di `C_VRELAY` riscritto con le cifre di oggi (NC-051).
- **Le catene a valle** (la lezione di L46b, report §8):
  - i 21 deck veloci (`data/2026-10-01/L44/script/regressione.sh` e `confronta_regressione.py`,
    riferimento in `data/2026-10-01/L44/regressione/dopo/`);
  - la catena dei guasti di L41c (i comandi in `data/2026-10-01/L46b/README.md`);
  - il firmware sull'host (blocco 2k).
- **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta all'ADR o
  al lotto; `validate_models.py --check-provenance` pulito; nessun deck canonico più sulla VTL5C4.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #24 nodi del blocco, #29 `altermod` e i modelli rinominati;
  - #33/#38 il «transient op», e **#40**: con `abstol=1e-15` l'op di un modello a stato dipende dal
    percorso di Newton, e «Dynamic gmin stepping failed» precede un op valido. Leggere stdout e
    stderr;
  - #34 un `alter` che sopravvive a `destroy all`, #36 la PWL lunga ignorata, #37 le Note dentro
    le tabelle, #39 un editor che normalizza i CRLF dei file del costruttore (vale per
    `mmbfj112.lib`).
- `docs/preamp/STATE.md`: «In breve» e le voci di diario di **«Dopo L47a»**, L47a, L44, L46b,
  L41b1, L41b2, L29b2.
- `docs/preamp/reports/2026-10-02-L47a-cella-mute.md` e
  `data/2026-10-02/L47a/nsl32sr3_modello/README.md`.
- `NONCOMPLIANCE.md`: **NC-043** (con l'avanzamento di L47a), **NC-045**, **NC-049**, **NC-050**,
  **NC-051**, e la chiusa NC-038 (il LED nel telaio caldo).
- `decisions/ADR-022*` (percorso del segnale e quota ausiliaria), `ADR-037*` (il JFET al jack e
  perché fu scartato lì), `ADR-038*`, `ADR-039*`, `ADR-040*`, `ADR-049*`, `ADR-050*`, `ADR-053*`
  (il PRB), **`ADR-058*`**; `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte**, mai con Edit
  (#39). Il `.lib` della NSL-32SR3 è generato: si corregge `genera_modello.py` e si rigenera.
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la
  corsa (#33, #38, #40).
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): le forme d'onda grosse
  vanno in `.gitignore` prima del commit (L46b ne ha escluse ~6,3 GB).

## NON fa parte di questo lotto

- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- il blocco di guadagno (ADR-054, ADR-056) e il flicker (ADR-057): decisi;
- l'attenuatore a relè, i MOSFET contrapposti, VCA e integrati di volume: scartati con l'utente
  (tabella sopra);
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` dice ancora «solo l'LSK489A porta KF» e «niente distorsione»,
    superato da L44 e L46a;
  - il mute descritto è quello della VTL5C4.

## CHIUSURA

1. `STATE.md` con L47b **fatto** (o L47b1, se l'utente lo divide) e il prossimo lotto nella
   tabella (L47b2, oppure L48).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47b` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
