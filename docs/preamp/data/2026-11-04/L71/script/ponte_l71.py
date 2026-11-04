#!/usr/bin/env python3
"""L71: which runs go to the chain to the jack, in groups of nine (the V2 deck's slots), and their
bridges (ponte/estrai_ponte_l71.py).

  - spl_riacceso_*, spl_sw3_*: all (from MUSICA, the front off: the rails move with the jack closed
    until it opens);
  - acc_spento_*: only those whose jack closed after TE (an_l71.csv n_su >= 1). The others never
    closed it: no path to the jack (an_l71.csv: n_su = 0), nothing to bridge;
  - ins_ritorno_*, ril_ritorno_*: none. The front stays on and the rails do not move (stato_l71.csv
    dvp50_mv); the jack's contacts move as in inserimento / rilascio, V2's own geometry (L29c-L29e),
    and the order of the permissive is read on the supply side (C2, C3, perm_anticipo_ms).
Per mains (l71, l71_m10, l71_p10) the runs fill groups of nine; the last group is padded by
repeating its first case (marked «ripetuto» in posti.csv: the same JSON in two slots).

    /usr/bin/python3 -I script/ponte_l71.py
writes ponte/<etichetta>_g<n>/ (nine JSONs, posti.csv), ponte/rientro/, and gruppi.txt (one group
per line).
"""
import csv
import os
import subprocess
import sys

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTI = ("spegnimento_l", "perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503",
         "guasto_u503_min", "cf_nodelta", "corto_u503")
an = {r["caso"]: r for r in csv.DictReader(open(os.path.join(L, "an_l71.csv")))}
gruppi = []
for et in ("l71", "l71_m10", "l71_p10"):
    casi = sorted(c.split("/")[1] for c in an if c.split("/")[0] == et)
    if not casi:
        raise SystemExit("RIFIUTATO: nessuna corsa di %s in an_l71.csv" % et)
    for c in casi:
        if an["%s/%s" % (et, c)]["esito"] != "letto":
            raise SystemExit("RIFIUTATO: %s/%s non letta" % (et, c))
    sel = [c for c in casi if c.startswith(("spl_riacceso_", "spl_sw3_"))]
    sel += [c for c in casi if c.startswith("acc_spento_") and int(an["%s/%s" % (et, c)]["n_su"] or 0) >= 1]
    for g in range(0, len(sel), 9):
        pezzo = sel[g:g + 9]
        nome = "%s_g%d" % (et, g // 9 + 1)
        coppie = ["%s=%s" % (p, c) for p, c in zip(POSTI, pezzo)]
        coppie += ["%s=%s" % (p, pezzo[0]) for p in POSTI[len(pezzo):]]
        out = os.path.join(L, "ponte", nome)
        subprocess.run([sys.executable, "-I", os.path.join(L, "ponte", "estrai_ponte_l71.py"),
                        os.path.join(L, "seq", et), out] + coppie, check=True)
        if len(pezzo) < 9:
            p = os.path.join(out, "posti.csv")
            r = list(csv.reader(open(p)))
            for x in r[1 + len(pezzo):]:
                x[1] += " (ripetuto)"
            csv.writer(open(p, "w", newline="")).writerows(r)
        gruppi.append(nome)
# the music coming BACK on rails that moved (stato_l71.csv dvp50_mv > 0: spl_riacceso_140 at -10 %,
# spl_riacceso_200 at +10 %, K501 closing again 12-20 ms before the jack), with 140 / 200 / 400 at
# every mains for comparison: nine slots, the RIENTRO mode of estrai_ponte_l71.py (R:)
RIENTRO = ["R:%s/spl_riacceso_%s" % (et, ms) for ms in ("140", "200", "400")
           for et in ("l71", "l71_m10", "l71_p10")]
subprocess.run([sys.executable, "-I", os.path.join(L, "ponte", "estrai_ponte_l71.py"),
                os.path.join(L, "seq"), os.path.join(L, "ponte", "rientro")]
               + ["%s=%s" % (p, c) for p, c in zip(POSTI, RIENTRO)], check=True)
gruppi.append("rientro")
open(os.path.join(L, "gruppi.txt"), "w").write("\n".join(gruppi) + "\n")
print(len(gruppi), "gruppi:", " ".join(gruppi))
