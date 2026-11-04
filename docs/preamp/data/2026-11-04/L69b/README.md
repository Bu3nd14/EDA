# L69b — l'evidenza dell'alimentatore e il dossier sul sorgente nuovo: i dati

L69 ha cambiato il circuito (ADR-116: i pull-up di AT_MRQ e di AT_ON in due metà in serie, R572 100 kΩ +
**R588** 100 kΩ, R576 4,99 kΩ + **R589** 4,99 kΩ) e il dossier rifiutava: l'evidenza dell'alimentatore di
L64b (`data/2026-11-03/L64b/`) è del circuito di prima. Qui la stessa evidenza **rifatta sul sorgente di
oggi** (`main` dopo L69, 2dfc25c9c), con gli stessi script e gli stessi nomi dei file. Il circuito **non
cambia** in questo lotto. Sotto, `<L>` è questa cartella e `<R>` la radice del repo. Al più tre
simulazioni insieme, a priorità bassa (la catena al jack due).

## Il primo giro

`rifiuti_primo_giro.txt`: `build_dossier.py --standalone` sul `main` di L69, prima di ogni cambio. **124
rifiuti**, tutti dell'evidenza di L64b sul circuito di prima:

- **120 sequenze** (le 117 di `lista_l64b.txt` più le 3 dello standby): il deck rigenerato dal `psu.net` di
  oggi ha le due metà dei pull-up, quello corso la resistenza unica;
- **i deck dei banchi `rete` e `guasti`**, per la stessa ragione;
- **`parti_schede.csv`** di L64c (due righe): R572 / R576 a metà valore, R588 / R589 in più, 118 / 189.

Il calore e la catena al jack non rifiutavano (i loro deck non portano i pull-up del temporizzatore): si
rifanno lo stesso, perché il dossier legge tutto l'alimentatore da una cartella sola.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `psu/`, `script/`, `termica/`, `deck/`, `ponte/`, `carico.txt`, `lista_consumo.txt` | Il banco di L64b, copiato. Il `modi.py` di L64b non ha righe su R572 / R576 (sono arrivate con L68) e nessuna delle 117 righe tocca i pull-up: niente da portare da `L69/psu/modi.py`. Gli script ricavano la cartella da sé; i nomi dei file restano quelli di L64b (`lista_l64b.txt`, `an_l64b.csv`, `stima_telaio_l64b.txt`), perché è la stessa evidenza e il dossier li legge per nome |
| `script/confronta.py` | La seconda strada contro i lotti (L58b, L54b3b), di L64b; **un cambio**: nei deck di oggi le due metà si leggono come la resistenza unica di L58b (`HALVES`: `RR572 v5 at_mrq_m 100k` + `RR588 at_mrq_m at_mrq 100k` = `RR572 v5 at_mrq 200k`; R576 + R589 = `RR576 v5 vrelay_en 10k`), e rifiuta se le due righe non ci sono una volta o il nodo di mezzo compare altrove. 9,98 kΩ contro 10 kΩ resta nelle cifre, non nel controllo dei deck |
| `script/confronta_l64b.py`, `confronto_l64b.csv` | **La seconda strada contro L64b**: ogni file di risultato di qui contro l'omonimo di L64b, cella per cella (le sequenze, il censimento, lo standby, i banchi, il calore, la catena); ogni cella diversa nel CSV. Esce 1 solo se la struttura non coincide |
| `script/parti_schede.py`, `parti_schede.csv` | Lo script di L64c, copiato e corso qui |
| `script/dopo.sh` | La coda dopo le sequenze: `coda.sh` (2 alla volta) e `banchi.sh` (1) insieme |
| `script/sabotaggi.py`, `sabotaggi.txt` | La lista di L68 (L64a + L64b + L64c + L68) coi file spostati dove il generatore li legge oggi, più i sabotaggi nuovi |

Le forme d'onda e le corse grezze non stanno nel repository (`.gitignore`).

## Come si rifà

```sh
/usr/bin/python3 -I <L>/script/lista.py
/bin/zsh <L>/script/corri_sequenze.sh 3
/bin/zsh <L>/script/dopo.sh                         # i mancanti, lo standby, il ponte, la catena; rete, guasti, calore
/usr/bin/python3 -I <L>/script/controlla_ok.py
/usr/bin/python3 -I <L>/psu/analizza.py <L>/rete 3.0 ; /usr/bin/python3 -I <L>/psu/analizza.py <L>/guasti 3.0
/usr/bin/python3 -I <L>/termica/stima_telaio_l64b.py > <L>/termica/stima_telaio_l64b.txt
/bin/zsh <L>/script/analizza.sh                     # an_l64b.csv, censimento_psu.csv, le due seconde strade
/usr/bin/python3 -I <L>/script/parti_schede.py <R>
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html
/usr/bin/python3 <L>/script/sabotaggi.py
```
