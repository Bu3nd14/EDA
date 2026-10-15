# L60b — il rivelatore esce, J1 a sette pin, il moltiplicatore in SOT-223

Data: 2026-10-15 · Lotto: L60b (seconda parte di L60, diviso dall'utente all'inizio: «Tre parti»)
Decisioni: **ADR-081** (il rivelatore esce), **ADR-082** punti 2 e 4, **ADR-083** (nuova).

## In breve

- **Il rivelatore di continua è uscito dal progetto, da sorgente unica.** Le netlist rigenerate sono,
  parte per parte e pin per pin, quelle di prima di L45d2b1 (`ab6c22f0`), salvo J1 e i moltiplicatori
  di Vbe: la scheda audio **490 parti** (583 con il rivelatore), l'alimentatore **118** (124).
- **J1 a sette pin** (ADR-083, «Due pin di massa»): 1–2 `VPLUS`, 3–4 `GND`, 5–6 `VMINUS`, 7 `VRELAY`.
  **J4 di nuovo a tre** («Torna a tre pin»).
- **Q127 in SOT-223**: DZT5551, lo stesso die e lo stesso modello del MMBT5551 (ADR-082 punto 4).
  Cambia in tutti e otto i blocchi (Q127, Q226, Q327, Q426, Q526, Q626, Q726, Q826).
- **NC-064…NC-068 chiuse per superamento**; NC-042 avanza. **19 voci aperte, 2 bloccanti** (NC-062
  per G1, NC-044 per G2).
- `run_tests.sh` **13 passed / 0 failed**, firmware **19 falsi su 19**.

## 1. Il metodo: il ripristino, non una riscrittura

Dal commit prima di L45d2b1 (`ab6c22f0`, L45d2a) a `main` prima di questo lotto, i file di codice
sono cambiati **solo** per il rivelatore: il diff letto per intero (sorgenti, firmware, spec, test,
script, disegni) non contiene altro. Le 14 versioni di allora sono state ripristinate, e sopra di
esse le note storiche nello stile del repo («PA1 read the DC detector's line in L45d2b1 only»), più
le modifiche nuove di J1 e Q127.

| Uscito | Dove |
|---|---|
| `dc_detector.py` e `spice/preamp/dc_detector.subckt` | eliminati (nessun deck fuori da `data/` li includeva) |
| la rete `DC_FLT`, J4 pin 4, `fouts`, la chiamata del rivelatore | `preamp_audio.py` |
| R548, C535, D525–D527, R549, `DC_FLT_IN`; PA1 di nuovo libero | `psu.py` |
| `T_DC_PERSIST_US`, `dc_flt_in`, `t_dc`, la logica e PA1 fra i liberi | `timer_core.h`, `timer_core.c` |
| § 4.9, le righe di L45d2b1; la nota di L60b in testa | `spec/timer_spec.md` |
| `guasto_dc`, `dc_trip`, la nona colonna di `ponte.c`, i falsi 31–34 | `test/` |
| J4 pin 4 nel contratto; i 23 falsi | `check_psu_harness.py`, `run_tests.sh` |
| gli asserti e le didascalie del rivelatore; un asserto nuovo che non torni | i due `*_blocks_draw.py` |

Il rivelatore della **rete** (`ADC_MD`, la spec ~:142, :148, `psu_blocks_draw.py`:183) non c'entra
ed è rimasto.

## 2. Le netlist contro quelle di prima del rivelatore

`data/2026-10-15/L60b/confronto_netlist.py` (il parser di `check_psu_harness.py`; le due versioni
vecchie estratte dalla storia del repository in una cartella temporanea, i percorsi sono quelli
della sessione) confronta le tre versioni: prima di L45d2b1, `main`, L60b. L'uscita è
`confronto_netlist.txt`.

| | prima di L45d2b1 | `main` (con il rivelatore) | L60b |
|---|---|---|---|
| scheda audio, parti | 490 | 583 | **490** |
| alimentatore, parti | 118 | 124 | **118** |

Differenze di L60b contro prima di L45d2b1:
- **parti in più o in meno**: nessuna, sulle due schede;
- **valori**: J1 (`Conn_01x07`), e Q127, Q226, Q327, Q426, Q526, Q626, Q726, Q826 da `MMBT5551` a
  `DZT5551`;
- **pin**: J1 2…7 come ADR-083, sulle due schede;
- **un nome**: la rete fusa del canale destro che entra nei buffer delle fisse si chiama `F1R_IN`
  invece di `F2R_IN`, con gli stessi nove pin (C337, K7, R334–R336, R708, R808, R911). È il nome
  instabile delle reti fuse (limitations #23, il commento di `channel()`); la connettività non cambia;
- **nessuna rete** con `DC_` o `DET` nel nome resta, salvo le `ADC_*` del micro.

`spice/preamp/gain_block.subckt` rigenerato è **identico** a prima: il modello di Q127 resta MMBT5551.
Cambia solo `gain_block.net` (valore e impronta).

## 3. L'ERC dell'alimentatore

Letto dall'esecuzione di `psu.py`: **24 avvisi e i 2 «errori» noti** (le due uscite di ciascun
TPS7A4701 unite). I non collegati del micro sono di nuovo PA1, PA2, PA3, PA4, PB4 e PC3. Il commento
in `psu.py` dice 24 e lo data a L60b.

## 4. J1 a sette pin e il controllo del cablaggio

`check_psu_harness.py` porta il contratto a sette pin e lo verifica sulle due schede.
`data/2026-10-15/L60b/falsi/falsi.py` lo prova su copie sabotate delle due netlist, un pin alla
volta (`verdetti.txt`):

| | Sabotaggio | Esito |
|---|---|---|
| — | la coppia intatta | exit 0 |
| s01–s03 | scheda audio: J1 pin 2, 4, 6 aperti (un filo di ciascuna coppia) | exit 1 |
| s04–s06 | alimentatore: J1 pin 1, 3, 5 aperti | exit 1 |
| s07 | scheda audio: J1 pin 2 su `VMINUS` | exit 1 |
| s08 | alimentatore: J1 pin 6 su `VPLUS` | exit 1 |
| s09 | alimentatore: J1 pin 7 su `GND` (`VRELAY` persa) | exit 1 |

9 su 9 presi. Il disegno dell'alimentatore asserisce i sette pin e che `DC_FLT` e J4 pin 4 non
esistano; quello della scheda audio che `DC_FLT` non esista.

**Che cosa non è provato qui**: che un filo aperto di una coppia non tocchi più la Stax. È una prova
di L60c (ADR-082, Conseguenze: «il filo del rail con un solo pin dei due aperto»).

## 5. Q127 in SOT-223

`gain_block.py`: `Q("npn", "DZT5551", "MMBT5551", NX, NBB, NY, fp=FP_SOT223)`, come Q125 (ADR-068).
Il commento sull'accoppiamento termico (ADR-034) è riscritto: con R126 in corto 0,49 W per sempre,
~231 °C in SOT-23 e ~88 °C (27 °C d'aria) / ~121 °C (60 °C d'aria) sulla piazzola minima, sotto i
125 °C di P7; la linguetta è il collettore, NX, non un rail, quindi l'accoppiamento in rame col
MJE15032 senza contatto galvanico resta possibile e ha una piazzola grande su cui lavorare. I numeri
sono quelli di L60a / ADR-082 (125 °C/W, la stessa ipotesi dichiarata di Q125), non rimisurati.

## 6. La suite

`run_tests.sh` dal worktree: **13 passed / 0 failed**. `validate_models.py` 59/59; 2d (il disegno del
blocco contro la netlist) passa; 2e passa; 2j (il cablaggio) passa sui sette pin; 2f rigenera i due
disegni coi loro asserti; 2g, 2h, 2i passano sui deck; 2k: test sull'host passano e **19 falsi su
19** fanno fallire il loro test.

## 7. Per L60c

Il condensatore da 1 µF della Stax dopo K3, la geometria del mute su quell'uscita, e le prove: E9,
P10 col carico della Stax (i guasti di K3 sul NO e sul comune, 10 Ω e 1 kΩ; il filo del rail con un
pin dei due aperto), V2, l'inserimento a caldo. Il valore di `CFIX2` non è stato toccato qui.
