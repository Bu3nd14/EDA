# L40 — V1 coi modelli del costruttore (2026-09-23)

**Chiude NC-034 e NC-035. Aggiorna NC-025 e NC-029. ADR nuova: ADR-042.**

- **Dati**: `data/2026-09-23/L40/`, con un README che dice cosa c'è in ogni cartella.
- **Esplorazione, Fase A**: deck versionati con righe `alter` in testa al `.control`,
  e ogni famiglia di varianti ha un controllo che ridà L39/dopo.
- **Regressione, Fase B**: `prima/` è il `main` di L39 (C124 470 p) e `dopo/` è L40
  (C124 1 nF). Stessi deck, stessa sessione.

## 1. Perché è caduto V1

In L39, coi modelli del costruttore, V1 è sceso di 5,5–7° su ogni istanza a
guadagno unitario, e nessuno sapeva ancora quale modello pesasse di più. Qui si
rimette **una famiglia alla volta** al suo segnaposto di prima di L39, con gli
stessi parametri ma sotto il nome del costruttore, così il blocco generato non
cambia. Si misura sulla cella del minimo: blocco B, 0 dB, 2,611 kΩ, cavo al jack.
Script: `cause/` (`separa_cause.py`) e `mje/` (`separa_mje.py`).

| Variante | V1 min | T a 10 Hz | I_q |
|---|---|---|---|
| tutto costruttore (= L39/dopo) | 55,55° | 81,42 dB | 20,29 mA |
| JFET al segnaposto | 54,47° | 81,77 dB | 20,29 |
| MMBT5551/5401 al segnaposto | 55,64° | **70,91 dB** | 19,86 |
| diodo al segnaposto | 55,92° | 81,71 dB | 20,10 |
| **MJE al segnaposto** | **62,02°** | 83,85 dB | 15,17 |
| tutto al segnaposto (= L39/prima) | **61,80°** | **72,40 dB** | **14,56** |

- **Controlli**: le due righe estreme ridanno L39 cifra per cifra.
- **Lo specchio** (LS350) non è una famiglia: era già il modello del costruttore
  prima di L39. Il primo tentativo lo includeva, e il controllo dava 62,05° invece
  di 61,80°. È così che l'errore si è visto.
- **La VAF dei MMBT** spiega da sola i 9 dB di guadagno d'anello in più (70,9 contro
  81,4 dB), ma non il margine.

Dentro i MJE, una grandezza alla volta con `altermod`. Ogni variante riparte dai
valori pubblicati, stampa `showmod`, e una variante «ritorno» ridà la prima cella
per cella (#29):

| MJE, cambiato rispetto al pubblicato | V1 min |
|---|---|
| niente | 55,55° |
| **CJE/CJC al segnaposto** (300 p / 100–120 p invece di 3,06 nF / 0,30 nF) | **62,49°** |
| TF al segnaposto | 55,06° |
| VAF a 100 | 55,42° |
| ritorno ai pubblicati | 55,55° |

**La caduta è la capacità di giunzione dei MJE**, cioè la f_T sotto il minimo di
NC-025. MMBT e JFET non c'entrano.

**La corrente di riposo** va nel verso opposto a quello che ci si aspetterebbe.
R128 spazzato da 1,20 a 1,69 kΩ, sul Miller vecchio:

| R128 | 1,20k | 1,25k | 1,30k | **1,33k** | 1,35k | 1,40k | 1,45k | 1,50k | 1,69k |
|---|---|---|---|---|---|---|---|---|---|
| I_q (Q132) | 12,60 | 13,37 | 14,15 | **14,61** | 14,92 | 15,70 | 16,49 | 17,28 | 20,29 mA |
| V1 min | 53,52 | 53,83 | 54,11 | **54,27** | 54,36 | 54,59 | 54,80 | 54,98 | 55,55° |

Tornare a ~15 mA **toglie** 1,3° di margine, ed E96 1,33 kΩ è il valore dei 14,6 mA
di progetto. 1,50 k ridà i 17,28 mA di L39.

## 2. Le due strade

### (a) Banda ridotta: il Miller

`strada_a/`: C124 470p–1,2n × R128 1,69k / 1,33k, sulle tre istanze, col criterio
di ADR-024 (`sintesi_v1.py`, lo stesso di `L39/script/margini.py`). Riga di
controllo: 470p / 1,69k ridà L39/dopo su ogni istanza.

| C124 | I_q | B 0 dB | B +3 | B +10 | blocco A | buffer | crossover B 0 dB |
|---|---|---|---|---|---|---|---|
| 470p | 20,3 | 55,55 | 63,90 | 100,19 | 57,93 | 54,92 | 889 kHz |
| 680p | 20,3 | 59,26 | 70,96 | 100,26 | 64,00 | 59,69 | 622 kHz |
| 820p | 20,3 / 14,6 | 60,70 / 60,02 | 73,75 | 98,59 | 66,02 | 61,48 | 520 kHz |
| **1n** | 20,3 / 14,6 | **62,08 / 61,57** | 76,20 | 96,66 | 67,69 | 63,21 | **430 kHz** |
| 1,2n | 20,3 / 14,6 | 63,24 / 62,86 | 77,88 | 94,98 | 68,89 | 64,66 | 361 kHz |

**Lo slew** si misura col metodo di L12 (`slew3_B.cir`, validato allora su
I_tail/C124), portato al blocco di oggi (`slew/`, `genera_slew.py`):
- blocco B a +10 dB;
- gradino di ±1,9 V all'ingresso;
- una sinusoide a 20 kHz e 12 V di picco in uscita, pendenza ideale 1,51 V/µs.

| C124 | SR salita / discesa | 20 kHz fondo scala: continua a valle | pendenza − |
|---|---|---|---|
| 470p | 8,25 / −3,40 V/µs | 0,054 V | −1,465 V/µs |
| 820p | 5,35 / −2,02 | 0,373 V | −1,385 |
| **1n** | 4,42 / **−1,68** | **0,572 V** | −1,335 |
| 1,2n | 3,70 / −1,41 | 0,811 V | −1,270 |

La discesa, limitata dalla corrente del VAS, è il lato stretto. Già da 820 pF la
sinusoide a fondo scala comincia a entrare in slew. A metà ampiezza (6 V di picco)
la continua resta ≤ 0,11 V fino a 1,2 nF.

### (b) Guadagno minimo sopra 0 dB

`strada_b/`: una gamba fissa RG0 da FB a massa su **ogni** istanza oggi a guadagno
1, e R_G3 ricalcolata perché +3 e +10 dB restino dove sono. R_G10 non cambia.

| Guadagno minimo | RG0 | R_G3 |
|---|---|---|
| +0,5 dB | 25,5 kΩ | 4,12 kΩ |
| +1,0 dB | 12,4 kΩ | 4,99 kΩ |
| +1,5 dB | 7,87 kΩ | 6,49 kΩ |

**Il guadagno da solo compra poco.** A +1,5 dB e 470 pF: blocco B 59,95°, buffer
59,11°. Il motivo è C_f: 330 pF su R_f fa uno zero a 321 kHz, sopra il quale il
guadagno di rumore torna verso 1. Al crossover, quindi, la gamba in più conta
poco.

Allora C_f si spazza con la gamba presente (`strada_b_cf/`, +1,5 dB):

| C_f | C124 | V1 min, 20,3 / 14,6 mA | B +10 dB |
|---|---|---|---|
| 330p | 470p | 59,11 / 57,73 | 100,21 |
| 220p | 470p | 60,89 / 59,55 | 96,66 |
| **220p** | **560p** | **63,11 / 62,12** | 95,56 |
| 150p | 560p | 62,48 / 61,54 | 90,39 |
| 100p | 560p | 60,94 / 60,03 | 86,55 |

Il candidato migliore è +1,5 dB, C_f 220 p e Miller 560 p:
- slew in discesa −2,89 V/µs, continua a 20 kHz a fondo scala 0,12 V;
- banda del modo basso 1,16 MHz, senza picco.

Ma cambia **E1** (ADR-001) a +1,5 dB e porta le uscite fisse a +3 dB (blocco A più
buffer). È topologia su tre istanze, supera ADR-025, e V2 va rimisurato.

### I costi dei candidati sui deck flat

`candidati/`: `cand_ac.py`, `cand_costi.py`, sui deck versionati con le `alter`.

| | ctrl | (a) 1 nF | (b) +1,5 dB, 220p, 560p |
|---|---|---|---|
| guadagno del modo basso | −0,007 dB | −0,007 dB | +1,508 dB |
| −3 dB modo basso / picco | 2,45 MHz / 0,52 dB | 912 kHz / 0,11 dB | 1,16 MHz / 0 |
| −3 dB a +10 dB; a 20 kHz rispetto a 1 kHz | 182 kHz; −0,054 dB | 113 kHz; −0,134 dB | 194 kHz; −0,047 dB |
| E5, modo basso / peggiore | 1,176 / 4,283 µV | 1,176 / 4,270 | 1,357 / 4,287 |
| PSRR+ 10 kHz, basso / +10 dB | 39,5 / 29,5 dB | 33,0 / 23,0 | 36,5 / 28,0 |
| V3: recupero, DC al jack | 1,07 µs, +3,2 mV | 3,03 µs, +3,2 mV | 0,65 µs, +3,2 mV |
| Zout al nodo, 20 kHz | 0,27 Ω | 0,57 Ω | 0,39 Ω |

A 14,6 mA (R128 1,33 k) la potenza a riposo del blocco scende da 0,993 a
**0,822 W**. Il resto non cambia oltre ±0,7 dB di PSRR.

## 3. La decisione dell'utente

Domanda posta con le tabelle del §2 (punto 4 del mandato: niente nel sorgente prima
della risposta). **Risposte (2026-09-23)**:
- **strada (a), Miller da 1 nF**, la raccomandata;
- **corrente di riposo ~20,3 mA con R128 a 1,69 kΩ**. La raccomandazione era 1,33 kΩ:
  l'utente ha preferito non cambiare il valore.

Diventano **ADR-042**. ADR-025 non si riscrive: il suo C_f resta, e il suo scarto di
1 nF, deciso sui segnaposto, è superato qui con il prezzo dichiarato.

## 4. Il sorgente

- `gain_block.py`: `C("1n", NX, NHI)`, col commento che cita ADR-042 e il prezzo.
  Il commento di R128 dice che 1,69 kΩ dà ora ~20,3 mA ed è la corrente di
  progetto. Ritoccate quattro frasi che dicevano «15 mA», qui, in `trim.py` e in
  `preamp_audio.py`. Aggiornato il blocco «SIMULATED RESULTS».
- **Rigenerati** il blocco e i due netlist KiCad. Nel blocco SPICE cambia **una riga**
  in ciascuna delle due forme (`C124 NX NHI 470p` → `1n`). La copia di prima è in
  `prima/gain_block_flat_L39.inc` e `prima/gain_block_L39.subckt`.
- Nei `.net` cambiano i nove valori di C124 (1 nel blocco, 8 nel canale); il resto
  del diff sono UUID, data e tag di SKiDL.

## 5. La regressione di L39, rifatta

21 deck veloci e una cella di V2 (1 kHz, 100 kΩ), prima e dopo:
- rc 0 ovunque, nessuna riga `Error`;
- `confronto_grezzo.csv`: 28 062 cifre, nessuna presente da una parte sola.

| Cifra | Soglia | Prima | Dopo | Esito |
|---|---|---|---|---|
| **V1 blocco B 0 dB** | ≥ 60° | 55,55° | **62,08°** | **regge** |
| V1 blocco B +3 / +10 dB | ≥ 60° | 63,90 / 100,19° | 76,20 / 96,66° | regge |
| **V1 blocco A** (≤ 1 nF) | ≥ 60° | 57,93° | **67,68°** | **regge** |
| **V1 buffer** | ≥ 60° | 54,92° | **63,21°** | **regge** |
| V1 gruppo B, blocco B (b_min/tip/max) | ≥ 60° | 55,76–55,87° | 62,19–62,24° | regge |
| V1 gruppo B, blocco A / buffer (nuovo, ADR-031) | ≥ 60° | 58,01–58,06 / 54,94–54,97° | 67,71–67,74 / 63,23–63,25° | regge; dispersione ≤ 0,06° |
| guadagno d'anello a 10 Hz | ~81 dB (#24) | 81,42 dB | 81,19 dB | controllo del #24 |
| punto di lavoro (`tb_op`, 81 cifre) | — | — | identico | — |
| E2 +3 / +10 dB a 1 kHz | ±0,1 dB / 9,5–10,5 | 3,039 / 9,963 dB | 3,039 / 9,963 dB | regge |
| banda −3 dB a 0 / +3 / +10 dB | nessuna soglia | 2,45 MHz / 577 / 182 kHz | 912 / 303 / 113 kHz | voluto (ADR-042) |
| E3 peggiore | ≥ 100 kΩ | 110,71 kΩ | 110,72 kΩ | regge |
| E4 Re(Z) max principale / fisse | < 100 Ω | 60,09 / 53,12 Ω | 60,09 / 53,12 Ω | regge |
| E5 peggiore (`tb_e3_e5_ldr`) | ≤ 9,95 µV | 5,049 µV | 5,034 µV | regge |
| E5, `tb_noise_breakdown` | ≤ 9,95 µV | 1,176…4,283 µV | 1,176…4,270 µV | regge |
| PSRR+ (+10 dB) 100 Hz / 1 kHz / 10 kHz / 20 kHz | quota di ADR-020 | 68,05 / 49,49 / 29,53 / 23,55 dB | 62,63 / 42,99 / 23,03 / 17,11 dB | limiti per tono ricalcolati |
| Zout al nodo, 1 / 20 kHz | — | 0,027 / 0,274 Ω | 0,037 / 0,572 Ω | — |
| V3: clip, recupero, DC al jack | recupera, niente latch | +13,23 / −13,79 V, 1,07 µs, +3,2 mV | +13,23 / −13,79 V, 3,03 µs, +3,2 mV | regge |
| P7: MJE / MMBT peggiore | 1,04 W / 310 mW | 0,362 / 0,093 W | 0,371 / 0,098 W | regge |
| classe A (`tb_blockA_carichi` F2; `tb_mute_corto` caso 0) | tutte | 36/36; 104/104 | 36/36; 104/104 | regge |
| V2 relè (`tb_switch_v2`), controfattuale | — | — | nessuna cifra mossa oltre 0,5 % | regge |
| V2 mute, 1 kHz 100 k principale: S ins / rel | ≤ 20 dB in 100 ms | 7,163 / 5,32 dB; A ≤ 3,75 µV, B2 0,327 µV, C_pav 0,267 mV | 7,163 / 5,32 dB; A ≤ 3,75 µV, B2 0,330 µV, C_pav 0,341 mV | regge (C_pav è diagnostica) |

- **I limiti per tono di ADR-020** si ricalcolano (`script/limiti_psrr.py`, che
  riproduce esattamente la tabella di L18 dai suoi CSV). Sul rail + a 1–20 kHz
  **si dimezzano circa**: 10 kHz da 31,0 a **14,2 µV RMS**, rumore bianco da 190
  a **87 nV/√Hz**. Il rail − cambia poco. La tabella in `REQUIREMENTS.md` era
  ancora quella di L18: ora ha i valori di L40.
- **Le righe «SOTTO 60» di `margini.csv`** sono celle informative, non di verdetto:
  la sonda sul nodo, e il blocco A col cablaggio a 4,7 nF. Salgono tutte di 30–37°
  (28,6 → 58,0° la peggiore).

## 6. Due trappole trovate per strada

- **Un corpo di `if` vuoto** in `.control` fa uscire ngspice con **139** a fine
  corsa, a tabelle complete: `docs/limitations.md` **#32**.
- **In `tb_ac.cir` le misure `fhi` e `flo` hanno i nomi scambiati**: `flo` è l'angolo
  alto (2,45 MHz a 0 dB), `fhi` quello basso (0,49 Hz). La cifra di banda di L39 era
  giusta perché letta a mano. Il deck non è stato toccato: rinominare cambia le
  chiavi del confronto. Resta da correggere insieme a una modifica vera del deck.

## 7. Cosa non è stato fatto

- **Nessuna misura di THD a 20 kHz a fondo scala.** Lo slew è misurato come continua
  indotta e come pendenza. Una cifra di distorsione su modelli che mancano parti
  del proprio datasheet non sarebbe evidenza (V4).
- **Il caso peggiore di V2** è di **L29c**, che viene subito dopo, sul circuito nuovo.
- Solo 27 °C, come ogni deck del repo.
- Il dossier non è rigenerato.
