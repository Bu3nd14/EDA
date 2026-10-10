#!/usr/bin/env python3
"""L51b: the probe of the two U503-off cases, as L47c2b2's (data/2026-10-06/L47c2b2/sonda_u503/).

With today's load (carico.txt: the rails of today, the selector's coil) the first pass of
guasto_u503 did not end (> 6 min at 100 %, L47c2b2 ~17-24 s) and guasto_u503_min stopped at
2.968 s, "Timestep too small" on b.xu502.bi - both with L47c2b2's trap + gmin 1e-9. The probe
runs pass 1 of each case (today's ../seq/<caso>/..._g1.cir, the core's pass 0 as input) in
variants of the numerics, and of the end:

  com_e_05   today's options, the run stopped at TE + 0.5 s (2.5 s)
  gear_05    gear (the sequence decks' method, L47c2b2's reference), stopped at TE + 0.5 s
  reltol     trap + gmin 1e-9 + reltol 1e-3, to the end (3 s)   (L47c2b2: 15 s on _min)
  gmin8      trap + gmin 1e-8, to the end
  gear       gear + gmin 1e-10, to the end                      (L47c2b2: > 45 min)

    /usr/bin/python3 prepara.py      # writes <variante>/<caso>.cir next to itself
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
SEQ = os.path.join(QUI, "..", "seq")
OPT = ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=trap gmin=1e-9"
TRAN = "tran 100u 3 0 20u uic"
VAR = {
    "com_e_05": (OPT, "tran 100u 2.5 0 20u uic"),
    "gear_05": (OPT.replace("method=trap gmin=1e-9", "method=gear gmin=1e-10"), "tran 100u 2.5 0 20u uic"),
    "reltol": (OPT.replace("reltol=1e-4", "reltol=1e-3"), TRAN),
    "gmin8": (OPT.replace("gmin=1e-9", "gmin=1e-8"), TRAN),
    "gear": (OPT.replace("method=trap gmin=1e-9", "method=gear gmin=1e-10"), TRAN),
}
for caso in ("guasto_u503", "guasto_u503_min"):
    src = open(os.path.join(SEQ, caso, "tb_psu_seq_%s_g1.cir" % caso)).read()
    assert src.count(OPT) == 1 and src.count(TRAN) == 1, caso
    assert src.count("wrdata tb_psu_seq_%s_g1_out.txt" % caso) == 1, caso
    for v, (o, t) in VAR.items():
        s = src.replace(OPT, o).replace(TRAN, t)
        s = s.replace("wrdata tb_psu_seq_%s_g1_out.txt" % caso, "wrdata %s_out.txt" % caso)
        os.makedirs(os.path.join(QUI, v), exist_ok=True)
        open(os.path.join(QUI, v, caso + ".cir"), "w").write(s)
print("ok: %d varianti x 2 casi" % len(VAR))
