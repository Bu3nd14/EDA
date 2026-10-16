# L60c2 — la Stax col condensatore da 1 µF prima di K3, K3 un TE Axicom IM06TS (2026-10-15/16)

Report `../../../reports/2026-10-15-L60c2-stax-condensatore-e-rele.md`. Decisioni ADR-085 (il relè)
e ADR-086 (la ridondanza nel blocco, il tetto della Stax a 150 ms). `<C>` = questa cartella, `<R>` la
radice del repo.

## I file

| File | Cosa |
|---|---|
| `script/im_pinmap_svg.py` | la seconda gamba della piedinatura dell'IM06: le coordinate vettoriali della p. 5 del datasheet |
| `script/confronta_netlist.py` | due netlist confrontate per significato (parti, valori, impronte, gruppi di pin) |
| `falsi/falsi.py`, `falsi/verdetti.txt` | 7 sabotaggi di K3 contro `check_relay_safe_state.py`: 7 su 7 presi |
| `script/genera_L60c2.py` | il banco: quello di L60c1 importato (G0 = il circuito, verificato sulla netlist); gruppi `g0`, `e9`, `guasti` (107 modi di L45a × C nominale e +5 %), 237 deck in `deck/` |
| `script/uno.sh`, `script/corri.sh` | le corse, 8 alla volta, esiti in `run/esiti.tsv` |
| `script/analizza_L60c2.py` | `v2.csv`, `caldo.csv`, `e9.csv` |
| `p10.csv` | `analizza_p10.py` di L45b sulle corse di P10 (`run/g0/G0_CTRL_*`, `G0_pin_*`, `run/guasti/*`) |
| `script/sintesi_p10.py`, `p10_stax.csv` | P10 sul jack della Stax contro 150 ms (ADR-086) e 125 ms (colonna `fuori_125`) |
| `script/onde_fuori.py`, `onde_fuori.txt`, `script/salti.py` | come sono fatti i guasti fuori (rampe, oscillazione) |
| `script/ricorsa_q122.py`, `p10_ricorse.csv` | Q122 in corto in A col gear: 118 / 124 ms |
| `script/prepara_rete.py`, `script/corri_rete.sh`, `rete/` | la tenuta di `VRELAY` sul banco di L51b con la sola `RMUTECOIL` cambiata |
| `v2/` | la matrice di V2 dal deck versionato rigenerato: `manifest_sel.csv`, `manifest_finale.csv` (senza le 6 corse ferme), `analisi.csv`, `verdetto.csv`, `verdetto_per_uscita.txt`, `tempi.txt` |
| `script/sonda_v2.py`, `script/corri_sonda_v2.sh`, `script/corri_gear.sh`, `script/manifesto_gear.py`, `v2/gear/` | le corse ferme col contatto a 0,1 pF e col gear, coi riferimenti col gear; il confronto gear / default (`confronto_gear_g10mai_1k_iii.txt`, `script/confronta_gear.py`) |
| `script/controllo_principale.py`, `script/corri_controllo.sh`, `script/finestre_jack.py`, `v2/controllo_principale/` | il riferimento «sempre in mute» senza le due righe di L60c2: il jack principale uguale (NC-070) |
| `script/verdetto_per_uscita.py` | il verdetto diviso per uscita, contro L48b |
| `NEXT-SESSION-L45d2b2.md` | il prompt pronto di L45d2b2, aggiornato con ADR-081…086, per dopo L60d |

Le forme d'onda e le corse (`run/`, decine di GB) non stanno nel repository: si rifanno.

## Rifare

```sh
/Users/roberto/EDA/env/venv/bin/python3 <R>/circuits/preamp/preamp_audio.py
/usr/bin/python3 <C>/script/confronta_netlist.py <netlist di prima> <R>/circuits/preamp/preamp_audio.net
/usr/bin/python3 <C>/falsi/falsi.py <R> <cartella di lavoro>
/usr/bin/python3 -I <C>/script/genera_L60c2.py
/bin/zsh <C>/script/corri.sh <C>/deck/lista.txt                 # ~10 min, 237 corse
/usr/bin/python3 -I <C>/script/analizza_L60c2.py
/usr/bin/python3 -I <R>/docs/preamp/data/2026-10-13/L45b/script/analizza_p10.py <C>/p10.csv <C>/run/g0/G0_CTRL_*/ <C>/run/g0/G0_pin_*/ <C>/run/guasti/*/
/usr/bin/python3 -I <C>/script/sintesi_p10.py
/usr/bin/python3 -I <C>/script/prepara_rete.py
/bin/zsh <C>/script/corri_rete.sh
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py
/bin/zsh <R>/docs/preamp/data/2026-09-23/L29c/script/corri.sh <C>/run/v2 <R>/spice/preamp/tb/tb_v2_casopeggiore.cir '.*' 7   # ~8 h
/usr/bin/python3 <R>/docs/preamp/data/2026-10-03/L47b2b1/script/guardia_v2.py <C>/run/v2
/usr/bin/python3 <R>/docs/preamp/data/2026-10-07/L48b/v2/filtra_manifesto.py <C>/run/v2/manifest_sel.csv <C>/run/v2/manifest_finale.csv gm3x10_1k_iii gm10x3_1k_iii gm10x0_1k_iii mh01_1k_iii mev_1k_iii off_r10m_d20_iii
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/script/analizza_par.py <C>/run/v2/manifest_finale.csv <C>/run/v2 <C>/run/v2/analisi.csv 8
/usr/bin/python3 <R>/docs/preamp/data/2026-10-05/L47c2b1/script/verdetto.py <C>/run/v2/manifest_finale.csv <C>/run/v2/analisi.csv <C>/run/v2/verdetto.csv
```
