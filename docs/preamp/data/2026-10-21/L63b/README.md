# L63b — dati

Lo schematico completo della scheda audio. Report: `docs/preamp/reports/2026-10-21-L63b-schematico-scheda-audio.md`.

## Che cosa c'è

| File | Che cosa |
|---|---|
| `script/sabotaggi.py` | 22 sabotaggi della pagina ripiegata: il manifesto espanso manomesso (A), il ripiegamento sulla pagina vera col kit manomesso o su copie della netlist rotte apposta (B), piccoli disegni sbagliati (C), i 14 di L63a (D). Esce 0 se li prende tutti |

Il resto del lotto non è un dato: è la pagina e il kit, versionati in `docs/preamp/schematic/`
(`audio_draw.py` → `audio.svg`, `audio.pdf`, `audio.manifest.json`; `sheet_kit.py`).

## Come si rifà

```sh
/Users/roberto/EDA/env/venv/bin/python3 /Users/roberto/EDA/docs/preamp/schematic/audio_draw.py
/usr/bin/python3 /Users/roberto/EDA/scripts/check_schematic.py \
    /Users/roberto/EDA/docs/preamp/schematic/audio.manifest.json \
    /Users/roberto/EDA/circuits/preamp/preamp_audio.net
/Users/roberto/EDA/env/venv/bin/python3 /Users/roberto/EDA/docs/preamp/data/2026-10-21/L63b/script/sabotaggi.py
```

Le copie della netlist rotte apposta e le pagine dei sabotaggi vanno in una cartella temporanea, non
nel repo.

## Esito (2026-10-21, dal worktree)

- `audio_draw.py`: 138 parti disegnate (il blocco 59, la scheda 79), 491 espanse, 404 terminali, 41
  piedini liberi con la croce, 123 reti in 236 pezzi, 100 giunzioni; nessun rifiuto.
- `check_schematic.py`: 570 dispositivi nella netlist, 570 nel disegno, OK nei due sensi.
- `sabotaggi.py`: 22 su 22 presi.
- `run_tests.sh`: 15 passed / 0 failed.
