# L62a — il moltiplicatore di Vbe: i guasti rifatti, i rimedi sul banco (2026-10-19)

Report: `docs/preamp/reports/2026-10-19-L62a-moltiplicatore-vbe.md`. Decisione: **ADR-090**. Il
circuito non cambia: i rimedi sono varianti testuali del `gain_block.subckt` e del
`gain_block_flat.inc` generati, in `varianti/<v>/`.

## Il banco

- **Il canale di L45a** (`2026-10-13/L45a/script/genera_canale.py`, importato): C_IN, la scala del
  trim, C_T, il volume, le tre uscite con la geometria iii, il guasto a 0,3 s con un interruttore
  ideale (10 µs), 2,3 s di corsa; le potenze di ogni parte del blocco guasto mediate sugli ultimi
  10 ms in `<modo>_fine.csv`.
- **Le copie guaste rifatte** (limitations #62): `inc/<v>/<modo>.subckt` dal subckt della variante,
  con `subckt_guasto()` di L45a; il generatore rifiuta una copia senza R150–R153 o senza le parti
  nuove della variante. Anche i blocchi sani del canale includono la variante.
- **Le varianti**: `base` (il blocco di oggi; il generatore verifica che i due file siano uguali a
  `spice/preamp/` byte per byte), `guardia` (Q160 MMBT5551 con R161 2,7 kΩ / R162 1 kΩ, il secondo
  moltiplicatore di Self), `diodi` (D160–D163, quattro 1N4148 in serie fra NX e NY), `limite` (Q160 /
  Q163 sulle due 22 Ω, partitore 1,2 kΩ / 1 kΩ, ~72 mA).
- **I modi**: i quattro di NC-062 (`Q127_ae`, `Q127_be`, `R129_cc`, `R128_ap`) e quelli delle parti
  nuove, nelle posizioni A, F1, F2, B e B a +10 dB, più il riferimento sano; il controllo
  `CTRL_OUT_VP` sulla base (`modi.csv`, 46 righe).

## Script (`script/`)

| Script | Cosa fa |
|---|---|
| `genera_L62a.py` | varianti, copie guaste, i 246 deck di guasto (`deck/lista.txt`) e i 24 a blocco sano (`deck/lista_tb.txt`: tb_op, i quattro deck d'anello, tb_mute_corto con le misure di L60d1/p7_l56.py) |
| `corri.sh`, `uno.sh` | le corse, 8 alla volta, in `run/` (non versionato) |
| `analizza_L62a.py` | il jack con `analizza_tr.py` di L45a → `analisi_jack.csv`; il calore a 27 e 60 °C d'aria → `calore.csv` (Q127 a 125 °C/W, SOT-223) |
| `sintesi_L62a.py` | il peggiore sulle cinque posizioni per variante e modo → `sintesi.csv`; i controlli |
| `confronta_tb.py` | le varianti a blocco sano contro la base: riposo, V1, P7 → `blocco_sano.csv` |
| `temperatura_op.py` | il riposo a 27 / 60 / 90 °C uniformi, varianti e guasti delle parti nuove → `temperatura.csv` |
| `diagnosi_scatto.py`, `analizza_diagnosi.py` | il gradino nell'istante del guasto: la copia di L45a e il blocco di oggi senza R150, R151 / R152, con R153 a 1 Ω → `diagnosi_scatto.csv` |
| `metodo_scatto.py` | lo stesso gradino col metodo della media (di oggi) e col puntuale (di L45a) |

Per rifare: `genera_L62a.py`, `corri.sh deck/lista.txt`, `corri.sh deck/lista_tb.txt`,
`analizza_L62a.py`, `sintesi_L62a.py`, `confronta_tb.py`; `temperatura_op.py`, `corri.sh
deck/lista_temperatura.txt`, `temperatura_op.py leggi`; `diagnosi_scatto.py`, `corri.sh
deck/lista_diagnosi.txt`, `analizza_diagnosi.py`. Tutti i Python con `/usr/bin/python3 -I`.

## Esiti

- **Controlli**: il riferimento sano −2,9 mV all'uscita del blocco, 151,9 mA dal rail + del canale
  (38 mA per blocco); `CTRL_OUT_VP` 16,0 V alla principale, oltre il tetto. 270 + 8 + 8 corse, tutte
  con uscita 0 e in fondo.
- **I quattro modi sul blocco di oggi sono quelli di L45a**: finali 181–183 °C a 27 °C d'aria e
  **213–216 °C a 60 °C**, le 22 Ω 1,72–7,54 W (R128 aperta: finali 137 °C a 60, 22 Ω 7,54 W).
- **Il gradino nell'istante del guasto**: 74 mV «A» alla principale (B; 227 mV a +10 dB) contro i
  0,42 mV di L45a. Non è il blocco (la copia di L45a dà lo stesso): è un impulso di ~2 µs
  dell'interruttore ideale, che il metodo con la media di ADR-087 / ADR-088 conta per area e quello di
  L45a scartava; col metodo puntuale le stesse corse danno 0,43 mV (limitations #64).
- **Diodi**: finali **97–98 °C** a 60 °C d'aria, 22 Ω ≤ 0,041 W, nessuna parte oltre i limiti; i
  guasti dei diodi lasciano il riposo a 19,7–22,1 mA (27–90 °C); blocco sano −0,05 mA, V1 ≤ 0,05°, P7
  uguale.
- **Guardia**: finali 94–95 °C; ma Q160 in corto C-E, R161 in corto, R162 aperta portano il riposo a
  0–7,6 mA (classe B).
- **Limite**: finali 121–123 °C; in P7 la corrente dei finali da 214 a 118 mA e il finale PNP da 0,36
  a 0,52 W; Q160 in corto porta il VAS a 135 °C a 60 °C d'aria.

## Limiti dichiarati

- Il calore è Tj = Ta + P · R_thJA dalle potenze a 27 °C (il metodo di L45a); la temperatura
  uniforme di `temperatura_op.py` è un limite grossolano (diodi e guardia non sono accoppiati ai
  finali).
- La potenza dei diodi non è nelle misure del deck (i diodi non hanno `[p]`): a calcolo ~10 mA ·
  0,76 V ≈ 8 mW per diodo.
- V4 a caldo non è rifatta: il riposo a blocco sano cambia di −0,05 mA coi diodi (−0,09 / −0,13 a 60 /
  90 °C), contro gli 0,8 mA che il sorgente dà per 50 Ω di R128. Si rifà in L62b col blocco nel sorgente.
