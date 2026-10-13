# L45b — i guasti del blocco di L45a contro P10, a vuoto

Generato da `script/sintesi_p10.py`. **P10** (ADR-069): tempo sopra 0,87 V sul jack senza filtro, a vuoto, dal guasto; ≤ 100 ms su ogni uscita. Le corse finiscono a 2,3 s (0,6 s le accorciate): un jack ancora sopra alla fine dà una durata «≥». Le fisse a vuoto decadono con τ 1,1 s: il blocco al rail le tiene sopra 0,87 V **3,15 s** (`analisi_lunghe.csv`, fino a 6 s), il principale **1,47 s**.

| Posizione | Modi | P10 fuori | di cui ancora sopra alla fine | L45a sopra il tetto | P10 fuori e L45a no | L45a sopra e P10 no | Principale: tempo sopra (mediana / max) |
|---|---|---|---|---|---|---|---|
| A | 108 | **48** | 34 | 50 | 2 | 4 | 181 / 578 ms |
| F1 | 106 | **53** | 33 | 49 | 5 | 1 | — |
| F2 | 106 | **53** | 33 | 49 | 6 | 2 | — |
| B | 112 | **49** | 6 | 52 | 3 | 6 | 1047 / 1999 ms |
| B_g10 | 112 | **54** | 4 | 52 | 4 | 2 | 1203 / 1749 ms |

## I casi in cui i due criteri non sono d'accordo

| Posizione | Modo | Classe (L45a) | Disaccordo | Principale grezzo / sopra | Singxer | Stax | Stato |
|---|---|---|---|---|---|---|---|
| A | C116_cc | continua -0.55 V | L45a sopra, P10 no | 1.252 V / 0.1 ms | 1.253 V / 0.1 ms | 1.253 V / 0.1 ms | ok |
| A | Q106_be | nessuna | L45a sopra, P10 no | 13.66 V / 90.0 ms | 14.09 V / 16.7 ms | 14.09 V / 16.7 ms | ok |
| A | R108_ap | continua 4.51 V | P10 fuori, L45a no | 0.5136 V / 0.0 ms | 2.356 V / 1898.0 ms | 2.356 V / 1898.0 ms | ok |
| A | R115_cc | continua -0.55 V | L45a sopra, P10 no | 1.252 V / 0.1 ms | 1.253 V / 0.1 ms | 1.253 V / 0.1 ms | ok |
| A | R120_cc | ? | P10 fuori, L45a no | 1.745 V / 42.2 ms | 1.764 V / 298.6 ms | 1.764 V / 298.6 ms | CORSA CORTA (0.600 s) |
| A | R126_cc | continua -0.22 V | L45a sopra, P10 no | 12.16 V / 33.9 ms | 12.17 V / 44.1 ms | 12.17 V / 44.1 ms | ok |
| F1 | Q125_ae | continua 4.73 V | P10 fuori, L45a no | 8.417e-07 V / 0.0 ms | 2.019 V / 1998.5 ms | 8.422e-07 V / 0.0 ms | ok |
| F1 | R108_ap | continua 4.50 V | P10 fuori, L45a no | 1.712e-11 V / 0.0 ms | 2.357 V / 1898.1 ms | 1.781e-11 V / 0.0 ms | ok |
| F1 | R114_ap | continua -1.61 V | P10 fuori, L45a no | 5.463e-07 V / 0.0 ms | 1.059 V / 531.1 ms | 2.529e-06 V / 0.0 ms | ok |
| F1 | R120_cc |  | P10 fuori, L45a no | 0.0001235 V / 0.0 ms | 2.09 V / 246.0 ms | 0.0001236 V / 0.0 ms | CORSA CORTA (0.600 s) |
| F1 | R126_ap | continua 4.73 V | P10 fuori, L45a no | 8.417e-07 V / 0.0 ms | 2.019 V / 1998.5 ms | 8.422e-07 V / 0.0 ms | ok |
| F1 | R126_cc | continua -0.22 V | L45a sopra, P10 no | 3.887e-08 V / 0.0 ms | 11.74 V / 44.2 ms | 3.889e-08 V / 0.0 ms | ok |
| F2 | Q125_ae | continua 4.58 V | P10 fuori, L45a no | 8.493e-07 V / 0.0 ms | 8.498e-07 V / 0.0 ms | 2.02 V / 1998.5 ms | ok |
| F2 | Q125_be | nessuna | L45a sopra, P10 no | 9.02e-07 V / 0.0 ms | 9.025e-07 V / 0.0 ms | 1.249 V / 0.1 ms | ok |
| F2 | Q146_ce | nessuna | P10 fuori, L45a no | 6.233e-10 V / 0.0 ms | 3.418e-09 V / 0.0 ms | 14.36 V / 2000.0 ms | ok |
| F2 | R108_ap | continua 4.50 V | P10 fuori, L45a no | 1.914e-11 V / 0.0 ms | 1.486e-11 V / 0.0 ms | 2.357 V / 1898.1 ms | ok |
| F2 | R114_ap | continua -1.61 V | P10 fuori, L45a no | 5.352e-07 V / 0.0 ms | 2.518e-06 V / 0.0 ms | 1.059 V / 531.1 ms | ok |
| F2 | R120_cc | ? | P10 fuori, L45a no | 0.0001191 V / 0.0 ms | 0.0001191 V / 0.0 ms | 2.1 V / 246.4 ms | CORSA CORTA (0.600 s) |
| F2 | R126_ap | continua 4.58 V | P10 fuori, L45a no | 8.493e-07 V / 0.0 ms | 8.498e-07 V / 0.0 ms | 2.02 V / 1998.5 ms | ok |
| F2 | R126_cc | continua -0.22 V | L45a sopra, P10 no | 3.756e-08 V / 0.0 ms | 3.757e-08 V / 0.0 ms | 11.74 V / 44.2 ms | ok |
| B | C116_cc | continua -0.43 V | L45a sopra, P10 no | 1.356 V / 1.4 ms | 1.24e-05 V / 0.0 ms | 1.24e-05 V / 0.0 ms | ok |
| B | JQ110A_gs | continua 4.77 V | P10 fuori, L45a no | 3.362 V / 953.5 ms | 1.03e-06 V / 0.0 ms | 1.03e-06 V / 0.0 ms | ok |
| B | JQ110B_gs | continua -0.99 V | L45a sopra, P10 no | 1.002 V / 65.2 ms | 2.269e-07 V / 0.0 ms | 2.269e-07 V / 0.0 ms | ok |
| B | Q106_be | continua -1.49 V | L45a sopra, P10 no | 14.34 V / 66.2 ms | 6.789e-06 V / 0.0 ms | 6.789e-06 V / 0.0 ms | ok |
| B | Q125_be | nessuna | L45a sopra, P10 no | 1.153 V / 0.0 ms | 9.289e-07 V / 0.0 ms | 9.289e-07 V / 0.0 ms | ok |
| B | R108_ap | continua 4.51 V | P10 fuori, L45a no | 1.712 V / 1225.7 ms | 1.93e-11 V / 0.0 ms | 1.828e-11 V / 0.0 ms | ok |
| B | R115_cc | continua -0.43 V | L45a sopra, P10 no | 1.356 V / 1.4 ms | 1.24e-05 V / 0.0 ms | 1.24e-05 V / 0.0 ms | ok |
| B | R120_cc | ? | P10 fuori, L45a no | 2.089 V / 204.1 ms | 0.0001206 V / 0.0 ms | 0.0001206 V / 0.0 ms | CORSA CORTA (0.600 s) |
| B | R126_cc | continua -0.22 V | L45a sopra, P10 no | 11.74 V / 43.0 ms | 1.109e-08 V / 0.0 ms | 1.108e-08 V / 0.0 ms | ok |
| B_g10 | Q106_be | nessuna | L45a sopra, P10 no | 14.06 V / 16.6 ms | 6.611e-06 V / 0.0 ms | 6.611e-06 V / 0.0 ms | ok |
| B_g10 | R108_ap | continua 7.31 V | P10 fuori, L45a no | 3.74 V / 1376.2 ms | 4.537e-09 V / 0.0 ms | 4.535e-09 V / 0.0 ms | ok |
| B_g10 | R114_ap | continua -2.22 V | P10 fuori, L45a no | 1.018 V / 558.8 ms | 2.15e-08 V / 0.0 ms | 2.15e-08 V / 0.0 ms | ok |
| B_g10 | R120_cc | ? | P10 fuori, L45a no | 5.145 V / 300.0 ms | 0.0001164 V / 0.0 ms | 0.0001164 V / 0.0 ms | CORSA CORTA (0.600 s) |
| B_g10 | R126_cc | continua -0.66 V | L45a sopra, P10 no | 11.68 V / 53.8 ms | 1.477e-08 V / 0.0 ms | 1.477e-08 V / 0.0 ms | ok |
| B_g10 | R144_ap | rail- | P10 fuori, L45a no | 8.94 V / 1749.4 ms | 3.343e-07 V / 0.0 ms | 3.342e-07 V / 0.0 ms | ok |
