#!/usr/bin/env python3
"""L56: guasto_u503_min col carico di L56 (carico.txt: +10 mA per rail, ADR-067) non finisce il
passo 1 con gear + gmin 1e-10, il metodo di L51b: «Timestep too small» a 2,47 s su b.xu508b.bq.
Come in L51b (data/2026-10-09/L51b/sonda_u503/prepara.py), il passo 1 di ../seq/guasto_u503_min/..._g1.cir in varianti
della numerica, fino alla fine (3 s):

  gear_rel3   gear + gmin 1e-10, reltol 1e-3
  gear_gmin9  gear + gmin 1e-9
  trap9       trap + gmin 1e-9 (il metodo di L47c2b2)
  trap8       trap + gmin 1e-8

e lo stesso per guasto_u503 (che oggi finisce) come controllo della variante che si sceglie.

    /usr/bin/python3 prepara_l56.py   # scrive l56_<variante>/<caso>.cir e lista_l56.txt
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SEQ = os.path.join(QUI, "..", "seq")
GEAR = ".options reltol=1e-4 abstol=1e-10 vntol=1e-6 temp=25 method=gear gmin=1e-10"
VAR = {
    "gear": GEAR,
    "gear_rel3": GEAR.replace("reltol=1e-4", "reltol=1e-3"),
    "gear_gmin9": GEAR.replace("gmin=1e-10", "gmin=1e-9"),
    "trap9": GEAR.replace("method=gear gmin=1e-10", "method=trap gmin=1e-9"),
    "trap8": GEAR.replace("method=gear gmin=1e-10", "method=trap gmin=1e-8"),
    "trap8_rel3": GEAR.replace("reltol=1e-4", "reltol=1e-3").replace("method=gear gmin=1e-10", "method=trap gmin=1e-8"),
}
# L56, seconda corsa: con un argomento, il giro (es. 2) del solo guasto_u503_min, dal deck che
# corri_seq.sh ha lasciato (le uscite del core del giro precedente gia' dentro): la prima corsa
# della sonda era sul giro 1, dove trap8 passa; il giro 2 cade a 2,93 s su b.xu502.bi.
GIRO = sys.argv[1] if len(sys.argv) > 1 else "1"
CASI = ("guasto_u503", "guasto_u503_min") if GIRO == "1" else ("guasto_u503_min",)
lista = []
for caso in CASI:
    src = open(os.path.join(SEQ, caso, "tb_psu_seq_%s_g%s.cir" % (caso, GIRO))).read()
    opt = re.findall(r"^\.options reltol.*$", src, re.M)
    assert len(opt) == 1, caso
    assert src.count("wrdata tb_psu_seq_%s_g%s_out.txt" % (caso, GIRO)) == 1, caso
    for v, o in VAR.items():
        s = src.replace(opt[0], o)
        s = s.replace("wrdata tb_psu_seq_%s_g%s_out.txt" % (caso, GIRO), "wrdata %s_out.txt" % caso)
        d = os.path.join(QUI, "l56_" + v + ("" if GIRO == "1" else "_g" + GIRO))
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, caso + ".cir")
        open(p, "w").write(s)
        lista.append(p)
open(os.path.join(QUI, "lista_l56.txt"), "w").write("\n".join(lista) + "\n")
print("ok: %d deck" % len(lista))
