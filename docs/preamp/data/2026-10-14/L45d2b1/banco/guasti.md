# I guasti del blocco col rivelatore vero (L45d2b1, ADR-072)

Generato da `script/sintesi_guasti.py`. **P10**: tempo con |v(jack)| > 0,87 V, a vuoto, senza filtro, sul peggiore dei tre jack (`L45b/script/analizza_p10.py`, invariato). «Prima» e' la stessa corsa di L45b senza rivelatore. Il guasto entra a 0,3 s; lo scatto e' DC_FLT sotto 2,5 V, il mute il contatto staccato (3 ms di rilascio del G6K).

| Posizione | Corse | P10 fuori prima | P10 fuori ora | Scattati | Scatto (min / mediana / max, ms) | Mute max (ms) | P10 max ora (ms) |
|---|---|---|---|---|---|---|---|
| A | 108 | 45 | **0** | 50 | 69.7 / 69.8 / 1689.2 | 1691.6 | 90.0 |
| F1 | 106 | 52 | **0** | 53 | 73.1 / 73.2 / 1413.0 | 1416.0 | 76.4 |
| F2 | 106 | 51 | **0** | 53 | 73.1 / 73.2 / 1413.0 | 1416.0 | 76.4 |
| B | 112 | 48 | **0** | 52 | 73.1 / 73.2 / 1866.0 | 1867.8 | 76.3 |
| B a +10 dB | 112 | 53 | **0** | 59 | 73.1 / 73.1 / 1358.7 | 1360.5 | 76.4 |
| B, C d'uscita in corto | 112 | — | **0** | 51 | 73.1 / 73.2 / 1866.0 | 1867.8 | 76.4 |
| F1, C d'uscita in corto | 106 | — | **0** | 53 | 73.1 / 73.2 / 1413.0 | 1416.0 | 76.4 |

## Le corse da leggere

P10 fuori col rivelatore, o nessuno scatto dove senza rivelatore P10 era fuori, o una corsa non finita.

| Variante | Modo | Stato | Scatto (ms) | P10 ora (ms) | P10 prima (ms) | Uscita alla fine (V) |
|---|---|---|---|---|---|---|
| riv_A | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | — | -3.803e-05 |
| riv_A | R120_cc | CORSA CORTA (0.450 s) | 69.9 | 72.9 | — | -1.452 |
| riv_A | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | — | -3.803e-05 |
| riv_F1 | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.02948 |
| riv_F1 | R120_cc | CORSA CORTA (0.450 s) | 73.3 | 70.8 | — | -1.459 |
| riv_F1 | R131_ap | CORSA CORTA (0.639 s) | — | 0.0 | 0.0 | 0 |
| riv_F1 | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.02948 |
| riv_F2 | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.02991 |
| riv_F2 | R120_cc | CORSA CORTA (0.450 s) | 73.3 | 70.8 | — | -1.459 |
| riv_F2 | R131_ap | CORSA CORTA (0.638 s) | — | 0.0 | 0.0 | 0 |
| riv_F2 | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.02991 |
| riv_B | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.0218 |
| riv_B | R120_cc | CORSA CORTA (0.450 s) | 73.3 | 67.8 | — | -1.456 |
| riv_B | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | 0.0 | 0.0218 |
| riv_B_g10 | R120_cc | CORSA CORTA (0.450 s) | 73.2 | 76.2 | — | -4.605 |
| riv_B_cc | JQ110A_ds | LOG: Note: Transient op started | 73.1 | 0.0 | — | 3.346 |
| riv_B_cc | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | — | 0.01819 |
| riv_B_cc | R120_cc | CORSA CORTA (0.450 s) | 73.3 | 73.4 | — | -1.442 |
| riv_B_cc | R131_ap | CORSA CORTA (0.621 s) | — | 0.0 | — | 0 |
| riv_B_cc | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | — | 0.01819 |
| riv_B_cc | R138_ap | LOG: Note: Transient op started | — | 0.0 | — | -0.002874 |
| riv_F1_cc | Q133_ae | CORSA CORTA (0.600 s) | — | 0.0 | — | 0.02858 |
| riv_F1_cc | R120_cc | CORSA CORTA (0.450 s) | 73.3 | 73.9 | — | -1.445 |
| riv_F1_cc | R131_ap | CORSA CORTA (0.608 s) | — | 0.0 | — | 0 |
| riv_F1_cc | R135_ap | CORSA CORTA (0.600 s) | — | 0.0 | — | 0.02858 |
