# Prompt per la sessione successiva — L41b2 (il firmware del temporizzatore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L41b2** e si ferma. Non iniziarne un secondo. Se si divide
ancora (L41b2a, L41b2b…), la divisione si scrive nella tabella dei lotti di `STATE.md` prima di
chiudere.

## Il mandato

La metà hardware del temporizzatore è in `circuits/preamp/psu.py`, fatta nel lotto precedente
(**ADR-049**):
- il micro U509, ATtiny3216;
- il DAC U510, MCP4822;
- Δ e Δ₂ in hardware;
- l'interruttore di `VRELAY` per lo standby;
- il pilota esponenziale delle LDR.

Il **contratto** del firmware è scritto: `firmware/preamp_timer/spec/timer_spec.md`. L41b2 lo
realizza e lo prova:

1. **`firmware/preamp_timer/src/timer_core.c`**: la logica pura, `tick(ingressi, dt) → uscite`,
   senza registri. Deve fare tutte le sequenze di § 4 della specifica:
   - l'accensione dallo standby, coi rail, la calibrazione e ≥ 50 ms da `VRELAY_EN` (i 13 ms di
     ADR-027);
   - l'inserzione e il rilascio del mute, reversibili a metà (profilo v4, Td = 6 s, `MUTE_REQ`
     0,5 s dopo d = 1, `PERMIT_REQ` 20 ms dopo);
   - lo spegnimento morbido (≥ 50 ms fra il mute completo e `MAINS_REQ`);
   - il debounce, l'OR con SW3, un filo rotto in mute;
   - il buco di rete nelle sue tre classi, con `MUTE_REQ` giù entro 1 ms da `MUTE_G_IN`;
   - la ritenuta dopo un guasto con la rete presente;
   - la legge delle LDR (§ 5): Vt col sensore, la calibrazione a 20 mA e 2 mA.
2. **I test sull'host** in `firmware/preamp_timer/test/`, compilati con `clang`
   (`/usr/bin/clang`, Apple clang 21):
   - uno per sequenza, che asserisce i tempi della specifica;
   - **ciascuno fatto fallire su un falso** prima di fidarsene;
   - la legge del DAC contro la tabella v4 a 15, 25, 35, 45 e 60 °C.
3. **Il ponte verso SPICE**:
   - i test scrivono le uscite del core in CSV;
   - il generatore del banco di L41b1 (`data/2026-09-26/L41b1/deck/genera_tb_psu.py`, da
     copiare nella cartella di L41b2 ed estendere) le trasforma in PWL delle sorgenti del micro;
   - si simulano sul circuito l'accensione, un rilascio, un'inserzione con inversione a metà,
     lo spegnimento, un buco di rete e un guasto.
4. **La SPI su PA2**: verificare sul datasheet (`vendor/microcontroller/microchip/ATtiny3216`)
   se SPI0 in modalità host lascia PA2 all'ADC (AIN2, `ADC_I_P`). Se no, la SPI si fa in
   software (§ 2 della specifica).
5. **`src/main_attiny.c`**, l'adattatore verso i registri, solo se resta tempo. Non si compila per
   l'AVR: `avr-gcc` non è installato, e non va installato in questo lotto.

## Prima di tutto

- **La cima della tabella delle LDR è aperta** (**NC-038**): la VTL5C4 non regge 20 mA sopra
  ~52 °C. **Chiedi all'utente**, conversando e con i numeri (report di L41b1 § 5), se abbassare
  la cima, limitare la temperatura o cambiare pezzo, **prima** di fissare la legge nel core. Il
  circuito non cambia: cambia la tabella del firmware. Se decide, scrivi un'ADR.
- **I bump si dicono in dB SPL di picco a 1 m contro il silenzio di una stanza**, non in mV.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**: la #33 aggiornata in L41b1, la #34.
2. **`docs/preamp/STATE.md`**: la voce di diario di L41b1, e le righe L41b1, L41b2, L41c.
3. **`firmware/preamp_timer/spec/timer_spec.md`** (tutta) e **ADR-049**; poi ADR-048 punto 6,
   ADR-046, ADR-045, ADR-039, ADR-027, ADR-022.
4. **Il report di L41b1** (`reports/2026-09-26-L41b1-temporizzatore-hardware.md`) e il README
   dei suoi dati: `genera_tb_psu.py`, `analizza_timer.py`, `analizza_ldr.py`, la calibrazione
   in due passi.
5. **`circuits/preamp/psu.py`** (il blocco del micro e i commenti delle costanti), **NC-036**,
   **NC-037**, **NC-038**.

## Quello che il lotto precedente ti consegna

- **Il sorgente** `psu.py` → `psu.net`: ERC con 21 avvisi e 2 «errori», spiegati nel sorgente.
- **Il banco**: `genera_tb_psu.py`, coi deck `timer` (transitori), `ldr` (punti di lavoro in
  temperatura) e `rumore`.
  - Il micro comportamentale ha per ogni uscita due PWL: `set_` (il livello) e `drv_` (1 =
    pilotata, 0 = alta impedenza). **È lì che entrano le forme d'onda del core.**
  - Guardie: nessun «Transient op» (limitations #33); ogni caso rimette tutte le alterazioni
    (#34); i tempi dei PWL con `%.12g` (non `%g`).
- **Le cifre**:
  - Δ ≥ 16,9 ms col micro in reset o a zero;
  - standby: 0 V a J1 e 92,5 mW dal secondario;
  - LDR calibrate entro ±0,92 dB (la calibrazione è `cal.json`, e il core deve ritrovare gli
    stessi `off` e `r_ohm` sul banco);
  - rumore ~1,4 µV/√Hz.
- **I controlli**: il 2j (`check_psu_harness.py`) e il 2e `--timer`
  (`check_relay_safe_state.py`), con 15 falsi in `data/2026-09-26/L41b1/falsi/`.

## I vincoli

- **L'hardware non si tocca**, se non per un difetto trovato: `psu.py` rigenerato deve dare la
  stessa netlist, il 2e e il 2j verdi.
- **La scheda audio non si tocca.** Il deck V2 `spice/preamp/tb/tb_v2_casopeggiore.cir`
  rigenerato deve restare **byte-identico** (generatore di L29c, `--matrice sorgente`, `cmp`).
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - i cicli con variabili calcolate a runtime;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando);
  - gli heredoc che eseguono script.

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. `cd` in un comando a sé.

## NON fa parte di questo lotto

- **L41c**, il banco di L30 col circuito vero, e la decisione sul corto dell'uscita di U503
  (~90 dB SPL, sotto il tetto);
- **NC-037** oltre il suo criterio (il giro BOM di T2 è di G2);
- **NC-004** (il rumore 1/f, bloccante per G1);
- **NC-011** (la quota di ADR-020 coi TPS7A4701);
- **L28**;
- il dossier;
- la compilazione per l'AVR e la programmazione;
- il layout dei PCB e il contenitore (G2).

## CHIUSURA

1. `STATE.md` con L41b2 (o la parte fatta) **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L41b2` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
