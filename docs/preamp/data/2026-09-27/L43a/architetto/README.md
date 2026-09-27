# L43a — i deck dell'architetto avversariale

Copiati il 2026-09-27 da `/tmp/l43a/`, dove `adversarial-architect` li aveva scritti durante la
sua revisione (fuori dal repo, perché è in sola lettura). Sono l'evidenza di **NC-039** (rilievo
R1) e della riesecuzione del rumore citata in R4. Report:
`../../../../reports/2026-09-27-L43a-architetto-avversariale.md`.

**Cifre di modello, non misure** (`docs/limitations.md`).

| File | Cosa |
|---|---|
| `thd_<guadagno>_<freq>.cir/.log` | THD con `.four` (griglia 8192, passo 0,02 µs) di un blocco di `gain_block_flat.inc` coi 7 modelli del costruttore, sorgente 2,5 kΩ, carico 10 kΩ dopo 47 Ω e 4,7 µF, 2 V RMS. `_470p`: Miller a 470 pF (`gb_470p.inc`); `_lowz`: sorgente 1,5 Ω; `_lo`: sorgente a un quarto dell'ampiezza (0,2238 contro 0,895 V di picco, −12 dB): a +10 dB e 20 kHz dà **0,00543 %** contro 0,168 %, cifra che il report non cita |
| `thd_3_*.cir` | +3 dB, senza log (non eseguiti o non conservati dall'architetto) |
| `imd_A.cir/.log`, `imd_A_470p.*` | IMD CCIF 19 + 20 kHz, 1,909 V di picco per tono, blocco A a guadagno unitario |
| `noise/` | la ricorsa di `tb_noise_breakdown.cir` (deck risolto, log, riassunto JSON); i CSV non sono stati copiati |
| `noise_run.txt` | l'uscita della ricorsa del rumore |

**Per rieseguire**: le righe `.include` puntano al worktree
`/Users/roberto/EDA/.claude/worktrees/L43a-architetto/`, che non esiste più dopo la chiusura del
lotto. Sostituire quel prefisso con `/Users/roberto/EDA/` e lanciare con
`/opt/homebrew/bin/ngspice -b <deck>.cir`.

Non copiati: `jung.txt` (il testo dell'articolo di Jung, Stephens e Todd, fonte e non dato).
