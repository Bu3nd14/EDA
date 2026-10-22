# L45d2b3b2b1 — i rimedi del calore (ADR-099) nel sorgente (2026-10-22)

Prima parte di **L45d2b3b2b** (diviso dall'utente all'inizio, «Due parti»: b1 il sorgente, l'impronta, le
netlist, i disegni, la regressione, V1 e P7; **b2** il calore dei quindici e delle parti nuove, la Stax dei
casi lunghi, la corrente di riposo e V4 a caldo col dissipatore, i «Da riaprire se»). Report
`../../../reports/2026-10-22-L45d2b3b2b1-rimedi-sorgente.md`. `<L>` = questa cartella. Python di banco
con `/usr/bin/python3 -I`.

## Che cosa è cambiato nel circuito

`circuits/preamp/gain_block.py`, le otto istanze:

| Parte | Prima | Ora | Sul banco di L45d2b3b2a (rv2) |
|---|---|---|---|
| R101 | 6,81 kΩ GND–NREF | 3,40 kΩ GND–NREFH, **+ R191** 3,40 kΩ NREFH–NREF | R101 + R162 |
| Q106 (coda) | collettore su SRC | collettore su NTCX, **+ R194** 1 kΩ SRC–NTCX (≥ 0,5 W a 60 °C) | R169 |
| R123 (VAS) | 56 Ω VPF–NVE | 33 Ω VPF–NVS, **+ R192** 22 Ω NVS–NVE, **+ Q193** MMBT5401 (E VPF, B NVS, C NVB) | R167, Q168 |
| Q148 (aiuto dello specchio) | collettore su V− | collettore su NHC, **+ R190** 10 kΩ NHC–V− | R161 |
| Q132 / Q133 (finali) | TO-220-3_Vertical | `preamp:TO-220-3_Vertical_Ohmite_WA-T220-101E` | — |

- **Le sigle nuove partono da base + 90** (sezione 14), non dal contatore: col contatore il blocco A
  arrivava a 163 e il B a 264, sulle parti del canale (R161 la 47 Ω dell'uscita fissa, R261 la 47 Ω
  dell'uscita principale, R163 / R264 i bleed), e SKiDL ha rinominato i doppioni in `R161_1` senza
  errore (prima rigenerazione di questo lotto). x90–x99 è libero su ogni istanza. Il disegno lo sa:
  `sheet_kit.py`, `fold(fixed=90)`; `audio_draw.py`, `left()` esclude x90–x99.
- **L'impronta** (`library/preamp.pretty/`): il TO-220 più i due piedini del dissipatore, dalla land
  pattern Ohmite (`vendor/heatsink/ohmite/WA-T220-101E/sink-w.pdf`, rev 8/21-1, congelato con la
  provenienza): piedini Ø 1,5 mm su fori da 2,0 mm, 12,7 mm fra loro, 4,6 mm dietro la fila dei reofori
  dal lato del tab. Le piazzole si chiamano **B / C / E** come i piedini di `Device:Q_NPN` / `Q_PNP`
  (onsemi MJE15032/D, STYLE 1), e i due piedini del dissipatore sono **C**: al potenziale del
  collettore per costruzione. `script/impronta.py` la carica con pcbnew e controlla le piazzole.
- **Un rilievo per il layout, non di questo lotto**: `Device:Q_NPN` / `Q_PNP` numerano i piedini «B»,
  «C», «E», mentre le impronte KiCad dei transistor (SOT-23, SOT-223, TO-220) hanno piazzole «1», «2»,
  «3»: oggi nessun transistor della netlist si collegherebbe alle sue piazzole. Va risolto prima di
  G2 (una mappa piedini per impronta, o impronte con le piazzole nominate come questa).

## Le verifiche

| Verifica | Esito |
|---|---|
| Il blocco generato contro rv2 (`confronta_rv2.py`) | **coincidono**: 69 righe del subckt e 67 dell'include piatto, a meno delle cinque sigle |
| La netlist del blocco per piedini (`nomi_reti.py`) | 4 reti cambiano piedini (NREF, NVE, SRC, VMINUS: perdono R101, R123, Q106, Q148), 4 nuove (NREFH, NVS, NTCX, NHC), nessun nome cambiato |
| La scheda audio (`parti_nuove.py`, `nomi_reti.py`) | 578 → **618 parti** (5 × 8), nessuna sparita; cambiano solo le 8 R101 (6,81k → 3,40k), le 8 R123 (56 → 33) e l'impronta dei 16 finali; 25 reti cambiano piedini (3 per istanza + VMINUS), 32 nuove; **2 nomi cambiati** con gli stessi piedini (#74): `L_ATT_W` → `BL_IN`, `BR_IN` → `R_ATT_W`, dichiarati in `audio_draw.py` (`SINONIMI`) |
| L'impronta (`impronta.py`, pcbnew) | 5 piazzole: B, C, E sui reofori (fori 1,3 mm), due C sul dissipatore (fori 2,0 mm) a 12,7 mm, 4,6 mm dietro i reofori; courtyard 18,9 × 16,6 mm |
| I tre disegni | blocco 67 / 67 dispositivi, 149 / 149 terminali; scheda 618 / 618; alimentatore invariato (`check_schematic.py` OK sui tre) |
| La regressione dei 21 deck (`regressione.sh`) | **21 su 21 rc 0** |
| … contro rv2 (`confronta_regressione.py`, `riassunto_rv2.py`) | 17 deck su 18 confrontabili **entro 1e-3** su ogni misura; P7 (`tb_mute_corto`) 536 misure oltre 1e-3 su 27 550, le più grandi sui minimi di corrente del finale spento (classe B): l'ordine delle righe del netlist cambia l'arrotondamento del transitorio. Le potenze di P7 entro lo **0,12 %** |
| … contro il blocco di main (`margini.py`, `margini.csv`) | **V1**, il margine di fase minimo: blocco A 43,11 → **43,64°**, buffer fisso 43,18 → 43,71°, `tb_loop` 47,18 → 47,57°, anello con I_DSS 64,09 → 64,25°; rumore e E3 entro 2e-5 |
| **P7** (`p7.py`, `p7_sorgente.csv`; 60 °C d'aria) | nessuna parte fuori. Finale PNP 0,522 → **0,404 W**, 85 °C nudo, **70 °C col dissipatore**; NPN 82 / 69 °C; Q148 0,046 → 0,0067 W, 63 °C; R123 0,0059 W; le parti nuove R190 0,024, R194 0,020, R191 0,014, R192 0,004 W, Q193 0,0043 W, 62 °C |
| `run_tests.sh` | **15 passed / 0 failed** |

**I deck canonici toccati.** `tb_mute_corto.cir` (P7): la potenza di R123 era i² × 56 scritta a mano,
ora × 33, e il deck scrive `tb_mute_corto_parti.csv` con Q146, Q148, R123, R126 e le cinque parti
nuove (ricavato da `p7_deck.py` dal deck di rv2). `tb_idss_op_noise.cir`: la Vce di Q106 era
v(src) − v(nte), che col collettore su NTCX avrebbe contato anche la caduta su R194 (#22, il secondo
modo: il nome esiste ma non è più la cosa); ora v(ntcx) − v(nte).

## Rifare

```sh
/Users/roberto/Applications/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 <L>/script/impronta.py
/bin/zsh <L>/script/rigenera.sh
/usr/bin/python3 -I <L>/script/confronta_rv2.py
/usr/bin/python3 -I <L>/script/parti_nuove.py <L>/prima/preamp_audio.net circuits/preamp/preamp_audio.net
/usr/bin/python3 -I docs/preamp/data/2026-10-22/L45d2b3b1/script/nomi_reti.py <L>/prima/gain_block.net circuits/preamp/gain_block.net R190,R191,R192,Q193,R194
/usr/bin/python3 -I docs/preamp/data/2026-10-22/L45d2b3b1/script/nomi_reti.py <L>/prima/preamp_audio.net circuits/preamp/preamp_audio.net <le 40 sigle di parti_nuove.py>
/Users/roberto/EDA/env/venv/bin/python3 docs/preamp/schematic/gain_block_draw.py      # e audio_draw.py, psu_draw.py
/usr/bin/python3 -I <L>/script/p7_deck.py          # una volta: riscrive spice/preamp/tb/tb_mute_corto.cir
/bin/zsh <L>/script/regressione.sh
/usr/bin/python3 -I <L>/script/confronta_regressione.py
/usr/bin/python3 -I <L>/script/riassunto_rv2.py
/usr/bin/python3 -I <L>/script/margini.py
/usr/bin/python3 -I <L>/script/p7.py
/usr/bin/python3 -I <L>/script/pulisci.py          # le forme d'onda che si rifanno
```

`prima/` tiene le netlist, il blocco e i due deck di `main` 23fca7fb. Le corse (`regressione/dopo/`) stanno
qui per i `.log` e i `.csv`; le forme d'onda grandi no.
