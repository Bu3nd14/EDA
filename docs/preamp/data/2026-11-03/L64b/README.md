# L64b — il dossier rigenerato, l'alimentatore e il temporizzatore: i dati

La seconda delle tre parti di L64 (l'utente, 2026-11-02: «Three parts, like last time»). Il circuito è
quello di `main` dopo L64a (00911506b): **non cambia**. `psu.py` è quello di L58b (6a8e626), la
scheda audio quella di L66 / L67. Sotto, `<L>` è questa cartella e `<R>` la radice del repo. Tutte le
corse a priorità bassa, al più due di queste insieme (l'utente, 2026-11-03: «non caricare troppo la
CPU … ci sono altre sessioni di claude running oggi»).

## Il primo giro

`rifiuti_primo_giro.txt`: `build_dossier.py` con `PARTI = ("audio", "alimentatore")` sul `main` di
L64a, prima di ogni cambio. **57 rifiuti, tutti dell'alimentatore** (la scheda audio passa):

- **R512 a 220 kΩ in ogni caso dei log di L51b** (la guardia di limitations #34): da ADR-094 R512 è la
  metà di R_MD, 110 kΩ. Dati vecchi, non un difetto.
- **I deck di L51b non si rigenerano più**: il `genera_tb_psu.py` di L51b rifiuta la netlist di oggi
  (`TP501`, i test point di ADR-107); quello di L58b sì, col temporizzatore del sorgente.
- **Le 15 sequenze del firmware e i 4 deck del temporizzatore col micro**: il micro non c'è più
  (ADR-102). Il loro posto lo prendono le sequenze del temporizzatore a comparatori (sotto).
- **Il calore**: la scheda audio di oggi pesa 9,2227 W (tb_op di L64a), L51b 8,93; il carico di L51b
  293,62 / 301,79 mA contro 303,3288 / 311,5182 di oggi.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `carico.txt` | Il carico della scheda audio sul banco: 8 × i rail di `tb_op` di L64a, il resto di `VRELAY` di L48a, il metodo gear |
| `psu/` | Il banco dell'alimentatore di L58b, copiato. **Un cambio**: in `modi.py` i guasti della coppia (`RIGHE_SERIE`, `RIGHE_SERIE_R`) coi nomi del sorgente di oggi (`q501_mid`, `q501_g`, `q509_g`, R586, R587 al posto di `n501m`, `g501a`, `g501b`, `RQ501G`, `RQ509G` della variante `--q501serie`), gli stessi nodi: è la mappa di `sorgente_uguale.py` di L58b |
| `script/lista.py`, `lista_l64b.txt`, `mappa.csv` | Le sequenze sul circuito di oggi: le 31 di L54b3b (`lista_v25.txt`), le 25 + 8 + 6 di L58b (`lista_l58b`, `lista_sorg`, `lista_rete`), le 80 della coppia (`lista_s1m`, `lista_s1m2`, senza `--q501serie`: la coppia è nel sorgente), più `corto_u503` e `perdita_min` a ±10 % per il ponte. Lo stesso caso con le stesse opzioni corre una volta: **117 corse per 138 righe dei lotti**. **Fuori** le 12 righe di Q501 di prima della coppia (`f_q501_corto_*`, `f_q501_gd_*`): sul deck di oggi «corto» cortocircuita la coppia intera (due guasti) e «gd» unisce due nodi che non sono gate e drain di nessun transistor |
| `script/corri_sequenze.sh`, `seq/` | Le corse (`psu/corri_lista_an.sh`, 2 alla volta); un `ok.txt`, un deck e un log per corsa |
| `script/controlla_ok.py` | Ogni `ok.txt` con le opzioni esatte della sua riga: la lista dei mancanti è stata riscritta una volta mentre `xargs` la leggeva, e una riga è arrivata tagliata («struttore»); quella corsa e le otto saltate sono state rifatte |
| `script/analizza.sh`, `an_l64b.csv`, `censimento_psu.csv` | `psu/analizza_mc.py --te=3.0` (le colonne di L54b3b) e `psu/censimento.py` (lo standby a regime, le bobine del mute) |
| `script/confronta.py`, `confronto_seq.csv` | **La seconda strada** delle sequenze: ogni corsa contro le righe dei lotti che rappresenta, colonna per colonna. Contro L58b (lo stesso `psu.py`) all'unità della cifra; contro L54b3b e le righe di L58b sul sorgente di prima della coppia, in più lo 0,1 ms / 0,1 mV della variante (L58b); i deck di oggi contro quelli di L58b, uguali a meno del carico (la coppia letta coi nomi della variante su ogni riga, o tolta). **4255 celle, 4002 identiche, 253 entro, 0 fuori; 107 deck uguali.** Al primo giro due celle fuori, `on_min` (il minimo di `VRELAY_EN` letto dalla `.meas` sui punti del transitorio) a 3,1 mV con la tolleranza di 1e-4 V: lo stesso caso sano dà 4,4533 V a rete nominale e 4,4564 a ±10 %; la tolleranza è ora 0,01 V come le altre tensioni |
| `script/sabotaggi.py`, `sabotaggi.txt` | Ogni controllo nuovo di `build_dossier.py` fatto fallire: **21 su 21** |
| `rete/`, `guasti/`, `script/banchi.sh` | I banchi di L51b sull'alimentatore di oggi (`--nome rete | guasti --timer sorgente --tss 3.0` con le opzioni di L58b); `analisi.csv` da `psu/analizza.py <banco> 3.0` (l'evento a 3 s: senza l'argomento i tempi escono spostati di 1000 ms) |
| `termica/` | `genera_calore.py` (da L51b, con le voci nuove: R550 / R551, gli SB340, i diodi inversi; medie su 2,5–3,0 s), `tb_calore.cir/.log`, `stima_telaio_l64b.py/.txt` |
| `lista_consumo.txt`, `consumo.txt` | Lo standby da T2: `accensione --sonda-t2` alle tre reti, `psu/potenza_t2.py` su 2,5–3,0 s (il metodo di L54b2) |
| `ponte/`, `deck/`, `corse/`, `tabella_*.csv`, `script/ponte.sh`, `script/catena_audio.sh` | La catena al jack di L54b2 sulla scheda audio di oggi: il ponte dalle sequenze di oggi, il deck di V2 `--matrice l41c`, 18 corse per rete (2 alla volta invece di 9) |
| `script/coda.sh` | Quello che segue le sequenze, in coda: i mancanti, lo standby, il ponte e la catena |

Le forme d'onda (`*_out.txt`, ~45 MB a sequenza; `rete/*.txt`, `guasti/*.txt`, ~180 MB a caso) e le
corse grezze non stanno nel repository (`.gitignore`).

## Come si rifà

```sh
/usr/bin/python3 -I <L>/script/lista.py
/bin/zsh <L>/script/corri_sequenze.sh 2
/usr/bin/python3 -I <L>/script/controlla_ok.py
/bin/zsh <L>/script/banchi.sh                       # rete, guasti, calore
/usr/bin/python3 -I <L>/psu/analizza.py <L>/rete 3.0 ; /usr/bin/python3 -I <L>/psu/analizza.py <L>/guasti 3.0
/usr/bin/python3 -I <L>/termica/stima_telaio_l64b.py > <L>/termica/stima_telaio_l64b.txt
/bin/zsh <L>/script/coda.sh                         # i mancanti, lo standby, il ponte, la catena
/bin/zsh <L>/script/analizza.sh                     # an_l64b.csv, censimento_psu.csv, la seconda strada
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py --standalone <fuori dal repo>/dossier.html
```
