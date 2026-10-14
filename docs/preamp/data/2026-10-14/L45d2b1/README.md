# L45d2b1 — il rivelatore di continua sulle uscite dei blocchi (2026-10-14)

Prima parte di **L45d2b** (scelta dell'utente all'inizio della sessione, «Tre parti»): il
rivelatore di **ADR-072**, da solo. Report `../../../reports/2026-10-14-L45d2b1-rivelatore-continua.md`;
la decisione di realizzazione è **ADR-079**. I diodi della tenuta, il regolatore negativo, il comando,
i 5 V e i massimi del blocco sono di L45d2b2; i guasti rifatti nella forma di ADR-070 di L45d2b3.

`<A>` = questa cartella. Gli script ricavano la radice del repo dalla propria posizione.

## Il circuito

| File | Cosa |
|---|---|
| `circuits/preamp/dc_detector.py` | il rivelatore: sorgente, valori con le ragioni, e `spice/preamp/dc_detector.subckt` |
| `circuits/preamp/preamp_audio.py` | le sei prese (F1, F2, B per canale) e J4 a quattro pin, `DC_FLT` al pin 4 |
| `circuits/preamp/psu.py` | R548, C535, D525–D527 (i tre gate), R549 verso PA1 |
| `firmware/preamp_timer/` | `DC_FLT_IN` su PA1, la sequenza 4.9 della specifica, il test `guasto_dc` e i falsi 31–34 |
| `scripts/check_psu_harness.py` | J4 pin 4 = `DC_FLT` |

## I file

| Cartella / file | Cosa |
|---|---|
| `studio/studio_filtro.py` | perché non un filtro: 1–4 poli contro un gradino di 0,95 V e un basso a 20 Hz da 14 V |
| `studio/dist_dc.py` | la continua finale dei 148 guasti di L45b fuori da P10 (15 sotto 1 V, 57 sotto 2 V) |
| `scelte/dimensiona.py`, `dimensiona.csv` | la finestra, T_HOLD, il filtro, l'inibizione, lo stadio d'uscita, con le tolleranze |
| `netlist/confronta.py` | due netlist a confronto per contenuto (i tstamp cambiano a ogni generazione) |
| `netlist/falsi/` | la netlist audio di prima (J4 a tre pin): `check_psu_harness.py` deve rifiutarla |
| `banco/inc/cmpoc.lib` | il comparatore a collettore aperto, **comportamentale e dichiarato** |
| `banco/script/genera_rivelatore.py` | i deck: `prova`, `musica`, `rail`, `accensione`, `guasti POS [--gain G] [--ccout] [--tfine T] [--gear] [MODO...]` |
| `banco/script/genera_tutto.sh` | tutti i deck e la lista unica, le corse lente (R120 in corto, Q133 e R135 nel blocco A) fino a 0,6 s come in L45a |
| `banco/script/genera_corte2.sh`, `genera_r120.sh`, `genera_gear.sh`, `genera_rshunt.sh` | le corse che non finiscono, rifatte: Q133 / R135 fino a 0,6 s nelle altre posizioni; R120 in corto fino a 0,45 s (~2 ms simulati al minuto); R131, Q146, JQ110A, R138 col metodo gear; Q146 in corto con `rshunt = 1e10` (si fermava all'istante dello scatto) |
| `banco/guasti.csv`, `guasti.md` | la sintesi: **0 guasti fuori da P10** in sette posizioni (erano 45–53 per posizione), il peggiore 90,0 ms |
| `banco/script/verifica_prova.py`, `banco/prova.csv` | lo strumento contro il calcolo a mano: 12 casi |
| `banco/script/analizza_guasti.sh`, `sintesi_guasti.py` | P10 di L45b (invariato) su ogni guasto, e la sintesi `banco/guasti.csv`, `guasti.md` |
| `banco/script/medie.py` | le medie a finestre delle uscite in una corsa (l'accensione, il clip) |
| `banco/piccole.csv` | la musica, il filo di un rail aperto e l'accensione: scatto sì / no |
| `psu/` | il banco dell'alimentatore, **copiato da L45c2** (sotto), più la primitiva `riv` |
| `psu/analizza_riv.py`, `psu_riv.csv` | l'ordine mute → VRELAY → toroidale, la scarica dei rail, il calore di R144 |
| `psu/misura_accensione.py` | i rail all'accensione e i jack: l'inibizione contro il banco |

## Il controllo

- **Lo strumento su un caso noto** (`verifica_prova.py`): il rivelatore da solo, gradini di
  ±0,95 / ±14,9 / 0,70 V, senza VPLUS, sotto soglia (0,50 V), la musica di prova a 20 Hz da 14 V e
  un treno a 10 Hz che deve scattare, e un guasto già presente all'accensione: 12 su 12 entro 3 ms
  dalla formula chiusa di `dimensiona.py` (il resto è il diodo e la corrente di TMAX).
- **Il banco dell'alimentatore copiato**: prima di ogni cambio al generatore, sul `psu.net` di oggi
  (coi diodi del rivelatore), `perdita` dà il CSV del firmware al punto fisso **identico byte per
  byte** a quello di L56: con `DC_FLT` alta i tre diodi non fanno niente.
- **`check_psu_harness.py`** rifiuta la netlist audio di prima contro il `psu.net` nuovo (J4 a tre
  pin, rc = 1); i test del firmware: 84 controlli, 23 falsi su 23 fanno fallire il loro test.

## Rifare

```sh
/usr/bin/python3 -I <A>/scelte/dimensiona.py --prova
/usr/bin/python3 -I <A>/scelte/dimensiona.py
/Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/dc_detector.py      # dalla radice
/Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/preamp_audio.py
/Users/roberto/EDA/env/venv/bin/python3 circuits/preamp/psu.py
/bin/zsh <A>/banco/script/genera_tutto.sh                                 # 807 deck, una lista
/bin/zsh <A>/banco/script/corri.sh <A>/banco/deck/lista_tutto.txt          # ~1,5 h, 8 alla volta;
        # le corse lente oltre ~10 min si fermano (pkill -f con la coda del percorso del deck) e si
        # rifanno coi quattro genera_*.sh qui sotto e corri.sh sulle loro liste
/bin/zsh <A>/banco/script/genera_corte2.sh
/bin/zsh <A>/banco/script/genera_r120.sh
/bin/zsh <A>/banco/script/genera_gear.sh
/bin/zsh <A>/banco/script/genera_rshunt.sh
/usr/bin/python3 -I <A>/banco/script/genera_rivelatore.py guasti F1 --ccout --rshunt Q146_ce
/usr/bin/python3 -I <A>/banco/script/verifica_prova.py <A>/banco/run/prova <A>/banco/prova.csv
/usr/bin/python3 -I <A>/banco/script/riassunto_piccole.py <A>/banco
/bin/zsh <A>/banco/script/analizza_guasti.sh                              # ~1 h
/usr/bin/python3 -I <A>/banco/script/sintesi_guasti.py <A>/banco
/bin/zsh <A>/psu/corri_seq.sh --solo-compila
/bin/zsh <A>/psu/corri_seq.sh f_riv_linea_mus                              # e f_riv_c145_mus,
                                                                         # f_riv_c145sola_mus, accensione
/usr/bin/python3 -I <A>/psu/analizza_riv.py <A>/seq <A>/psu_riv.csv f_riv_linea_mus f_riv_c145_mus f_riv_c145sola_mus
/usr/bin/python3 -I <A>/psu/misura_accensione.py <A>/seq/accensione
```

Le corse (`banco/run/`, `seq/`) si rigenerano; nel repository restano i deck, le sintesi e i CSV.
