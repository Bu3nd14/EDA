# ADR-123 — Le resistenze del guadagno e del trim allo 0,1 %

Data: 2026-11-05 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Completa ADR-004 / ADR-026** (R_F 1,50 kΩ, R_G3 3,57 kΩ, R_G10 866 Ω del blocco commutato) e
  **ADR-027** (la scala del trim 845 / 464 / 464 Ω): i valori non cambiano, si fissa la tolleranza.
- Riscrive la prima clausola di **E10** col caso peggiore. Chiude **NC-081**.

## Contesto

La revisione dell'architetto avversariale di L65 (rilievo **R6**): E10 (≤ 0,2 dB fra i canali in ogni
posizione di trim e guadagno, col volume al massimo) «si garantisce con la tolleranza delle parti», ma la
tolleranza di queste resistenze non era scritta. All'1 % il caso peggiore è 0,49 dB. Correggerlo dopo il
prototipo vorrebbe dire cambiare resistenze per un difetto, non per l'ascolto (PR-12, ADR-118).

## Decisione

Le **sei posizioni per canale** che fissano il guadagno fra i canali sono **allo 0,1 %**, TCR ≤ 25 ppm/K:
R235 / R237 / R242 e R435 / R437 / R442 (R_F, R_G3, R_G10 del blocco B), R901–R903 e R911–R913 (la scala
del trim). Nel sorgente è il campo `Tolerance = 0.1%` della parte (`gain_block.TOL_GAIN`, `trim.TOL_TRIM`),
che arriva nel netlist e nella distinta. Il blocco A e i buffer delle fisse sono inseguitori a guadagno 1: il
loro R_F resta all'1 %.

## Perché

`data/2026-11-05/L72/script/e10_caso_peggiore.py` (ogni canale ai 2⁶ angoli; un canale al più alto, l'altro
al più basso; carico della presa 8 kΩ, 10 kΩ e a vuoto, il peggiore). Ridà prima le cifre dell'architetto
all'1 %: **0,237 dB** a +10 dB, **0,257 dB** col trim a −12 dB, **0,494 dB** insieme. Allo 0,1 %: **0,024 /
0,026 / 0,049 dB**. A 20 Hz la tolleranza ±5 % dei condensatori aggiunge al più 0,032 dB (la fissa 2,
`finestre.py`): **0,081 dB** in tutto, contro 0,2 dB. Una resistenza a film metallico allo 0,1 % in DIN0207
costa pochi decimi di euro più dell'1 %, e ne servono 12.

Il netlist rigenerato è uguale a quello di main salvo il campo, sulle dodici parti esatte
(`data/2026-11-05/L72/confronto_preamp_audio.txt`: 653 parti, 396 reti); `run_tests.sh` 14 / 0.

## Alternative scartate

- **Un trimmer di bilanciamento sulla scheda**: una parte in più, una taratura, e non copre i tre modi di
  guadagno e le tre posizioni del trim insieme.
- **Lo 0,5 %**: 0,25 dB nel caso peggiore, ancora fuori.
- **Coppie selezionate a mano**: lavoro di banco, contro la regola che ciò che si può decidere ora si decide.

## Da riaprire se

- Cambiano i valori della rete di guadagno o della scala del trim.
- La serie scelta alla distinta (`data/2026-11-05/L72/distinta/README.md`) non ha uno dei cinque valori.
- Il potenziometro di volume e il bilanciamento entrano nella scheda (lo scarto fra le loro sezioni oggi è la
  seconda clausola di E10, corretta all'ascolto).
