# Dati di L20 — quanto il progetto dipende da I_DSS (2026-09-15)

Lotto **L20**, report `reports/2026-09-15-L20-sensibilita-idss.md`. Chiude
**NC-013**. Decisione: **ADR-031** (JFET del gruppo B, tolleranza 8,0–15,0 mA).

**Topologia**: quella di `main` a `8a36e9e` (L13). **Nessun valore del circuito
cambia.**

## Provenienza dei modelli

Letta dagli `.include` dei deck.

- **Coppia d'ingresso = `LSK489A`**, il modello del costruttore di
  `models/jfet/lsk489.lib`, **incluso intatto**, con `Kf = 0.0009f`, `Af = 1`.
  - Le varianti ne spostano `Vto` con `altermod` dentro `.control`, `Beta` 2,2m
    invariato (NC-013).
  - **Non esiste un modello del costruttore del gruppo B**: le cifre B sono
    questo modello col `Vto` spostato.
- **Specchio = LS352** (`models/bjt_pnp/ls350.lib`), del costruttore, senza `KF`.
- **Ogni altro dispositivo** è un segnaposto scritto a mano
  (`spice/preamp/placeholder_devices.lib`), `KF = 0` (NC-017).
- **Rumore**: pavimento senza flicker per ogni dispositivo tranne la coppia
  d'ingresso.
- **Il blocco** è `spice/preamp/derived/gain_block_flat_lsk489a.inc`, derivato
  da `gain_block_flat.inc` da `scripts/derive_jfet_variant.py`. Cambia solo il
  nome del modello su JQ110A/B; il blocco 2i lo tiene aggiornato.

## I `Vto` dichiarati — `esplorazione/vto_dichiarati.csv`

Da `esplorazione/script/cerca_vto.py`:
- bisezione a V_DG = 15 V, V_GS = 0, 25 °C;
- `Vto` arrotondato al mV, e gli estremi di finestra arrotondati verso
  l'interno (il più vicino dava 7,998 mA per il minimo B);
- I_DSS **rimisurata** col valore arrotondato.

| Variante | `Vto` | I_DSS 25 °C | I_DSS 27 °C |
|---|---|---|---|
| `A_come_e` | −1,130 V (pubblicato) | 2,59283 mA | 2,59188 mA |
| `A_tip` | −1,696 V | 5,50250 mA | 5,48711 mA |
| `B_min` | −2,086 V | 8,00484 mA | 7,97616 mA |
| `B_tip` | −2,557 V | 11,49940 mA | 11,45200 mA |
| `B_max` | −2,976 V | 14,99650 mA | 14,93060 mA |

I circuiti girano a 27 °C, come ogni deck del repo. A 27 °C il minimo B vale
7,976 mA.

## Le cartelle

Tutti i deck girano con `scripts/run_simulation.sh`, ngspice rc 0, **0 righe
`Error`**.
- In ogni log compare 1 avviso sui quattro parametri che ngspice ignora
  (`isr`, `alpha`, `vk`, `mj`, atteso: `models/jfet/lsk489.lib`).
- Nei deck di blocco compaiono anche le 2 righe «model type mismatch» su
  `q121a`/`q121b`, preesistenti.
- Si versionano `.csv` e `.log`. I `.txt` di `wrdata`, i `.json` e i deck
  risolti no.

### `deck/tb_idss_jfet.cir` → `dopo/tb_idss_jfet/`

Il JFET da solo, alle condizioni di L7, `LSK489X` e `LSK489A` affiancati.

Non sta sotto `spice/*/tb` per una ragione precisa. Istanzia i JFET
direttamente, e `provenance()` legge i modelli istanziati solo dagli include del
blocco: il 2h lo rifiuterebbe.

`tb_idss_jfet_tab.csv`: una riga per variante e temperatura; per X e per A
`idss` [A], `gfs` [S], `vgsoff` [V] a 1 nA, `vgs500` [V] a 500 µA.

### `dopo/tb_idss_op_noise/` — `spice/preamp/tb/tb_idss_op_noise.cir`

| File | Cosa |
|---|---|
| `tb_idss_op_noise_op.csv` | una riga per variante: la I_DSS della sonda a 27 °C, poi `id`/`vgs`/`gm`/`ig` delle due metà, `vds`, Q106 `ic` e `vce`, cascode, NCASC, VAS, Q125, uscita, `v_src`, `v_out`, correnti dai rail. A 0 dB, sorgente 430 Ω |
| `tb_idss_op_noise_rumore.csv` | `onoise_total`/`inoise_total` [V RMS, 20 Hz–20 kHz] per variante × i cinque casi di `tb_noise_breakdown` |
| `tb_idss_op_noise_cm_<var>.csv` | VSRC da −3,82 a +3,82 V a 0 dB: col1 v(d1n), col3 v(g1), col5 v(d2n), col7 v(g2), col9 v(src), col11 v(nte), col13 v(out); colonne pari = VSRC |
| `tb_idss_op_noise_d_<var>.csv` | spettro del caso D (+10 dB, 2,5 k): col1 `onoise_spectrum`, col3 `inoise_spectrum` [V/√Hz]; colonne pari = frequenza |

Le varianti, nell'ordine:
- `a_come_e`, `a_come_e_kf0`;
- `a_tip`, `b_min`, `b_tip`, `b_max`;
- `a_ripristinato`, che deve ridare `a_come_e`;
- `xa`, il modello portato ai parametri di `LSK489X`: controllo positivo.

### `dopo/tb_idss_loop/` — `spice/preamp/tb/tb_idss_loop.cir`

`tb_idss_loop_margini.csv`, 550 righe: variante × carico (100 k, 10 k) ×
sorgente (1 mΩ, 1 k, 2,5 k, 2,571 k, 2,611 k) × cavo al jack (11 valori fino a
4,7 nF). Colonne: `var`, `rsrc`, `pos`, `cprobe`, `fcross_hz`, `pm_deg`,
`tdb_10hz`, `rload`.

Varianti: `a_come_e`, `b_min`, `b_tip`, `b_max`, `xa`.

## `esplorazione/`

| File | Cosa |
|---|---|
| `script/cerca_vto.py` | la bisezione dei `Vto` |
| `script/verifica.py` | tutti i controlli e i numeri; esce 0 sui dati veri |
| `verdetto.txt` | il suo output sui dati veri |
| `script/derive_jfet_variant.py` | non c'è: sta in `scripts/` |
| `script/sabotaggi_derive.sh`, `sabotaggi_derive.txt` | 6 casi su `scripts/derive_jfet_variant.py`, tutti come attesi |
| `sabotaggi_deck/s1…s4.txt` | `verifica.py` sui quattro deck sabotati: quale controllo cade |
| `2h/0…4_*.txt` | il 2h prima e dopo la voce `LSK489A` in `build_dossier.PART`, con l'intestazione copiata e con quella vera |
| `script/ast_identico.py` | la modifica a `gain_block.py` è solo commento |

## Numeri chiave

Da `esplorazione/verdetto.txt`.

**Il JFET da solo, 25 °C.** Finestre del datasheet: A 2,5/5,5/8,5 mA, B
8,0/11,5/15,0 mA, V_GS(off) −1,5…−3,5 V, Gfs ≥ 1,5 mS.

| | I_DSS | Gfs | V_GS(off) | V_GS a 500 µA |
|---|---|---|---|---|
| `LSK489X` (segnaposto di ogni deck di `main`) | **4,8422 mA** | 6,672 mS | **−1,49935 V** | −1,02873 V |
| `LSK489A` com'è | 2,59283 mA | 4,952 mS | −1,12435 V | −0,65021 V |
| B min / tip / max | 8,005 / 11,499 / 14,997 mA | 8,70 / 10,42 / 11,90 mS | −2,080 / −2,551 / −2,970 V | −1,606 / −2,077 / −2,496 V |

**Blocco B a 0 dB e rumore.**

| | coda | I_D | V_GS | v(OUT) | sat. min a ±3,82 V | rumore D | V1 min |
|---|---|---|---|---|---|---|---|
| `xa` (= L27) | 4,37385 mA | 2,21131 mA | −0,491 V | −16,576 mV | 3,891 V | 4,2289 µV | 61,803° |
| `a_come_e` | 4,37306 mA | 2,21091 mA | −0,146 V | −17,261 mV | 4,261 V | 4,3033 µV | 62,508° |
| `b_min` | 4,37500 mA | 2,21188 mA | −1,100 V | −17,280 mV | 3,305 V | 4,3055 µV | 62,708° |
| `b_tip` | 4,37894 mA | 2,21229 mA | −1,570 V | −17,291 mV | 2,834 V | 4,3066 µV | 62,763° |
| `b_max` | 4,37952 mA | 2,21272 mA | −1,988 V | −17,300 mV | 2,415 V | 4,3076 µV | 62,802° |

- **1/f del JFET** nel caso D, in quadratura: 0,116 µV. A 20 Hz lo spettro sale
  del 5,1 %.
- **E5** peggiore: 4,308 µV, contro 9,95.
- **V1**: la dispersione del gruppo B nella stessa cella è ≤ 0,104°.
