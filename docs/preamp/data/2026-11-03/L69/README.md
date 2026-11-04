# L69 — la ritenuta che tiene i 5 V a massa (NC-079): i dati

Il lotto di NC-079 (l'utente, L68: «Non conformità maggiore», poi «Prima la correzione»). **Il circuito
cambia**: ADR-116, i pull-up di AT_MRQ e di AT_ON in due metà in serie (R572 + R588, R576 + R589). Sotto,
`<L>` è questa cartella e `<R>` la radice del repo. Le corse a priorità bassa, al più tre insieme. Report:
`reports/2026-11-04-L69-ritenuta.md`.

## Le scelte dell'utente

- il rimedio: **«Due metà per pull-up»** (ADR-116), contro una resistenza da 1 kΩ sull'anodo della ritenuta;
- il dossier: **«Lotto a parte»** — l'evidenza dell'alimentatore di L64b rifatta sul sorgente nuovo e il
  dossier rigenerato in L69b, prima di L65.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `psu/`, `script/`, `carico.txt` | Il banco di L68, copiato. In `genera_tb_psu.py` due opzioni di solo banco: `--l69ra R` (R fra AT_ON e l'emettitore di Q514, R584 / C555 sul nodo nuovo), `--l69rd R` (R in serie al catodo di D537). In `modi.py` i corti di R572 / R576 sulle loro metà (`at_mrq_m`, `at_on_m`) e le righe di R588 / R589. `psu/lista_l69.py` scrive tutte le liste |
| `lista_meccanismo.txt`, `seq/mecc/`, `meccanismo.csv` | NC-079 col sorgente di prima, con le sonde sui piedini di Q513 / Q514 (`script/calore_ritenuta.py`: P = Σ V·I, 403 K/W, 60 °C d'aria) |
| `lista_vaglio.txt`, `lista_vaglio_c.txt`, `seq/{a220,a470,a1k,a2k2,b,c}/` | Lo screening delle opzioni (30 corse): `an_vaglio*.csv`, `confronto_vaglio*.{csv,txt}` (`psu/confronta_l69.py` contro `L64b/an_l64b.csv`), `calore_vaglio*.txt` |
| `lista_piena.txt`, `seq/{a1k,c}_{m10,p10,t22}/` | La matrice piena di A (1 kΩ) e C (46 corse): `an_piena.csv`, `confronto_piena.{csv,txt}`, `calore_piena.txt` |
| `lista_prova.txt`, `lista_sorgente.txt`, `seq/oggi/`, `seq/sano/` | Il sorgente nuovo: **672 corse** (le simulazioni del temporizzatore di L68 e R588 / R589 contro gli otto eventi, gli otto eventi sani), tutte con `ok.txt`, nessun ripiego. `script/analizza_sorgente.sh` → `an_sorgente.csv`, `confronto_sorgente.{csv,txt}` (`psu/confronta_sorgente.py`: contro L64b e contro lo stesso caso in L68) |
| `script/calore_tutte.sh`, `calore_5v.csv` | U504 / U512 su tutte le corse del sorgente nuovo: fuori solo C545 in corto (accettato in L68) |
| `script/fmea_l69.py`, `fmea_l69.csv` | Le **8 righe** di R572 / R576 / R588 / R589 (tutte basse); controlla che ogni altro caso del temporizzatore sia uguale a L68 |
| `script/fmea_oggi.py`, `fmea_oggi.csv`, `fmea_oggi_conti.csv` | La FMEA di oggi dalle **sette fonti**: 692 righe, 47 alte, 70 medie, 570 basse, 5 escluse |
| `script/copertura.py`, `copertura.csv` | Dell'alimentatore **0 parti su 189 senza riga** |

Le forme d'onda (`*_out.txt`, ~44 GB) e i `.dat` non stanno nel repository (`.gitignore`).

## Comandi

```sh
/usr/bin/python3 -I <L>/psu/lista_l69.py sorgente > <L>/lista_sorgente.txt
/bin/zsh <L>/script/corri_sequenze.sh 3 <L>/lista_sorgente.txt
/bin/zsh <L>/script/analizza_sorgente.sh ; /bin/zsh <L>/script/calore_tutte.sh
/usr/bin/python3 -I <L>/script/fmea_l69.py ; /usr/bin/python3 -I <L>/script/fmea_oggi.py
/usr/bin/python3 -I <L>/script/copertura.py <R>
/bin/zsh <L>/script/analizza_l69.sh <nome> <etichetta> ...    # le opzioni: an_, confronto_, calore_<nome>
```
