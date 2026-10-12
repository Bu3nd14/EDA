# L53 — le misure veloci prima di G1 (2026-10-12)

Report: `../../../reports/2026-10-12-L53-misure-veloci.md`. Cifre di modello (ngspice 47, i modelli
di `models/`); il blocco è `spice/preamp/gain_block_flat.inc` / `gain_block.subckt` di `main` dopo
L52, nessuna modifica al circuito. `<R>` = la radice del repo, `<L>` = questa cartella.

## Le cartelle

| Cartella | Che cosa | Voce |
|---|---|---|
| `rs/` | la THD del blocco contro l'impedenza di sorgente (0 / 1,5 / 2,5 / 5,6 kΩ, più la scansione fine 1–2 kΩ), tre modi, 1 / 10 / 20 kHz, 0,2 e 2 V, a 27, 57 e 80 °C uniformi | NC-055, NC-058 |
| `temp/` | perché la THD cresce col calore: il punto di lavoro (`op_temp.cir`), la sonda per gruppi (`sonda.py`), la corrente di coda (`coda.py`), le giunzioni (`op_cliff.cir`, `giunzioni.py`), l'autoriscaldamento (`autoriscaldamento.py`, `tj.csv`) e la prova del meccanismo con l'RC dell'LS350 a zero | NC-060 |
| `v1/` | V1 del blocco B a caldo, dal deck di L48b, cinque varianti | NC-058 |
| `imd/` | l'intermodulazione CCIF col blocco autoriscaldato | NC-060 |
| `catena/` | V4 sulla catena di un canale (selettore, A, due fisse, trim, C_T, bilanciamento, volume, B) a 27 °C uniformi | NC-055 |
| `rca/` | l'RCA inserito a caldo sull'ingresso selezionato, e i gate del blocco A | NC-059 |

## Le cifre

**`rs/run/sintesi.csv`** (27 °C): la THD cresce con la sorgente, **senza minimo** a R_F = 1,5 kΩ
(il meccanismo di L52 R5 non c'è nella forma attesa); a 0 dB, 20 kHz, 0,2 V: 0,000326 / 0,000446 /
0,000526 / 0,000772 % a 0 / 1,5 / 2,5 / 5,6 kΩ. Dentro V4 su tutti i modi fino a 5,6 kΩ, margine
minimo **2,1 dB** (0 dB, 5,6 kΩ, 2 V). A 57 e 80 °C uniformi fuori, 4–60 volte.

**`temp/`**:
- `op_temp.log`: da 27 a 57 °C la coda 4,51 → 4,39 mA, il VAS 10,7 → 10,4, i finali 20,5 → 21,7 mA;
- `run/sonda/sonda.csv`: a 57 °C, tenuto a 27 °C il solo Q106 (la coda) la THD torna 0,00059 %;
  tenuti a 27 i diodi che lo polarizzano, 0,0090 %; ogni altro gruppo quasi niente;
- `coda.py` (log in `run/coda/`): il gradino, THD piatta sotto ~4,6 mA di coda a 27 °C e ~4,2 mA
  a 57 °C, poi un ordine di grandezza in pochi punti percentuali;
- `giunzioni.py`: lo specchio (Q121B, LS350, RC 231 Ω) ha 0,79 V ai morsetti e ~0,5 V persi in RC:
  la giunzione base-collettore interna è a ~+0,42 V;
- `tj.csv`: le Tj (VAS 77,6 / 84,1 °C, carico del VAS 86,2, coda 53,7 a 27 °C d'aria);
- `run/aut/aut.csv`: con ogni giunzione alla sua Tj, **48 casi su 48 fuori da V4** (27 °C d'aria:
  0,0024–0,012 % a 0,2 V; 57 °C: 0,020–0,078 %); con l'RC dell'LS350 a zero
  (`inc/ls350_rc0.lib`, copia di prova) **24 su 24 dentro**.

**`v1/minimi.txt`**: il controllo ridà 64,42° di L48b; a caldo ≥ 63,72° ovunque. Il guadagno
d'anello a 10 Hz scende da 78,7 a 69,8 dB (57 °C, rame) e 67,7 (piazzola minima): lo specchio in
saturazione.

**`imd/run/t27|t57/distorsione.csv`**: il prodotto a 1 kHz a 0,2 V, −92,9 / −89,8 / −82,8 dB a
27 °C d'aria e −74,6 / −71,5 / −64,5 dB a 57 °C (0 / +3 / +10 dB); era −130,8 / −130,7 / −125,6.

**`catena/run/catena/catena.csv`** (27 °C): 53 su 56 dentro; fuori il principale a volume a metà,
0 e +3 dB, 20 kHz, 0,2 V (0,0010–0,0016 %). Prima corsa scartata (fourier al jack: il transitorio del
4,7 µF a 1 kHz), detto in `genera.py`. A 1 kHz pavimento del metodo ~−110 dB sulle armoniche alte.

**`rca/out/rca_spl.csv`, `rca/out_gate/gate.csv`**: sorgente in classe II, il clip del finale
(~113,8 dB SPL) al volume in cima, 107 dB SPL alla posizione del K11; le fisse +10,9 dB sul K11; il
gate-gate del blocco A a −28,1 V (rottura ±30 V minimo). Sorgente a terra con 0,65 V: 110 dB SPL in
cima.

## Rifare

```sh
# rs (27/57/80 °C), sintesi
/usr/bin/python3 <L>/rs/script/genera.py ; genera.py 57 ; genera.py 80   # uno per volta
/bin/zsh <L>/rs/script/esegui.sh <L>/rs/deck/lista_tutte.txt
/usr/bin/python3 <L>/rs/script/leggi_four.py rs t57 t80
/usr/bin/python3 <L>/rs/script/sintesi.py rs t57 t80
# temp
/bin/zsh <R>/scripts/run_simulation.sh <L>/temp/op_temp.cir <L>/temp/run_op
/usr/bin/python3 <L>/temp/sonda.py ; /bin/zsh <L>/temp/script/esegui.sh <L>/temp/deck/lista_sonda.txt ; /usr/bin/python3 <L>/temp/leggi_sonda.py
/usr/bin/python3 <L>/temp/coda.py ; /bin/zsh <L>/temp/script/esegui.sh <L>/temp/deck/lista_coda.txt
/bin/zsh <R>/scripts/run_simulation.sh <L>/temp/op_cliff.cir <L>/temp/run_cliff ; /usr/bin/python3 <L>/temp/giunzioni.py
/usr/bin/python3 <L>/temp/autoriscaldamento.py ; /bin/zsh <L>/temp/script/esegui.sh <L>/temp/deck/lista_aut.txt
/bin/zsh <L>/temp/script/esegui.sh <L>/temp/deck/lista_rc0.txt ; /usr/bin/python3 <L>/temp/leggi_aut.py
# v1: genera.py, poi run_simulation.sh su ogni <L>/v1/<var>/tb_loop_<var>.cir -> <L>/v1/<var>/out, poi minimi.py
# imd, catena: genera.py, esegui.sh <deck>/lista.txt, leggi_four.py t27 t57 / leggi_catena.py
# rca: genera.py, run_simulation.sh rca.cir -> out, spl.py; gate.py, run_simulation.sh gate.cir -> out_gate
```

`aut_t27_rame_rc0.cir` e `aut_t57_rame_rc0.cir` sono i deck di `autoriscaldamento.py` con il solo
include dell'LS350 cambiato a mano con `sed` (la riga è nel report). `inc/ls350_rc0.lib` e
`inc/mmbt5551_noquasi.lib` sono **copie di prova**, non modelli: non vanno in `models/`.
