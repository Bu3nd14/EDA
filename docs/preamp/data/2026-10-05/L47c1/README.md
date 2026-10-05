# L47c1 — il mute coi soli relè: i dati

ADR-062 (scelta dell'utente del 2026-10-04, «Taglio coi soli relè»). Report:
`docs/preamp/reports/2026-10-05-L47c1-mute-coi-soli-rele.md`. Sotto, `<L>` è questa cartella e
`<R>` la radice del repo.

| Percorso | Cosa |
|---|---|
| `falsi/falsi.py`, `falsi/verdetti.txt` | i 9 sabotaggi del 2e e del 2j e i 2 controlli; **9 su 9 cadono per il motivo giusto** |
| `falsi/main_audio.net`, `falsi/main_psu.net` | le netlist di `main` prima di L47c1 (le celle e J3): la base dei falsi |
| `falsi/2e_*.net`, `falsi/2j_*.net` | le netlist sabotate, generate da `falsi.py` |
| `e3_e5/` | `tb_e3_e5.cir` senza celle: E3 (`tb_e3_e5_e3.csv`) ed E5 (`tb_e3_e5_e5.csv`) |
| `e3_e5/sonda_zmin.cir`, `e3_e5/sonda/` | la sonda che mostra il punto saltato da `meas min` (limitations #45) |
| `script/regressione.sh`, `script/confronta_regressione.py`, `regressione/` | i 21 deck veloci contro L47b2b1 |
| `script/confronta_e3_e5.py` | `tb_e3_e5` contro `tb_e3_e5_ldr` di L47b2b1 |

## I risultati

**Le netlist, per connettività** (`script/netdiff.py`: confronto per insiemi di piedini, non per
nomi di rete, limitations #23; `falsi/main_*.net` contro `circuits/preamp/*.net`):
- **scheda audio**: escono **U101, U102, U301, U302 e J3** (420 → 415 componenti). L'unico
  cambiamento di rete: J101 pin 1 entra in `AL_IN` (con R108, R113), J301 pin 1 in `AR_IN` (con
  R308, R313). ERC 47 avvisi e 0 errori, come prima (cambiano solo i nomi delle reti fuse, #23);
- **alimentatore**: escono **33 parti** (151 → 118): U510 (MCP4822), U511 (MCP6004), Q507–Q512,
  R548–R556, R560–R568, C535–C538, C541, C542, J3. Restano senza connessione i pin 2, 7, 17, 18,
  19 del micro (PA4, PB4, PA1, PA2, PA3). Nessun'altra rete cambia. ERC da 21 a **24 avvisi** (−2
  «insufficient drive» di U510 / U511, +5 pin del micro), gli stessi 2 errori spiegati in
  `psu.py`.

**I controlli**: il 2e nuovo (`check_input`) e il 2j nuovo (`check_retired`) passano sulle netlist
nuove e cadono su quelle di `main` e su sette sabotaggi (`falsi/verdetti.txt`).

**E3 ed E5 senza celle** (`script/confronta_e3_e5.py`):

| | senza celle (L47c1) | con le celle (L47b2b1) |
|---|---|---|
| E3, minimo vero (20 kHz, selettore 68 pF) | **114,7 kΩ** | 105,8 kΩ (riportato 110,7: #45) |
| E5, peggiore (trim 0, +10 dB, attenuatore al massimo, 430 Ω) | **5,496 µV** | 5,530 µV |
| E5 contro la riga «nessuna» di L47b2b1 | differenza ≤ 5,4·10⁻⁶ | — |

**La regressione dei 21 deck** (`regressione/confronto.csv`): 248 file, rc 0 su 21. Cambia
**solo la colonna `zmin_ohm` di `tb_trim_e3.csv`** (massimo −4,4 %, 120 051 → 114 721 Ω: #45),
più il deck rinominato (`tb_e3_e5_ldr` → `tb_e3_e5`).

## Come si rifà

```sh
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_e3_e5.cir <L>/e3_e5
/bin/zsh <R>/scripts/run_simulation.sh <L>/e3_e5/sonda_zmin.cir <L>/e3_e5/sonda
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 <L>/script/confronta_regressione.py
/usr/bin/python3 <L>/script/confronta_e3_e5.py
/usr/bin/python3 <L>/falsi/falsi.py
/usr/bin/python3 <L>/script/netdiff.py <L>/falsi/main_audio.net <R>/circuits/preamp/preamp_audio.net
/usr/bin/python3 <L>/script/netdiff.py <L>/falsi/main_psu.net <R>/circuits/preamp/psu.net
```
