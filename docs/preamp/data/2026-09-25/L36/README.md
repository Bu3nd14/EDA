# L36 — il guadagno interbloccato dal mute (2026-09-25)

Dati del lotto L36 (ADR-041, strada B di ADR-030; NC-028). Report:
`docs/preamp/reports/2026-09-25-L36-guadagno-interbloccato.md`.
I deck espansi e i log della corsa **non si committano**: si rifanno correndo (~1 min). Si
tengono tre deck di esempio, il CSV e la sintesi.

## Le cartelle

| Cartella / file | Cosa |
|---|---|
| `falsi/genera_falsi.py` | il 2e esteso al guadagno, fatto fallire. 11 varianti sabotate più la netlist di `main` (prima di L36), un `.txt` per variante con l'uscita del 2e, e `esito.csv` con il primo problema trovato |
| `falsi/regressione.txt` | i falsi di L16 (trim) e di L29e (mute) rifatti col 2e nuovo: esiti uguali a quelli dei loro lotti |
| `corsa/corsa.py` | la corsa al rilascio del mute, un deck ngspice per cella. Tre varianti: `ingenua` (senza polo ponte), `progetto`, `residuo` (manopola girata fuori mute, poi mute inserito). Il modello di relè è **dichiarato** nel docstring |
| `corsa/corsa.csv` | 1440 corse: 3 varianti × 5 L × 4 buchi di K6 × 3 R × 4 soglie di rilascio × 2 VRELAY |
| `corsa/analisi.py`, `corsa/sintesi.txt` | la sintesi |
| `corsa/*_L20m_g1m_R237_f0.5_v5.cir` | un deck di esempio per variante |

## Come si rifà

```sh
# i falsi (la netlist di main: git show <main>:circuits/preamp/preamp_audio.net > <tmp>/main.net)
/usr/bin/python3 falsi/genera_falsi.py <repo>/circuits/preamp/preamp_audio.net <tmp>/main.net <abs>/falsi

# la corsa (deck e log in una cartella di lavoro qualsiasi)
/usr/bin/python3 corsa/corsa.py <tmp>/corsa_lavoro <abs>/corsa/corsa.csv 8
/usr/bin/python3 corsa/analisi.py corsa/corsa.csv corsa/sintesi.txt
```

## I risultati in breve

- **2e**: la netlist vera passa; le 11 varianti e `main` falliscono, ciascuna per la ragione
  voluta (colonna `prima_riga` di `esito.csv`).
- **Corsa**, 480 celle per variante, tutte rc 0, nessuna col transient op:
  - `progetto`: **0 cadute**, né al rilascio né all'inserimento. La corrente minima è uguale a
    quella di regime;
  - `ingenua`: cade al rilascio in **373 celle**, e dove cade dipende da L, dal buco e dalla
    soglia;
  - `residuo`: dopo l'apertura del NO di K6, K1 cade in 2,6–33,6 µs a 5 mH e in
    83,7–1322 µs a 200 mH, solo per la parte elettrica.
