# L29b — serie graduale più derivazione graduale al jack, con la capacità da aperto (scratch)

**SIMULATO, elemento IDEALE, modelli segnaposto (NC-017). Non è il deck
versionato di L29b**: serve a dire quanto lenta dev'essere la derivazione prima di
scegliere una tecnica. Segue `../capacita_da_aperto/`.

## Il banco

`build.py` genera il deck scratch dalle prime 181 righe (blocco CANALE) di
`spice/preamp/tb/tb_v2_mute_graduale.cir` a 2471bab:
- `g4`: elemento in serie graduale, ponte `RBY*` aperto, bleeder lato
  condensatore 220 k / 470 k;
- **più** `BJK*`, graduale al jack (conduttanza log-lineare 1e-12 → 10 S con
  rampa `Tj`);
- **più** `CF*`, capacità da aperto in parallelo all'elemento in serie: 2 pF o
  50 pF.

Tolleranze del deck d'origine (`vntol=1e-6 abstol=1e-12`). `tran 10u`. +10 dB,
tono 2,7 V RMS a 1 kHz, fase π/2, carichi **100 k** soltanto.

**La sequenza.**
- Inserzione a 1,0 s: la serie si apre con rampa da 3 s, poi la derivazione si
  chiude in `Tj`.
- Rilascio a `t_rel`: la derivazione si apre in `Tj`, poi la serie si chiude in
  3 s.
- `t_grad = 3 + Tj` nel manifesto: `v2_metodo.py analizza` allarga a tutta la
  sequenza le finestre di C e l'inizio di B2. **Il metodo non è cambiato.**
- Riferimenti: mai in mute; sempre in mute, cioè serie aperta e derivazione chiusa
  da t = 0.

Esecuzione: `ngspice -b seq.cir`, 13 corse in 747 s, 0 errori. Analisi:
`/usr/bin/python3 scripts/v2_metodo.py analizza manifest.csv <dir> analisi.csv`.
Le forme d'onda (1,6 GB) non sono versionate.

## Esito (`analisi.csv`)

| C_off / Tj | B2 principale | C2 principale ins / rel | C2 fisse ins / rel |
|---|---|---|---|
| 2 pF / 20 ms | 16 nV | 2,92 / **3,54** mV | **1,02 / 1,09** mV |
| 2 pF / 200 ms | 15 nV | 2,92 / 3,00 mV | 0,82 / 0,88 mV |
| 2 pF / 1 s | 15 nV | 2,92 / 3,00 mV | 0,82 / 0,88 mV |
| 50 pF / 20 ms | 0,38 µV | **67,2 / 66,2** mV | **25,5 / 25,4** mV |
| 50 pF / 200 ms | 0,38 µV | 2,98 / 3,43 mV | 0,92 / **1,03** mV |
| 50 pF / 1 s | 0,38 µV | 2,98 / 2,97 mV | 0,83 / 0,87 mV |

B1 dai riferimenti sempre in mute: 15 nV (2 pF), 0,38 µV (50 pF).
A senza segnale (50 pF, Tj = 20 ms, il caso più rapido): 4–17 pV.

**Pavimento.** Il `C_pav` scritto qui è del **C1** della corsa mai in mute
(principale 1,04–1,11 mV, fisse 0,12–0,14 mV). **Non è il pavimento di C2**: quello
di L29a a 1 kHz sulla principale vale 0,57–0,80 mV. In questo scratch il
pavimento di C2 non è stato misurato.

## Cosa dice

1. **Con una derivazione graduale da ≈ 1 s la coppia reale torna alle cifre
   dell'elemento ideale di L29a** (principale 2,93–3,05 mV, fisse 0,83–0,87 mV)
   anche con 50 pF da aperto. Con 2 pF bastano 200 ms.
2. **Una derivazione rapida (20 ms) non va bene**: da 50 pF porta 67 mV di C.
3. **B scende a nV–µV**: la derivazione risolve il problema di
   `../capacita_da_aperto/`.
4. **Il prezzo**: ogni inserzione e ogni rilascio durano 3 s + Tj.
