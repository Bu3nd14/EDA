# L29e — la geometria iii nel sorgente (2026-09-25)

Dati del lotto L29e (ADR-044, NC-028). Report: `docs/preamp/reports/2026-09-25-L29e-geometria-iii-sorgente.md`.
Le forme d'onda (`*.dat`) e i deck espansi **non si committano**: si rifanno correndo. Si tengono
manifesti, analisi, verdetti, tempi e log.

## La decisione dell'utente (2026-09-25)

Il bleed dal lato del condensatore: **«Tenerlo»**. 470 k sulle fisse, 220 k sulla principale.

## Le cartelle

| Cartella / file | Cosa |
|---|---|
| `falsi/` | il 2e esteso fatto fallire: `genera_falsi.py`, un `.txt` per variante, `esito.csv` |
| `celle/` | le 5 celle peggiori di L29d2 e i loro riferimenti, sul deck versionato dal sorgente |
| `script/confronto_deck.py` | il deck dal sorgente contro il banco di L29d2, corsa per corsa |
| `script/tabella_sorgente.py` | i verdetti del sorgente contro quelli di L29d2 |
| `tabella_sorgente.csv` | la tabella: 18 righe, 0 fuori criterio, scarto 0 |

## Come si rifà

```sh
# i falsi (la netlist di main: git show 1cb233a:circuits/preamp/preamp_audio.net > <tmp>/main.net)
/usr/bin/python3 falsi/genera_falsi.py <repo>/circuits/preamp/preamp_audio.net <tmp>/main.net <abs>/falsi

# il deck versionato, dalla netlist (default del generatore)
/usr/bin/python3 docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py

# le celle
corri.sh <abs>/celle <repo>/spice/preamp/tb/tb_v2_casopeggiore.cir \
  '^(gm0x10_lz|x01000_dpmaxmax|on_r300p|mh01_1k|mh01_20|g0(mai|sempre)_lz|g10(mai|sempre)_(lz|1k|20)|r(mai|sempre)_g(0|10)t0_dpmaxmax)_iii$' 8
analizza_par.py celle/manifest_sel.csv celle celle/analisi.csv 8
verdetto.py     celle/manifest_sel.csv celle/analisi.csv celle/verdetto.csv
script/tabella_sorgente.py celle/verdetto.csv ../L29d2/matrice/verdetto.csv tabella_sorgente.csv
```

`corri.sh`, `analizza_par.py` e `verdetto.py` sono in `docs/preamp/data/2026-09-23/L29c/script/`.
Tempi: 17 corse in ~14 min con 8 processi; l'analisi in ~3 min.
