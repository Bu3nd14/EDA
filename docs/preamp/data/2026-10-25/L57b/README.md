# L57b — il limitatore d'ingresso nel sorgente (2026-10-25)

Report: `docs/preamp/reports/2026-10-25-L57b-limitatore-sorgente.md`. Decisione: **ADR-101** (le parti
scelte qui, nel suo perimetro). Non conformità: **NC-059 chiusa**. L'utente all'inizio: «Una sessione».

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `script/rigenera.sh` | Rigenera il blocco, `spice/preamp/input_limiter.subckt` e `preamp_audio.net` dal sorgente |
| `script/falsi.py`, `falsi/` | I falsi del controllo del limitatore (2e): cinque varianti sbagliate generate in una cartella temporanea e la netlist di main di prima (`falsi/prima_di_adr101.net`); `falsi/esito.txt` 6 su 6 |
| `parti/` | Le parti: i controlli in ngspice dei due modelli nuovi (`bav199_fit.cir`, `lm4040_5v0_*.cir`, i log di `validate_models.py`); i due banchi del riferimento da solo (`lm4040_rif_*.cir` / `.log`, limitations #76). Gli script con cui è stato adattato il modello di TI e scritte le ricette sono in `script/` (`patch_lm4040_5v0.py`, `insert_tb_lm4040.py`, `insert_tb_bav199.py`) |
| `script/deck_limitatore.py` | Una volta: mette `XLIM` / `XREF` nei quattro deck canonici dell'ingresso (poi `INREF_EQ`, limitations #76) |
| `script/regressione.sh <prima\|dopo>`, `script/confronta_regressione.py`, `script/verdetti_regressione.py` | La regressione dei quattro deck (E3, E5, F1, V1 del blocco A): `regressione/confronto.csv`, `regressione/verdetti.csv` |
| `regressione/tb_e3_e5_2c.cir`, `dopo_2c/` | E3 / E5 col BAV199 a capacità raddoppiata |
| `regressione/tb_f1_selettore_ti.cir`, `dopo_ti/` | Il deck del selettore coi riferimenti del modello di TI: l'evidenza della #76 |
| `script/limitatore.py` | La protezione per i banchi, **presa dal subckt generato** (corpo di `INLIM` e `INREF` / `INREF_EQ`); `prova()` la confronta con `preamp_audio.net` dispositivo per dispositivo (9 su 9) |
| `script/genera.py`, `dist.py`, `spl.py`, `nodeset.py`, `leggi_costo.py`, `sintesi.py` | I banchi di L57a copiati, con `--prot S[,rif=…][,dio=…]`; `dist.py` ha in più 10 kHz e la CCIF (`imd`) |
| `script/esegui.py <gruppo>` | `noto`, `reti`, `mute`, `costo` (tre corse alla volta) |
| `script/verifica_noto.py` | Il caso noto contro `L57a/rca/strade/out_r1k_lim5/rca.csv`: 256 celle su 256 |
| `modelli/` | Scritti da `limitatore.py` dai file di `models/`: il BAV199 col modello del 1N4148 (il caso noto) e con la capacità raddoppiata |
| `rca/noto`, `rca/reti`, `rca/mute`, `costo/`, `sintesi.csv` | Le corse e la sintesi |

Varianti: `noto` = la topologia generata coi modelli di L57a (1N4148, riferimenti ideali a 5 V);
`lim` = il circuito (BAV199 stimato, riferimenti `INREF_EQ`); `lim_2c` = `lim` con la capacità del
diodo raddoppiata; `mute_lim` = `lim` col mute inserito.

## Rifare

```sh
S=/Users/roberto/EDA/docs/preamp/data/2026-10-25/L57b/script
/bin/zsh $S/rigenera.sh
/usr/bin/python3 $S/falsi.py
/usr/bin/python3 $S/limitatore.py                 # e la prova contro la netlist
/bin/zsh $S/regressione.sh prima                  # su main; poi i deck nuovi:
/bin/zsh $S/regressione.sh dopo
/usr/bin/python3 $S/confronta_regressione.py
/usr/bin/python3 $S/verdetti_regressione.py
/usr/bin/python3 $S/esegui.py noto
/usr/bin/python3 $S/verifica_noto.py
/usr/bin/python3 $S/esegui.py reti                # e mute
/usr/bin/python3 $S/nodeset.py                    # prima del costo
/usr/bin/python3 $S/esegui.py costo
/usr/bin/python3 $S/leggi_costo.py
/usr/bin/python3 $S/sintesi.py
```

## Ipotesi dichiarate

- Quelle di L57a e di L53 (la sorgente, la mano 10 ms, i condensatori Y, il contatto).
- **Il BAV199 è una stima** (`models/diodes/bav199_fit.lib`): nexperia.com risponde 403 e il modello
  del costruttore non c'è. La capacità è la fig. 5 del datasheet (tipica, letta a occhio: 1,85 pF a 0 V,
  1,10 a 5 V); la parte statica e la dispersione sono quelle del 1N4148 (3,91 nA a 5 V inversi, un
  tetto: il BAV199 dà 3 pA tipici e 5 nA massimi a 75 V). La sensibilità alla capacità è la variante
  `lim_2c`. I datasheet di BAV199 e BAV99 vengono da uno specchio di terzi, dichiarato nella loro
  provenienza.
- **I riferimenti nei banchi sono `INREF_EQ`**: le R e le C generate, ogni LM4040 come 4,992 V dietro
  1,1 Ω (la ZR massima). Il modello di TI non trova il punto di lavoro dietro i 10 kΩ (limitations #76).
  Il rumore dei due LM4040 (80 µV RMS tipici, 10 Hz–10 kHz) non è nel banco: a calcolo, nel report.
- Il costo legge la THD sul nodo dopo i 47 Ω (come L57a); la CCIF col metodo di L46a.
