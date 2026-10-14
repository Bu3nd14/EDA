# I guasti del blocco col rivelatore vero (L45d2b1, ADR-072)

Generato da `script/sintesi_guasti.py`. **P10**: tempo con |v(jack)| > 0,87 V, a vuoto, senza filtro, sul peggiore dei tre jack (`L45b/script/analizza_p10.py`, invariato). «Prima» e' la stessa corsa di L45b senza rivelatore. Il guasto entra a 0,3 s; lo scatto e' DC_FLT sotto 2,5 V, il mute il contatto staccato (3 ms di rilascio del G6K).

| Posizione | Corse | P10 fuori prima | P10 fuori ora | Scattati | Scatto (min / mediana / max, ms) | Mute max (ms) | P10 max ora (ms) |
|---|---|---|---|---|---|---|---|
| A | 108 | 14 | **0** | 48 | 69.7 / 69.8 / 1689.2 | 1691.9 | 90.0 |
| F1 | 106 | 20 | **1** | 57 | 73.1 / 73.2 / 1413.0 | 1416.0 | 123.9 |
| F2 | 106 | 20 | **1** | 57 | 73.1 / 73.2 / 1413.0 | 1416.0 | 122.8 |
| B | 112 | 43 | **1** | 57 | 73.1 / 73.2 / 1866.0 | 1867.8 | 121.9 |
| B a +10 dB | 112 | 50 | **0** | 57 | 73.1 / 73.1 / 1358.7 | 1360.5 | 76.3 |
| B, C d'uscita in corto | 112 | — | **1** | 57 | 73.1 / 73.2 / 1866.0 | 1867.8 | 110.9 |
| F1, C d'uscita in corto | 106 | — | **1** | 57 | 73.1 / 73.2 / 1413.0 | 1416.0 | 121.3 |

## Le corse da leggere

P10 fuori col rivelatore, o nessuno scatto dove senza rivelatore P10 era fuori, o una corsa non finita.

| Variante | Modo | Stato | Scatto (ms) | P10 ora (ms) | P10 prima (ms) | Uscita alla fine (V) |
|---|---|---|---|---|---|---|
| riv_A | C104_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C104_cc | LOG: rror | — | 0.0 | 0.0 | 1.426e-05 |
| riv_A | C105_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C105_cc | LOG: rror | — | 0.0 | 0.0 | 1.426e-05 |
| riv_A | C116_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C116_cc | LOG: rror | — | 0.1 | 0.1 | -0.5465 |
| riv_A | C124_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C124_cc | CORSA CORTA (0.303 s) | — | 2.9 | — | 0 |
| riv_A | C137_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C137_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C139_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C140_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C141_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C142_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | C145_ap | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | D102_cc | LOG: rror | — | 0.0 | 0.0 | -0.00352 |
| riv_A | D103_cc | LOG: rror | — | 0.0 | 0.0 | -0.00352 |
| riv_A | Q117_ce | LOG: rror | — | 0.0 | 0.0 | 0.01197 |
| riv_A | Q118_ce | LOG: rror | — | 0.0 | 0.0 | -0.01793 |
| riv_A | Q125_ae | LOG: rror | — | 0.0 | 0.0 | 0.4095 |
| riv_A | Q125_be | LOG: rror | — | 0.0 | 0.0 | 1.385e-05 |
| riv_A | Q127_ae | LOG: rror | — | 0.0 | 0.0 | -0.00326 |
| riv_A | Q127_be | LOG: rror | — | 0.0 | 0.0 | -0.003188 |
| riv_A | Q127_ce | LOG: rror | — | 0.0 | 0.0 | -0.002845 |
| riv_A | Q132_ae | LOG: rror | — | 0.0 | 0.0 | -0.002847 |
| riv_A | Q132_be | LOG: rror | — | 0.0 | 0.0 | -0.008815 |
| riv_A | Q133_ae | MANCA .dat | — |  | — |  |
| riv_A | Q133_be | LOG: rror | — | 0.0 | 0.0 | 0.0005274 |
| riv_A | Q146_be | LOG: rror | — | 0.0 | 0.0 | -0.4072 |
| riv_A | Q148_be | LOG: rror | — | 0.0 | 0.0 | 0.04119 |
| riv_A | R101_ap | LOG: rror | — | 0.0 | 0.0 | -0.005413 |
| riv_A | R108_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | R109_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | R111_cc | LOG: rror | — | 0.0 | 0.0 | 0.2233 |
| riv_A | R112_cc | LOG: rror | — | 0.0 | 0.0 | -0.2282 |
| riv_A | R113_ap | LOG: rror | — | 0.0 | 0.0 | -0.00287 |
| riv_A | R113_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_A | R115_ap | LOG: rror | — | 0.0 | 0.0 | -0.0784 |
| riv_A | R115_cc | LOG: rror | — | 0.1 | 0.1 | -0.5465 |
| riv_A | R120_cc | MANCA .dat | — |  | — |  |
| riv_A | R123_cc | LOG: rror | — | 0.0 | 0.0 | -0.0006529 |
| riv_A | R126_ap | LOG: rror | — | 0.0 | 0.0 | 0.4095 |
| riv_A | R126_cc | LOG: rror | — | 44.1 | 44.1 | -0.221 |
| riv_A | R128_ap | LOG: rror | — | 0.0 | 0.0 | -0.002717 |
| riv_A | R128_cc | LOG: rror | — | 0.0 | 0.0 | -0.002845 |
| riv_A | R129_ap | LOG: rror | — | 0.0 | 0.0 | -0.002847 |
| riv_A | R129_cc | LOG: rror | — | 0.0 | 0.0 | -0.003188 |
| riv_A | R130_ap | LOG: rror | — | 0.0 | 0.0 | -0.002847 |
| riv_A | R130_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | R131_ap | CORSA CORTA (0.436 s) | — | 0.0 | — | 0 |
| riv_A | R131_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | R134_ap | LOG: rror | — | 0.0 | 0.0 | -0.002847 |
| riv_A | R134_cc | LOG: rror | — | 0.0 | 0.0 | -0.002891 |
| riv_A | R135_ap | MANCA .dat | — |  | — |  |
| riv_A | R135_cc | LOG: rror | — | 0.0 | 0.0 | -0.002896 |
| riv_A | R136_ap | LOG: rror | — | 0.0 | 0.0 | -0.09363 |
| riv_A | R136_cc | LOG: rror | — | 0.0 | 0.0 | -0.002871 |
| riv_A | R144_cc | LOG: rror | — | 0.0 | 0.0 | -0.00287 |
| riv_A | R147_ap | LOG: rror | — | 0.0 | 0.0 | 4.696e-05 |
| riv_A | R149_ap | LOG: rror | — | 0.0 | 0.0 | -0.003286 |
| riv_F1 | C104_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C105_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C116_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C124_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C137_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C137_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C139_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C140_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C141_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C142_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | C145_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | D102_cc | LOG: rror | — | 0.0 | 0.0 | -0.006394 |
| riv_F1 | D103_cc | LOG: rror | — | 0.0 | 0.0 | -0.006394 |
| riv_F1 | JQ110A_gs | LOG: rror | — | 0.0 | 0.0 | 0.1071 |
| riv_F1 | Q106_be | ok | 134.4 | 123.9 | 122.8 | 5.902 |
| riv_F1 | Q117_ce | LOG: rror | — | 0.0 | 0.0 | 0.009096 |
| riv_F1 | Q118_ce | LOG: rror | — | 0.0 | 0.0 | -0.0208 |
| riv_F1 | Q127_ae | LOG: rror | — | 0.0 | 0.0 | -0.006134 |
| riv_F1 | Q127_be | LOG: rror | — | 0.0 | 0.0 | -0.006061 |
| riv_F1 | Q127_ce | LOG: rror | — | 0.0 | 0.0 | -0.005719 |
| riv_F1 | Q132_ae | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F1 | Q132_be | LOG: rror | — | 0.0 | 0.0 | -0.01169 |
| riv_F1 | Q133_be | LOG: rror | — | 0.0 | 0.0 | -0.002345 |
| riv_F1 | Q146_be | LOG: rror | — | 0.0 | 0.0 | -0.4101 |
| riv_F1 | Q146_ce | CORSA CORTA (0.373 s) | — | 73.1 | 1631.2 | 0 |
| riv_F1 | Q148_be | LOG: rror | — | 0.0 | 0.0 | 0.03831 |
| riv_F1 | R101_ap | LOG: rror | — | 0.0 | 0.0 | -0.008287 |
| riv_F1 | R108_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | R109_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | R111_cc | LOG: rror | — | 0.0 | 0.0 | 0.2204 |
| riv_F1 | R112_cc | LOG: rror | — | 0.0 | 0.0 | -0.231 |
| riv_F1 | R115_ap | LOG: rror | — | 0.0 | 0.0 | -0.08127 |
| riv_F1 | R120_cc | MANCA .dat | — |  | — |  |
| riv_F1 | R123_cc | LOG: rror | — | 0.0 | 0.0 | -0.003527 |
| riv_F1 | R126_cc | LOG: rror | — | 44.2 | 44.2 | -0.2239 |
| riv_F1 | R128_ap | LOG: rror | — | 0.0 | 0.0 | -0.00559 |
| riv_F1 | R128_cc | LOG: rror | — | 0.0 | 0.0 | -0.005719 |
| riv_F1 | R129_ap | LOG: rror | — | 0.0 | 0.0 | -0.005721 |
| riv_F1 | R129_cc | LOG: rror | — | 0.0 | 0.0 | -0.006061 |
| riv_F1 | R130_ap | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F1 | R130_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | R131_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | R134_ap | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F1 | R134_cc | LOG: rror | — | 0.0 | 0.0 | -0.005765 |
| riv_F1 | R135_cc | LOG: rror | — | 0.0 | 0.0 | -0.00577 |
| riv_F1 | R136_ap | LOG: rror | — | 0.0 | 0.0 | -0.1313 |
| riv_F1 | R136_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F1 | R144_cc | LOG: rror | — | 0.0 | 0.0 | -0.005743 |
| riv_F1 | R147_ap | LOG: rror | — | 0.0 | 0.0 | -0.002827 |
| riv_F1 | R149_ap | LOG: rror | — | 0.0 | 0.0 | -0.006159 |
| riv_F2 | C104_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C105_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C116_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C124_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C137_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C137_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C139_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C140_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C141_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C142_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | C145_ap | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | D102_cc | LOG: rror | — | 0.0 | 0.0 | -0.006394 |
| riv_F2 | D103_cc | LOG: rror | — | 0.0 | 0.0 | -0.006394 |
| riv_F2 | JQ110A_gs | LOG: rror | — | 0.0 | 0.0 | 0.1071 |
| riv_F2 | Q106_be | ok | 134.4 | 122.8 | 122.8 | 5.902 |
| riv_F2 | Q117_ce | LOG: rror | — | 0.0 | 0.0 | 0.009096 |
| riv_F2 | Q118_ce | LOG: rror | — | 0.0 | 0.0 | -0.0208 |
| riv_F2 | Q127_ae | LOG: rror | — | 0.0 | 0.0 | -0.006134 |
| riv_F2 | Q127_be | LOG: rror | — | 0.0 | 0.0 | -0.006061 |
| riv_F2 | Q127_ce | LOG: rror | — | 0.0 | 0.0 | -0.005719 |
| riv_F2 | Q132_ae | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F2 | Q132_be | LOG: rror | — | 0.0 | 0.0 | -0.01169 |
| riv_F2 | Q133_be | LOG: rror | — | 0.0 | 0.0 | -0.002345 |
| riv_F2 | Q146_be | LOG: rror | — | 0.0 | 0.0 | -0.4101 |
| riv_F2 | Q146_ce | CORSA CORTA (0.373 s) | — | 73.1 | — | 0 |
| riv_F2 | Q148_be | LOG: rror | — | 0.0 | 0.0 | 0.03831 |
| riv_F2 | R101_ap | LOG: rror | — | 0.0 | 0.0 | -0.008287 |
| riv_F2 | R108_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | R109_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | R111_cc | LOG: rror | — | 0.0 | 0.0 | 0.2204 |
| riv_F2 | R112_cc | LOG: rror | — | 0.0 | 0.0 | -0.231 |
| riv_F2 | R115_ap | LOG: rror | — | 0.0 | 0.0 | -0.08127 |
| riv_F2 | R120_cc | MANCA .dat | — |  | — |  |
| riv_F2 | R123_cc | LOG: rror | — | 0.0 | 0.0 | -0.003527 |
| riv_F2 | R126_cc | LOG: rror | — | 44.2 | 44.2 | -0.2239 |
| riv_F2 | R128_ap | LOG: rror | — | 0.0 | 0.0 | -0.00559 |
| riv_F2 | R128_cc | LOG: rror | — | 0.0 | 0.0 | -0.005719 |
| riv_F2 | R129_ap | LOG: rror | — | 0.0 | 0.0 | -0.005721 |
| riv_F2 | R129_cc | LOG: rror | — | 0.0 | 0.0 | -0.006061 |
| riv_F2 | R130_ap | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F2 | R130_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | R131_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | R134_ap | LOG: rror | — | 0.0 | 0.0 | -0.00572 |
| riv_F2 | R134_cc | LOG: rror | — | 0.0 | 0.0 | -0.005765 |
| riv_F2 | R135_cc | LOG: rror | — | 0.0 | 0.0 | -0.00577 |
| riv_F2 | R136_ap | LOG: rror | — | 0.0 | 0.0 | -0.1313 |
| riv_F2 | R136_cc | LOG: rror | — | 0.0 | 0.0 | -0.005745 |
| riv_F2 | R144_cc | LOG: rror | — | 0.0 | 0.0 | -0.005743 |
| riv_F2 | R147_ap | LOG: rror | — | 0.0 | 0.0 | -0.002827 |
| riv_F2 | R149_ap | LOG: rror | — | 0.0 | 0.0 | -0.006159 |
| riv_B | C104_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C105_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C116_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C116_cc | LOG: rror | — | 1.4 | 1.4 | -0.4344 |
| riv_B | C124_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C137_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C137_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C139_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C140_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C141_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C142_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | C145_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | D102_cc | LOG: rror | — | 0.0 | 0.0 | -0.003523 |
| riv_B | D103_cc | LOG: rror | — | 0.0 | 0.0 | -0.003523 |
| riv_B | Q106_be | ok | 133.5 | 121.9 | 66.2 | 5.714 |
| riv_B | Q117_ce | LOG: rror | — | 0.0 | 0.0 | 0.01197 |
| riv_B | Q118_ce | LOG: rror | — | 0.0 | 0.0 | -0.01793 |
| riv_B | Q127_ae | LOG: rror | — | 0.0 | 0.0 | -0.003263 |
| riv_B | Q127_be | LOG: rror | — | 0.0 | 0.0 | -0.00319 |
| riv_B | Q127_ce | LOG: rror | — | 0.0 | 0.0 | -0.002848 |
| riv_B | Q132_ae | LOG: rror | — | 0.0 | 0.0 | -0.002849 |
| riv_B | Q132_be | LOG: rror | — | 0.0 | 0.0 | -0.008816 |
| riv_B | Q133_be | LOG: rror | — | 0.0 | 0.0 | 0.0005264 |
| riv_B | Q146_be | LOG: rror | — | 0.0 | 0.0 | -0.4072 |
| riv_B | Q148_be | LOG: rror | — | 0.0 | 0.0 | 0.04118 |
| riv_B | R101_ap | LOG: rror | — | 0.0 | 0.0 | -0.005416 |
| riv_B | R108_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R109_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R111_cc | LOG: rror | — | 0.0 | 0.0 | 0.2233 |
| riv_B | R112_cc | LOG: rror | — | 0.0 | 0.0 | -0.2282 |
| riv_B | R113_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R113_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R115_ap | LOG: rror | — | 0.0 | 0.0 | -0.0784 |
| riv_B | R115_cc | LOG: rror | — | 1.4 | 1.4 | -0.4344 |
| riv_B | R120_cc | MANCA .dat | — |  | — |  |
| riv_B | R123_cc | LOG: rror | — | 0.0 | 0.0 | -0.0006558 |
| riv_B | R126_cc | LOG: rror | — | 43.0 | 43.0 | -0.2211 |
| riv_B | R128_ap | LOG: rror | — | 0.0 | 0.0 | -0.00272 |
| riv_B | R128_cc | LOG: rror | — | 0.0 | 0.0 | -0.002848 |
| riv_B | R129_ap | LOG: rror | — | 0.0 | 0.0 | -0.00285 |
| riv_B | R129_cc | LOG: rror | — | 0.0 | 0.0 | -0.00319 |
| riv_B | R130_ap | LOG: rror | — | 0.0 | 0.0 | -0.002849 |
| riv_B | R130_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R131_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R134_ap | LOG: rror | — | 0.0 | 0.0 | -0.002849 |
| riv_B | R134_cc | LOG: rror | — | 0.0 | 0.0 | -0.002894 |
| riv_B | R135_cc | LOG: rror | — | 0.0 | 0.0 | -0.002899 |
| riv_B | R136_ap | LOG: rror | — | 0.0 | 0.0 | -0.09367 |
| riv_B | R136_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R138_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R138_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R143_ap | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R143_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B | R144_cc | LOG: rror | — | 0.0 | 0.0 | -0.002872 |
| riv_B | R147_ap | LOG: rror | — | 0.0 | 0.0 | 4.409e-05 |
| riv_B | R149_ap | LOG: rror | — | 0.0 | 0.0 | -0.003288 |
| riv_B_g10 | C104_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C104_cc | LOG: rror | — | 0.0 | 0.0 | 0.05222 |
| riv_B_g10 | C105_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C105_cc | LOG: rror | — | 0.0 | 0.0 | 0.05222 |
| riv_B_g10 | C116_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C124_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C137_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C137_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B_g10 | C139_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C140_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C141_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C142_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | C145_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | D102_cc | LOG: rror | — | 0.0 | 0.0 | -0.0111 |
| riv_B_g10 | D103_cc | LOG: rror | — | 0.0 | 0.0 | -0.0111 |
| riv_B_g10 | Q106_be | LOG: rror | — | 16.5 | 16.6 | 0.05159 |
| riv_B_g10 | Q117_ae | CORSA CORTA (0.301 s) | — | 0.6 | 1443.9 | 0 |
| riv_B_g10 | Q117_ce | LOG: rror | — | 0.0 | 0.0 | 0.03772 |
| riv_B_g10 | Q118_ce | LOG: rror | — | 0.0 | 0.0 | -0.05652 |
| riv_B_g10 | Q125_be | LOG: rror | — | 0.0 | 0.0 | 0.05222 |
| riv_B_g10 | Q127_ae | LOG: rror | — | 0.0 | 0.0 | -0.01028 |
| riv_B_g10 | Q127_be | LOG: rror | — | 0.0 | 0.0 | -0.01006 |
| riv_B_g10 | Q127_ce | LOG: rror | — | 0.0 | 0.0 | -0.008976 |
| riv_B_g10 | Q132_ae | LOG: rror | — | 0.0 | 0.0 | -0.008982 |
| riv_B_g10 | Q132_be | LOG: rror | — | 0.0 | 0.0 | -0.02778 |
| riv_B_g10 | Q133_ae | LOG: rror | — | 0.0 | 0.0 | 0.0522 |
| riv_B_g10 | Q133_be | LOG: rror | — | 0.0 | 0.0 | 0.001659 |
| riv_B_g10 | Q148_be | LOG: rror | — | 0.0 | 0.0 | 0.1298 |
| riv_B_g10 | R101_ap | LOG: rror | — | 0.0 | 0.0 | -0.01707 |
| riv_B_g10 | R101_cc | LOG: rror | — | 0.0 | 0.0 | 0.1024 |
| riv_B_g10 | R108_cc | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R109_cc | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R113_ap | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R113_cc | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R115_ap | LOG: rror | — | 0.0 | 0.0 | -0.247 |
| riv_B_g10 | R120_cc | MANCA .dat | — |  | — |  |
| riv_B_g10 | R123_cc | LOG: rror | — | 0.0 | 0.0 | -0.002067 |
| riv_B_g10 | R128_ap | LOG: rror | — | 0.0 | 0.0 | -0.008568 |
| riv_B_g10 | R128_cc | LOG: rror | — | 0.0 | 0.0 | -0.008978 |
| riv_B_g10 | R129_ap | LOG: rror | — | 0.0 | 0.0 | -0.008984 |
| riv_B_g10 | R129_cc | LOG: rror | — | 0.0 | 0.0 | -0.01006 |
| riv_B_g10 | R130_ap | LOG: rror | — | 0.0 | 0.0 | -0.008982 |
| riv_B_g10 | R130_cc | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R131_ap | LOG: rror | — | 0.0 | 0.0 | 0.0521 |
| riv_B_g10 | R131_cc | LOG: rror | — | 0.0 | 0.0 | -0.009058 |
| riv_B_g10 | R134_ap | LOG: rror | — | 0.0 | 0.0 | -0.008982 |
| riv_B_g10 | R134_cc | LOG: rror | — | 0.0 | 0.0 | -0.009122 |
| riv_B_g10 | R135_ap | LOG: rror | — | 0.0 | 0.0 | 0.0522 |
| riv_B_g10 | R135_cc | LOG: rror | — | 0.0 | 0.0 | -0.009137 |
| riv_B_g10 | R136_cc | LOG: rror | — | 0.0 | 0.0 | -0.002874 |
| riv_B_g10 | R138_ap | LOG: rror | — | 0.0 | 0.0 | -0.007851 |
| riv_B_g10 | R143_ap | LOG: rror | — | 0.0 | 0.0 | -0.004081 |
| riv_B_g10 | R144_cc | LOG: rror | — | 0.0 | 0.0 | -0.009054 |
| riv_B_g10 | R147_ap | LOG: rror | — | 0.0 | 0.0 | 0.000139 |
| riv_B_g10 | R149_ap | LOG: rror | — | 0.0 | 0.0 | -0.01037 |
| riv_B_cc | C104_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C105_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C116_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C116_cc | LOG: rror | — | 1.4 | — | -0.4344 |
| riv_B_cc | C124_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C137_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C137_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C139_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C140_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C141_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C142_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | C145_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | D102_cc | LOG: rror | — | 0.0 | — | -0.003523 |
| riv_B_cc | D103_cc | LOG: rror | — | 0.0 | — | -0.003523 |
| riv_B_cc | Q106_be | ok | 125.5 | 110.9 | — | 0.001122 |
| riv_B_cc | Q117_ce | LOG: rror | — | 0.0 | — | 0.01197 |
| riv_B_cc | Q118_ce | LOG: rror | — | 0.0 | — | -0.01793 |
| riv_B_cc | Q127_ae | LOG: rror | — | 0.0 | — | -0.003263 |
| riv_B_cc | Q127_be | LOG: rror | — | 0.0 | — | -0.00319 |
| riv_B_cc | Q127_ce | LOG: rror | — | 0.0 | — | -0.002848 |
| riv_B_cc | Q132_ae | LOG: rror | — | 0.0 | — | -0.002849 |
| riv_B_cc | Q132_be | LOG: rror | — | 0.0 | — | -0.008816 |
| riv_B_cc | Q133_be | LOG: rror | — | 0.0 | — | 0.0005264 |
| riv_B_cc | Q146_be | LOG: rror | — | 0.0 | — | -0.4072 |
| riv_B_cc | Q148_be | LOG: rror | — | 0.0 | — | 0.04118 |
| riv_B_cc | R101_ap | LOG: rror | — | 0.0 | — | -0.005416 |
| riv_B_cc | R108_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R109_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R111_cc | LOG: rror | — | 0.0 | — | 0.2233 |
| riv_B_cc | R112_cc | LOG: rror | — | 0.0 | — | -0.2282 |
| riv_B_cc | R113_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R113_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R115_ap | LOG: rror | — | 0.0 | — | -0.0784 |
| riv_B_cc | R115_cc | LOG: rror | — | 1.4 | — | -0.4344 |
| riv_B_cc | R120_cc | MANCA .dat | — |  | — |  |
| riv_B_cc | R123_cc | LOG: rror | — | 0.0 | — | -0.0006558 |
| riv_B_cc | R126_cc | LOG: rror | — | 45.4 | — | -0.2211 |
| riv_B_cc | R128_ap | LOG: rror | — | 0.0 | — | -0.00272 |
| riv_B_cc | R128_cc | LOG: rror | — | 0.0 | — | -0.002848 |
| riv_B_cc | R129_ap | LOG: rror | — | 0.0 | — | -0.00285 |
| riv_B_cc | R129_cc | LOG: rror | — | 0.0 | — | -0.00319 |
| riv_B_cc | R130_ap | LOG: rror | — | 0.0 | — | -0.002849 |
| riv_B_cc | R130_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R131_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R134_ap | LOG: rror | — | 0.0 | — | -0.002849 |
| riv_B_cc | R134_cc | LOG: rror | — | 0.0 | — | -0.002894 |
| riv_B_cc | R135_cc | LOG: rror | — | 0.0 | — | -0.002899 |
| riv_B_cc | R136_ap | LOG: rror | — | 0.0 | — | -0.09367 |
| riv_B_cc | R136_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R138_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R138_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R143_ap | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R143_cc | LOG: rror | — | 0.0 | — | -0.002874 |
| riv_B_cc | R144_cc | LOG: rror | — | 0.0 | — | -0.002872 |
| riv_B_cc | R147_ap | LOG: rror | — | 0.0 | — | 4.409e-05 |
| riv_B_cc | R149_ap | LOG: rror | — | 0.0 | — | -0.003288 |
| riv_F1_cc | C104_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C105_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C116_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C124_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C137_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C137_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C139_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C140_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C141_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C142_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | C145_ap | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | D102_cc | LOG: rror | — | 0.0 | — | -0.006394 |
| riv_F1_cc | D103_cc | LOG: rror | — | 0.0 | — | -0.006394 |
| riv_F1_cc | JQ110A_gs | LOG: rror | — | 0.0 | — | 0.1071 |
| riv_F1_cc | Q106_be | ok | 132.5 | 121.3 | — | 0.001126 |
| riv_F1_cc | Q117_ce | LOG: rror | — | 0.0 | — | 0.009096 |
| riv_F1_cc | Q118_ce | LOG: rror | — | 0.0 | — | -0.0208 |
| riv_F1_cc | Q125_be | LOG: ransient op | — | 0.0 | — | 0.001126 |
| riv_F1_cc | Q127_ae | LOG: rror | — | 0.0 | — | -0.006134 |
| riv_F1_cc | Q127_be | LOG: rror | — | 0.0 | — | -0.006061 |
| riv_F1_cc | Q127_ce | LOG: rror | — | 0.0 | — | -0.005719 |
| riv_F1_cc | Q132_ae | LOG: rror | — | 0.0 | — | -0.00572 |
| riv_F1_cc | Q132_be | LOG: rror | — | 0.0 | — | -0.01169 |
| riv_F1_cc | Q133_be | LOG: rror | — | 0.0 | — | -0.002345 |
| riv_F1_cc | Q146_be | LOG: rror | — | 0.0 | — | -0.4101 |
| riv_F1_cc | Q148_be | LOG: rror | — | 0.0 | — | 0.03831 |
| riv_F1_cc | R101_ap | LOG: rror | — | 0.0 | — | -0.008287 |
| riv_F1_cc | R108_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | R109_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | R111_cc | LOG: rror | — | 0.0 | — | 0.2204 |
| riv_F1_cc | R112_cc | LOG: rror | — | 0.0 | — | -0.231 |
| riv_F1_cc | R115_ap | LOG: rror | — | 0.0 | — | -0.08127 |
| riv_F1_cc | R120_cc | MANCA .dat | — |  | — |  |
| riv_F1_cc | R123_cc | LOG: rror | — | 0.0 | — | -0.003527 |
| riv_F1_cc | R126_cc | LOG: rror | — | 45.4 | — | -0.2239 |
| riv_F1_cc | R128_ap | LOG: rror | — | 0.0 | — | -0.00559 |
| riv_F1_cc | R128_cc | LOG: rror | — | 0.0 | — | -0.005719 |
| riv_F1_cc | R129_ap | LOG: rror | — | 0.0 | — | -0.005721 |
| riv_F1_cc | R129_cc | LOG: rror | — | 0.0 | — | -0.006061 |
| riv_F1_cc | R130_ap | LOG: rror | — | 0.0 | — | -0.00572 |
| riv_F1_cc | R130_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | R131_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | R134_ap | LOG: rror | — | 0.0 | — | -0.00572 |
| riv_F1_cc | R134_cc | LOG: rror | — | 0.0 | — | -0.005765 |
| riv_F1_cc | R135_cc | LOG: rror | — | 0.0 | — | -0.00577 |
| riv_F1_cc | R136_ap | LOG: rror | — | 0.0 | — | -0.1313 |
| riv_F1_cc | R136_cc | LOG: rror | — | 0.0 | — | -0.005745 |
| riv_F1_cc | R144_cc | LOG: rror | — | 0.0 | — | -0.005743 |
| riv_F1_cc | R147_ap | LOG: rror | — | 0.0 | — | -0.002827 |
| riv_F1_cc | R149_ap | LOG: rror | — | 0.0 | — | -0.006159 |
