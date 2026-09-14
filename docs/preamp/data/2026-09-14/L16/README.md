# Dati di L16 — il trim entra nel progetto (2026-09-14)

Lotto **L16**, report `reports/2026-09-14-L16-trim.md`. Decisione **ADR-027**: un
solo trim, sul ramo dell'uscita variabile, fra il blocco A e l'attenuatore,
a relè bistabili G6KU-2F-Y, con LED dai contatti e interblocco dal mute (K6).

Tutti i deck girano con `scripts/run_simulation.sh`, ngspice rc 0, nessuna riga
`Error` nei log. Il solo avviso è il noto «model type mismatch» dell'LS350
(`models/bjt_pnp/ls350.lib`). Modelli: segnaposto più LS352 e LSK489 vendor,
come L12 e L27. Si versionano `.csv` e `.log`.

## `prima/`

- `tb_loop_blockA_main.log`: il deck di `main` rieseguito prima di toccare
  qualcosa. I suoi 17 CSV, e i 3 di `tb_dc_headroom`, sono **byte-identici** a
  `L27/dopo/`.

## `dopo/` — il circuito di L16

| Directory | Per cosa |
|---|---|
| `tb_trim/` | `spice/preamp/tb/tb_trim.cir`: attenuazione e **E3** (`tb_trim_e3.csv`, Zin al connettore nelle tre posizioni, CSEL 1 fF / 22 pF / 68 pF), **E5** della catena (`tb_trim_e5.csv`: posizioni 99 = senza trim, 0, 6, 12; tre modi; attenuatore max e metà; sorgente K11 e phono). Due scale candidate: `cand 2` (845 / 464 / 464) è quella scelta |
| `tb_loop/` | **V1 blocco B**, `tb_loop.cir` esteso alle sorgenti 2,571 k e 2,611 k che il trim dà all'attenuatore. Le 396 righe di L27 tornano identiche |
| `tb_loop_blockA/` | **V1 blocco A**: `tb_loop_blockA.csv` senza trim (identico a L27), `tb_loop_blockA_trim.csv` col partitore nelle tre posizioni e le due scale |
| `tb_dc_headroom/` | la base della cifra di **NC-009** (identica a L27) |

## `esplorazione/` — scratch, deck e script d'analisi

| File | Cosa |
|---|---|
| `tb_trim_prima-decisione/` | il trim **all'ingresso** del blocco A, prima della scelta «B» dell'utente: E3 cade con 10–47 pF, E5 a +10 dB con attenuatore al massimo e trim −6 dB fa 10,60 / 11,24 µV |
| `deck/tb_trim_bound.cir`, `bound/` | la scala più piccola che E3 consenta all'ingresso (50 k / 25 k / 25 k): **10,12 µV**, senza trim 4,77 µV |
| `deck/toll_L16.cir`, `toll_L16/` | gli spigoli di L27 (C124, C137 ±5 %, R_iso ±1 %) con la sorgente 2,611 k: 0 dB **61,422°**, +3 dB 68,644° |
| `deck/tb_blockA_carichi_trim.cir`, `tb_blockA_carichi_trim/` | classe A del blocco A col carico del trim a 0 dB (1506 Ω): I_C minima **13,28 mA** (L27: 14,36) |
| `falsi/<variante>/` | netlist **generate** da copie di scratch di `trim.py` con un difetto ciascuna, e l'uscita del guardiano 2e (`guardiano.txt`). Sei varianti cadono (rc 1); `scala_fuori_finestra` passa il 2e e fa cadere il 2f |
| `script/trim_e96.py` | ricerca E96 della scala **all'ingresso** (con R_IN) |
| `script/trim_ramo_e96.py` | ricerca E96 della scala **sul ramo** (col carico dell'attenuatore) |
| `script/v1_trim.py` | minimi di V1 e confronto con L27 per chiave |
| `script/toll_L16.py` | minimi agli spigoli |
| `script/headroom_nc009.py` | le tre metriche di headroom, M1 dichiarata |
| `script/cmpdir.py` | confronto byte per byte di due cartelle di CSV |
| `script/falsi.py` | genera le varianti difettose e ci lancia il guardiano |
