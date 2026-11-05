# L73a — la prova di spazio a due strati sul circuito di oggi

Report: `reports/2026-11-05-L73a-prova-di-spazio-due-strati.md`. Gli script sono **copie** di
`layout/preamp/` (L49a / L49b) cambiate dove dicono le intestazioni; le originali non si toccano.

## Rigenerare

```sh
K=/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9
D=docs/preamp/data/2026-11-05/L73
/usr/bin/python3 $D/script/footprints/make_stax_fp.py $D/footprints/L73.pretty
L73_PACK=height /bin/zsh $D/script/audio/run.sh $D/audio 1.0 80 3.0 40      # ~4 min di kinet2pcb, poi il router
$K $D/script/audio/heights.py $D/audio 10
$K $D/script/audio/fill.py $D/audio
/bin/zsh $D/script/psu/run.sh $D/psu 110 3.0 8.0 3.0 1.0 1.0
/Users/roberto/EDA/env/venv/bin/python3 $D/script/assembly/floorplan.py $D/audio/placement.json $D/psu $D/assembly
```

Le scansioni di misura (solo piazzamento): `script/audio/sweep_size.sh <dir>` e
`script/psu/sweep_size.sh <dir>`, su una cartella con la scheda grezza.

## Che cosa cambia rispetto a L49a / L49b

| Script | Cambio |
|---|---|
| `audio/make_board.py` | netlist di oggi (653 parti); i condensatori di segnale col **pezzo più grande della lista ammessa** (P6, ADR-122), la Stax con l'impronta sua (`footprints/`); **i transistor SMD mappati sulle piazzole** (`pinmap.py`) |
| `pinmap.py` | **il rilievo**: `Device:Q_NPN` / `Q_PNP` hanno piedini B / C / E, le impronte SOT-23 / SOT-223 piazzole 1 / 2 / 3: kinet2pcb non collega nulla e non dà errore. Le piedinature lette dai datasheet in `vendor/` (Diodes Inc. MMBT5551 / 5401, DZT5551 / 5401): SOT-23 1 = B, 2 = E, 3 = C; SOT-223 1 = B, 2 = C (e la linguetta), 3 = E. 72 transistor |
| `audio/place.py` | gruppi di oggi (test point dei blocchi, limitatore d'ingresso); il sensore di bias è il DZT5551 del moltiplicatore; la distanza fra i dissipatori; `L73_PACK=height` (più alti prima) |
| `audio/heights.py`, `fill.py` | nuovi: le altezze per fasce di profondità (con la fonte di ciascuna), il riempimento per gruppo |
| `psu/make_board.py`, `place.py` | le reti dei regolatori di oggi (RAW_PR / RAW_MR, VPLUS_REG / VMINUS_REG); R550 / R551, D513–D516, U512, C536 nei gruppi |
| `assembly/floorplan.py` | la scheda audio a **fasce di altezza** (`heights.json`), non un'altezza unica |

## I numeri

| Che cosa | Valore |
|---|---|
| Scheda audio, connettività come L49a (gap 1,0, blocco 85) | 409,7 × 268,1 mm, riempimento 0,33 |
| Scheda audio, **più alti prima** (gap 1,0, blocco 80) | **392,6 × 198,3 mm**, 778 cm², riempimento **0,46** (parti 359 cm²) |
| Sbroglio a 2 strati (Freerouting 2.4.1, 40 passi) | 6154 tracce, 419 vie; DRC **1 connessione aperta** (K3 piedino 6), **2 distanze 0,248 mm** (Q122, Q621, SOT-223), 34 serigrafie, 18 avvisi di libreria |
| Dissipatori | 16, distanza minima fra i contorni 10,9 mm (coppia NPN / PNP dello stesso blocco) |
| Sensore di bias – MJE15032 | 19,2 mm centro-centro (L49a: 10,9 col MMBT5551, senza dissipatore) |
| Alimentatore (189 parti, 118 in L49b) | 306,8 × 100 / 246,9 × 110 / 226,9 × 120 mm (logica a 4,0 / 3,0 / 3,0) |
| Pesante 3U, tutto sul fondo | **mancano 18,3 mm** di profondità; 3,6 mm d'altezza sotto i RCA (C162 / C362, 32 mm) |
| Alimentatore sotto la scheda audio | fino a 21 mm contro la IEC e 20 contro i RCA |

## File

| File | Cosa |
|---|---|
| `audio/audio_routed.kicad_pcb` / `.kicad_pro` | la scheda piazzata e sbrogliata |
| `audio/drc_audio_routed.json` | la DRC |
| `audio/placement.json`, `heights.json`, `fill.json`, `footprint_swaps.json` | piazzamento, altezze, riempimento, impronte e piedini cambiati |
| `audio/audio.dsn`, `audio.ses`, `freerouting.log` | il giro del router |
| `assembly/` | la pianta: PNG / PDF per variante e `assembly.json` |
| `footprints/L73.pretty/` | l'impronta di prova della Stax (passo 22,5, «STAX 1uF 5% ONLY») |
