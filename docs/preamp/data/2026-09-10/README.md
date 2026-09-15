# Dati del 2026-09-10 — lo stadio d'ingresso con l'LS352

Prodotti dal lotto **L22 + L23**. Decisione: **ADR-018**. Report:
`../../reports/2026-09-10-L22-L23-specchio-ingresso.md`.

**Cosa descrivono e cosa no.** Questi file misurano la topologia con lo
specchio d'ingresso **LS352** al posto del THAT320, e con la degenerazione a
**220 Ω** al posto di 47. Ogni **altro** dispositivo del blocco è ancora un
segnaposto scritto a mano (`spice/preamp/placeholder_devices.lib`): nel
percorso di segnale solo lo specchio e l'LSK489 hanno un modello del
costruttore.

I dati in `../2026-09-09/` descrivono la topologia **precedente**, col
THAT320, e non sono stati rigenerati: restano validi come ciò che erano.

## I file

| File | Cosa |
|---|---|
| `tb_op-LS352.log` | punto di lavoro completo del blocco, `tb_op.cir` |
| `tb_noise_breakdown-LS352.log` | rumore, tutte e quattro le configurazioni |
| `tb_noise_breakdown_a_0db_1r.csv` | spettro di rumore, config A (intrinseco, R_sorgente 1 Ω) |
| `tb_noise_breakdown_b_0db_430r.csv` | config B, R_sorgente 430 Ω |
| `tb_noise_breakdown_c_0db_2500r.csv` | config C, R_sorgente 2500 Ω |
| `tb_noise_breakdown_d_10db_2500r.csv` | config D, **caso peggiore**: +10 dB, R_sorgente 2500 Ω |

**Colonne dei CSV**: `col0` = frequenza (Hz), `col1` = `onoise_spectrum`
(V/√Hz). `run_simulation.sh` intesta i CSV `col0…colN` e l'identità delle
colonne esiste solo nel deck — vedi `spice/preamp/tb/tb_noise_breakdown.cir`.

## I numeri chiave, e il confronto che conta

Rumore totale in uscita, integrato sulla banda audio:

| Config | THAT320 @ 47 Ω | **LS352 @ 220 Ω** | |
|---|---|---|---|
| A intrinseco | 1,676 µV | **1,157 µV** | −31,0% |
| B (430 Ω) | 1,718 µV | **1,216 µV** | −29,2% |
| C (2500 Ω) | 1,906 µV | **1,470 µV** | −22,9% |
| D caso peggiore | 5,697 µV | **4,231 µV** | **−25,7%** |

Requisito **E5**: ≤ 10 µV. Il caso peggiore ci sta con più margine di prima.

Punto di lavoro dello specchio (da `tb_op-LS352.log`): I_C = 2,134 / 2,136 mA,
V_BE 0,7028 / 0,7026 V, V_BC **interno** +0,493 / +0,369 V. Il secondo è la
metà d'uscita, ed è il numero che dice quanto dista dal ginocchio: a 47 Ω
valeva **−0,4 mV**, cioè esattamente sopra.

## Il caveat che va letto insieme a ogni cifra di rumore

**Il modello LS350 non ha `KF`/`AF`**, quindi **non c'è rumore 1/f**: lo
spettro simulato è piatto. Nel repo solo l'LSK489 ha flicker. Queste cifre
sono un **pavimento**, non una previsione, e il pavimento cade proprio dove
l'analisi dice che il rumore domina — lo specchio e le sue degenerazioni.
È **NC-004**, bloccante, e questi dati non la chiudono.

Da leggere anche insieme a **NC-013**: il modello LSK489 descrive un esemplare
d'angolo a bassa I_DSS, quindi il contributo del JFET qui è conservativo.

## Nota di L33 (2026-09-15) — la provenienza dell'LSK489

Il testo sopra resta com'era: è l'output di un'esecuzione datata. **Una sua frase non è vera**: «nel percorso di segnale solo lo specchio e l'LSK489 hanno un modello del costruttore».

- L'LSK489 simulato è **`LSK489X`**, il segnaposto scritto a mano di
  `spice/preamp/placeholder_devices.lib`, con `KF = 0`. Il modello del
  costruttore, `models/jfet/lsk489.lib` (`LSK489A`), non l'ha mai incluso
  nessun deck, né oggi né alla data di questi dati:
  `git log -S "jfet/lsk489.lib" -- spice circuits` è vuoto.
- L'unico modello del costruttore simulato è l'**LS352**
  (`models/bjt_pnp/ls350.lib`), che non ha `KF`. Quindi **nessun dispositivo
  simulato ha rumore 1/f**.
- **Nessun numero cambia**, cambia cosa se ne crede: ogni cifra di rumore qui è
  un pavimento senza flicker, JFET compresi (NC-004, NC-031).
- Due frasi che ne discendono vanno lette così:
  - «Nel repo solo l'LSK489 ha flicker» è vera della libreria `models/`, non di
    questi dati;
  - «il contributo del JFET qui è conservativo» (NC-013) non si applica: il
    modello d'angolo di NC-013 è `LSK489A`, che qui non è simulato.
