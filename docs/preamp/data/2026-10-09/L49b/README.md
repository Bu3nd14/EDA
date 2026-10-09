# L49b — dati dell'alimentatore di prova e dell'assieme nel contenitore

Report: `reports/2026-10-09-L49b-alimentatore-assieme.md`. Sorgenti: `layout/preamp/psu/` (la
scheda) e `layout/preamp/assembly/` (la pianta).

## La scheda dell'alimentatore — `psu/`

```sh
/bin/zsh layout/preamp/psu/run.sh <out_dir> 100 3.0 8.0 4.0 1.0
#   altezza 100 mm, 3,0 mm fra le parti, 8,0 mm di fascia di rete, 4,0 mm nella logica, rail 1,0 mm
/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 \
    layout/preamp/psu/measure.py <out_dir>
/bin/zsh layout/preamp/psu/images.sh <out_dir>/psu_routed.kicad_pcb <out_dir>
```

**Freerouting non è ripetibile, e qui conta.** Con questi parametri la corsa consegnata (la 34 del
report) chiude a **0 / 0**; la sua replica (35) ne lascia **2** aperte, e la stessa disposizione
con 3,5 mm nella logica ne ha lasciate 1 e 4 (31–33). Per questo i file qui sotto **sono quelli
della corsa 34, copiati**, non rigenerati: una nuova corsa può dare 0–4 connessioni aperte, sempre
con 0 violazioni. La DRC qui sotto è stata rifatta sulla copia (`run_drc.sh`, exit 0).

| File | Cosa |
|---|---|
| `psu_routed.kicad_pcb` / `.kicad_pro` | la scheda piazzata e sbrogliata. **Le classi e il foro minimo stanno nel `.kicad_pro`**: senza, la DRC torna ai valori di KiCad (limitations #52) |
| `psu_routed.kicad_dru` | le regole su misura: rete ↔ bassa tensione ≥ 6,4 mm (la copia di `layout/preamp/psu/psu.kicad_dru`) |
| `psu.dsn`, `psu.ses`, `freerouting.log` | il giro con Freerouting 2.4.1 (restringimento automatico acceso, fan-out spento) |
| `drc_psu_routed.json` | la DRC: **0 violazioni, 0 connessioni mancanti** |
| `placement.json` | parametri, misura della scheda, rettangoli dei gruppi, sovrapposizioni (0) |
| `escape.json` | le uscite dai piedini dei tre regolatori e di NT501, e le vie d'ancoraggio (34 elementi) |
| `classes.json` | le larghezze delle classi con cui è stata fatta la scheda |
| `measure.json` | densità, rame per classe, **i tratti ristretti** uno per uno, **le distanze di rete** misurate sul rame |
| `placement_3d_top.png` | render 3D dall'alto |
| `routing_both.*`, `routing_top.*`, `routing_bottom.*` | il rame, PDF vettoriale e PNG a 200 dpi |

Freerouting, nel suo log, chiude con «16 unrouted and 54 violations»: **non è il verdetto**. Le 54
violazioni sono i fori da 0,2 mm delle vie termiche nell'impronta dei regolatori (fissi, Freerouting
non li sa giudicare); le 16 connessioni sono quelle che passano per le uscite fisse di `escape.py`,
che Freerouting non conta come collegamenti. La DRC di KiCad le vede collegate: 0 / 0.

## L'assieme — `assembly/`

```sh
/Users/roberto/EDA/env/venv/bin/python3 layout/preamp/assembly/floorplan.py \
    docs/preamp/data/2026-10-09/L49a/placement.json docs/preamp/data/2026-10-09/L49b/psu \
    docs/preamp/data/2026-10-09/L49b/assembly
```

| File | Cosa |
|---|---|
| `assembly_A_tutto_sul_fondo.png` / `.pdf` | **la variante che ci sta**: pianta quotata e sezione laterale |
| `assembly_A0_come_L49a.png` / `.pdf` | la lettura di L49a (pannelli come fasce a tutta altezza): non ci sta |
| `assembly_B_alimentatore_sotto.png` / `.pdf` | l'alimentatore sotto la scheda audio: non ci sta |
| `assembly.json` | ogni controllo, le altezze ipotizzate, le distanze dei toroidali dagli ingressi e dal volume |

## Le misure che il repo non fissava (lette il 2026-10-09)

Nessuna cifra a memoria. Quasi tutte vengono da pagine di distributori: sono **involucri** per la
prova, non le parti della distinta (che è di G2).

| Cosa | Misura | Fonte |
|---|---|---|
| T1, toroidale 2×15 V 50 VA | **Ø 87,3 × 41,7 mm** (la più grande trovata), vite M5 | Talema 0050P1-2-015K, RS (`uk.rs-online.com/web/p/toroidal-transformers/2238617`) |
| | 82,4 × 37,5 mm | Talema 70083K, DigiKey |
| | Ø 80 × 33 / Ø 84 × 34 mm | RS PRO 1730102; Talema 55121 (Electrokit) |
| T2, piccolo toroidale 12 V | **Ø 60 × 26,3 mm** (15 VA) | Talema 70050K, Distrelec / DigiKey |
| | 55 × 55 × 26 mm (10 VA) | Amgis L01-6342, DigiKey |
| Elettrolitico 4700 µF 35 V | **D16 × 35,5 mm** (in D16 esiste: i più comuni sono D18) | Nichicon UVY1V472MHD, RS; Panasonic ECA1VM472 e Nichicon UVZ1V472MHD sono D18 × 35,5 |
| Presa IEC con fusibile e interruttore bipolare | flangia 65 × 31,6 mm, foratura 47,1 × 28,1, corpo **33,1 mm** dietro il pannello, faston 4,8 mm; conforme a IEC/UL 62368-1 | Schurter DD11, `schurter.com/en/datasheet/typ_DD11.pdf` |
| RCA da pannello | flangia 31 × 26 mm, lunghezza 28,3 mm | Neutrik NF2D, Adam Hall |
| Volume ALPS RK27 stereo | 27 × 25,3 × 24,5 mm | Audiophonics |
| Bilanciamento Alpha RV16 doppio | corpo 17 × 11,5 mm | CE Distribution |
| Commutatore Lorlin CK a un wafer | Ø 27,5 mm stampato; 18,1 mm dietro il pannello | Lorlin CKS (scheda tecnica); RS, CK1061 |
| Distanze di rete, 230 V, PD2, gruppo IIIb | superficiali **2,5 mm** base / **5,0** rinforzato (IEC 62368-1 tab. 17, **lette da fonti secondarie**); **3,2 mm** base da una tabella IEC 60664-1 a 250 V; in aria 1,5 / 3,0 mm (2,5 kV, cat. II) | EEVblog, TI SLUP421, Power Electronic Tips, In Compliance; la norma è a pagamento e non è stata letta |

**La prova usa la cifra più severa**: 2 × 3,2 = **6,4 mm** fra rete e bassa tensione. `SAFETY.md`
resta «norma da identificare e confermare prima di G2».
