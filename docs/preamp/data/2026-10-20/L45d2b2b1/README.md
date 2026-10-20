# L45d2b2b1 — i diodi della tenuta e il regolatore negativo (2026-10-20)

Prima parte di **L45d2b2b**, divisa dall'utente all'inizio («Due parti»: b1 i diodi della tenuta e
U502, ADR-074; b2 il comando e i 5 V, ADR-075). Report
`../../../reports/2026-10-20-L45d2b2b1-diodi-tenuta.md`; decisione **ADR-093**; **NC-073 aperta**,
NC-042 e NC-072 avanzano.

`<A>` = questa cartella, `<R>` = la radice del repo. Gli script ricavano la radice dalla propria
posizione (questa cartella è alla stessa profondità di `../L45d2b2a/`).

## Il circuito

| File | Cosa |
|---|---|
| `circuits/preamp/psu.py` | ADR-093: D515 / D516 (SB340) in serie fra il piedino d'uscita di U501 / U502 (`VPLUS_REG` / `VMINUS_REG`) e il rail; SENSE di U501 e il partitore di U502 sul piedino; U501 a 15,3 V (piedini ANY-OUT 11 e 12 a massa), R501 120 kΩ (−15,28 V); C511 / C512 sul piedino; D510 + D513 e D511 + D514, due SB340 in parallelo dal piedino d'uscita all'ingresso al posto del 1N5819. 120 → 124 parti |
| `docs/preamp/schematic/psu_blocks_draw.py` | il diodo in serie nel riquadro del regolatore; le asserzioni: l'uscita sul piedino, uno Schottky in serie, due sul piedino; il partitore di U502 dal piedino. La netlist di prima (`falsi/psu_senza_diodi_in_serie.net`) è rifiutata |

## Il banco

`psu/` è il banco dell'alimentatore di L45d2b2a, **copiato** (le intestazioni di `genera_tb_psu.py` e
`modi.py` dichiarano ogni cambio):

| Cambio | Perché |
|---|---|
| `modi.py`: `RIGHE_074` (C501, C502, C509, C510, D501 a–d in corto) a rete −10 / 0 / +10 % (eventi `musm10`, `mus`, `musp10`), e D510 / D511 in corto | le righe di ADR-074 di L45c1, sui nodi di oggi; C509 / C510 sul piedino (in L45c1 «uguali» al serbatoio) |
| le sonde dei guasti: l'ingresso al piedino (`raw_pr` / `raw_mr`), la corrente di ogni Schottky (una sorgente da 0 V in serie, solo nei casi di guasto), i piedini d'uscita | l'uscita contro l'ingresso **al piedino**, i diodi contro i loro limiti |
| `--file-carico` | il controllo sul carico di L45c1 |
| `--variante uscita`, `--senso rail/piedino`, `--dvset`, `--dserie`, `--dclamp`, `--valore` | le opzioni di ADR-074 senza toccare il sorgente |
| il modello `DSB340` e `TPS7A4701 15.3V` quando la netlist li ha; la potenza a regime al piedino col diodo della netlist | il banco sul sorgente nuovo |

Senza opzioni, sulla netlist di prima del lotto, il deck `rete` è quello di L45d2b2a riga per riga
(salvo i percorsi).

**Il modello dell'SB340** (Vishay 88719 Rev 13-Aug-13, fig. 3, tipico a 25 °C): Is 8,7e-5 A, N 1,47,
Rs 0,0136 Ω, dai tre punti 0,1 A 0,27 V, 1 A 0,37 V, 10 A 0,58 V letti a occhio dalla curva
(±0,03–0,05 V) dall'agente bom-component-manager. Dichiarato, non un modello del costruttore.
Il 1N5819 sulla curva di Vishay 88525: Is 1e-3, N 2,5, Rs 0,022 (non usato; il banco tiene `DSCH`).

## I controlli

| Cosa | Esito |
|---|---|
| `controllo_l45c1.csv` / `.txt`: la netlist di prima di ADR-092 (`../L45d2b2a/falsi/psu_senza_r550_r551.net`) con `--ss no --cap-audio no --bobine g6k --file-carico` di L45c1 | C501 e C502 in corto: tempi uguali, uscita oltre l'ingresso **1,7562 / 1,7609 V** come L45c1; la sonda nuova dice 25,4 A in D510 / D511 |
| la catena audio sugli stessi due casi (`corse/k_l45c1_100k/`) | C501 letto fino ai rimbalzi **9,017 mV** (L45c1 9,0); C502 0,2455 mV (L45c1 0,2353: la scheda audio di oggi) |
| `rete/oggi` contro `../L45d2b2a/rete/rpre_sorgente` | deck uguale riga per riga salvo i percorsi |

## Le corse

| Etichetta | Cosa | Analisi |
|---|---|---|
| `seq/oggi/` | le 26 righe sul circuito di L45d2b2a (C502 a rete nominale non converge con nessuno dei due metodi a TE + 61 ms: le due reti a fianco lo racchiudono) | `analisi_oggi.csv` |
| `seq/uscita_dsch/` | il diodo in serie col regolatore che regola il rail, modello generico | `analisi_uscita_dsch.csv` |
| `seq/clamp_sb340/` | il circuito di oggi con D510 / D511 SB340 | `analisi_clamp_sb340.csv` |
| `seq/serie_47_sb340/`, `seq/serie_33_sb340/` | SB340 in serie e sul piedino, retroazione sul piedino, +0,3 V; 4,7 / 3,3 Ω | `analisi_serie_*.csv` |
| `seq/serie_47_sb340x2/` | come sopra con due SB340 sul piedino | `analisi_serie_47_sb340x2.csv` |
| `seq/sorgente/` | **il sorgente dopo ADR-093** | `analisi_sorgente.csv` |
| `confronto_opzioni.csv` | il caso peggiore di ogni grandezza sulle 24 righe, per opzione | |
| `rete/<etichetta>/`, `rete_opzioni.csv` | regime e perdita di rete a −10 / 0 / +10 % per opzione e sul sorgente | `psu/riassunto_rete_074.py` |
| `seq/acc_serie_47/`, `seq/acc_sorgente/`, `accensione_*.csv` | l'accensione a rete nominale e −10 % | `psu/misura_ss.py` |
| `corse/<etichetta>_100k/` | la catena audio (ponte → V2 `--matrice l41c`, 100 kΩ) per oggi, le due forme in serie e il sorgente | `analisi.csv`, `aborto.csv` |

Le forme d'onda (`*_out.txt`, i `.dat`), i deck rigenerati e le corse V2 non stanno nel repository: si
rifanno.

## Rifare

```sh
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/usr/bin/python3 -I <A>/psu/lista_074.py > <A>/lista_074.txt
# il controllo
/bin/zsh <A>/psu/uno.sh k_l45c1 f_c501_corto_mus --net <R>/docs/preamp/data/2026-10-20/L45d2b2a/falsi/psu_senza_r550_r551.net --ss no --cap-audio no --bobine g6k --file-carico <R>/docs/preamp/data/2026-10-13/L45c1/carico.txt
/usr/bin/python3 -I <A>/script/analizza_074.py <A>/seq/k_l45c1 <A>/controllo_l45c1.csv f_c501_corto_mus f_c502_corto_mus
/usr/bin/python3 -I <A>/script/confronta_l45c1.py <A>/controllo_l45c1.csv <A>/controllo_l45c1.txt
# le opzioni (la netlist di prima del lotto: <A>/falsi/psu_senza_diodi_in_serie.net con --net)
/bin/zsh <A>/psu/corri_lista.sh <A>/lista_074.txt oggi --net <A>/falsi/psu_senza_diodi_in_serie.net
/bin/zsh <A>/psu/corri_opzioni_074.sh          # sulla netlist corrente: col sorgente nuovo va aggiunto --net come sopra alle sue righe
/bin/zsh <A>/psu/corri_rete_074.sh <etichetta> [opzioni]
# il sorgente
/bin/zsh <A>/psu/corri_finale_074.sh
/usr/bin/python3 -I <A>/script/analizza_074.py <A>/seq/sorgente <A>/analisi_sorgente.csv @<A>/lista_074.txt
/usr/bin/python3 -I <A>/script/confronto_opzioni.py <A>/confronto_opzioni.csv oggi=<A>/analisi_oggi.csv ... sorgente=<A>/analisi_sorgente.csv
/usr/bin/python3 -I <A>/psu/riassunto_rete_074.py <A>/rete_opzioni.csv <A>/rete/oggi ... <A>/rete/sorgente
/usr/bin/python3 -I <A>/psu/misura_ss.py <A>/accensione_sorgente.csv <A>/seq/acc_sorgente/accensione <A>/seq/acc_sorgente/accensione_m10
# la catena audio
/bin/zsh <A>/script/catena_074.sh sorgente 100k f_c501_corto_mus f_c502_corto_mus f_c509_corto_mus f_c510_corto_mus f_d501a_corto_mus f_d501b_corto_mus f_d501c_corto_mus f_d501d_corto_mus
```

Le opzioni furono corse prima del sorgente nuovo, sulla netlist di allora (la stessa di `falsi/`).
