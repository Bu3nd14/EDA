# L45d2b2a — la partenza morbida dei regolatori dei rail (2026-10-20)

Prima parte di **L45d2b2**, divisa dall'utente all'inizio («Tre parti»). Report
`../../../reports/2026-10-20-L45d2b2a-partenza-morbida.md`; decisioni **ADR-091** (i condensatori
NR) e **ADR-092** (le resistenze davanti ai regolatori); **NC-063 chiusa**, **NC-072 aperta**.

`<A>` = questa cartella. Gli script ricavano la radice del repo dalla propria posizione.

## Il circuito

| File | Cosa |
|---|---|
| `circuits/preamp/psu.py` | C507 4,7 µF, C508 470 nF (ADR-091); R550 / R551 4,7 Ω, 2 W assiali, e i nodi `RAW_PR` / `RAW_MR` coll'ingresso, l'abilitazione, C509 / C510 e D510 / D511 (ADR-092). 118 → 120 parti |
| `circuits/preamp/gain_block.py` | il commento della cella RC sulla rampa del regolatore positivo |
| `docs/preamp/schematic/psu_blocks_draw.py` | la resistenza davanti a ciascun regolatore nel disegno, con l'asserzione: la netlist di prima (`falsi/psu_senza_r550_r551.net`) è rifiutata |

## I file

| Cartella / file | Cosa |
|---|---|
| `carico.txt` | il carico della scheda audio di oggi (tb_op di L62b: 303,4 / 311,5 mA per rail) |
| `psu/genera_tb_psu.py` | il banco dell'alimentatore, **copiato da L45d2b1**: senza il rivelatore, K3 IM06TS, la partenza morbida (`REGPSS` / `REGMSS`), i condensatori della scheda audio sui rail, `--cnr`, `--rpre`, le misure a regime (l'intestazione elenca tutto) |
| `psu/corri_seq.sh` | una sequenza al punto fisso col firmware: `corri_seq.sh <caso> <etichetta> [opzioni del generatore]` → `seq/<etichetta>/<caso>` |
| `psu/capacita_rail.py` | i condensatori della scheda audio sui rail, da `preamp_audio.net` |
| `psu/misura_ss.py`, `accensione.csv`, `accensione_sorgente.csv` | le rampe, le soglie del firmware, le correnti e gli stati, per corsa |
| `psu/verifica_ss.py`, `verifica_ss.txt` | lo strumento contro le equazioni dei datasheet: 14 rampe entro lo 0,22 %, due sabotaggi presi |
| `psu/termico_avvio.py`, `termico_avvio.csv`, `termico_sorgente.csv` | la stima del calore dei regolatori all'avvio (rete termica a due nodi, ipotesi nell'intestazione) |
| `psu/corri_opzioni.sh`, `seq/{oggi,n1u,p4u7_n470n,p1u_n1u}/` | l'accensione coi condensatori di oggi e con le tre alternative, a rete nominale e −10 % |
| `psu/corri_rpre.sh`, `psu/riassunto_rpre.py`, `rpre.csv`, `rete/rpre_*/` | il calore a regime con 0–5,6 Ω davanti ai regolatori, a rete −10 / 0 / +10 %, e la tenuta |
| `psu/corri_finale.sh`, `seq/sorgente/`, `rete/rpre_sorgente/`, `rete_sorgente.csv` | lo stesso banco sul sorgente nuovo, senza opzioni che sostituiscano la netlist |
| `controllo/k1_ripulito/` | il banco senza le righe del rivelatore, sulla netlist di prima: `accensione` = L45d2b1, `perdita` = L56 e L45d2b1, byte per byte |
| `controllo/k2_prima/`, `controllo/k2_im06/` | con `--ss no --cap-audio no --bobine g6k` l'accensione uguale a k1; con `--bobine im06` la tenuta di `VRELAY_REG` 46,367 ms (L60c2: 46,372) |
| `v2/genera_v2_accensione.py` | V2 all'accensione con le rampe del banco: tre casi al rilascio del firmware (`on_ss_*`), tre col rilascio di L29c (`on_ssl_*`), nominale e coi condensatori a ±20 % in senso opposto |
| `v2/controlla_rampe.py`, `controllo_rampe.txt` | le rampe simulate da V2 contro il banco (limitations #66), il caso di L29c come sabotaggio |
| `v2/analisi.csv`, `v2/verdetto.csv`, `v2/tempi.txt`, `v2/manifest_sel.csv` | l'analisi (`v2_metodo.py`, la media) e il verdetto |
| `falsi/psu_senza_r550_r551.net` | la netlist dell'alimentatore di prima: `psu_blocks_draw.py` la rifiuta |

Le forme d'onda (`*_out.txt`, i `.txt` della rete), le corse di V2 (`run/`) e il deck di V2 generato
non stanno nel repository (~10 GB): si rifanno.

## Rifare

```sh
/usr/bin/python3 -I <A>/psu/capacita_rail.py
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/bin/zsh <A>/psu/corri_opzioni.sh                       # ~10 min, 8 corse
/bin/zsh <A>/psu/corri_rpre.sh                          # ~5 min
/bin/zsh <A>/psu/corri_finale.sh                        # sul sorgente
/usr/bin/python3 -I <A>/psu/verifica_ss.py
/usr/bin/python3 -I <A>/psu/termico_avvio.py <A>/termico_avvio.csv <A>/seq/oggi/accensione <A>/seq/n1u/accensione <A>/seq/p4u7_n470n/accensione <A>/seq/p4u7_n470n/accensione_m10 <A>/seq/p1u_n1u/accensione
/usr/bin/python3 -I <A>/v2/genera_v2_accensione.py
/bin/zsh <R>/docs/preamp/data/2026-09-23/L29c/script/corri.sh <A>/run/v2 <A>/v2/tb_v2_accensione.cir '^(on_ss_.*|on_ssl_.*|on_r300s_iii|g10sempre_lz_iii|g10mai_lz_iii)$' 9
/usr/bin/python3 <R>/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <A>/run/v2
/usr/bin/python3 -I <A>/v2/controlla_rampe.py <A>/run/v2
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <A>/run/v2/manifest_sel.csv <A>/run/v2 <A>/run/v2/analisi.csv 6
/usr/bin/python3 <R>/docs/preamp/data/2026-10-05/L47c2b1/script/verdetto.py <A>/run/v2/manifest_sel.csv <A>/run/v2/analisi.csv <A>/run/v2/verdetto.csv
```

I controlli k1 / k2 girano sulla netlist dell'alimentatore di prima del lotto (`falsi/`, con
`--net`) e col `carico.txt` di L45d2b1.
