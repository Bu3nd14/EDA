# L56 — lo specchio d'ingresso del blocco di guadagno (2026-10-12)

Report: `../../../reports/2026-10-12-L56-specchio.md`. Decisioni: **ADR-067** (inseguitore davanti al
VAS e transistor di aiuto sullo specchio, R120 220 Ω) e **ADR-068** (VAS e suo carico in SOT-223).
Cifre di modello (ngspice 47, i modelli di `models/`). `<R>` = la radice del repo, `<L>` = questa
cartella. La catena dell'alimentatore sta nella cartella sorella `../L56-alimentatore/` (stessa
profondità di L51b, perché i suoi script ricavano la radice dalla posizione).

## Le cartelle e gli script

| Percorso | Che cosa |
|---|---|
| `base/gain_block_flat_adr056.inc` | il blocco di `main` prima di L56 (96bacb07): la base delle varianti |
| `script/varianti.py` | le varianti (dizionario `VARIANTI`, docstring col meccanismo), → `inc/<variante>.inc` |
| `script/caldo.py` | **ogni giunzione alla sua temperatura, iterata**: `op` (passo 1, uniforme), `p<K>` (passo K alle Tj del K-1), `deck<K>` (Tj del passo K → `inc/<spec>__<cond>.inc`, `tj/<spec>.csv`, deck di THD 20 kHz / IMD / gradino della coda). Opzioni termiche `--acc`, `--freddo`, `--sot223`. Rifiuta un `op` non convergente (vedi sotto) |
| `script/sintesi_caldo.py` | per variante e condizione: casi fuori da V4, margine, IMD, gradino della coda → `sintesi_caldo.csv` |
| `script/prove.py` | le prove del meccanismo: l'LS350 con RC = 0 (copia di L53) e con VAF 1000 V (`inc/prove/ls350_vaf1k.lib`, **copia di prova, non un modello**) |
| `script/dzt_identico.py` | il modello del costruttore dei DZT5401 / DZT5551 contro quello degli MMBT: **identico** |
| `script/genera.py`, `esegui.sh`, `leggi_four.py`, `sintesi.py`, `psrr_tab.py`, `clip.py`, `riassumi_op.py` | il banco di L46b (copiato; `leggi_four.py` con la colonna `rs`) |
| `regressione/prima`, `dopo`, `script/` | i 21 deck veloci (`script/regressione.sh` di L47c1): `prima` sul blocco di `main` fatto girare in una copia staccata di 96bacb07, `dopo` sul blocco di ADR-067; `confronto.csv` (grezzo), `cifre.csv` (E3, E4, E5, punto di lavoro), `script/margini.py`, `p7.py`, `classe_a.py`, `v3_con_continua.py` di L46b |
| `catena/` | NC-055: la catena di un canale di L53 (`script/` copiato), sul blocco nuovo |
| `rs/` | NC-055: la THD contro l'impedenza di sorgente di L53, a 27 e 57 °C uniformi |

## Le varianti (nomi usati nei dati)

`ctrl` il blocco di oggi; `ef_*` l'inseguitore (1,2k / 2,2k, R120 226 o 220); `re82`, `re100`, `re150`
R123; `rm150`, `rm100` lo specchio meno degenerato; `diodo`, `diodo2` diodi in serie alla base del
VAS; `coda_bassa` R107 150; `aiuto` il solo transistor di aiuto; **`ef_aiuto`** la scelta (collettori
a massa), `ef_aiuto_vm` coi collettori al rail negativo (quella del sorgente), `ef_aiuto_r226`
scartata (+17 mV); `ef_1k2_r120_*` la scansione di R120; `adr067` = `spice/preamp/gain_block_flat.inc`
generato dal sorgente (identico a `ef_aiuto_vm`, `cmp`). Opzioni: `--acc` i diodi della coda alla Tj
di Q106, `--freddo` VAS e carico a metà R_thJA, `--sot223` VAS e carico a 125 °C/W.

## Le cifre

- `sintesi_caldo.csv`: **`adr067` 0 casi fuori su 60** (u27 e aria 27 / 57 °C, rame e piazzola
  minima), margine ≥ 2,7 dB, IMD ≤ −131,8 dB, gradino della coda oltre +24 %; `ctrl` 12 / 12 fuori
  a caldo, IMD fino a −61 dB. `adr067--sot223` uguale.
- `tj/adr067.csv`, `tj/adr067--sot223.csv`: le Tj convergenti (passo 5 / 4) e le due metà dello
  specchio (giunzione base-collettore interna).
- `run/prove/distorsione.csv`: RC = 0 toglie il secondo ordine (−134,5 dB a +10 dB); VAF 1000 V no.
- `regressione/`: V1 (margini.py), P7 (p7.py: Q125 0,191 W col corto), classe A invariata, V3
  (recupero 0,65 µs, continua al jack 13–14 ms dopo +19,3 mV), `cifre.csv` (E5 5,10 µV).
- `catena/run/catena/catena.csv`: 54 su 56 dentro (L53: 53). `rs/run/sintesi.csv`: 20 su 20.

## Una trappola trovata qui (limitations #57)

Un `op` che non converge — «gmin stepping failed» **e** «source stepping failed» — ngspice lo
stampa lo stesso, con valori senza senso (qui VPF a 0,94 V e correnti quasi nulle), e il primo
`leggi_op` di `caldo.py` lo prendeva per buono: il passo 2 di `adr067` con l'aria a 57 °C sul rame
aveva dato Tj ≈ aria. Ora `caldo.py` rifiuta il log con «source stepping failed» e un punto di
lavoro spento (VPF < 14,5 V o coda < 3 mA). «gmin stepping failed» da solo è normale.

## Rifare

```sh
/usr/bin/python3 <L>/script/varianti.py
/usr/bin/python3 <L>/script/caldo.py op <spec>...         # poi esegui.sh <L>/deck/lista_op.txt
/usr/bin/python3 <L>/script/caldo.py p2 <spec>...         # poi esegui.sh <L>/deck/lista_p2.txt; p3, p4 (p5) allo stesso modo
/usr/bin/python3 <L>/script/caldo.py deck4 <spec>...      # poi esegui.sh <L>/deck/lista_deck4.txt
/usr/bin/python3 <L>/script/leggi_four.py <spec>...
/usr/bin/python3 <L>/script/sintesi_caldo.py <spec>...
/usr/bin/python3 <L>/script/genera.py op,v1,psrr,clip,slew,thd,imd <variante>...   # il banco di L46b
/usr/bin/python3 <L>/script/prove.py ctrl ef_1k2_r220 re100
/usr/bin/python3 <L>/script/dzt_identico.py
/bin/zsh <L>/script/regressione.sh dopo                    # prima: lo stesso script in una copia di 96bacb07
/usr/bin/python3 <L>/script/confronta_regressione.py
/usr/bin/python3 <L>/regressione/script/margini.py          # e p7.py, classe_a.py, cifre.py; v3_con_continua.py col venv
/usr/bin/python3 <L>/catena/script/genera.py ; esegui.sh <L>/catena/deck/lista.txt ; leggi_catena.py
/usr/bin/python3 <L>/rs/script/genera.py ; genera.py 57 ; esegui.sh lista_rs.txt / lista_t57.txt ; leggi_four.py rs t57 ; sintesi.py rs t57
```

`esegui.sh` è quello di L46b: un deck alla volta per riga, 8 in parallelo. Le forme d'onda di
`tb_v3_overload` sono in `.gitignore` (~8 MB a variante).
