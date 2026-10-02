# Prompt per la sessione successiva — L47b2 (il mute con la NSL-32SR3: il sorgente, la cima del LED, il profilo a 3 s, le misure sul preamp intero)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47b2**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L47 è stato diviso due volte dall'utente: **L47a** la parte e il modello (ADR-058), **L47b1**
la prova del JFET contro la fotoresistenza e la decisione (ADR-059), **L47b2** il resto: questo.

**Cosa ha deciso L47b1** (2026-10-02, `reports/2026-10-02-L47b1-prova-mute.md`, ADR-059):
- **il JFET è provato e scartato**: S 24–39 dB anche a 6 s, distorsione 20–60 % nella sfumatura.
  È un limite fisico coi 2,7 V RMS del progetto (col correttivo ideale ancora 6–30 %), non della
  geometria. Non si riapre senza una ragione nuova (ADR-059, «Da riaprire se»);
- **la cella resta la NSL-32SR3** di Advanced Photonix (ADR-058 confermata);
- **il tempo della sfumatura**: l'utente, «proviamo target a 3s». È un **bersaglio** di 3 s per
  verso, **non un tetto del PRB**. Sul banco ridotto, col profilo v4 compresso a 3 s e la cima del
  LED a 12 mA, S vale 12,7–16,9 dB sulle curve A–E (peggiore la D); a 2 s 20–22 dB.

Viene **prima del placement di prova (L49)** perché fissa la parte e il suo footprint.

Le non conformità del lotto:
- **NC-043 (bloccante per G2)**: si chiude col sorgente e le misure sulla NSL-32SR3;
- **NC-045 (minore)**: il tempo è deciso (3 s); restano il profilo ricalibrato e, se si può, il
  pilota semplificato;
- **NC-049 (maggiore)**: S con la cima a 12 mA, misurato in L47b1 solo sul banco ridotto: si
  chiude sul preamp intero col pilota vero;
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`. Chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`.

## Il mandato

### 1. All'inizio, con l'utente

Le domande si fanno **per nome**, mai per sigle («non ricordo sigle a memoria»); i livelli in
**dB SPL** contro una stanza silenziosa, non in mV.

- **Se dividere il lotto.** È grande: sorgente, pilota, firmware, misure, catene a valle. Proporre,
  non decidere (per esempio: sorgente e cima del LED in uno; profilo, pilota, firmware e misure
  nell'altro).
- **La cima del LED.** Il declassamento in temperatura della NSL-32SR3 non è pubblicato: ~7,2 mA a
  60 °C se vale quello della cella, contro i 12 mA di ADR-050. Due strade: un'ipotesi dichiarata,
  o una domanda scritta al costruttore (techsupport@advancedphotonix.com). La sceglie l'utente.

### 2. Il sorgente

`circuits/preamp/preamp_audio.py`, righe ~186–193: `ls` e `lp` (oggi `VTL5C`) passano alla
NSL-32SR3. Simbolo `Isolator:NSL-32`, footprint `OptoDevice:Luna_NSL-32`. **Il passo delle
piazzole** del footprint (3,81 / 2,53 mm) va confrontato col disegno Silonex (~3,3 / 2,54) in
`vendor/optocoupler/`. Il commento del sorgente punta ad ADR-058 e ADR-059. Poi:
- `scripts/check_relay_safe_state.py`, blocco 2e («le LDR del mute graduale stanno dove ADR-038
  le vuole»): deve riconoscere la parte nuova, ed essere **fatto fallire prima di fidarsene**;
- i deck canonici che includono `vtl5c4_comportamentale.lib` (`tb_e3_e5_ldr.cir`, la famiglia
  `tb_v2_*`, il generatore `L29c/deck/genera_tb_v2_casopeggiore.py`) passano al modello della
  NSL-32SR3. **Nessun deck canonico resta sulla VTL5C4.**

### 3. Il profilo e il pilota

- **Il profilo a 3 s**, ricalibrato sull'inviluppo A–E della NSL-32SR3, non solo compresso. Il
  banco di L47b1 (`data/2026-10-02/L47b1/banco/sfumatura.py`, opzioni `--cima12`) è il punto di
  partenza: dice già che il v4 compresso passa, con 3,1 dB di margine sulla curva D.
- **Il pilota** in `circuits/preamp/psu.py` (ADR-049, ADR-050): la cima che l'utente sceglie, e il
  profilo nuovo. Se si semplifica (NC-045: RC più generatore di corrente al posto di DAC,
  convertitori e calibrazione), con l'utente e un'ADR.
- **Il firmware** `firmware/preamp_timer/`: la legge delle LDR in `timer_core.c` e la sua tabella,
  `spec/timer_spec.md`, i test sull'host (blocco 2k: 65 + 45 controlli, 21 falsi) e i falsi nuovi
  per il tempo di 3 s.
- Il cablaggio J3 (`LDR_CMD`) non cambia se il pilota resta a correnti di LED: il 2j lo dice.

### 4. Le misure, sul preamp intero

Col banco V2 (`tb_v2_casopeggiore.cir`, rigenerato sulla NSL-32SR3 e sul profilo a 3 s), metodo di
`REQUIREMENTS.md`, V2; script in `data/2026-09-25/L29d2/` e `data/2026-09-26/L41c/`:

| Grandezza | Requisito | Note da L47b1 |
|---|---|---|
| **S** | ≤ 20 dB in 100 ms | 12,7–16,9 dB sul banco ridotto; chiude NC-049 |
| **B** | ≤ 100 µV, ~33 dB SPL | **a 20 kHz prima che chiuda il relè: 42–49 dB SPL sul banco ridotto**, dai 5 pF di cella che il modello prende dalla VTL5C4 (ipotesi). A 1 kHz 21–27 dB SPL. Va visto quanto dura prima della chiusura del relè al jack (ADR-038) e se il verdetto di B lo prende |
| **E3** | ≥ 100 kΩ | 771 kΩ in gioco sul banco ridotto. **Una |Zin| a sorgente staccata cambia l'op di una cella con un gate**: con la LDR no, ma se il banco cambia, si misura con la corrente di ramo (README di L47b1) |
| **E5** | 9,90 µV | il modello della NSL-32SR3 non ha rumore: la cella in serie si conta come resistore |

Le cifre portano l'etichetta «modello comportamentale da dati pubblicati, una sola cella misurata
nella regione del mute». La distorsione della NSL-32SR3 **non è modellata**: dirlo accanto a ogni
cifra di distorsione.

### 5. Comunque

- **`psu.py`**: la tenuta di `VRELAY` a rete −10 %, ricorsa col carico nuovo (NC-050); il commento
  di `C_VRELAY` riscritto con le cifre di oggi (NC-051).
- **Le catene a valle** (la lezione di L46b, report §8): i 21 deck veloci
  (`data/2026-10-01/L44/script/regressione.sh` e `confronta_regressione.py`, riferimento in
  `data/2026-10-01/L44/regressione/dopo/`); la catena dei guasti di L41c (i comandi in
  `data/2026-10-01/L46b/README.md`); il firmware sull'host (blocco 2k).
- **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta all'ADR o
  al lotto; `validate_models.py --check-provenance` pulito.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #24 nodi del blocco, #29 `altermod` e i modelli rinominati;
  - #33/#38 il «transient op», e **#40**: con `abstol=1e-15` l'op di un modello a stato dipende dal
    percorso di Newton; «failed» nel log non vuol dire fallito. Leggere stdout e stderr;
  - #34 un `alter` che sopravvive a `destroy all`, #35 la `tran` abortita che scrive zeri, #36 la
    PWL lunga ignorata, #37 le Note dentro le tabelle;
  - **da L47b1** (nel README del banco, non ancora in limitations): la NSL-32SR3 **a stato fermo**
    fa collassare il passo della `tran` («Timestep too small … b.xlp.bdx», rc 0); in sfumatura
    corre. `print nome = espressione` esce 0 con «is not available».
- `docs/preamp/STATE.md`: «In breve» e le voci di diario di **L47b1**, «Dopo L47a», L47a, L46b,
  L41b1, L41b2, L29b2.
- `docs/preamp/reports/2026-10-02-L47b1-prova-mute.md`, `data/2026-10-02/L47b1/README.md`,
  `reports/2026-10-02-L47a-cella-mute.md`, `data/2026-10-02/L47a/nsl32sr3_modello/README.md`.
- `NONCOMPLIANCE.md`: **NC-043**, **NC-045**, **NC-049**, **NC-050**, **NC-051**, con gli
  avanzamenti di L47a e L47b1.
- `decisions/ADR-038*`, `ADR-039*`, `ADR-040*`, `ADR-049*`, `ADR-050*`, `ADR-053*` (il PRB),
  `ADR-058*`, **`ADR-059*`**; `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni). **Anche `cd … && script`** è rifiutato:
    gli script si lanciano col percorso assoluto;
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
  vanno in `.gitignore` prima del commit (L47b1 ne ha escluse ~1,3 GB, L46b ~6,3 GB).

## NON fa parte di questo lotto

- il JFET e ogni altra alternativa alla fotoresistenza: decisi in ADR-059 e prima (STATE, «Dopo
  L47a»);
- un tetto del tempo di mute nel PRB: l'utente ha scelto un bersaglio. Se dopo le misure lo vuole,
  vuole un'ADR (ADR-053);
- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- il blocco di guadagno (ADR-054, ADR-056) e il flicker (ADR-057): decisi;
- rigenerare il dossier. Quando lo si rigenera:
  - il §14 di `build_dossier.py` dice ancora «solo l'LSK489A porta KF» e «niente distorsione»,
    superato da L44 e L46a;
  - il mute descritto è quello della VTL5C4, e la prova del JFET non c'è.

## CHIUSURA

1. `STATE.md` con L47b2 **fatto** (o il primo sotto-lotto, se l'utente lo divide) e il prossimo
   lotto nella tabella (L48, o il secondo sotto-lotto).
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47b2` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
