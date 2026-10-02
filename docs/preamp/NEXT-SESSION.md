# Prompt per la sessione successiva — L47b (il tempo del mute, il pilota e le misure sulla NSL-32SR3)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47b**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. All'inizio di L47 l'utente l'ha diviso in due:
- **L47a la parte e il modello**, fatto il 2026-10-02 (ADR-058);
- **L47b il tempo del mute, il pilota e le misure**: questo lotto.

L47a ha scelto, con l'utente, la **NSL-32SR3** di Advanced Photonix: l'unica sostituta della
VTL5C4 acquistabile (DigiKey, 7867 pezzi). Il modello è
`models/optocoupler/nsl32sr3_comportamentale.lib`, comportamentale, da dati pubblicati con ipotesi
dichiarate:
- cinque curve A–E: gli estremi dei 61 pezzi misurati da JC Maillet e le due diagonali;
- **una sola cella misurata nella regione del mute**, da 0,1 mA a 2,5 µA;
- la coda dello spegnimento pessimistica.

Le cifre della scheda audio usano ancora la VTL5C4: il sorgente non è cambiato.

Viene **prima del placement di prova (L49)** perché cambia una parte e il suo footprint.

Le non conformità del lotto:
- **NC-043 (bloccante per G2)**: si chiude con le misure sulla cella nuova;
- **NC-045 (minore)**: il pilota delle LDR e Td = 6 s servono un criterio che ADR-040 ha
  cambiato. L'utente ha detto «sono disposto a cambiare e a ridurre il tempo di mute».
  L'architetto indica Td 1–2 s e un pilota RC più un generatore di corrente;
- **NC-049 (maggiore)**: S del mute con la cima a 12 mA (ADR-050) non è mai stato misurato;
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`. Chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`.

## Il mandato

1. **All'inizio, con l'utente.** Le domande si fanno **per nome**, mai per sigle («non ricordo
   sigle a memoria»); i gradini e i livelli in **dB SPL** contro una stanza silenziosa, non in mV.
   - **Il tempo massimo del mute.** L'utente ha detto «decido dopo la tabella». Il dato nuovo: la
     NSL-32SR3 scende a 100 kΩ in **10 ms** (la VTL5C4 in 1,5 s), quindi la cella non pone un
     limite e la gradualità la dà tutta il pilota. Il limite che resta è S ≤ 20 dB in 100 ms:
     dal livello pieno a −70 dB servono almeno ~0,35 s. Se l'utente vuole un tetto, va nel PRB
     con un'ADR (ADR-053).
   - **La cima della corrente del LED.** Il datasheet non pubblica un declassamento della
     corrente del LED: «derate linearly to 0 at 75 °C» è attaccato alla sola dissipazione della
     cella. Se lo si applica al LED, da 25 mA a 23 °C, a 60 °C restano **~7,2 mA**, sotto la cima
     di 12 mA di ADR-050. Due strade da proporre:
     - un'ipotesi dichiarata (la lettura prudente);
     - una domanda scritta al costruttore (techsupport@advancedphotonix.com), che ferma la
       decisione.

     Cambia la cella in derivazione accesa, quindi il residuo B.
2. **Il pilota e Td.** Prima della domanda, le strade misurate e in tabella, non scelte da soli:
   - il pilota di oggi (DAC a 12 bit, due convertitori esponenziali, compensazione,
     calibrazione, ADR-049);
   - un pilota RC più un generatore di corrente (l'architetto);
   - altre, se servono.

   **Il profilo v4 è tarato sulla VTL5C4** (ADR-039, ADR-040): va rifatto sull'inviluppo A–E
   della NSL-32SR3, che nella regione del mute è largo ~5,5× fra gli estremi a 10 µA.
3. **Il sorgente.** In `circuits/preamp/preamp_audio.py` le due celle per canale (`ls`, `lp`)
   diventano NSL-32SR3: simbolo `Isolator:NSL-32`, footprint `OptoDevice:Luna_NSL-32`.
   - **Confronta col disegno** (`vendor/optocoupler/silonex/NSL-32SR3/`) il passo delle piazzole
     (3,81 mm fra i terminali del LED e 2,53 mm fra quelli della cella, contro ~3,3 e 2,54) e la
     piedinatura del simbolo.
   - Il commento riscritto con ADR-058; il 2e e il 2j di `run_tests.sh` devono restare verdi.
   - **Due LED in serie fra i canali** (ADR-039) cadono fino a 2 × 2,5 V, contro 2 × 2,0: il
     commento di `psu.py` alla riga 182 e la tensione del pilota.
4. **Le misure**, ognuna sulle cinque curve, o sulle peggiori motivate:
   - **S** ≤ 20 dB in 100 ms su `tb_v2_casopeggiore.cir` e la matrice di V2. Il metodo è in
     `REQUIREMENTS.md`, V2; gli script in `data/2026-09-25/L29d2/` e `data/2026-09-26/L41c/`;
   - **B**: il residuo a mute inserito, ≤ 100 µV. Dipende dai 25 MΩ al buio e dalla **coda dello
     spegnimento ipotizzata** (0,238 decadi/s oltre 100 kΩ). Se B esce, dirlo come «l'ipotesi
     pessimistica», non come un fatto della parte;
   - **E3 ed E5** su `tb_e3_e5_ldr.cir`. Gli 0,5 pF ingresso-uscita sono quelli della VTL5C4, non
     pubblicati: dichiararlo;
   - la calibrazione della cima.

   I deck si sostituiscono da `VTL5C4_B` a `NSL32SR3_*` (`tb_v2_casopeggiore.cir` righe 184–185,
   `tb_e3_e5_ldr.cir` righe 86–87).
5. **`psu.py`.**
   - La tenuta di `VRELAY` a rete −10 %, ricorsa col carico nuovo (NC-050).
   - Il commento di `C_VRELAY` riscritto con le cifre di oggi (NC-051).
   - Netlist uguale salvo i campi volatili, dove il circuito non cambia.
6. **Le catene a valle** (la lezione di L46b, report §8). Una modifica che tocca la scheda audio o
   l'alimentatore ricorre:
   - i 21 deck veloci: `data/2026-10-01/L44/script/regressione.sh` e `confronta_regressione.py`,
     col riferimento in `data/2026-10-01/L44/regressione/dopo/`;
   - la catena dei guasti di L41c: i comandi sono in `data/2026-10-01/L46b/README.md`;
   - il firmware sull'host: il blocco 2k di `run_tests.sh`.
7. **Tracciabilità.**
   - Ogni valore nuovo in `circuits/preamp/*.py` porta il commento che punta alla ADR o al lotto.
   - Il modello della VTL5C4 resta in `models/` se qualche deck storico lo cita, ma nessun deck
     canonico deve più usarlo.
   - `validate_models.py --check-provenance` pulito.

## Prima di tutto

- `CLAUDE.md` e `docs/limitations.md`. Le trappole che falliscono in silenzio:
  - #22 rinumerazione, #24 nodi del blocco;
  - #33/#38 il «transient op», e **#40**: con `abstol=1e-15` l'op del modello a stato dipende dal
    percorso di Newton, e «Dynamic gmin stepping failed» precede un op valido. Leggere stdout e
    stderr;
  - #34 un `alter` che sopravvive a `destroy all`, #36 la PWL lunga ignorata, #37 le Note dentro
    le tabelle, #39 un editor che normalizza i CRLF dei file del costruttore.
- `docs/preamp/STATE.md`: «In breve» e le voci di diario di L47a, L44, L46b, L41b1, L41b2, L29b2.
- `docs/preamp/reports/2026-10-02-L47a-cella-mute.md` e
  `data/2026-10-02/L47a/nsl32sr3_modello/README.md`: il modello, le sue ipotesi, le sue opzioni di
  convergenza.
- `NONCOMPLIANCE.md`: **NC-043** (con l'avanzamento di L47a), **NC-045**, **NC-049**,
  **NC-050**, **NC-051**, e la chiusa NC-038 (il LED nel telaio caldo).
- `decisions/ADR-038*`, `ADR-039*`, `ADR-040*`, `ADR-049*`, `ADR-050*`, `ADR-053*` (il PRB),
  **`ADR-058*`** («Cosa resta aperto per L47b»); `firmware/preamp_timer/spec/timer_spec.md`.

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
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto. Il modello
  della cella è comportamentale, con una sola cella misurata nella regione del mute: va scritto
  accanto a ogni cifra.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la corsa
  (#33, #38, #40).
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): le forme d'onda grosse
  vanno in `.gitignore` prima del commit (L46b ne ha escluse ~6,3 GB).

## NON fa parte di questo lotto

- il selettore d'ingresso e la continua del blocco A (L48); il placement e il routing di prova
  (L49); la FMEA (L45); la massa e la terra (L50);
- il blocco di guadagno (ADR-054, ADR-056) e il flicker (ADR-057): decisi;
- un'altra cella: la parte è decisa (ADR-058), salvo le condizioni del suo «Da riaprire se»;
- rigenerare il dossier. Quando lo si rigenera, il §14 di `build_dossier.py` dice ancora «solo
  l'LSK489A porta KF» e «niente distorsione», testo superato da L44 e L46a; e il mute con la
  VTL5C4, superato da ADR-058.

## CHIUSURA

1. `STATE.md` con L47b **fatto** (o L47b1, se l'utente lo divide) e il prossimo lotto (L48) nella
   tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47b` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
