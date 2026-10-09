# L48b — la continua del blocco A attraverso trim e volume (NC-041), i dati

Sotto, `<L>` è questa cartella e `<R>` la radice del repo.

## La misura delle strade, prima delle domande all'utente

| Percorso | Cosa |
|---|---|
| `scatti/genera_scatti.py` | il generatore dei deck: `--op` (la continua propria del blocco A), un deck per variante (gli scatti), `--ac` (E9 ed E5), `--rapido` (la sonda, un caso per variante con le forme d'onda) |
| `scatti/deck/tb_l48b_op.cir`, `.log` | la continua propria del blocco A nel banco: **−6,623 mV** (ADR-056: −6,6) |
| `scatti/deck/tb_l48b_scatti_v{0..4}.cir`, `scatti_v*.csv`, `v*.log` | i 324 casi: 4 strade (6 condensatori) più il circuito finale (v4: C_T 10 µF, R_G 1 MΩ, il bilanciamento al centro), × 3 continue × 3 guadagni × 4 eventi, coi due cursori per il volume. v0–v3 sono le corse prima delle domande, ricorse con l'elemento `RBAL` in più (a 1e12: i picchi uguali, la linea di base prima dello scatto diversa di nV) |
| `scatti/ac/tb_l48b_ac_rumore.cir`, `ac_rumore.csv` | E9 a 20 Hz su tutta la catena (100 k e 10 k) ed E5 al jack, per ogni strada |
| `scatti/analizza.py`, `sintesi.txt`, `sintesi.csv` | la sintesi in µV e in dB SPL, più il limite della corrente di gate col cursore aperto |
| `scatti/sonda/` | la sonda (prima del `gmin` a 1e-15) e la sua prova `gmin_v3.*` |
| `scatti/corri.sh`, `leggi_onde.py` | corre i deck di una cartella in parallelo, con la guardia sui log; legge una forma d'onda |

**Il banco.** È la catena di `spice/preamp/tb/tb_trim.cir`: la rete d'ingresso di ADR-064, il
blocco A, la scala del trim di `trim.py` coi suoi contatti, il cablaggio, il blocco B 0 / +3 /
+10 dB, 47 Ω, 4,7 µF, il bleed e 100 kΩ. In più:
- **La continua del blocco A** si impone con `VOSA` davanti al gate, e `IOSA` dà a R113 la sua
  corrente (limitations #44). Si misura a −6,6 mV (nominale) e a ±30 mV (la dispersione di
  NC-041, per eccesso). La continua misurata è controllata caso per caso da `analizza.py`.
- **L'attenuatore** è una scala in serie da 10 kΩ col cursore fra due punti. **m1** è il
  cursore cortocircuitante, che chiude il nuovo punto prima di aprire il vecchio (1 ms); **m0**
  è quello non cortocircuitante, aperto per 1 ms. Sul cursore ci sono 100 pF di cavo.
- **Gli eventi**: il volume da 0 a −2 dB e da −29 a −27 dB; il trim da 0 a −6 dB e da −6 a
  −12 dB, senza mute, cioè un limite per eccesso: il trim si cambia solo in mute.

**Tre difetti del banco, trovati dalla sonda e corretti prima delle cifre:**
1. **R113 è nel sottocircuito, il blocco B vero non l'ha** (`r_in=None`). Col cursore aperto
   decideva il gate: si scaricava in ~100 µs. Il generatore scrive una copia del sottocircuito
   senza R113 per il blocco B, e rifiuta se R113 non c'è esattamente una volta.
2. **`gmin` inventa una corrente di gate.** Con 1e-12 S su ogni giunzione, il gate-drain del
   JFET a ~14 V porta ~14 pA che il modello dell'LSK489 non ha (`Isr` ignorato, Is 3 fA). Col
   cursore aperto davano 289 µV al jack, 0,48 µV con `gmin=1e-15`. La corrente vera del
   datasheet si aggiunge a parte (sotto).
3. **In AC un interruttore `SW` resta aperto** anche col comando a 1, e anche con `ON`
   sull'istanza: la cima dell'attenuatore era a −58 dB, il jack a −165 dB, ed E5 era il rumore
   del solo blocco B. Nel deck AC i contatti sono resistenze ferme. La `tran` non ne soffre:
   la continua passa, e il controfattuale ridà il calcolo dell'architetto.

## I risultati

dB SPL di picco a 1 m con la catena di NC-028: 100 µV ≈ 33,5 dB SPL, la soglia di V2.
«Peggiore» è il peggiore di −6,6 / −30 / +30 mV.

**Lo scatto del volume in cima alla corsa (da 0 a −2 dB), a +10 dB:**

| Strada | nominale | peggiore |
|---|---|---|
| oggi (il controfattuale) | 4,30 mV · **66,1 dB SPL** | 19,5 mV · **79,3 dB SPL** |
| condensatore all'ingresso del blocco B, 1 µF + 1 MΩ | 4,29 mV · 66,1 | 19,4 mV · 79,2 |
| condensatore prima del trim, 47 / 68 / 100 µF | ≤ 0,002 µV | ≤ 0,002 µV |
| condensatore fra trim e volume, 10 µF | ≤ 0,002 µV | ≤ 0,002 µV |

Il controfattuale ridà il calcolo dell'architetto (3,2 / 10 mV a −15,45 mV) riportato a −6,6 mV:
4,27 mV a +10 dB. **Il condensatore all'ingresso del blocco B non toglie il gradino**: il calcolo
di L48a è confermato dalla misura. A metà corsa, oggi: 192 µV (39,1 dB SPL) nominali, 872 µV
(52,3) peggiori. Con le due strade che tolgono la continua, ogni scatto del volume, a ogni
guadagno e continua, sta sotto 0,002 µV col cursore cortocircuitante e sotto 0,48 µV con l'altro.

**Il cambio del trim, senza mute (limite per eccesso), a +10 dB, da 0 a −6 dB:** oggi 20,8 mV
(79,8 dB SPL), peggiore 94,4 mV (93,0); prima del trim ≤ 0,002 µV; **fra trim e volume 9,5 mV
(73,0), peggiore 43,1 mV (86,1)**. Lì la continua resta sulla scala del trim. In mute il jack è
staccato, ma il gradino decade nel condensatore con τ ≈ 10 µF × 10,4 kΩ ≈ 0,1 s. Calcolato e non
simulato: rilasciando il mute 0,5 s dopo il cambio restano ~78 µV (~33 dB SPL), peggiori ~350 µV
(~44 dB); dopo 1 s ≤ 3 µV.

**E9 ed E5** (`ac/ac_rumore.csv`), trim a 0 dB, volume in cima:

| Strada | 20 Hz, 100 k | 20 Hz, 10 k (finale futuro) | E5 peggiore (+10 dB, 430 Ω) |
|---|---|---|---|
| oggi | −0,005 dB | −0,135 dB | 5,496 µV |
| blocco B, 1 µF | −0,006 | −0,136 | 5,496 |
| prima del trim, 47 µF | **−0,060** | −0,190 | 5,496 |
| prima del trim, 68 µF | −0,031 | −0,162 | 5,496 |
| prima del trim, 100 µF | −0,017 | −0,147 | 5,496 |
| fra trim e volume, 10 µF | −0,033 | −0,163 | 5,496 |

E5 di oggi è la cifra canonica (5,496 µV, L48a): il deck AC è tarato. Nessuna strada cambia il
rumore.

**La corrente di gate col cursore aperto (m0)**, per ogni strada, oggi compresa. Il gate del
blocco B non ha ritorno in continua mentre il cursore passa fra due punti, e deriva di
I_G · t / C. Datasheet dell'LSK489: I_G −2 pA tipica, −25 pA massima a 25 °C; a 55 °C ~200 pA
(stima per raddoppio ogni 10 °C). Con 104 pF, a +10 dB: 1 ms 61 µV (29 dB SPL) tipica, 760 µV
(51 dB) massima a 25 °C, ~6 mV (69 dB) a 55 °C; con 5 ms di passaggio, cinque volte tanto.
**Col cursore cortocircuitante non c'è.**

## Dopo le scelte dell'utente (ADR-065)

| Percorso | Cosa |
|---|---|
| `sorgente/confronta_netlist.py`, `confronto_netlist.txt` | la netlist di prima contro quella nuova per connettività (reti come insiemi di piedini): nuove C265 / C465 10u, R265 / R465 1M; J120 / J320 `ATT_` → `VOL_`; la rete del trim spezzata da C_T e il cursore con R_G a massa; nient'altro |
| `falsi/falsi.py`, `verdetti.txt`, `main_audio.net` | i sabotaggi del 2e (`check_volume()` in `check_relay_safe_state.py`) e del 2f (`preamp_blocks_draw.py`): **8 su 8** cadono dove devono, la netlist vera passa |
| `misure/tb_trim/`, `misure/tb_e3_e5/`, `confronta_l48a.py`, `confronto_l48a.txt` | i due deck canonici con C_T e il bilanciamento al centro: E5 5,496 µV, E3 108,2 kΩ invariati; il trim −6,076 / −11,997 dB (col carico di 8,33 kΩ) |
| `e5_bilanciamento/` | E5 col bilanciamento girato di 3 dB (partitore MN 14,6k / 35,4k): **5,60 µV** |
| `v1_bilanciamento/` | V1 del blocco B con 2,611 / 3,77 / 5,07 / 5,6 kΩ di sorgente (copia di `tb_loop.cir`): minimo **64,42°** a 5,6 kΩ |
| `v2/matrice/` | `tb_v2_casopeggiore.cir` rigenerato (155 corse): il gruppo 6, lo scatto del volume a ogni guadagno, e la diagnostica del trim col mute rilasciato 0,5 s dopo |
| `v2/controfattuale/` | il controfattuale del generatore (C_T scavalcato, il bilanciamento tolto) |
| `v2/sonda_vosb/` | il gruppo 6 a +10 dB con VOSB = 0: il gradino del volume nel banco V2 è il difetto noto di VOSB (limitations #44), 9,2 nV senza |
| `script/regressione.sh`, `confronta.py`, `regressione/` | i 21 deck veloci contro L48a |

## Come si rifà

```sh
/usr/bin/python3 <L>/scatti/genera_scatti.py --va0=0 --op
/opt/homebrew/bin/ngspice -b <L>/scatti/deck/tb_l48b_op.cir -o <L>/scatti/deck/tb_l48b_op.log
/usr/bin/python3 <L>/scatti/genera_scatti.py --va0=-6.62307e-3
/bin/zsh <L>/scatti/corri.sh <L>/scatti/deck
/usr/bin/python3 <L>/scatti/genera_scatti.py --va0=0 --ac --uscita <L>/scatti/ac
/opt/homebrew/bin/ngspice -b <L>/scatti/ac/tb_l48b_ac_rumore.cir -o <L>/scatti/ac/tb_l48b_ac_rumore.log
/usr/bin/python3 <L>/scatti/analizza.py
```

`--va0` è `v(aout)` del log di op. Le forme d'onda della sonda (`onde_*.txt`) non si committano.

Dopo le scelte (`<C>` = `docs/preamp/data/2026-09-23/L29c`, `<P>` =
`/Users/roberto/EDA/env/venv/bin/python3`):

```sh
<P> <R>/circuits/preamp/preamp_audio.py
/usr/bin/python3 <L>/sorgente/confronta_netlist.py <netlist di L48a> <R>/circuits/preamp/preamp_audio.net
<P> <R>/docs/preamp/schematic/preamp_blocks_draw.py
/usr/bin/python3 <L>/falsi/falsi.py
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_trim.cir <L>/misure/tb_trim
/bin/zsh <R>/scripts/run_simulation.sh <R>/spice/preamp/tb/tb_e3_e5.cir <L>/misure/tb_e3_e5
/usr/bin/python3 <L>/misure/confronta_l48a.py
/bin/zsh <R>/scripts/run_simulation.sh <L>/e5_bilanciamento/tb_e5_bilanciamento.cir <L>/e5_bilanciamento/out
/bin/zsh <R>/scripts/run_simulation.sh <L>/v1_bilanciamento/tb_loop_bilanciamento.cir <L>/v1_bilanciamento/out
/usr/bin/python3 <L>/v1_bilanciamento/minimi.py
/usr/bin/python3 <C>/deck/genera_tb_v2_casopeggiore.py
/usr/bin/python3 <C>/deck/genera_tb_v2_casopeggiore.py --matrice controfattuale --uscita <L>/v2/controfattuale/cf.cir
/bin/zsh <C>/script/corri.sh <L>/v2/controfattuale/corse <L>/v2/controfattuale/cf.cir '.*' 4
/bin/zsh <C>/script/corri.sh <L>/v2/matrice <R>/spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 7
/usr/bin/python3 <R>/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <cartella>
/usr/bin/python3 <C>/script/analizza_par.py <cartella>/manifest_sel.csv <cartella> <cartella>/analisi.csv 8
/bin/zsh <L>/script/regressione.sh dopo
/usr/bin/python3 <L>/script/confronta.py
```

`tb_e5_bilanciamento.cir` e `tb_loop_bilanciamento.cir` sono i deck canonici con un `sed`: il
primo sostituisce `RBAL ATT 0 50k` con il partitore `RBALH ATT VTOP 14.6k` / `RBALL VTOP 0
35.4k` e porta `RATTH` su `VTOP`; il secondo cambia la sola riga `foreach rs`. La sonda di VOSB
sono `corsa_vol_g10_iii.cir` e `corsa_vrif_g10_iii.cir` della matrice con `alter vosb dc = 0` e
il `wrdata` su `v2/sonda_vosb/`, analizzate col `manifest_sel.csv` di quella cartella.
