# L70 — le due semplificazioni: i dati

Lo studio di **S1** (la ritenuta dopo un guasto di rail sostituita da fusibili) e **S2** (togliere il
rivelatore di rete), proposte dall'architetto in L65 (`reports/2026-11-04-L65-architetto-avversariale.md`).
Il report è `reports/2026-11-04-L70-semplificazioni.md`.

## Che cosa c'è

| Percorso | Che cos'è |
|---|---|
| `psu/`, `script/` (salvo i file nuovi sotto), `carico.txt`, `lista_l64b.txt`, `mappa.csv`, `ponte/estrai_ponte.py`, `deck/controlla_deck.py` | Il banco di L69b, **copiato** (L69b non si riesegue sul posto) |
| `psu/genera_tb_psu.py` | Quello di L69b con **due cambi**, solo sulle varianti: senza Q513/Q514 (S1) non misura `at_bn` né la scrive (`_SENZA_RITENUTA`); senza Q504 (S2) la lista di default delle sonde di corrente lo salta. Sul netlist di oggi il deck è **quello di L69b riga per riga** (controllato su `perdita`, a meno dei percorsi) |
| `varianti/fai_varianti.py`, `varianti.txt`, `psu_<v>.net`, `psu_<v>.py` | Le quattro varianti di `circuits/preamp/psu.py` per sostituzione di testo: `oggi` (ridà `psu.net` a meno dei puntatori di SKiDL al file sorgente), `s2` (−10 parti), `s1` (−7), `s1s2` (−17). I fusibili **non** sono parti: la posizione A è la corrente del secondario di T1 (`--sonda-t2`), la B quella di R550 / R551 |
| `script/lista_l70.py`, `lista_l70.txt` | 144 corse: i 32 eventi sani di L69b × tre varianti; i corti lato grezzo (C501, C502, C509, C510, i quattro diodi di D501) a rete −10/0/+10 % su `oggi` e `s1` |
| `lista_c145.txt` | La cella RC di un blocco in corto (`f_c145_corto_*`), su `oggi` e `s1`: 6 corse |
| `an_l70.csv` | `psu/analizza_mc.py` (le colonne di `an_l64b.csv` di L69b) su tutte le corse |
| `script/fusibili.py`, `fusibili.csv` | Fusibile in posizione A e B, R550 / R551: sano, regime dopo il guasto, picco, I²t, energia, accensione |
| `script/cella_s1.py`, `cella_s1.csv` | La cella RC in corto a regime: U501, R550, le due 20 Ω |
| `script/fmea_conta.py`, `fmea_l70.csv`, `fmea_l70_conti.csv` | La FMEA di oggi (L69, 692 righe, 47 alte) riga per riga per variante: tolta, scesa, resta |
| `calore/` | **La scheda audio con un rail solo**, il banco del calore di L66 (blocco uguale byte per byte a `spice/preamp/gain_block.subckt`), nelle cinque posizioni: `rif` e quattro modi (rail − a 0 V / aperto, rail + a 0 V / aperto). `calore_rail.csv` coi dissipatori di ADR-099 |
| `script/ponte_l70.sh`, `ponte/s1s2_*`, `corse/s1s2_*`, `tabella_s1s2_*.csv` | La catena al jack (il ponte di L69b) sulle sequenze di S1+S2, alle tre reti |
| `vendor/fuse/schurter/FST_5x20/`, `vendor/resistor/vishay/PR01-PR03/` | I datasheet del fusibile e della resistenza antifiamma, con la provenienza |

## Come si rifà

```sh
L=docs/preamp/data/2026-11-04/L70
/usr/bin/python3 -I $L/varianti/fai_varianti.py
/usr/bin/python3 -I $L/script/lista_l70.py
/bin/zsh $L/script/corri_sequenze.sh 3 $L/lista_l70.txt
/usr/bin/nice -n 10 /bin/zsh $L/psu/corri_lista_an.sh $L/lista_c145.txt 3
/usr/bin/python3 -I $L/calore/prepara.py ; /bin/zsh $L/calore/corri.sh 3 ; /usr/bin/python3 -I $L/calore/analizza.py
/bin/zsh $L/script/analizza_l70.sh ; /usr/bin/python3 -I $L/script/cella_s1.py ; /usr/bin/python3 -I $L/script/fmea_conta.py
/bin/zsh $L/script/ponte_l70.sh s1s2
```

Tutte le corse rc 0, 150 sequenze con `ok.txt`, nessun ripiego; le 25 del calore rc 0; le tre catene rc 0.
