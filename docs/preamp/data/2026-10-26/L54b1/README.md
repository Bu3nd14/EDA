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

### Gli esiti

`lista_noto.txt`, 34 corse con `corri_lista_an.sh … 5`: 34 pulite, nessun ripiego del metodo.

- **Sequenza** (`an_sorgente.csv` contro `an_comparatori.csv` di L54a, `confronta_noto_seq.txt`):
  21 righe su 24 uguali in tutto, ogni istante a +0,00 ms. Le altre tre (perdita, buco20, buco200 a
  rete −10 %) hanno lo stesso verdetto e il guadagno a **55,4 ms invece di 55,5**: 0,1 ms, fuori dal
  limite di 0,05 ms che avevo scritto. **Il limite era sotto la risoluzione del banco**: i deck
  scrivono le forme d'onda su una griglia di 100 µs (`tran 100u` + `linearize`), e 0,1 ms è un
  campione. Provato su una griglia di 10 µs (`fine/`, `corri.sh`: lo stesso deck salvo `tran 10u`),
  il deck di L54a sulla netlist di prima e quello del sorgente danno **gli stessi istanti**: jack 17,31
  / 17,31 ms, guadagno 55,4 / 55,4, K501 162,13 / 162,14 (`fine/an_fine.csv`). La differenza è della
  corsa di L54a, non del circuito.
- **Guasti** (`an_fmea_sorgente.csv` contro le prime 7 righe di `an_fmea.csv`,
  `confronta_noto_fmea.txt`): 7 su 7 uguali, ogni istante a +0,00 ms.
- **Energie** (`energia.py`): R550 7,651 / 9,347 J nel corto davanti al regolatore + (L54a 7,65 /
  9,35), R552 0,473 / 0,539 J con la bobina di K501 in corto (L54a 0,47 / 0,54).
- **Standby** (`potenza_t2.py`, 2,5–3,0 s): **116,14 / 130,08 / 144,21 mW** a rete −10 / 0 / +10 %,
  contro 116,7 / 130,1 / 145,1 del README di L54a: −0,48 / −0,02 / **−0,61 %**, l'ultimo fuori dallo
  0,5 %. Il deck di L54a stesso, rifatto oggi sulla netlist di prima (`lista_consumo_l54a.txt`), dà
  **116,14 / 130,08 / 144,21 mW**, gli stessi del sorgente: a non tornare sono le due cifre a ±10 %
  stampate da L54a (e riportate nella tabella di ADR-102), di al più 0,9 mW — presumibilmente da una
  corsa prima della sua ultima correzione. Nessuna decisione ne dipende (il limite è 0,5 W); **le cifre
  di partenza per lo standby sono 116,1 / 130,1 / 144,2 mW**.
- Il controfattuale senza Δ (`cf_nodelta`) fallisce come in L54a (C3 = 0, il guadagno a 14,5 ms prima
  del jack a 17,4).

Il caso noto torna: il temporizzatore del sorgente è quello del banco di L54a.

## Rifare

```sh
/usr/bin/python3 -I <L>/confronta_timer.py <L>/../../2026-10-25/L54a/psu/genera_tb_psu.py circuits/preamp/psu.net
/usr/bin/python3 -I <L>/falsi/falsi.py circuits/preamp/preamp_audio.net circuits/preamp/psu.net
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_noto.txt 5
/bin/zsh <L>/psu/corri_lista_an.sh <L>/lista_consumo_l54a.txt 3
/usr/bin/python3 -I <L>/psu/analizza_an.py --te=3.0 <L>/an_sorgente.csv <L>/seq/sorgente/<caso> ...
/usr/bin/python3 -I <L>/confronta_noto.py <L>/../../2026-10-25/L54a/an_comparatori.csv <L>/an_sorgente.csv
/usr/bin/python3 -I <L>/confronta_noto.py <L>/../../2026-10-25/L54a/an_fmea.csv <L>/an_fmea_sorgente.csv 7
/usr/bin/python3 -I <L>/psu/energia.py 3.0 <L>/seq/fmea_sorgente/f_c509_corto_mus/*_g1_out.txt ...
/usr/bin/python3 -I <L>/psu/potenza_t2.py <L>/seq/consumo_sorgente/accensione/*_g1_out.txt 2.5 3.0
```

Le forme d'onda (`*_out.txt`) non stanno nel repository: si rifanno.
