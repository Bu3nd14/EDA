# L48a — il selettore d'ingresso coi condensatori per ingresso, i dati

La prima parte di L48 (scelta dell'utente: «Due parti»). ADR-064. Report:
`docs/preamp/reports/2026-10-06-L48a-selettore.md`. Sotto, `<L>` è questa cartella e `<R>` la
radice del repo.

| Percorso | Cosa |
|---|---|
| `dimensionamento/tb_l48a_rete_ingresso.cir`, `out/` | C_IN 1 / 2,2 / 4,7 µF contro R_SEL 470 k / 1 M: E3, perdita a 20 Hz, E5; il caso «oggi» ridà L47c2b2 |
| `dimensionamento/tb_l48a_f1_passo.cir`, `out_f1/` | il gradino al cambio d'ingresso per scegliere R_SEL (470 k contro 1 M, 10 mV / 100 mV / 1 V, trasferimento e sovrapposizione) |
| `misure/tb_e3_e5/`, `misure/tb_trim/` | i due deck canonici sull'ingresso nuovo |
| `misure/tb_f1_selettore/` | `spice/preamp/tb/tb_f1_selettore.cir`: F1 sul banco, tre modi, quattro continue, il controfattuale |
| `psu/deck/genera_tb_psu.py`, `analizza.py` | il generatore e l'analisi di L47c2a; il solo cambio è il carico «resto» di `VRELAY`, 42,4 → 51,5 mA (`--resto 42,4` ridà il deck di L47c2a, provato) |
| `psu/rete/` | la tenuta di `VRELAY_REG` col selettore; `analisi.csv` |
| `falsi/falsi.py`, `verdetti.txt` | i sabotaggi del 2e sul selettore: **10 su 10** |
| `script/regressione.sh`, `confronta.py`, `regressione/` | i 21 deck veloci contro L47c2b2: `regressione/confronto.txt` |

Le forme d'onda di `psu/rete/*.txt` non si committano (`.gitignore` di radice).

## Come si rifà

```sh
/bin/zsh <R>/scripts/run_simulation.sh <L>/dimensionamento/tb_l48a_rete_ingresso.cir <L>/dimensionamento/out
/bin/zsh <R>/scripts/run_simulation.sh <L>/dimensionamento/tb_l48a_f1_passo.cir <L>/dimensionamento/out_f1
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_f1_selettore.cir <L>/misure/tb_f1_selettore
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_e3_e5.cir <L>/misure/tb_e3_e5
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_trim.cir <L>/misure/tb_trim
/usr/bin/python3 <L>/psu/deck/genera_tb_psu.py --uscita <L>/psu/rete --nome rete
/opt/homebrew/bin/ngspice -b <L>/psu/rete/tb_psu_rete.cir -o <L>/psu/rete/tb_psu_rete.log
/usr/bin/python3 <L>/psu/deck/analizza.py <L>/psu/rete
/usr/bin/python3 <L>/falsi/falsi.py
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 <L>/script/confronta.py
```

## I risultati

**F1, il gradino al cambio d'ingresso** (`misure/tb_f1_selettore/f1_selettore.csv`), picco su
ogni uscita, A a 0 V, B alla continua VB, trasferimento 1 ms, perdita al minimo del poliestere:

| VB | fisso | 0 dB | +3 dB | +10 dB |
|---|---|---|---|---|
| 0 / 10 mV / 100 mV | 6,28 µV | 6,29 µV | 8,93 µV | **19,8 µV** |
| 1 V | 44,3 µV | 44,3 µV | 63,0 µV | **140 µV** |
| sovrapposizione, 100 mV / 1 V | 1,0 / 23,0 µV | 1,1 / 23,6 µV | 1,6 / 31,6 µV | 3,5 / 70,8 µV |
| controfattuale (ingresso di prima), 10 mV / 1 V, +10 dB | 10,1 mV / 1,01 V | | | 31,6 mV / 3,15 V |

**R_SEL** (`dimensionamento/out_f1/f1_passo.csv`): con 1 MΩ, 1 V dà 303 µV al principale a +10 dB.

**E3** 108,2 kΩ con 68 pF, uguale nelle tre posizioni del trim (L47c2b2: 114,7 kΩ). **E5** il
peggiore 5,496 µV, invariato. **Perdita della rete a 20 Hz** 0,0027 dB.

**`VRELAY_REG` ≥ 11,4 V** dopo la perdita di rete: **48,3 / 121,7 / 195,4 ms** a rete −10 / nom
/ +10 % (L47c2a 61,1 / 142,2 / 223,6); P9 ≥ 25 ms.

**Regressione**: 244 file su 248 uguali a L47c2b2; cambiano le colonne di E3 di `tb_e3_e5_e3.csv`
e `tb_trim_e3.csv` (la rete d'ingresso) e E5 di 1,7·10⁻⁵ relativo; nessun deck con rc ≠ 0.
