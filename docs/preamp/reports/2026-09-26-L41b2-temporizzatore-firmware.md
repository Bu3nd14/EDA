# L41b2 — il temporizzatore dell'alimentatore: il firmware, provato sull'host e sul circuito (2026-09-26)

**Mandato**: la seconda metà di L41b (ADR-048 punto 6, ADR-049; NC-036, NC-038). Decisione:
**ADR-050**. Dati: `data/2026-09-26/L41b2/` (README). Firmware: `firmware/preamp_timer/`
(`src/timer_core.c`, `test/`). Specifica aggiornata: `firmware/preamp_timer/spec/timer_spec.md`.
L'hardware (`circuits/preamp/psu.py`) e la scheda audio **non sono stati toccati**.

Il lotto è stato fatto in due sessioni: la prima si è interrotta per il limite d'uso con tre
commit pushati (il core, i test, ADR-050, il banco LDR); la seconda ha fatto convergere le
sequenze sul circuito e chiuso.

**Sintesi.**
- **NC-038 chiusa** da una decisione dell'utente (ADR-050): la cima delle LDR a 12 mA a ogni
  temperatura. A 60 °C il LED della VTL5C4 regge 13 mA.
- **Il core** (`timer_core.c`, `tick(ingressi, dt) → uscite`, senza registri) fa tutte le
  sequenze di § 4 della specifica e la legge delle LDR di § 5.
- **Sull'host**: 65 + 45 controlli verdi, **21 falsi su 21** fanno fallire il proprio test.
  Agganciato a `run_tests.sh` come blocco 2k.
- **Sul circuito**: il core fa da micro del banco di L41b1, iterato fino al punto fisso fra
  firmware e circuito. **7 sequenze su 7 passano i criteri**, scritti prima delle corse, e due
  falsi del core le fanno fallire sul criterio giusto.
- **La SPI su PA2** va bene così: in modalità host MISO è un ingresso, e l'ADC legge AIN2.

## 1. Le decisioni

**Dell'utente** (ADR-050): fra quattro strade portate coi numeri (abbassare la cima, una cima che
scende con la temperatura, limitare il telaio a ~50 °C, cambiare pezzo), la cima a **12 mA** su
tutte e due le stringhe. Il resto del profilo v4 non cambia.

**Di progetto** (ADR-050 punti 2–4, nel firmware):
- la calibrazione legge a 12 mA e a **2 mA** (20 mV sui 10 Ω, 37 passi dell'ADC);
- il fit usa come ascissa la **corrente letta**: con quella voluta una pianta lineare lasciava
  −0,38 dB alla cima;
- il firmware legge lo **zero** di ogni pin di corrente con la stringa a 10 nA e lo sottrae:
  offset e perdita del pin valevano fino a −2,06 dB.

Correzioni alla specifica di L41b1, trovate sul circuito (ognuna con la sua ragione in
`timer_spec.md`):
- **80 ms, non 50,** fra `PERMIT_REQ` e il relè di rete: ADR-046 vuole ≥ 50 ms da `PERMIT_CMD`,
  che arriva Δ dopo. Con 50 ms K501 si apriva 33 ms dopo `PERMIT_CMD`;
- **200 ms di assestamento** della cima corretta prima di `VRELAY_EN`: 50 ms dopo il fit la cima
  era ancora a 10,6 mA, −1 dB;
- il fronte d'apertura dei due interruttori: il pull-up da 100 kΩ sui 100 nF, **7,0 ms** al pin,
  non 0,1 ms;
- la finestra di **20 ms** per classificare un buco di rete: `MUTE_G` cade ~1 ms prima che
  `ADC_MD` passi 2,5 V.

## 2. Il firmware e i test sull'host

- `test_sequenze` (65 controlli): accensione, inserzione, rilascio, inversione, spegnimento,
  debounce, buco di classe 1 e 2, guasto e ritenuta, calibrazione con rilettura e rifiuto. Il
  mondo (`mondo.c`) ha una pianta con un errore vero (4,5 mV, 0,43 Ω).
- `test_legge` (45 controlli):
  - i codici del DAC contro i deck di L41b1: 250 su 250 uguali;
  - `cal.json` di L41b1 ritrovato dal core entro 2,8 nV e 0,15 µΩ;
  - la tabella v4 da 15 a 60 °C entro **+0,061 dB**;
  - il bilancio con gli errori tipici (ADC ±3 LSB, guadagno ±5 LSB, sensore ±3 °C, 50 nA di
    perdita): peggiore **−0,88 dB**, quasi tutto il sensore al ginocchio.
- **21 falsi** (`FALSO_n`), `falsi/esito.txt`: ognuno fa fallire il suo test. Fra questi: i
  5 ms al posto dei 13 di ADR-027, d che si muove col relè aperto, `PERMIT_REQ` insieme a
  `MUTE_REQ`, `MUTE_G_IN` ignorato, un filo rotto di SW3 che suona, la cima a 20 mA.

## 3. Il ponte verso SPICE

`test/ponte.c` fa girare il core sui pin che il circuito simulato gli dà (un passo ogni 1 ms, più
l'interruzione su ogni discesa di `MUTE_G_IN`). `genera_tb_psu.py --nome seq` trasforma le uscite
del core nelle PWL del micro comportamentale di L41b1 (`set_` delle quattro richieste, `den_` e
`dset_` del DAC). `corri_seq.sh` itera circuito → core → circuito: il caso vale quando due giri
danno le stesse uscite (tempi entro 0,2 ms) **e il ponte non ha dovuto ricostruire nessun pin**.

**Tre difetti del banco trovati in questa sessione**, nessuno del circuito né del firmware:
1. **Il pin letto sulla soglia.** All'interruzione il ponte interpolava `MUTE_G_IN` proprio
   all'istante in cui attraversa 2,5 V: alto in un giro, basso nel successivo. Il guasto
   alternava due giri per 10 giri senza punto fisso, e il buco di 200 ms chiudeva con una
   sostituzione. All'interruzione il pin è basso per definizione.
2. **Lo spegnimento fermava ngspice** a 8,629 s: il core porta il codice del DAC a 0 nello
   stesso µs dello shutdown. Col DAC spento il codice non entra nella corrente: ora tiene
   l'ultimo valore. Provato su due varianti dello stesso deck: il fronte di 100 µs si ferma
   ancora, il codice tenuto passa.
3. **Una fragilità numerica all'apertura di K501.** Col falso 6 il core spegne a un altro
   istante, e la `tran` si fermava all'apertura del contatto. `rshunt`, `maxord`, `trtol` e un
   modello liscio del MCP6004 non bastavano; `gmin=1e-10` sì. Costa 50 pA sui 10 nA di riposo:
   la serie a riposo passa da 10,3 a 12,3 nA.

Nel frattempo: `corri_seq.sh` ora svuota la cartella del caso prima di ricominciare (un
`punto_fisso.txt` rimasto da una corsa precedente sarebbe sopravvissuto a un fallimento), e
`analizza_seq.py` segna un caso senza punto fisso invece di fermarsi. E una limitazione nuova,
la **#35**: dopo una `tran` abortita, `linearize` e `wrdata` scrivono comunque tutte le righe fino
a `tstop`, e dopo l'aborto è tutto zero. Proprio quello che uno spegnimento dovrebbe mostrare.

## 4. Le cifre sul circuito

`seq/analisi_seq.txt`. In ogni caso, dopo l'evento: `MUTE_CMD` mai eccitato senza `PERMIT_CMD`,
e ogni rilascio di `PERMIT_CMD` ≥ 16,9 ms dopo quello di `MUTE_CMD` (criteri C2, C3).

| Caso | Punto fisso | Cifre |
|---|---|---|
| accensione (dallo standby) | giro 5 | DAC acceso **100,7 ms** dopo i rail in regolazione; serie ≤ 12,3 nA durante la calibrazione; derivazione **12,016 mA (+0,012 dB)** dopo la calibrazione; `MUTE_CMD` **49,4 ms** dopo `VRELAY` ≥ 9,6 V (minimo 13 ms, ADR-027); la derivazione ancora a 12 mA quando il relè si chiude. Rilascio dopo **0,80 s** dal frontale |
| rilascio (da MUTO) | giro 4 | relè prima di d (derivazione a 12,016 mA quando `MUTE_CMD` si eccita); MUSICA a 6,03 s; serie calibrata in MUSICA **12,016 mA (+0,012 dB)** |
| inversione (mute a 0, musica a 3 s) | giro 2 | d arriva a 0,4987 e torna; `MUTE_CMD` mai rilasciato; serie minima +0,28 dB dalla tabella; derivazione ≤ 12,3 nA |
| spegnimento (frontale aperto in MUSICA) | giro 2 | `MUTE_CMD` rilasciato **6,522 s** dopo il pin (il pin a +7,1 ms dal frontale); Δ 39,8 ms; **K501 aperto 63,4 ms dopo `PERMIT_CMD`** (≥ 50, ADR-046); rail in regolazione fino al mute; STANDBY |
| buco di rete 20 ms | giro 2 | jack staccati **14,4 ms** dopo; `MUTE_REQ` giù all'interruzione; **classe 1**, V+ mai sotto 15,0 V; `MUTE_CMD` di nuovo dopo **0,501 s** dal ritorno della rete |
| buco di rete 200 ms | giro 4 | jack staccati 14,4 ms dopo; **classe 2** (V+ fino a 10,0 V): di nuovo l'accensione, `MUTE_CMD` dopo 0,785 s |
| guasto (U502 spento, rete presente) | giro 2 | jack staccati **10,7 ms** dopo; `MUTE_REQ` giù all'interruzione; **K501 aperto 102,9 ms** dopo e fino alla fine; GUASTO, `MUTE_CMD` mai più |

**I falsi sul circuito** (`falsi/seq_falso*.txt`):
- **falso 6** (`MUTE_G_IN` ignorato) nel guasto: `MUTE_REQ` giù **1,3 ms** dopo `MUTE_G_IN`
  contro ≤ 1 ms. Fallisce il criterio `n`, e solo quello;
- **falso 9** (la rete staccata senza i 50 ms) nello spegnimento: K501 aperto **15,6 ms prima**
  del rilascio di `PERMIT_CMD`. Fallisce il criterio `j`, e solo quello.

**Le regressioni**: `run_tests.sh` 12 su 12 (il 2k per la prima volta nella suite); `psu.py`
rigenerato dà la stessa netlist (cambia solo la data); il deck V2 rigenerato (`--matrice
sorgente`) è byte-identico.

## 5. Quello che resta aperto

- **`src/main_attiny.c`**, l'adattatore verso i registri: non scritto (il mandato lo chiedeva
  solo se restava tempo). Senza `avr-gcc`, che non va installato in questo lotto, non si
  compilerebbe comunque. Serve prima della programmazione.
- **Da provare sulla scheda**: una conversione su AIN2 con la SPI attiva contro una a SPI spenta
  (§ 2 della specifica).
- **Il banco in temperatura**: le sequenze girano a 25 °C (`t_c` del core e `.options temp`). La
  legge in temperatura è provata sull'host e sul banco in continua, non nei transitori.
- **NC-036** resta aperta e bloccante per G2: manca **L41c**, il banco di L30 col circuito vero,
  e la decisione sul corto dell'uscita di U503 (~90 dB SPL di picco a 1 m, sotto il tetto).
- **NC-037** resta aperta (il giro BOM di T2, G2).

## 6. Cosa cambia nel repo

- `firmware/preamp_timer/`: `src/timer_core.{c,h}`, `test/` (`test_sequenze.c`, `test_legge.c`,
  `mondo.{c,h}`, `ponte.c`, `run_host_tests.sh`), la specifica aggiornata;
- `scripts/run_tests.sh`: il blocco 2k;
- `docs/preamp/decisions/ADR-050-cima-ldr-12-ma.md`;
- `docs/preamp/data/2026-09-26/L41b2/` coi dati e il README;
- `docs/limitations.md`: la #35;
- `NONCOMPLIANCE.md`: NC-038 chiusa, NC-036 aggiornata.
