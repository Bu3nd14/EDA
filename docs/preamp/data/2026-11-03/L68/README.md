# L68 — la FMEA del temporizzatore a comparatori: i dati

Il lotto di NC-078 (l'utente, L64c: «Non conformità, lotto apposta»). Il circuito è quello di `main` dopo
L64c (07c8ee566): **non cambia**. Sotto, `<L>` è questa cartella e `<R>` la radice del repo. Le corse a
priorità bassa, al più tre insieme (due per la catena, ~1 GB l'una). Report:
`reports/2026-11-03-L68-fmea-temporizzatore.md`.

## Le scelte dell'utente

- la ritenuta cieca (31 righe): **«Accettare come R585»**;
- R572 / R576 in corto, la ritenuta che tiene i 5 V a massa: **«Non conformità maggiore»** (NC-079);
- C545–C547 in corto e TP507 a massa: **«Accettare come C536»**;
- i colpi al jack di J4 PERMIT_CMD e dei test point: **«Accettare tutti»** — ADR-115.

## I conti, prima delle corse

37 parti del temporizzatore → **97 righe** (U513 / U514 / U515: 12 uscite aperte, 12 bloccate basse, 3
alimentazioni perse; Q513 / Q514 6; diodi 10; condensatori 22; resistenze 32). I modi sugli stessi due nodi
sono un caso solo: **79 simulazioni distinte**, ognuna contro gli otto eventi (`EVENTI_L58B`) = **632
corse**. I connettori, **11 righe**: 4 simulazioni contro `muss`, `accs`, `spls`, `inss` (16 corse); J510 =
la perdita di rete, J511 = il primario di T2, J512 = K501 che si apre (TP514). I test point, **17 righe**:
4 sono riferimenti, 13 corse in musica. Più la base in musica (`f_base_niente_muss`) e le due basi di
controllo. Una corsa ~25 s.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `psu/` | Il banco di L64c, copiato. In `modi.py`: `RIGHE_L68` (il temporizzatore, contro `EVENTI_L58B`), `RIGHE_L68C` (i connettori), `RIGHE_L68T` (i test point), `f_base_niente_muss`, `TF["f_r570_corto_perds"]`. In `genera_tb_psu.py` due aggiunte: la primitiva `aperti` (più aperture su nodi diversi: le quattro uscite di un TLV1704 senza alimentazione — col piedino dei 5 V lasciato flottante ngspice si fermava sul comparatore) e `modi.TF` anche sui casi di sequenza. `lista_l68.py`, `confronta_l68.py` (i criteri di L54b3b, la base di ogni evento da `L64b/an_l64b.csv`) |
| `seq/base/` | Le due basi di controllo, `accensione` e `fredda`: **uguali a `an_l64b.csv` colonna per colonna** (`an_base.csv`) |
| `lista_l68.txt`, `lista_prova*.txt`, `lista_resto.txt`, `lista_coda.txt`, `lista_base_muss.txt`, `seq/oggi/` | **662 corse**, tutte con `ok.txt` e le opzioni della loro riga (`script/controlla_ok.py`), **nessun ripiego numerico**. Due prove rifiutate al primo giro e rifatte (l'alimentazione persa, il pin di J4 su MUTE_SW: `BSW3` e le bobine entrano nel deck dopo il guasto, il pin si apre dal lato dell'alimentatore); `f_r570_corto_perds` si fermava a TE + 0,98 s a tutto spento, accorciata a TE + 0,9 |
| `script/analizza.sh`, `an_l68.csv`, `an_base.csv`, `confronto_l68.csv`, `confronto_l68.txt`, `riassunto.txt` | `psu/analizza_mc.py` e il confronto con la corsa sana di ogni evento; `script/riassunto.py` per caso. `arm_pg_ms −1383,5` nelle accensioni a freddo è l'artefatto di limitations #85, tolto dalle righe |
| `script/calore_tutte.sh`, `calore_5v.csv` | U504 / U512 su tutte le corse (`calore_5v.py` di L64c). Fuori: C545 in corto 2,99 W, 245 °C; TP507 232 / 132 °C; **R572 / R576 in corto col rail che cade 2,34 / 2,55 W, 205 / 218 °C** (NC-079) |
| `catena/` | La catena al jack di L64c su 20 casi (`catena_l68.sh`, `catena_l68_resto.sh`; i criteri in `tabella.py` scritti prima). **Il controllo `corto_u503` ridà 6,492 mV.** 41 corse su 42; `f_tp501_corto_muss` si ferma 4 ms dopo il corto (il rail + che crolla), dichiarato per simmetria con TP502. `tabella_l68.csv` |
| `script/parti_l68.py`, `script/fmea_l68.py`, `fmea_l68.csv` | Le **125 righe**: 34 alte, 3 medie, 88 basse. Le funzioni e i tassi (`classi_l45c2.py`; il TLV1704 come due doppi; il film come il ceramico; i test point a P 1, dichiarato) |
| `script/fmea_oggi.py`, `fmea_oggi.csv`, `fmea_oggi_conti.csv` | La FMEA di oggi dalle **sei fonti**: **688 righe, 49 alte, 70 medie, 564 basse, 5 escluse** |
| `script/copertura.py`, `copertura.csv` | Dell'alimentatore **0 parti su 187 senza riga** |
| `script/sabotaggi.py`, `sabotaggi.txt` | I sabotaggi di L64a, L64b, L64c (i due su `fmea_oggi.csv` e `copertura.csv` riportati su L68) e sei nuovi |
| `script/guarda.py`, `script/genera_solo.py`, `script/cronometro.sh` | Leggere una corsa a occhio; generare un deck per caso senza correrlo; cronometrare una corsa |

Le forme d'onda (`*_out.txt`), i `.dat` e i deck delle singole corse della catena non stanno nel
repository (`.gitignore`): si rifanno coi comandi sotto (~40 GB per le sequenze).

## Comandi

```sh
/usr/bin/python3 -I <L>/psu/lista_l68.py > <L>/lista_l68.txt
/bin/zsh <L>/script/corri_sequenze.sh 3 <L>/lista_l68.txt
/bin/zsh <L>/script/corri_sequenze.sh 2 <L>/lista_coda.txt ; /usr/bin/python3 -I <L>/script/controlla_ok.py
/bin/zsh <L>/script/analizza.sh ; /usr/bin/python3 -I <L>/script/riassunto.py
/bin/zsh <L>/script/calore_tutte.sh
/bin/zsh <L>/catena/catena_l68.sh ; /bin/zsh <L>/catena/catena_l68_resto.sh   # la guardia rifiuta TP501
/usr/bin/python3 -I <L>/script/fmea_l68.py ; /usr/bin/python3 -I <L>/script/fmea_oggi.py
/usr/bin/python3 -I <L>/script/copertura.py <R>
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py
/usr/bin/python3 <L>/script/sabotaggi.py
```
