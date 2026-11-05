# L72 — i testi e le parti (2026-11-05)

Report: `reports/2026-11-05-L72-testi-e-parti.md`. ADR-121…ADR-124. Tutti gli script con `/usr/bin/python3 -I`
(solo stdlib), salvo `rigenera.sh` (il venv 3.13 del repo).

| File | Che cosa |
|---|---|
| `script/stax_finestra.py` | la finestra del condensatore della Stax: 0,895–1,265 µF reali (ADR-121) |
| `script/genera_stax.py`, `uno.sh`, `corri.sh`, `analizza_stax.py` | le 10 corse del limite alto (i cinque guasti più lunghi a 1,05 e 1,265 µF) → `stax/stax_limite_alto.csv`. `stax/run/` è ignorata dal `.gitignore` |
| `script/finestre.py` → `finestre.csv` | le finestre della lista ammessa, E9 a 20 Hz, E12 (ADR-122) |
| `distinta/README.md` | i tipi della lista e le resistenze 0,1 %, codici letti (bom-component-manager) |
| `script/e10_caso_peggiore.py` → `e10_caso_peggiore.csv` | E10 agli angoli all'1 % e allo 0,1 % (ADR-123) |
| `script/rigenera.sh`, `rigenera_*.txt` | i netlist rigenerati dal sorgente |
| `script/confronta_netlist.py`, `confronta.sh`, `confronto_*.txt` | i netlist contro main: uguali salvo il campo `Tolerance` |
| `script/principale_potenza.py` → `principale_potenza.txt` | il tetto del finale, 113,8 dB SPL (ADR-124) |
| `script/prove.sh` | `run_tests.sh` dal worktree, a `nice 10` |
