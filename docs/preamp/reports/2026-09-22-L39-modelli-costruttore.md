# L39 — Fase 4: i modelli del costruttore nel progetto (2026-09-22)

Lotto **L39**. **Chiude NC-017**, **apre NC-034** (bloccante) e **NC-035**; aggiorna
NC-004, NC-024 e NC-025. Dati: `data/2026-09-22/L39/`. Nessuna ADR nuova: nessun
valore del circuito cambia.

**In breve.**
- Il sorgente e i 25 deck simulano i sette modelli del costruttore di `models/`. Nel
  blocco generato cambiano **solo i nomi dei modelli**, su 12 righe (§2).
- Rispetto ai segnaposto reggono E2, E3, E4, E5, V3, P7, la classe A, il V2 dei relè e
  il V2 del mute (§4).
- **V1 cade** su ogni istanza a guadagno unitario, di 4,5–5 gradi sotto i 60: blocco B
  a 0 dB **55,55°**, blocco A **57,93°**, buffer **54,92°** (§4.2) → **NC-034**.
- La **corrente di riposo d'uscita** sale da 14,6 a **20,4 mA**, perché i MJE veri hanno
  una Vbe più bassa (§4.1) → **NC-035**.
- **Dall'utente**: il margine di fase prima della banda. Si può ridurre la banda
  passante, oppure alzare il guadagno minimo fino a +1,5 dB (§5). La correzione è di
  **L40**, prima di L29c.

**Provenienza dei modelli, dopo L39.** LSK489A (Linear Systems, trascritto: esemplare
d'angolo, I_DSS 2,59 mA, sotto la finestra del gruppo B che il progetto compra,
ADR-031); MMBT5551 e MMBT5401 (Diodes Inc.); LS350 per l'LS352 (Linear Systems);
Qmje15032 e Qmje15033 (onsemi, generati da terzi con MODPEX); D1N914 per l'1N4148 DO-35
(onsemi, limitations #20). **Solo l'LSK489A porta KF**, quindi c'è rumore 1/f sulla
coppia d'ingresso e in nessun altro punto. **Nessun modello porta la dispersione.**
Scarti già a registro rispetto ai propri datasheet: NC-020 (f_T dell'LS352), NC-024
(h_FE del MJE15032), NC-025 (f_T dei due MJE).

## 1. La mappa segnaposto → costruttore

| Segnaposto | Modello | File | Parte | Cosa il modello non ha, o non rispetta |
|---|---|---|---|---|
| `LSK489X` | `LSK489A` | `models/jfet/lsk489.lib` | LSK489 **gruppo B** | esemplare d'angolo A (ADR-031); ha KF; `isr`, `alpha`, `vk`, `mj` ignorati da ngspice |
| `NSS2N5551` | `MMBT5551` | `models/bjt_npn/mmbt5551.lib` | MMBT5551, SOT-23 (ADR-017) | niente KF; parametri `QUASIMOD` |
| `PSS2N5401` | `MMBT5401` | `models/bjt_pnp/mmbt5401.lib` | MMBT5401, SOT-23 | niente KF |
| `NMJE15032` | `Qmje15032` | `models/bjt_npn/mje15032.lib` | MJE15032 | niente KF; NC-024, NC-025 |
| `PMJE15033` | `Qmje15033` | `models/bjt_pnp/mje15033.lib` | MJE15033 | niente KF; NC-025; nessuna pagina prodotto (T8) |
| `D1N4148` | `D1N914` | `models/diodes/1n4148.lib` | 1N4148 DO-35 | #20: è il documento 1N914 di onsemi, *Package: DO-35*; l'URL `1n4148.lib` serve il `1N4148WT` SOD-323 |
| `PTHAT320` | — | — | — | non più istanziato da L22 (LS352, `LS350`) |

**Il D1N914 è capito prima di usarlo** (#17, #20). L'intestazione di
`models/diodes/1n4148.lib` e la sua provenienza lo dicono: onsemi scheda l'1N4148 sotto
il datasheet `1n914-d.pdf`, e il file che *sembra* giusto contiene un'altra parte. Il
nome del modello resta quello del costruttore, e il sorgente lo commenta.

## 2. La sostituzione

**Sorgente**, `circuits/preamp/gain_block.py`, con un commento ADR su ogni scelta:
- `Q()`: `MMBT5551` (×6), `MMBT5401`, `Qmje15032`, `Qmje15033`. I valori da 2N a MMBT,
  il footprint di default SOT-23 (`FP_SOT23`, ADR-017). `FP_TO92` non serve più;
- `D()`: `D1N914`, commento #20;
- JFET: `LSK489A`, commento ADR-013 e ADR-031;
- l'intestazione del `.subckt` elenca i file di `models/`; il blocco «SIMULATED
  RESULTS» porta le cifre di L39.

`spice_export.py` non cambia: passa il nome com'è. `preamp_audio.py` e `trim.py` non
nominano modelli.

**Rigenerati** `gain_block.subckt`, `gain_block_flat.inc`, `gain_block.net` e
`preamp_audio.net`. **Nel blocco cambiano solo i nomi dei modelli, su 12 righe**:
nessun nodo, nessun valore. La copia di prima sta in `prima/gain_block_flat_L29b2.inc`
e `prima/gain_block_L29b2.subckt`. È la prova che la topologia è identica.

**Il derivato di L20 è ritirato.** Con `LSK489A` nel sorgente,
`derive_jfet_variant.py` non trova righe `LSK489X` ed esce 2.
`spice/preamp/derived/gain_block_flat_lsk489a.inc` è rimosso; `tb_idss_loop.cir` e
`tb_idss_op_noise.cir` includono il blocco generato e tengono le loro varianti
`altermod`. Lo script resta, annotato: i dati di L20 lo citano.

**I deck.** `script/porta_deck.py` fa le parti meccaniche e conta ogni sostituzione;
si ferma se un testo atteso manca:
- la riga dei segnaposto diventa sei `.include` diretti. Devono essere diretti:
  `provenance()` non segue gli include annidati;
- il blocco di commento L22/L33 (13 deck) e il «PROVVISORIO SUI MODELLI» (4 deck)
  sono riscritti.

A mano, dieci frasi in otto deck che il 2h non vede perché non nominano una parte
(«Models are PLACEHOLDERS», «KF = 0 on every model»). A parte:
- `tb_v2_mute_ldr.cir` è generato: si è cambiata una riga d'intestazione nel suo
  generatore di L29b2, annotata, e si è rigenerato. La differenza sta tutta in
  intestazione e include;
- `build_dossier.PART` conosce i nomi nuovi: senza, il 2h cadeva per la ragione
  sbagliata, come in L20.

**`placeholder_devices.lib` resta** (58 file datati lo includono), con in testa una
nota: ritirato.

## 3. I guardiani

- **2h**: 25 deck, nessuna affermazione contraddetta.
- **2i nuovo**, `scripts/check_no_placeholders.py`: nessun deck canonico include la
  libreria dei segnaposto, e nessuna riga di dispositivo, né nei blocchi generati né
  nei deck, nomina un modello definito in essa (i nomi sono letti dalla libreria).
  Fatto cadere:
  - sul `main` di prima: **49 violazioni**;
  - su 8 casi (`script/sabotaggi_2i.sh`, `sabotaggi/esiti.txt`): copia intatta 0;
    include nel deck, nome nel blocco, nome nel `.subckt`, riga nel deck, include
    maiuscolo → 1; un commento → 0; libreria assente → 2. **8 su 8 come attesi.**
- `run_tests.sh` **10 passed / 0 failed**; `validate_models.py` 48/48.
- Nessun log di `dopo/` ha righe `Error`, e tutti escono con rc 0. Il blocco A coi
  modelli veri fallisce il gmin stepping (132 avvisi contro 0) e converge per source
  stepping in tutte e 50 le analisi. Lo annoto: ngspice ci arriva, ma con più fatica.

## 4. La regressione, prima e dopo

Stessa sessione, stessa macchina, stessi deck: `prima/` è il `main` di L29b2 sui
segnaposto, `dopo/` è L39. Il confronto grezzo di ogni cifra stampata o tabellata sta
in `confronto_grezzo.csv` (28 067 cifre; le 65 presenti da una parte sola sono
artefatti del parser, controllati); i riassunti in `margini.csv` e negli script
`margini.py`, `p7.py`, `classe_a.py`, `v3.py`.

| Cifra | Soglia | Prima | Dopo | Esito |
|---|---|---|---|---|
| I_q uscita (Q132/Q133) | ~15 mA di progetto | 14,56 mA | **20,29 / 20,40 mA** | **NC-035** |
| coda / VAS | — | 4,374 / 6,443 mA | 4,520 / 6,797 mA | — |
| offset blocco B (ADR-030) | nessuna soglia (L29c) | −16,58 mV | **−15,45 mV** | — |
| classe A, percorso ascoltabile (`tb_blockA_carichi` F2) | 36/36 | 36/36, min 14,5 mA | 36/36, min 20,2 mA | regge |
| classe A, `tb_mute_corto` caso 0 | tutte | 104/104 | 104/104 | regge |
| **V1 blocco B 0 dB** | ≥ 60° | 61,80° | **55,55°** | **NC-034** |
| V1 blocco B +3 dB | ≥ 60° | 69,77° | 63,90° | regge |
| V1 blocco B +10 dB | ≥ 60° | 102,98° | 100,19° | regge |
| **V1 blocco A** (≤ 1 nF) | ≥ 60° | 63,36° | **57,93°** | **NC-034** |
| **V1 buffer** | ≥ 60° | 61,63° | **54,92°** | **NC-034** |
| V1 gruppo B (8,0/11,5/15 mA) | ≥ 60° | 62,71–62,80° | 55,76–55,87° | NC-034; dispersione ≤ 0,3° |
| guadagno d'anello a 10 Hz | ~72 dB (#24) | 72,40 dB | 81,42 dB | controllo del #24 ricalibrato |
| E2 +3 dB / +10 dB a 1 kHz | ±0,1 dB / 9,5–10,5 | 3,0371 / 9,9545 dB | 3,0393 / 9,9591 dB | regge |
| banda −3 dB a 0 dB | — | 2,12 MHz | 2,45 MHz | — |
| E3 peggiore | ≥ 100 kΩ | 111,58 kΩ | 110,71 kΩ | regge |
| E4 Re(Z) max principale / fisse | < 100 Ω | 60,05 / 53,13 Ω | 60,04 / 53,12 Ω | regge |
| E5 peggiore (`tb_e3_e5_ldr`) | ≤ 9,95 µV | 4,957 µV | **5,050 µV** | regge; pavimento (1/f solo sul JFET) |
| E5, i cinque casi di `tb_noise_breakdown` | ≤ 9,95 µV | 1,157…4,229 µV | 1,176…4,283 µV | regge |
| PSRR da V+, 0 dB, 100 Hz / 1 kHz / 10 kHz | — | 72,1 / 59,6 / 39,8 dB | 78,0 / 59,5 / 39,5 dB | — |
| PSRR da V−, 100 kHz | — | 71,1 dB | 62,1 dB | — (≥ 53 dB ovunque) |
| V3: clip, recupero entro 5 %, DC al jack | recupera, niente latch | +13,26/−13,78 V, 1,21 µs, +2,8 mV | +13,23/−13,79 V, 1,07 µs, +3,2 mV | regge |
| P7: MJE peggiore / MMBT peggiore | 1,04 W / 310 mW | 0,348 / 0,087 W | 0,362 / 0,093 W | regge |
| V2 relè, inviluppo | la banda di +10 dB | +1,522 / −1,626 V | +1,526 / −1,624 V | regge |
| V2 controfattuale (relè su R_f) | la prova che ADR-004 serve | −13,77 V | −13,87 V | come prima |
| V2 mute, 1 kHz 100 k principale: S ins / rel | ≤ 20 dB in 100 ms | 7,163 / 5,32 dB | 7,163 / 5,32 dB | regge |
| V2 mute: A senza segnale | ≤ 100 µV | ≤ 3,90 µV | ≤ 3,75 µV | regge |
| V2 mute: B2 | ≤ 100 µV | 0,285 µV | 0,327 µV | regge |
| **fondo di distorsione della catena** (C_pav, `mai`, principale) | diagnostica | **0,962 mV** | **0,267 mV** | −3,6× |
| C2 ev ins / rel (principale) | diagnostica (ADR-040) | 2,51 / 1,47 mV | 2,14 / 1,04 mV | — |

### 4.1 La corrente di riposo

La Vbe dei MJE veri, a 20 mA, vale **0,566 / 0,539 V**; il segnaposto dava 0,662. Il
moltiplicatore di Vbe tiene la stessa tensione fra le basi, quindi la stessa tensione
cade su meno Vbe e più resistenze d'emettitore. Il sorgente lo aveva previsto (1,69k
«MUST be re-swept when the vendor MJE15032/33 and 2N5551 models arrive»). Risweepato
con `tb_bias_sweep.cir`:

| R (NX–NBB) | 1,50k | 1,60k | 1,65k | **1,69k** | 1,74k | 1,78k | 1,87k |
|---|---|---|---|---|---|---|---|
| prima | 11,66 | 13,18 | 13,94 | **14,56** | 15,33 | 15,95 | 17,34 mA |
| dopo | 17,28 | 18,86 | 19,65 | **20,29** | 21,09 | 21,73 | 23,17 mA |

I 14,7 mA di progetto stanno **sotto 1,5 kΩ**, fuori dallo sweep. Il valore non è
stato toccato: è un valore select-on-test, e la corrente di riposo è una decisione
(dissipazione di NC-029, budget dell'alimentatore, poli dello stadio d'uscita).

### 4.2 V1

La caduta è di 5,5–7° su ogni istanza a guadagno unitario, e più piccola a +3 e +10 dB,
dove il guadagno d'anello è minore. Il guadagno d'anello a bassa frequenza sale di 9 dB
(la VAF dei MMBT è 288/360 V contro 100/80 dei segnaposto); il crossover a 0 dB resta
intorno a 0,89 MHz; i poli non dominanti sono più bassi (f_T dei MJE sotto il minimo,
NC-025; CJE 57 pF del MMBT5551 contro 12 pF). Quale dei due pesi di più **non è stato
separato**: è di L40.

**Esplorazione, nessun valore cambiato** (`esplorazione/`, `script/esplora_compensazione.py`,
`riassumi_comp.py`). Sul blocco B, 0 e +10 dB, 100 k e 10 k, 1 mΩ e 2,611 kΩ, cavo al
jack 1 fF–4,7 nF. La coppia (330p, 470p) ridà 55,55°, la cella di `dopo/tb_loop`, e la
`print` finale conferma che gli `alter` colpiscono C137 e C124:

| C_f (C137) | Miller (C124) | minimo 0 dB | crossover a vuoto | minimo +10 dB |
|---|---|---|---|---|
| 330p | 470p | 55,55° | 889 kHz | 100,19° |
| 1n | 470p | 54,83° | 941 kHz | 70,34° |
| 330p | 680p | 59,26° | 622 kHz | 100,26° |
| **330p** | **820p** | **60,70°** | **520 kHz** | 98,59° |
| 330p | 1n | 62,08° | 430 kHz | 96,66° |

**C_f non aiuta a 0 dB**: con R_g aperta la controreazione è già totale, e C_f in
parallelo a R_f non la cambia. Aiuta solo a +10 dB, che non ne ha bisogno. **Il Miller
aiuta**, a prezzo di banda e di slew rate. Non misurato qui: blocco A e buffer col
Miller nuovo, slew rate, V3, la risposta a 20 kHz, THD di modello.

### 4.3 Il gruppo B

`tb_idss_*` gira ora sul blocco generato. Le varianti `altermod` (b_min, b_tip, b_max)
danno V1 55,76–55,87° ed E5 del caso D 4,286–4,288 µV. La dispersione del gruppo B su V1
resta ≤ 0,3°, come in ADR-031. **ADR-031 «da riaprire se» scatta**: la Fase 4 porta un
minimo di V1 **sotto** i 60°, non solo entro 0,5°. La rimisura della dispersione col
buffer e col blocco A è di L40, sul circuito corretto.

## 5. La decisione dell'utente, e perché il lotto si ferma qui

Il prompt diceva: se una cifra richiede una modifica di topologia, fermati e dillo.
Una compensazione nuova è un valore, non una topologia; alzare il guadagno minimo
tocca invece la rete di controreazione di tutte le istanze a guadagno unitario. In
entrambi i casi decide l'utente. Domanda posta a metà lotto, coi numeri del §4.2.

**Risposta dell'utente (2026-09-22)**: «non sono convinto che ci serva quasi un
megaherz di banda passante a 0 dB, preferisco rispettare i margini di fase e ridurre la
banda passante o alzare il guadagno fino a 1,5 dB».

E su NC-017: «chiudila, V1 va in NC nuova».

Il lotto non applica la correzione. La direzione diventa una ADR e un valore scelto e
misurato in **L40**, con la regressione di L39 rifatta sul circuito nuovo. Applicarla
qui avrebbe messo nel sorgente un valore scelto su un'esplorazione di un solo blocco.
L29c, il caso peggiore di V2, viene dopo L40: misurarlo su un circuito che cambierà
compensazione vorrebbe dire rifarlo.

## 6. Cosa non è stato fatto

- Nessun valore del circuito è cambiato: né il Miller, né C_f, né il moltiplicatore.
- La THD del `.four` di V3 è ora una cifra di modello, non una misura; non entra in V4.
- 27 °C soltanto, come ogni deck del repo.
- Il dossier non è rigenerato: resta fuori dal lotto.
