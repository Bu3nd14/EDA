# Prompt per la sessione successiva — L41c (il banco di L30 col circuito vero)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L41c** e si ferma. Non iniziarne un secondo. Se si divide
(L41c1, L41c2…), la divisione si scrive nella tabella dei lotti di `STATE.md` prima di chiudere.

## Il mandato

L30 ha provato lo spegnimento morbido e il failsafe (ADR-046, P9) su un banco in cui
l'alimentatore era **disegnato a mano**: PWL `@vpp` / `@vmm` / `@vpwl` per i rail e per `VRELAY`,
istanti scelti per i contatti dei relè. Da L41a, L41b1 e L41b2 l'alimentatore esiste davvero
(`circuits/preamp/psu.py`), col suo temporizzatore in hardware e col firmware provato sul circuito.
**L41c rifà il banco di L30 col circuito vero** e chiude NC-036, se i numeri reggono:

1. **Il ponte fra le due schede**: le forme d'onda dei rail, di `VRELAY` al connettore J1, di
   `MUTE_CMD` e `PERMIT_CMD` escono dalle sequenze di L41b2 (`data/2026-09-26/L41b2/seq/`, deck
   al punto fisso; le forme d'onda si rifanno con `tutti_seq.sh`) e diventano le sorgenti della
   scheda audio nel banco di L30 (`--matrice l30` del generatore di L29c). Una scheda sola non
   sta in un deck: la catena resta in due tempi, e va detto nel report.
2. **Le corse di L30 rifatte** col metodo di V2 (REQUIREMENTS, ADR-032):
   - lo spegnimento morbido sotto V2;
   - la perdita di rete, un regolatore aperto, un rail solo, `VRELAY` persa: sotto l'obiettivo di
     **2 mV** (tetto di non-danno 0,87 V, ADR-046);
   - il controfattuale senza Δ che **fallisce** (L30: 69 mV).
3. **La decisione dell'utente sul corto dell'uscita di U503**: un corto scarica anche la tenuta
   di `VRELAY`, tutte le bobine cadono insieme, ed è il caso «senza Δ» di L30 (~90 dB SPL di picco
   a 1 m: sotto il tetto di ~112 dB, sopra l'obiettivo di ~60 dB). **Chiedila conversando e coi
   numeri**, prima di scrivere il criterio. Se decide, un'ADR.

## Prima di tutto

- **I bump si dicono in dB SPL di picco a 1 m contro il silenzio di una stanza**, non in mV.
- **Il worktree di L41b2 può essere ancora bloccato** da una sessione Claude viva: se
  `EnterWorktree` rifiuta un worktree, è quello; se ne crea uno nuovo per L41c.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**: la #33, la #34, la **#35** (nuova in L41b2: dopo
   una `tran` abortita i dati arrivano comunque fino a `tstop`, e sono zeri).
2. **`docs/preamp/STATE.md`**: le voci di diario di L41b2 e di L30, le righe L41c, L28.
3. **ADR-046**, **ADR-047**, ADR-045, ADR-048 punto 5; **NC-036** (la voce intera, con gli
   aggiornamenti di L41a, L41b1, L41b2), **NC-037**.
4. **Il report di L30** (`reports/2026-09-26-L30-spegnimento-failsafe-calore.md`) e il README dei
   suoi dati; poi **il report di L41b2** e il README di `data/2026-09-26/L41b2/`.
5. `firmware/preamp_timer/spec/timer_spec.md` § 1 e § 4.4–4.6: cosa garantisce l'hardware, cosa il
   firmware.

## Quello che i lotti precedenti ti consegnano

- **L30**: il banco `deck/tb_v2_l30.cir` generato con `--matrice l30`, 29 corse, gli istanti e le
  rampe scritti a mano; le cifre (spegnimento 12 su 12 ≤ 2,7 µV; guasto 12 su 12 ≤ 1,77 mV;
  senza Δ 69 mV).
- **L41b2**, le sequenze sul circuito col firmware (`seq/analisi_seq.txt`):
  - spegnimento: `MUTE_CMD` rilasciato 6,522 s dopo il frontale, Δ 39,8 ms, K501 aperto 63,4 ms
    dopo `PERMIT_CMD`;
  - buco di 20 ms: jack staccati a 14,4 ms, V+ mai sotto 15,0 V; buco di 200 ms: V+ fino a 10,0 V,
    di nuovo l'accensione;
  - guasto di U502 con la rete presente: jack a 10,7 ms, K501 aperto dopo 102,9 ms.
- **Il generatore** `data/2026-09-26/L41b2/deck/genera_tb_psu.py` (`--nome seq`) e il ponte
  `firmware/preamp_timer/test/ponte.c`; `gmin=1e-10` nei deck delle sequenze (motivato nel
  sorgente).

## I vincoli

- **L'hardware non si tocca**, se non per un difetto trovato: `psu.py` rigenerato deve dare la
  stessa netlist (cambia solo la data), il 2e e il 2j verdi.
- **La scheda audio non si tocca.** Il deck V2 `spice/preamp/tb/tb_v2_casopeggiore.cir`
  rigenerato deve restare **byte-identico** (generatore di L29c, `--matrice sorgente`, `cmp`).
- **Il firmware non si tocca**, se non per un difetto trovato: `run_host_tests.sh --falsi` resta
  21 su 21.
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

- **NC-037** oltre il suo criterio (il giro BOM di T2 è di G2);
- **NC-004** (il rumore 1/f, bloccante per G1);
- **NC-011** (la quota di ADR-020 coi TPS7A4701);
- **L28**;
- il dossier;
- `src/main_attiny.c`, la compilazione per l'AVR e la programmazione;
- il layout dei PCB e il contenitore (G2).

## CHIUSURA

1. `STATE.md` con L41c (o la parte fatta) **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L41c` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
