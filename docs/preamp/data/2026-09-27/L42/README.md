# L42a — il dossier rigenerato, la scheda audio (2026-09-27)

Dati del lotto L42a. Il dossier è `docs/preamp/dossier/index.html`, generato da
`docs/preamp/dossier/build_dossier.py`: questa cartella è ciò che legge, più le sue seconde strade.

## Le decisioni dell'utente (2026-09-27), prima di scrivere codice

| Domanda | Risposta |
|---|---|
| Divisione | **L42a scheda audio, L42b alimentatore** |
| Da dove le curve (L40 le aveva tolte) | **ricorsa dei 21 deck veloci**, seconda strada contro i log di L40 |
| Il mute nel dossier | **tabella di sintesi** e **grafico del profilo v4** (niente confronto delle geometrie, niente matrice completa) |
| Lo schema a blocchi | **esteso** `preamp_blocks_draw.py`, un solo diagramma |

## Le cartelle

| Percorso | Cosa |
|---|---|
| `dopo/` | i 21 deck veloci di `spice/preamp/tb/` (l'elenco di `L40/script/deck_veloci.txt`) corsi sul `main` di L28, rc 0 tutti (`esiti.tsv`). Tolti prima del commit: i `.json` e i `.txt` (doppioni dei `.csv`), `tb_switch_v2.csv` e `tb_mute_corto_trans_*.csv` (forme d'onda che il dossier non legge) |
| `mute/` | la cella `mh01_1k_iii` e i suoi due riferimenti, dal deck versionato `tb_v2_casopeggiore.cir`: `analisi.csv` (v2_metodo.py analizza), `profilo.csv` (il livello al jack principale ogni ms), manifesto e tempi. I `.dat` (3 GB) non si committano |
| `script/esegui.sh` | la ricorsa dei 21 deck, 8 in parallelo |
| `script/profilo_mute.py` | la curva del livello, con le funzioni di `scripts/v2_metodo.py` |
| `script/e4_l42.py` | copia di `e4.py` di L13 con due modifiche dichiarate nel docstring: le print spezzate ricucite (limitations #37), il controllo G (numeri noti dei segnaposto) tolto |
| `script/sabotaggi.py`, `sabotaggi.txt` | 15 sabotaggi, uno per controllo nuovo del generatore: 15 su 15 caduti, e il generatore sui file veri esce 0 |

## Come si rifà

```sh
/bin/zsh docs/preamp/data/2026-09-27/L42/script/esegui.sh                      # ~35 s
/bin/zsh docs/preamp/data/2026-09-23/L29c/script/corri.sh <abs>/mute \
    <repo>/spice/preamp/tb/tb_v2_casopeggiore.cir '^(mh01_1k|g10(mai|sempre)_1k)_iii$' 3   # ~10 min
/usr/bin/python3 scripts/v2_metodo.py analizza <abs>/mute/manifest_sel.csv <abs>/mute mute/analisi.csv
/usr/bin/python3 docs/preamp/data/2026-09-27/L42/script/profilo_mute.py \
    <abs>/mute/manifest_sel.csv <abs>/mute mh01_1k_iii mute/profilo.csv
/usr/bin/python3 docs/preamp/dossier/build_dossier.py
/usr/bin/python3 docs/preamp/data/2026-09-27/L42/script/sabotaggi.py
```

## Cosa si è trovato

- **Oggi = L40.** Le 7720 righe di risultato dei 14 deck che il dossier legge coincidono con
  quelle di L40 (scarto 0), le 12 tabelle che L40 ha tenuto coincidono byte per byte; la cella
  del mute rifatta oggi ridà l'analisi di L29e riga per riga (S 7,163 / 5,445 dB).
- **Il generatore non girava più su `main`** da L39: il deck d'esplorazione degli spigoli di V1
  (`toll_L16`) includeva i segnaposto, e la provenienza rifiutava. Gli spigoli non sono stati
  rifatti coi modelli del costruttore, e la pagina lo dice.
- **Limitations #37**: una Note del gmin stepping spezza una `print` nel log, alla stessa riga in
  L40 e oggi.
- **S del mute con la cima a 12 mA (ADR-050) non è misurato**: la matrice di L29d2, le celle di
  L29e e la curva sono corse coi LED a 20 mA, letti dalla tabella del deck. ADR-050 ha rifatto E3 ed
  E5, non S. È scritto nel dossier; è materia per la revisione di L43.
