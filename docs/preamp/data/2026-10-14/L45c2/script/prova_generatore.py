#!/usr/bin/env python3
"""L45c1: every fault case of modi.py generated once (no ngspice), into a scratch folder given
as the first argument, with a core CSV given as the second (any pass-0 CSV of a MUSICA case).
Prints, per case, the lines the fault added or changed against the same deck without it
(perdita's deck for the perd cases, and so on), so a primitive that touched the wrong line shows."""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
PSU = os.path.join(QUI, "..", "psu")
sys.path.insert(0, PSU)
import modi  # noqa: E402

# L45c2: ins against its own base (f_base_niente_ins, whose own diff is SW3 alone against a mus
# deck), gu503 against guasto_u503
BASE = {"mus": None, "perd": "perdita", "spegn": "spegnimento_l", "gu502": "guasto",
        "gu501": "guasto_u501", "gu503": "guasto_u503", "ins": "f_base_niente_ins"}
out, core = sys.argv[1], sys.argv[2]
gen = os.path.join(PSU, "genera_tb_psu.py")


def deck(caso):
    d = os.path.join(out, caso)
    subprocess.run(["/usr/bin/python3", gen, "--uscita", d, "--nome", "seq", "--caso", caso,
                    "--uscite", core, "--giro", "1"], check=True, stdout=subprocess.DEVNULL)
    return [r for r in open(os.path.join(d, "tb_psu_seq_%s_g1.cir" % caso)).read().splitlines()
            if not r.startswith("* L47c2a tb_psu seq") and not r.startswith("wrdata")]


cache = {}
for caso, ref, modo, prim, cosa in modi.SIMULATI:
    ev = caso.split("_")[-1]
    b = BASE[ev] or "guasto_u501"
    if b not in cache:
        cache[b] = deck(b)
    righe = deck(caso)
    base = list(cache[b])
    if ev == "mus":
        # guasto_u501's U501 enable steps at TE; a mus case keeps it at 1
        base = [r.replace("VENU501 en_u501 0 pwl(0 1 2 1 2.000001 0 1000 0)",
                          "VENU501 en_u501 0 pwl(0 1 1000 1)") for r in base]
        base = [r for r in base if r != "VENU501 en_u501 0 pwl(0 1 1000 1)"] + \
               ["VENU501 en_u501 0 pwl(0 1 1000 1)"]
    sb, sr = set(base), set(righe)
    piu = [r for r in righe if r not in sb and not r.startswith("tran ")]
    meno = [r for r in base if r not in sr and not r.startswith("tran ")]
    print("== %s  (%s %s)" % (caso, ref, modo))
    for r in meno:
        print("   - " + r[:150])
    for r in piu:
        print("   + " + r[:150])
