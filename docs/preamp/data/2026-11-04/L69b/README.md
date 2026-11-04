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

## Le corse

Il 2026-11-04, 09:04–09:32: **117 sequenze** (3 alla volta, ~24 s l'una da sola), poi insieme lo standby
(3), il ponte e la catena al jack (18 corse per rete, 2 alla volta) e i banchi `rete`, `guasti` e il
calore (1 alla volta). **Tutte rc 0**; `controlla_ok.py`: ogni `ok.txt` con le opzioni della sua riga.
Nessuna lista riscritta mentre `xargs` la leggeva (la lista corsa era una copia ferma).

## La seconda strada contro i lotti (`confronta.py`)

Al primo giro **68 celle fuori** contro L58b, tutte in tre colonne: `t_arm_ms` (34), `arm_pg_ms` (26),
`bn_max` (8) — l'armo della ritenuta e la sua base, le colonne che leggono AT_ON. Il meccanismo, misurato
(`script/armo.py` → `armo.txt`, sulla forma d'onda dell'accensione di oggi): AT_ON alto 4,4712 V, 51,0 µA nel
pull-up; 20 Ω in meno (10 kΩ → 9,98 kΩ) alzano AT_ON di **1,02 mV**; AT_T2S si carica da AT_ON (R580 2,7 MΩ /
C552 1 µF) fino a VREF 2,47 V, e 1 mV in più anticipa l'armo di **0,76 ms** — misurati −0,6 / −0,7. La base
della ritenuta, su AT_ON attraverso Q514, si sposta di 0,3 mV. A queste tre colonne sole lo scarto di
ADR-116 in più (1 ms, 0,5 mV), scritto in `toll()`; nient'altro. Dopo: **4255 celle, 3772 identiche, 483
entro, 0 fuori; 107 deck di L58b uguali a quelli di oggi** a meno del carico e delle due metà.

## La seconda strada contro L64b (`confronta_l64b.py`)

**7578 celle, 386 diverse** (`confronto_l64b.csv`); la struttura (file, righe, colonne) coincide. Le
cifre del report di L64b, alla cifra stampata, sono le stesse: la tenuta di `VRELAY_REG` **50,3 / 109,6 /
169,1 ms**, il permissivo **39,6 ms**, la musica **612,8 ms** dopo il buco, K501 **75,6 ms** dopo il
permissivo allo spegnimento, al jack U501 spento **32,2 dB SPL** e la perdita di rete a −10 % **+4,3 dB
SPL**, il calore **17,68 / 15,42 / 19,98 W** (la stima del telaio identica, 0 numeri diversi). Le celle
diverse, per gruppo:

| Celle | Dove | Scarto | Perché |
|---|---|---|---|
| 94 | `on_min` (il minimo di AT_ON = VRELAY_EN) | −2,4 … +0,9 mV | è il nodo del pull-up; e la `.meas` sui punti del transitorio prende due valori col passo (L64b: 4,4533 / 4,4564 V lo stesso caso) |
| 50 | `t_arm_ms`, `arm_pg_ms` | −0,6 / −0,7 ms | l'armo da AT_ON, `armo.txt` (sopra) |
| 40 | `bn_max` (la base della ritenuta) | −0,1 … +0,4 mV | su AT_ON attraverso Q514 |
| 56 | `dvm_mv`, `dvp_mv` | — | `0.0` → `-0.0`: il segno di uno zero |
| 62 | `t_gain_ms`, `t_k501_ms`, `k_perm_ms`, `t_fpgt_ms`, `v5_min`, `rawv_max` | 0,1 ms; 1 mV | l'ultima cifra stampata. Non ho provato la causa (i passi del transitorio cambiano con la matrice) |
| 49 | i banchi `rete` e `guasti` | ≤ 0,03 ms; una cella −0,29 ms | l'ultima cifra dei tempi al microsecondo; la cella: `vr80_hold_ms` di `perdita_senza_rivelatore_m10`, 346,99 → 346,70 ms (0,08 %), una coda lenta di `VRELAY` che passa l'80 %, molto sopra P9 |
| 32 | la catena al jack | pochi nV | `spegnimento_l` 3,542 → 3,686 nV al jack principale, −55,6 → −55,2 dB SPL, contro un criterio di 100 µV |
| 3 | lo standby | +0,02 mW | 115,86 / 129,76 / 143,86 mW (L64b 115,84 / 129,74 / 143,84) |

## Il dossier

`build_dossier.py`: `L64B` → `L69B` (questa cartella), `PSU_DA` al 2026-11-04 (ogni dato di L64b sulla prima
strada è rifiutato), `PARTI_SCHEDE` di qui, le scritte («L58b sullo stesso circuito» non è più vero), e un
controllo nuovo: `confronta_l64b.py` rieseguito su una copia, `confronto_l64b.csv` uguale byte per byte,
le celle diverse contate in pagina. **«OK: tutti i controlli incrociati sono passati»**, 11 s.

**Sabotaggi 67 su 67** (`sabotaggi.txt`): i 61 di L68 (L64a, L64b, L64c, L68) coi file spostati, più sei
nuovi (una metà di un pull-up cambiata nel deck corso, la lettura delle due metà in `confronta.py`, il
dossier ripuntato sui dati di L64b, `confronto_l64b.csv` riscritto, due righe di L69 nella FMEA). Al primo
giro 61 su 67: tre testi da sabotare portavano le cifre di L64b (129,74 mW, 3,542 nV, la potenza del
calore a quattro decimali), riportati su quelle di oggi; **due di L68 passavano**, perché toccavano le
righe di R572 / R576 in corto (NC-079), che da L69 sono sostituite da `fmea_l69.csv` e non entrano più
nella FMEA di oggi — riportati su una riga di L68 ancora viva; uno mio toccava la priorità di prima del
rimedio invece di quella di dopo.

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
