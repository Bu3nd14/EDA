# Dopo L57b — il modello del costruttore del BAV199 nel limitatore (2026-10-25)

Report: `docs/preamp/reports/2026-10-25-dopo-L57b-modello-bav199.md`. Sessione «hi-fi preamp dopo L57b».
L'utente ha incollato il modello SPICE del BAV199 di **Diodes Incorporated** (`DI_BAV199`); sostituisce
la stima dal datasheet di L57b (`models/diodes/bav199_fit.lib`) e i conti si rifanno.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `vendor/diodes/diodes_inc/BAV199/` | Il file dell'utente, verbatim, con hash e provenienza (congelato) |
| `models/diodes/bav199.lib` | La copia byte per byte; ricetta `tb_bav199` in `validate_models.py` |
| `script/tb_bav199.py.txt`, `script/insert_tb_bav199_di.py` | Il testo della ricetta e lo script che l'ha inserita (una volta) |
| `script/rigenera.sh` | Il subckt e la netlist dal sorgente (`DIODE_MODEL = "DI_BAV199"`) |
| `script/regressione.sh dopo`, `confronta_regressione.py`, `verdetti_regressione.py` | I quattro deck dell'ingresso; il «prima» è il «dopo» di L57b; i verdetti nelle tre fasi |
| `script/limitatore.py` | Come in L57b; i modelli alternativi col nome `DI_BAV199` in `modelli/`: `di` (il default, il costruttore), `fit` (la stima di L57b), `1n4148` (il caso noto di L57a), `di2c` (capacità doppia) |
| `script/genera.py`, `dist.py`, `spl.py`, `nodeset.py`, `leggi_costo.py`, `sintesi.py`, `esegui.py` | I banchi di L57b |
| `script/verifica_noto.py`, `script/verifica_fit.py` | I due casi noti: L57a (256 / 256) e la stima di L57b (256 / 256) |
| `script/corri_tutto.sh` | I gruppi in fila: `noto`, `reti`, `mute`, il nodeset, `costo` |
| `script/rif_corrente.py`, `rca/rif/` | La corrente nei due riferimenti durante l'RCA a caldo (rete +10 %, classe II): 2,79 mA di picco nell'LM4040, la media il solo bias |
| `docs/preamp/schematic/audio_draw.py` | Due sinonimi in più: la netlist rigenerata ha scelto l'altro nome di due coppie di reti unite (limitations #74) |
| `rca/`, `costo/`, `regressione/`, `sintesi.csv` | Le corse e la sintesi |

## Rifare

```sh
S=/Users/roberto/EDA/docs/preamp/data/2026-10-25/dopo-L57b/script
/bin/zsh $S/rigenera.sh
/bin/zsh $S/regressione.sh dopo
/usr/bin/python3 $S/confronta_regressione.py
/usr/bin/python3 $S/verdetti_regressione.py
/bin/zsh $S/corri_tutto.sh
/usr/bin/python3 $S/verifica_noto.py
/usr/bin/python3 $S/verifica_fit.py
/usr/bin/python3 $S/leggi_costo.py
/usr/bin/python3 $S/sintesi.py
```

## Ipotesi dichiarate

- Quelle di L57b, salvo il diodo. Il modello è del **secondo costruttore** del tipo (Diodes Inc.); la
  parte scelta in L57b è il BAV199 sul datasheet di Nexperia, la cui riga dei limiti (85 V, 160 mA,
  3 µs) coincide con quella del modello. Il datasheet di Diodes Inc. non è nel repo. Un esemplare
  tipico: nessuna dispersione fra pezzi, nessun parametro di temperatura oltre i predefiniti.
- Il file viene dall'utente per incolla: l'identità byte per byte con quello di diodes.com non è
  verificata (gli spazi in coda o i fine riga possono essere cambiati); i parametri sì.
- I riferimenti nei banchi restano `INREF_EQ` (limitations #76).
