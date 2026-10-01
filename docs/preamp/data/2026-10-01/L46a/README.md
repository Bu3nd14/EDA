# L46a — la compensazione del blocco di guadagno (2026-10-01)

Esplorazione: le varianti del blocco stanno in `inc/`, **non** nel sorgente. Report:
`../../../reports/2026-10-01-L46a-compensazione.md`. **Cifre di modello, non misure**: conta il
trend fra varianti sullo stesso banco.

| Percorso | Cosa |
|---|---|
| `script/varianti.py` | scrive `inc/<variante>.inc`: copia di `spice/preamp/gain_block_flat.inc` con le righe cambiate (la prima riga dell'include dice quali) |
| `script/genera.py` | i deck di una variante in `deck/<variante>/`, per famiglia: `op`, `v1`, `psrr`, `thd`, `imd`, `slew`, `arch` (vedi la docstring) |
| `script/idss.py` | V1 nel gruppo B di I_DSS (ADR-031): `tb_idss_loop` versionato + i deck di `L40/script/idss_istanze.py`, con l'include della variante |
| `script/esegui.sh <lista>` | `run_simulation.sh` su ogni deck, 8 in parallelo, in `run/<variante>/<deck>/`; rc e durata in `run/esiti.tsv` |
| `script/leggi_four.py` | THD/IMD da `fourier` → `run/<v>/distorsione.csv`; ricuce le righe tagliate da una Note (#37), controlla l'ampiezza della sorgente e il pavimento numerico |
| `script/riassumi_op.py` | punto di lavoro → `run/punto_di_lavoro.csv` |
| `script/sintesi.py` | una riga per variante → `sintesi.csv` |
| `script/riassumi_idss.py` | gruppo B → `idss.csv` |

**Le varianti** (`script/varianti.py`, dizionario `VARIANTI`):
- `cm<C>`: solo C124. `cm1n` è il blocco di oggi (controllo: ridà L40), `cm470p` è L39;
- `drv_*`: il driver (QD1 MMBT5551, QD2 MMBT5401, RD12 330 Ω), R128 3,48k; `drv_r<R>_cm1n` è
  la taratura di R128 sulla corrente di riposo;
- `vas56_*`: R123 e R126 a 56 Ω (VAS ~10,7 mA), R128 1,58k;
- `drv_vas56_*`: tutte e due, R128 3,24k.

- `zxt_*`: i MJE sostituiti dai Diodes ZXTN/ZXTP25040DZ (modelli in `models/`), R128 1,87k
  (1,74k col VAS); `zxt_r<R>_cm1n` è la taratura.

**La regressione** (dopo la scelta, ADR-054): `script/regressione.sh prima|dopo` corre i 21 deck
veloci di L40 in `regressione/<fase>/`; `script/confronta.py` scrive
`regressione/confronto_grezzo.csv`; in `regressione/script/` gli script di L40 copiati **senza
modifiche** (`margini.py`, `p7.py`, `classe_a.py`, `v3.py`: leggono `regressione/prima|dopo`
perché calcolano la base dalla propria cartella), più `v3_con_continua.py` (V3 con la continua
tolta) e `mosse.py` (le cifre che si muovono oltre una soglia).

**I deck `thd` e `imd`** hanno `option itl1=1000`: coi ZXT l'op della `tran` ripiegava sul
«transient op» (#33, THD al 73 %), e `gminsteps=40` peggiorava; il report, §1.

**I controlli.** `deck/<v>/arch_*`: i deck dell'architetto (L43a) col solo include ripuntato;
con `cm1n` e `cm470p` ridanno 0,1682 % / −59,6 dB e 0,01182 % / −85,5 dB.

**Per rieseguire** (dalla radice del repo, una variante):

```
/usr/bin/python3 docs/preamp/data/2026-10-01/L46a/script/varianti.py vas56_cm470p
/usr/bin/python3 docs/preamp/data/2026-10-01/L46a/script/genera.py op,v1,psrr,thd,imd,slew vas56_cm470p
/bin/zsh docs/preamp/data/2026-10-01/L46a/script/esegui.sh docs/preamp/data/2026-10-01/L46a/deck/lista_opv1psrrthdimdslew.txt
/usr/bin/python3 docs/preamp/data/2026-10-01/L46a/script/riassumi_op.py vas56_cm470p
/usr/bin/python3 docs/preamp/data/2026-10-01/L46a/script/leggi_four.py vas56_cm470p
/usr/bin/python3 docs/preamp/data/2026-10-01/L46a/script/sintesi.py vas56_cm470p
```

`deck/lista_*.txt` è l'ultima lista scritta per quella combinazione di famiglie: una corsa
successiva la sovrascrive. I deck usano `@REPO@`, quindi restano rieseguibili fuori dal worktree.
