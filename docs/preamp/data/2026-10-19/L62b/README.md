# L62b — i quattro diodi di riserva nel sorgente e la verifica (2026-10-19)

Report: `docs/preamp/reports/2026-10-19-L62b-diodi-nel-sorgente.md`. Decisione: **ADR-090** (di
L62a, non riscritta). Chiude **NC-062**.

Il circuito cambia: `circuits/preamp/gain_block.py` sezione 11, D154–D157, quattro 1N4148 in serie
fra NX e NY, anodo verso NX, nelle otto istanze (scheda audio 522 → 554 parti).

## I banchi

- **Il banco di L62a sul blocco del sorgente** (`script/genera_L62b.py`, da `genera_L62a.py`): una
  sola variante, `base`, che è il blocco generato (il controllo byte per byte contro `spice/preamp/`
  resta); i modi delle parti nuove sono quelli dei diodi del sorgente (`PROPRIE`). I quattro modi di
  NC-062 e gli otto dei diodi (aperto / corto), cinque posizioni, il riferimento sano e
  `CTRL_OUT_VP`: 66 corse (`deck/lista.txt`). A blocco sano tb_op, i quattro anelli e tb_mute_corto
  con le misure di L60d1 (`deck/lista_tb.txt`). Il riposo a 27 / 60 / 90 °C uniformi
  (`temperatura_op.py`): il sorgente, lo stesso senza i diodi, D157 in corto; con la corrente dei diodi.
- **La regressione dei 21 deck veloci** (`script/regressione.sh`, da L60d1): `regressione/prima` è il
  blocco di main 5036d8e3, lanciato nel worktree prima di toccare il sorgente; `regressione/dopo` il
  blocco coi diodi.
- **V4 a caldo** (`script/caldo.py` e compagni, da L60d1): spec `l62b--sot223` sull'include piatto
  del sorgente (`inc/l62b.inc`) e `l62b--sot223--diodi`, con D154–D157 alla Tj del finale NPN.

## Script (`script/`)

| Script | Cosa fa |
|---|---|
| `genera_L62b.py`, `corri.sh`, `uno.sh` | i deck del banco di L62a sul sorgente e le corse, 8 alla volta, in `run/` |
| `analizza_L62b.py`, `sintesi_L62b.py` | il jack e il calore → `analisi_jack.csv`, `calore.csv`; il peggiore sulle cinque posizioni → `sintesi.csv` |
| `confronta_tb.py` | il blocco sano → `blocco_sano.csv`; lo scarto di V1 contro `regressione/prima` |
| `temperatura_op.py` | il riposo a 27 / 60 / 90 °C → `temperatura.csv` (con `I_diodi_uA`) |
| `confronta_L62a.py` | `sintesi.csv`, `temperatura.csv`, `blocco_sano.csv` contro la variante `diodi` di L62a → `confronto_L62a.csv` |
| `regressione.sh`, `confronta_regressione.py`, `misure_regressione.py`, `p7_massimi.py` | la regressione prima / dopo: cella per cella (`regressione/confronto.csv`), sulle misure dei log (`regressione/misure.csv`), i massimi di P7 |
| `caldo.py`, `genera.py`, `esegui.sh`, `leggi_four.py`, `sintesi_caldo.py` | V4 a caldo → `tj/`, `sintesi_caldo.csv` |
| `metodo_scatto.py` | copiato da L62a; non usato: nessun gradino è cambiato |

Per rifare (Python con `/usr/bin/python3 -I`): `regressione.sh prima` sul blocco senza diodi, poi
`regressione.sh dopo`; `genera_L62b.py`, `corri.sh deck/lista.txt`, `corri.sh deck/lista_tb.txt`,
`analizza_L62b.py`, `sintesi_L62b.py`, `confronta_tb.py`; `temperatura_op.py`, `corri.sh
deck/lista_temperatura.txt`, `temperatura_op.py leggi`; `confronta_L62a.py`; `caldo.py op
l62b--sot223 l62b--sot223--diodi`, `esegui.sh deck/lista_op.txt`, poi `p2`, `p3`, `p4`, `deck4` allo
stesso modo, `leggi_four.py` e `sintesi_caldo.py` con le due spec.

## Esiti

- **Controlli**: riferimento sano −2,9 mV all'uscita del blocco, 151,7 mA dal rail + del canale;
  `CTRL_OUT_VP` 16,0 V alla principale, oltre il tetto. 66 + 6 + 3 corse con uscita 0 e in fondo;
  la regressione 21 + 21.
- **Uguale a L62a**: `confronto_L62a.csv`, 211 confronti con la variante `diodi`, **0 diversi**.
- **NC-062**: i quattro modi danno finali 64–65 °C a 27 °C d'aria e **97–98 °C a 60 °C**, le 22 Ω
  0,039–0,041 W; il gradino alla principale 66 dB SPL (76 a +10 dB). I modi dei diodi 78–79 °C, il
  gradino 38–48 dB SPL.
- **La corrente dei diodi** a blocco sano: 94 / 134 / 177 µA a 27 / 60 / 90 °C; il riposo −0,05 /
  −0,09 / −0,13 mA. D157 in corto: 1,75 mA nei tre diodi rimasti, riposo 19,65 / 20,87 / 22,13 mA.
- **Regressione**: niente fuori dal riposo (−0,05 mA) e da ciò che ne segue. V1 +0,04–0,05°; il rumore
  1e-6 relativo; V2 al più 4e-4 relativo. P7: finali 0,362 / 0,363 W, 22 Ω 0,295 / 0,332 W, 47 Ω
  1,282 W, scarto ≤ 2 mW caso per caso; il picco positivo della corrente di collettore del finale PNP
  (icmax_q133) sale da 3,1 a 7,1 mA, senza effetto sulle potenze.
- **V4 a caldo**: 0 su 48 fuori per spec, THD ≤ 0,00072 % a 0,2 V, IMD ≤ −131,8 dB, coda oltre
  +23,6 %: cifra per cifra `l60d1--sot223` di `../../2026-10-18/L60d1/sintesi_caldo.csv`.

## Limiti dichiarati

- Il calore dei guasti è Tj = Ta + P · R_thJA dalle potenze a 27 °C (il metodo di L45a / L62a).
- La potenza dei diodi non è nelle misure dei deck (i diodi non hanno `[p]`); coi guasti di NC-062
  ~10 mA · 0,76 V ≈ 8 mW per diodo, a calcolo.
- In `regressione/prima/tb_trim/tb_trim.log` un messaggio di ngspice spezza un numero («3.099181eNote:
  …»): `misure.csv` lo legge come 3,1 contro 309918; i valori sono uguali.
