# Prompt per la sessione successiva — L47 (la cella del mute)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L47**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L46 (a e b) e L44 sono chiusi: il blocco di guadagno è quello di ADR-056, e da L44
(ADR-057) i bipolari portano il flicker a un tetto dichiarato; NC-004 è chiusa.

L47 viene **prima del placement di prova (L49)** perché cambia una parte, e quindi un footprint:

- **NC-043 (bloccante per G2)**: la VTL5C4 dell'Excelitas è fuori produzione (ultimo ordine 2015).
  Serve una cella sostitutiva disponibile (Xvive, CoolAudio o altro), col datasheet in `vendor/` e
  il modello con la provenienza.
- **NC-045 (minore)**: il pilota delle LDR (DAC a 12 bit, due convertitori esponenziali,
  compensazione in temperatura, calibrazione a due punti) e Td = 6 s servono un criterio che
  ADR-040 ha cambiato. L'utente ha già detto «sono disposto a cambiare e a ridurre il tempo di
  mute»; l'architetto indica Td 1–2 s e un pilota RC più un generatore di corrente.
- **NC-049 (maggiore)**: S del mute con la cima a 12 mA (ADR-050) non è mai stato misurato.
- **NC-050 e NC-051 (minori)**: il pilota sta in `psu.py`; chi lo tocca ricorre la tenuta di
  `VRELAY` a rete −10 % (oggi 36,1 ms contro ≥ 25) e riscrive il commento di `C_VRELAY`.

## Il mandato

1. **All'inizio, con l'utente** (le domande **per nome**, mai per sigle: «non ricordo sigle a
   memoria»; i gradini e i livelli in **dB SPL** contro una stanza silenziosa, non in mV):
   - **se dividere il lotto**. Tre decisioni diverse: la parte (NC-043), il tempo di mute e il
     pilota (NC-045), e le misure che ne seguono (S, E3, E5, `VRELAY`). L46 è stato diviso così;
     proporre una divisione, non deciderla;
   - **il tempo massimo del mute**: oggi il PRB non lo fissa. Se l'utente ne vuole uno, va nel PRB
     con un'ADR (il PRB si cambia solo con un'ADR, ADR-053).
2. **La parte** (`bom-component-manager`): sostituti della VTL5C4 verificati disponibili, coi
   datasheet in `vendor/` (`freeze_vendor.sh`) e le curve resistenza/corrente del LED. Mai un
   numero di parte plausibile non controllato. In tabella per l'utente: disponibilità, dispersione
   dichiarata fra esemplari, tempi di salita e discesa, corrente massima del LED a 60 °C (ADR-050 e
   NC-038 hanno insegnato che il declassamento conta).
3. **Il modello** della cella scelta, comportamentale dal datasheet come
   `models/optocoupler/vtl5c4_comportamentale.lib` (la sua intestazione dice come è fatto e cosa
   non ha: niente rumore), con la provenienza e una ricetta in `validate_models.py`.
4. **Il pilota e Td**, se l'utente sceglie di semplificarli: le strade misurate e in tabella prima
   della domanda, non scelte da soli. Poi S ≤ 20 dB in 100 ms su `tb_v2_casopeggiore.cir` e la
   matrice di V2 (il metodo è in `REQUIREMENTS.md`, V2; gli script in `data/2026-09-25/L29d2/` e
   `data/2026-09-26/L41c/`), E3 ed E5 su `tb_e3_e5_ldr.cir`, la calibrazione della cima.
5. **`psu.py`**: la tenuta di `VRELAY` a rete −10 % ricorsa col carico nuovo (NC-050), il commento
   di `C_VRELAY` riscritto con le cifre di oggi (NC-051), netlist uguale salvo i campi volatili
   dove il circuito non cambia.
6. **Le catene a valle** (la lezione di L46b, report §8): una modifica che tocca la scheda audio o
   l'alimentatore ricorre i 21 deck veloci (`data/2026-10-01/L44/script/regressione.sh` e
   `confronta_regressione.py`, il riferimento è `data/2026-10-01/L44/regressione/dopo/`), la catena
   dei guasti di L41c (i comandi in `data/2026-10-01/L46b/README.md`) e il firmware sull'host
   (blocco 2k di `run_tests.sh`).
7. **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` col commento che punta alla ADR o
   al lotto; la provenienza dei modelli aggiornata e `validate_models.py --check-provenance`
   pulito.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (le trappole che falliscono in silenzio: #22 rinumerazione,
  #24 nodi del blocco, #33/#38 il «transient op», #34 un `alter` che sopravvive a `destroy all`,
  #36 la PWL lunga ignorata, #37 le Note dentro le tabelle, **#39** un editor che normalizza i
  CRLF dei file del costruttore), e in `docs/preamp/STATE.md` «In breve» e le voci di diario di
  L44, L46b, L41b1, L41b2, L29b2.
- `NONCOMPLIANCE.md`: **NC-043**, **NC-045**, **NC-049**, **NC-050**, **NC-051**, e la chiusa
  NC-038 (il LED nel telaio caldo).
- `decisions/ADR-038*`, `ADR-039*`, `ADR-040*`, `ADR-049*`, `ADR-050*`, `ADR-053*` (il PRB);
  `firmware/preamp_timer/spec/timer_spec.md`.

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- I file di `models/` con un blocco del costruttore si modificano **sui byte**, mai con Edit (#39).
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto. Il modello
  della cella è comportamentale: va scritto accanto a ogni cifra.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la corsa
  (#33, #38).
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): forme d'onda grosse vanno
  in `.gitignore` prima del commit (L46b ne ha escluse ~6,3 GB).

## NON fa parte di questo lotto

- il selettore d'ingresso e la continua del blocco A (L48); il placement e routing di prova (L49);
  la FMEA (L45); massa e terra (L50);
- il blocco di guadagno (ADR-054, ADR-056) e il flicker (ADR-057): decisi;
- rigenerare il dossier. Quando lo si rigenera, il §14 di `build_dossier.py` dice ancora «solo
  l'LSK489A porta KF» e «niente distorsione»: testo superato da L44 e L46a.

## CHIUSURA

1. `STATE.md` con L47 **fatto** (o L47a, se l'utente lo divide) e il prossimo lotto nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L47` (o il nome del sotto-lotto).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
