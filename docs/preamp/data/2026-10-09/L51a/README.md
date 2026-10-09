# L51a — il dossier rigenerato, la scheda audio: i dati

Sotto, `<L>` è questa cartella e `<R>` la radice del repo. Il circuito è quello di **L48b**
(`c098be70`): dopo, circuito, deck, firmware e modelli non sono cambiati (L49a e L49b hanno
toccato solo `layout/`). Nessuna cifra di questi dati è nuova: la ricorsa serve a che il dossier
legga dati corsi **oggi** sul circuito di oggi, con una seconda strada indipendente.

| Percorso | Cosa |
|---|---|
| `script/ricorsa.sh <fase>` | i 21 deck veloci (la lista di L48b), più `tb_f1_selettore.cir` e le due copie di L48b col bilanciamento (`e5_bilanciamento/tb_e5_bilanciamento.cir`, `v1_bilanciamento/tb_loop_bilanciamento.cir`), con `run_simulation.sh`, 8 in parallelo; rc e durata in `<fase>/esiti.tsv` |
| `dopo/` | la corsa del 2026-10-09: per ogni deck CSV, log e deck risolto (le `.txt` e `.json` grezze in `.gitignore`, come in L42a) |
| `script/confronta.py`, `confronto.txt` | ogni CSV di oggi contro la seconda strada: i 21 deck contro `../../2026-10-07/L48b/regressione/dopo/`, il selettore contro `../../2026-10-06/L48a/misure/tb_f1_selettore/`, le copie contro `L48b/{e5,v1}_bilanciamento/out/`. **252 file su 252 uguali**, 24 deck, nessun rc ≠ 0 |
| `mute/tb_v2_casopeggiore_generato.cir` | il deck V2 rigenerato oggi dal sorgente (`L29c/deck/genera_tb_v2_casopeggiore.py --uscita`): **uguale byte per byte** a `spice/preamp/tb/tb_v2_casopeggiore.cir` |
| `script/mute.sh`, `mute/corse/` | la seconda strada del mute: 21 corse del deck versionato, le celle peggiori di ogni gruppo della matrice di L48b (gruppo 1 B2g, 2 B2g, 3 A, 4 il clic e B2g, 5 A, 6 A) con i loro riferimenti, con `corri.sh` di L29c, la guardia di L47b2b1 e `analizza_par.py`; `analisi.csv`, `manifest_sel.csv`, `tempi.txt`, i log. Le forme d'onda (~14 GB) e i deck che `dividi.py` rigenera sono in `.gitignore` |
| `script/sabotaggi.py`, `sabotaggi.txt` | ogni controllo nuovo di `build_dossier.py` fatto fallire (L42a, L42b, L42d per i loro) |

## Come si rifà

```sh
/bin/zsh <L>/script/ricorsa.sh dopo
/usr/bin/python3 <L>/script/confronta.py
/usr/bin/python3 <R>/docs/preamp/data/2026-09-23/L29c/deck/genera_tb_v2_casopeggiore.py --uscita <L>/mute/tb_v2_casopeggiore_generato.cir
/bin/zsh <L>/script/mute.sh
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html
/usr/bin/python3 <L>/script/sabotaggi.py
```

Le corse del mute sono lunghe: la più lunga, `g10sempre_1k_iii`, oltre un'ora.
