# L49a — dati della scheda audio di prova

Report: `reports/2026-10-09-L49a-scheda-audio-prova.md`. Sorgenti: `layout/preamp/audio/`.

## Rigenerare

```sh
/bin/zsh layout/preamp/audio/run.sh docs/preamp/data/2026-10-09/L49a 1.0 85 3.0
/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
    layout/preamp/audio/measure.py docs/preamp/data/2026-10-09/L49a
```

`run.sh` rifiuta di partire se il fan-out di Freerouting non è spento in
`~/Library/Application Support/freerouting/freerouting.json` (limitations #50). Freerouting non è
deterministico da una corsa all'altra: il numero di tracce e di via cambia di poco, l'esito (100 %,
DRC 0 / 0) no — due corse su due con questi parametri (2628 / 114 e 2591 / 117 tracce / via).

## File

| File | Cosa |
|---|---|
| `audio_routed.kicad_pcb` / `.kicad_pro` | la scheda piazzata e sbrogliata (si apre in KiCad) |
| `audio.dsn`, `audio.ses`, `freerouting.log` | il giro con Freerouting 2.4.1 |
| `drc_audio_routed.json` | la DRC di `run_drc.sh`: 0 violazioni, 0 connessioni mancanti |
| `placement.json` | parametri, misura della scheda, rettangoli dei gruppi, coppie termiche, sovrapposizioni (0) |
| `measure.json` | densità, lunghezze delle reti, reti che attraversano la spina (0), rame e via |
| `placement_3d_top.png` | render 3D dall'alto |
| `routing_both.*`, `routing_top.*`, `routing_bottom.*` | il rame, PNG a 200 dpi e PDF vettoriale |

Non versionati (si rigenerano): `audio_raw.*`, `audio_placed.*`, `*.kicad_prl`.

## La scansione delle dimensioni (`sweep_size.sh`, solo piazzamento)

| gap \ blocco | 75 | 80 | 85 | 88 |
|---|---|---|---|---|
| 1,0 | 371,6 × 186,0 | 388,9 × 178,1 | **399,0 × 162,8** | 423,3 × 158,3 |
| 1,2 | 372,7 × 191,0 | 389,3 × 184,8 | 407,8 × 167,2 | 416,6 × 167,2 |
| 1,5 | 379,4 × 200,0 | 395,8 × 192,0 | 416,3 × 182,0 | 421,0 × 173,8 |

Spina a 3,0 mm in tutte. Oltre ~400 mm di larghezza la scheda non lascia gioco fra i fianchi
(415 mm).
