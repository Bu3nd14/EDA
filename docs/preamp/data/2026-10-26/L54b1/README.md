# L54b1 — il temporizzatore a comparatori nel sorgente (2026-10-26)

Prima parte di **L54b** (diviso dall'utente all'inizio, «Tre parti»: L54b1 il sorgente, i guardiani,
i disegni e il banco sul sorgente col suo caso noto; L54b2 il modello del costruttore dei
comparatori, lo standby e la catena al jack; L54b3 la robustezza al banco). Decisione di riferimento
**ADR-102**. `<L>` = questa cartella. Python di analisi con `/usr/bin/python3 -I`.

## Il sorgente

`circuits/preamp/psu.py`: il temporizzatore di `TIMER_AN` (L54a, `../../2026-10-25/L54a/psu/
genera_tb_psu.py`) con gli stessi valori; fuori U509, C534, J515, R543–R547. Il TLV1704 non è nella
libreria di KiCad: il simbolo LM339, piedino per piedino il PW del TLV1704 (SBOS589D p. 5, letto dal
PDF in `vendor/comparator/ti/TLV1702/`). AT_ON del banco è la rete VRELAY_EN (il banco le univa con
1 Ω, `RATve`, solo per sondarle).

I riferimenti nuovi stanno su numeri mai usati sulla scheda (`riferimenti_storici.py`, su ogni
versione di `psu.net` in git): U513–U515, C545–C555, R569–R584, D533–D541, Q513 / Q514. C537,
C538, C541, C542, R556, R560–R568, Q507, Q508 erano del pilota delle LDR (fino a L47c1).

- `confronta_timer.py` → `confronta_timer.txt`: **il caso noto strutturale**, ogni elemento di
  `TIMER_AN` (senza `RATve`) contro la sua parte in `psu.net`: 47 / 47, niente spaiato. Fatto
  fallire con R571 a 680k (il valore che L54a aveva scartato).
- `nomi_reti.txt` (`../../2026-10-22/L45d2b3b1/script/nomi_reti.py`, limitations #74): prima
  (`psu_prima.net`) e dopo, per insiemi di piedini, senza le parti tolte e quelle nuove: **0 reti
  coi piedini cambiati**. I sei «nomi cambiati» sono le reti del micro (UPDI, MUTE_G_IN, ADC_*) che
  senza le sue parti restano vuote, e lo script le appaia a un'altra rete vuota: non sono cambi.
- ERC: 19 avvisi (erano 23: −6 piedini liberi e −1 massa del micro, +3 masse dei TLV1704), gli
  stessi 2 «errori» noti.

## I guardiani e i loro falsi

`scripts/check_relay_safe_state.py --timer` riscritto (T0 nessun micro e comparatori noti, T2
richieste open-drain con pull-down e nessun'altra alimentazione, T6 la ritenuta a tiristore; T1,
T3–T5 come prima); `scripts/check_psu_harness.py`: le richieste da uscite di comparatore.
`falsi/falsi.py` → `falsi/verdetti.txt`: 2 buoni passano, 23 sabotaggi falliscono ognuno per la sua
regola.

## Il banco sul sorgente

`psu/` è il banco di L54a, copiato, con `carico.txt` di L54a. `genera_tb_psu.py` esteso:
`--timer sorgente` prende il temporizzatore dalla netlist (LM339 → quattro `CMPOD`, gli stessi di
`TIMER_AN`) e rifiuta una netlist col micro; le tre modalità di L54a rifiutano una netlist col
temporizzatore (gli aggiungerebbero `TIMER_AN`). Coi vecchi argomenti e `psu_prima.net` il deck è
**byte per byte** quello del generatore di L54a (provato su `cf_nodelta`, che tocca il codice
cambiato). Il deck del sorgente differisce da quello di L54a solo dove deve: le righe del
temporizzatore rinominate una per una, i piedini del micro (1 GΩ, assorbimento 0) e R543–R547 (verso
1 GΩ) via, C534 al posto di C545–C547 (+200 nF su V5), `RATve` via, le sonde del micro via.

**Attenzione**: il generatore di L54a, senza `--net`, legge oggi la netlist nuova: per rifare L54a
serve `--net <L>/psu_prima.net`.

### Il caso noto numerico: i criteri, scritti prima delle corse

Le corse di L54a coi comparatori (`an_comparatori.csv`: 24 casi di sequenza; `an_fmea.csv`: i 7 casi
di guasto coi comparatori; le energie di `energia.py`; lo standby di `potenza_t2.py`), rifatte con
`--timer sorgente` e gli stessi argomenti, devono dare:

- gli stessi verdetti: `C2`, `C3`, `r41`, `s41`, `musica_TE`, `mus_end`, `k501_end`, `esito`;
- ogni istante (`t_jack_ms`, `t_gain_ms`, `t_v106_ms`, `t_k501_ms`, `t_mus_ms`) entro
  **max(0,05 ms; 0,1 %)** di quello di L54a; `vplus_end` entro 0,01 V;
- le energie di R550 e R552 entro lo **0,5 %**; lo standby entro lo **0,5 %**;
- il controfattuale senza Δ (`cf_nodelta`) fallisce come in L54a.

Una differenza fuori da questi limiti si spiega col circuito (i 200 nF su V5, il micro tolto), non
si accetta.
