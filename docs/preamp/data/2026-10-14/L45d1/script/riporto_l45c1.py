#!/usr/bin/env python3
"""L45d1: L45c1's table (the faults of the audio rails) in the form of ADR-070. Solo stdlib.

    riporto_l45c1.py <data/2026-10-13/L45c1> <data/2026-10-14/L45d1>

Reads L45c1's fmea_rail.csv AS PUBLISHED - the rows, the measured figures and the verdicts,
including what tabella_l45c1.py does and tabella_l45c2.py does not (the accepted shorts of P9 (c),
the welded NO, the runs read up to the abort) - and adds the columns of ADR-070 with motore.py and
classi_l45c1.py. Writes <L45d1>/fmea_rail_adr070.csv / .md. Refuses if a published column changes
(the note excepted, which gets the class's note appended) or a row is lost.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore  # noqa: E402
import classi_l45c1 as K  # noqa: E402

L, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
pubblicata = list(csv.DictReader(open(os.path.join(L, "fmea_rail.csv"))))
ORIG = list(pubblicata[0].keys())
righe = [dict(r) for r in pubblicata]
motore.classifica(righe, K, K.BASI_CLASSI)

for a, b in zip(pubblicata, righe):
    for k in ORIG:
        if k != "nota" and a[k] != b[k]:
            raise SystemExit("RIFIUTATO: %s / %s, la colonna pubblicata %s e' cambiata" % (a["ref"], a["modo"], k))
assert len(righe) == len(pubblicata)
senza = [r for r in righe if r["ref"] != "-" and r.get("priorita", "") == ""]
if senza:
    raise SystemExit("RIFIUTATO: righe senza priorita': %s" % [(r["ref"], r["modo"]) for r in senza])

i = ORIG.index("verdetto") + 1
CAMPI = ORIG[:i] + motore.ADR070 + ORIG[i:]
MD = ["ref", "funzione", "modo", "come", "verdetto", "G", "fit_modo", "P", "R", "priorita", "t_jack",
      "A_main_V", "A_main_dB", "sopra_main_ms", "sopra_fisse_ms", "nota", "rimedi"]
motore.scrivi(os.path.join(OUT, "fmea_rail_adr070"), righe, CAMPI, MD,
              "L45c1 — i guasti dei rail audio nella forma di ADR-070 (riporto di L45d1)",
              "Le righe, le misure e i verdetti sono quelli di L45c1 (`data/2026-10-13/L45c1/fmea_rail.csv`), "
              "invariati; le colonne di ADR-070 le aggiunge `script/riporto_l45c1.py` con le regole di "
              "L45c2 (`script/motore.py`) e le classi di `script/classi_l45c1.py`. Ordinata per "
              "priorita', poi gravita', poi FIT. Le colonne di dettaglio sono in `fmea_rail_adr070.csv`.",
              {"t_jack": "jack aperto (ms)", "A_main_V": "picco filtrato al principale, 100 k (V)",
               "A_main_dB": "dB SPL a 1 m", "sopra_main_ms": "sopra 0,87 V, principale (ms)",
               "sopra_fisse_ms": "sopra 0,87 V, fisse (ms)"})
print("scritto fmea_rail_adr070.csv / .md: %d righe (L45c1: %d); priorita' %s"
      % (len(righe), len(pubblicata), motore.conta(righe)))
