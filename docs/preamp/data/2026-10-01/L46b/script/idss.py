#!/usr/bin/env python3
"""L46b (copiato da L46a): V1 nel gruppo B di I_DSS (ADR-031) per una variante, sulle tre istanze.

- blocco B: spice/preamp/tb/tb_idss_loop.cir col solo include del blocco
  sostituito (genera.copia);
- blocco A e buffer: i deck di L40/script/idss_istanze.py (stesso corpo, stesse
  varianti altermod a_come_e / b_min / b_tip / b_max), con l'include della variante.
La variante a_come_e deve ridare V1 di tb_loop_blockA / tb_loop_bufferfissa della
stessa variante (#29).

Uso: /usr/bin/python3 idss.py <variante>...  -> deck/<v>/tb_idss_*.cir, deck/lista_idss.txt
"""
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L46A, *[".."] * 5))
L40S = os.path.join(ROOT, "docs", "preamp", "data", "2026-09-23", "L40", "script", "idss_istanze.py")

argv = sys.argv[1:]
spec = importlib.util.spec_from_file_location("gen", os.path.join(QUI, "genera.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

spec2 = importlib.util.spec_from_file_location("idss40", L40S)
i40 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(i40)

lista = []
for v in argv:
    d = os.path.join(L46A, "deck", v)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "tb_idss_loop.cir")
    open(p, "w").write(gen.copia(v, "tb_idss_loop", curve=False))
    lista.append(p)
    # i deck di L40 nella cartella della variante, poi l'include sostituito
    i40.L40 = os.path.dirname(d)
    sys.argv = ["idss_istanze.py", v]
    i40.main()
    for nome in ("tb_idss_blockA", "tb_idss_buffer"):
        p = os.path.join(d, nome + ".cir")
        t = open(p).read()
        if t.count(gen.INC_BLOCCO) != 1:
            sys.exit("%s: include del blocco" % p)
        open(p, "w").write(t.replace(gen.INC_BLOCCO, gen.inc_var(v)).replace(
            " - L40: ", " - L46a (variante %s, da L40/idss_istanze.py): " % v, 1))
        lista.append(p)
with open(os.path.join(L46A, "deck", "lista_idss.txt"), "w") as fh:
    fh.write("\n".join(lista) + "\n")
print("%d deck in deck/lista_idss.txt" % len(lista))
