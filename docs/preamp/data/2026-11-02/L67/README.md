# L67 — la distorsione delle istanze a guadagno unitario sulla catena (2026-11-02)

NC-055 (maggiore, prima di G1), chiusa. Decisione **ADR-112**; report
`../../../reports/2026-11-02-L67-catena-guadagno-unitario.md`. `<L>` = questa cartella, `<R>` la radice
del repo; Python con `/usr/bin/python3 -I`. Cifre di modello (ngspice 47, i modelli di `models/`).

## I banchi e i casi noti

| Banco | Copiato da | Caso noto |
|---|---|---|
| `catena/script/genera.py`, `leggi_catena.py`, `esegui.sh`, `confronta.py` (la catena di un canale, tre uscite) | `L56/catena/script/` (il blocco come argomento; `esegui.sh` col conteggio dei job di L60d1) | `l56` (il blocco di L56, `prima/gain_block_l56.subckt` da git 369f2aad2) contro `L56/catena/run/catena/catena.csv`: 224 celle, 1 diversa (h5+ della fissa 1 a 20 kHz, −187,5 contro −187,6 dB). `confronta.py noto` |
| `rs/script/genera.py`, `leggi_four.py`, `sintesi.py` (il blocco a 0 dB con la sorgente a 0–5,6 kΩ) | `L56/rs/script/` (il blocco come argomento) | `l56__u27`, `l56__u57` contro `L56/rs/run/sintesi.csv`: 80 celle, 0 diverse (`noto_rs_l56.csv`) |
| `noto/script/` (il blocco caldo dentro un subckt) | i deck `thd20k_*` di L66 per `lim365--sot223--diss` | il deck di L66 com'è = `L66/sintesi_caldo.csv`; col blocco avvolto le stesse 48 THD (`noto_caldo.csv`) |
| `script/avvolgi.py` | — | `oggi_avv` (il piatto di oggi avvolto) contro `oggi` (`gain_block.subckt`): 336 celle, 0 diverse |
| `catena/script/genera_imd.py`, `leggi_imd.py` (CCIF sulla catena) | il metodo di `L66/script/genera_imd.py` | nessun riferimento sulla catena; la fissa 1 col volume in cima −137,5 dB a 2,5 kΩ, il blocco da solo in L66 −132,4 dB (nei tre modi) |

I blocchi: `l56`, `oggi`, `oggi_avv`, `caldo_t27_rame`, `caldo_t27_minima`, `caldo_t57_rame`,
`caldo_t57_minima`. I blocchi caldi sono i `L66/inc/lim365--sot223--diss__<cond>.inc` (il passo 4 di
`v4caldo.py`); `lim365` = il blocco di oggi salvo una riga di commento (`diff`). Ipotesi dichiarata: le
quattro istanze della catena alla stessa Tj, perché il punto di lavoro in continua è lo stesso. I deck
a 57 °C portano `.temp 57`, come quelli di L66: ciò che non ha `temp=` sta all'aria.

## Il punto di lavoro della catena (limitations #86)

Col blocco di oggi a 27 °C (`oggi`, `oggi_avv`, `caldo_t27_*`) l'op della catena non convergeva in **68
casi su 68**, e la corsa partiva da una catena spenta: VPF a 4,9 V, 4,05 A dal +15 V, la principale a
pochi µV. `l56` e `caldo_t57_*` convergevano. Il blocco da solo converge sempre. Il rimedio:
`script/op_blocco.py` (l'op del blocco di oggi da solo → `op_oggi.csv`, 38 nodi interni, VPF 14,84 V) e
un `.nodeset` per ogni nodo di ogni istanza in `genera.py`, solo sui nodi che esistono nel blocco
incluso. Dopo: 0 casi non conversi (`op_falliti.csv`, `script/op_falliti.py`); il caso noto regge.
`leggi_catena.py` e `leggi_imd.py` rifiutano un caso con «source stepping failed», oltre al livello.

`m10` (il volume a −10 dB) è a 6,8 / 3,2 kΩ, cioè −9,9 dB: col valore esatto l'op del caso +10 dB a 2 V
non convergeva nemmeno da solo, e il transitorio partiva da uno stato morto (4,8 µV alla principale).

## Le cifre

- `sintesi_rs.csv`: la sorgente sul blocco di oggi, **60 su 60 dentro**, margine minimo 2,7 dB.
- `catena_<blocco>.csv`, `sintesi_catena.csv`: la catena con V4 letto alla lettera; colonne `griglia`
  (`l56` = volume in cima e a metà, `volbasso` = −10 / −20 dB), `livello_A_V`, `margine_dB`. Fuori solo
  la principale a 20 kHz e 0,2 V: 2 su 56 (oggi e aria 27 °C), 3 su 56 (aria 57 °C), fino a −3,1 dB; col
  volume basso fino a −14,2 dB.
- `imd_catena.csv`: CCIF sulla catena, **0 su 78 fuori**, margine minimo 10,8 dB.
- `verifica_livello.csv` (`script/verifica_livello.py`): la regola di ADR-112, **0 su 42 fuori per
  blocco**, margine minimo 1,9 dB (griglia di L56) e 1,3 dB (volume basso).

## Rifare

```sh
/usr/bin/python3 -I <L>/script/op_blocco.py genera   # l'op del blocco da solo (op_oggi.csv sta gia' nel repository)
/bin/zsh <R>/scripts/run_simulation.sh <L>/op/op_oggi.cir <L>/op/run
/usr/bin/python3 -I <L>/script/op_blocco.py leggi
/bin/zsh <L>/script/corri_tutto.sh            # avvolgi, la catena coi nodeset, il caso noto 4, la sorgente
/bin/zsh <L>/script/corri_catena.sh           # solo la catena coi nodeset, da zero, sette blocchi
/usr/bin/python3 -I <L>/script/op_falliti.py l56 oggi oggi_avv caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/usr/bin/python3 -I <L>/catena/script/leggi_catena.py l56 oggi oggi_avv caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/usr/bin/python3 -I <L>/catena/script/confronta.py noto ; /usr/bin/python3 -I <L>/catena/script/confronta.py oggi oggi_avv
/usr/bin/python3 -I <L>/script/sintesi_catena.py l56 oggi caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/usr/bin/python3 -I <L>/noto/script/confronta.py
/usr/bin/python3 -I <L>/rs/script/leggi_four.py l56__u27 l56__u57 oggi__u27 oggi__u57 caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/usr/bin/python3 -I <L>/rs/script/sintesi.py noto_rs_l56.csv l56__u27 l56__u57
/usr/bin/python3 -I <L>/rs/script/sintesi.py sintesi_rs.csv oggi__u27 oggi__u57 caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
/usr/bin/python3 -I <L>/catena/script/genera_imd.py oggi caldo_t27_rame caldo_t57_rame
/bin/zsh <L>/catena/script/esegui.sh <L>/catena/deck/lista_imd.txt 9
/usr/bin/python3 -I <L>/catena/script/leggi_imd.py oggi caldo_t27_rame caldo_t57_rame
/usr/bin/python3 -I <L>/script/verifica_livello.py l56 oggi caldo_t27_rame caldo_t27_minima caldo_t57_rame caldo_t57_minima
```

`corri_vb.sh` e `prova_nodeset.sh` sono i passi intermedi di questo lotto (il volume basso prima dei
nodeset, la prova su due deck). `run/`, `*/run/`, `*/deck/`, `inc/` e `op/` non stanno nel repository: si
rifanno (`.gitignore`).
