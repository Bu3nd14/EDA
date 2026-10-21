#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sabotaggi.py - L63a: the checks of the complete schematic must REFUSE, or they
are decorative. Each case below breaks one thing on purpose and asserts that it
is refused, for the reason it was broken.

Two halves:
  A. scripts/check_schematic.py on the KiCad netlist: the manifest of
     psu_draw.py tampered with (a pin moved, a part dropped, a part invented,
     a pin invented on a free pin of an integrated circuit).
  B. sheet_kit.py: small drawings on psu.net that are wrong in the ways a
     drawing lies - a wire between two nets, a short on a point, a net in two
     pieces without a name, a wire through a resistor, a label with the wrong
     name, a text on a text, a part left out.

Run (the venv: B needs schemdraw):
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/data/2026-10-21/L63a/script/sabotaggi.py
Exit 0 when every sabotage was caught.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")
NET = os.path.join(REPO, "circuits", "preamp", "psu.net")
MANIFEST = os.path.join(SCHEM, "psu.manifest.json")
CHECK = os.path.join(REPO, "scripts", "check_schematic.py")
sys.path.insert(0, SCHEM)

from sheet_kit import Sheet   # noqa: E402

results = []


def record(name, ok, detail):
    results.append((name, ok))
    print(f"  {'PRESO ' if ok else 'SFUGGITO'}  {name}: {detail}")


# =============================================================================
# A. the checker on the KiCad netlist
# =============================================================================
print("A. scripts/check_schematic.py contro psu.net")
base = json.load(open(MANIFEST, encoding="utf-8"))


def run_check(manifest, expect):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(manifest, f)
        path = f.name
    try:
        p = subprocess.run(["/usr/bin/python3", CHECK, path, NET], capture_output=True, text=True)
    finally:
        os.unlink(path)
    return p.returncode, expect in p.stdout, p.stdout


rc, _, _ = run_check(base, "OK")
record("il manifesto vero passa", rc == 0, f"rc={rc}")

m = copy.deepcopy(base)
m["devices"]["R506"]["2"] = "VREF"                       # SUP_P -> VREF
rc, hit, _ = run_check(m, "DISCORDE    R506.2")
record("un piedino spostato su un'altra rete", rc == 1 and hit, f"rc={rc}")

m = copy.deepcopy(base)
del m["devices"]["D522"]
rc, hit, _ = run_check(m, "OMESSO      D522")
record("una parte tolta dal disegno", rc == 1 and hit, f"rc={rc}")

m = copy.deepcopy(base)
m["devices"]["R999"] = {"1": "V5", "2": "MUTE_G"}
rc, hit, _ = run_check(m, "INVENTATO   R999")
record("una parte inventata", rc == 1 and hit, f"rc={rc}")

m = copy.deepcopy(base)
m["devices"]["U509"]["2"] = "MUTE_G"                     # PA4 is free in psu.net
rc, hit, _ = run_check(m, "PIN INVENTATO U509.2")
record("un piedino libero disegnato collegato", rc == 1 and hit, f"rc={rc}")

m = copy.deepcopy(base)
del m["devices"]["U501"]["13"]                           # EN dropped
rc, hit, _ = run_check(m, "PIN MANCANTE U501.13")
record("un piedino collegato non disegnato", rc == 1 and hit, f"rc={rc}")


# =============================================================================
# B. the kit
# =============================================================================
print("B. sheet_kit.py: disegni sbagliati apposta")
TMP = tempfile.mkdtemp(prefix="l63a_sab_")


def draw(build, expect, name):
    """Build a small drawing; finish() must raise with `expect` in the message."""
    S = Sheet(NET, "circuits/preamp/psu.net", width=122.0)
    try:
        build(S)
        S.finish(os.path.join(TMP, "s.svg"), os.path.join(TMP, "s.pdf"),
                 os.path.join(TMP, "s.json"))
    except AssertionError as e:
        msg = str(e)
        record(name, expect in msg, (expect if expect in msg else msg.splitlines()[0])[:110])
        return
    record(name, False, "nessun errore")


def divider(S):
    """R506 / R507 drawn correctly: the base the sabotages start from."""
    S.two("R506", {"VPLUS": (20, 40), "SUP_P": (20, 37)})
    S.two("R507", {"SUP_P": (20, 37), "RLY_RET": (20, 34)})


def wire_between_nets(S):
    divider(S)
    S.wire(S.N("R506", "VPLUS"), S.N("R507", "RLY_RET"), (23, 40), (23, 34))


draw(wire_between_nets, "reti diverse", "un filo fra due reti")


def short_on_point(S):
    divider(S)
    S.two("C515", {"SUP_P": (20, 40), "RLY_RET": (22, 40)})   # SUP_P on top of VPLUS


draw(short_on_point, "CORTO", "due reti sullo stesso punto")


def unnamed_islands(S):
    divider(S)
    S.two("C515", {"SUP_P": (30, 37), "RLY_RET": (30, 35)})
    S.ret(S.N("C515", "RLY_RET"))
    S.ret(S.N("R507", "RLY_RET"))
    S.rail(S.N("R506", "VPLUS"))
    # SUP_P drawn in two pieces (R506/R507 and C515), and neither is named


draw(unnamed_islands, "ISOLA SENZA NOME: SUP_P", "una rete in due pezzi senza nome")


def wire_through_resistor(S):
    divider(S)
    a = S.node("x_a", "SUP_P", (20, 37))
    b = S.node("x_b", "VREF", (18, 38.5))
    c = S.node("x_c", "VREF", (22, 38.5))
    S.wire(b, c)                                     # VREF runs across R506's body


draw(wire_through_resistor, "ATTRAVERSA", "un filo sopra una resistenza")


def wrong_label(S):
    divider(S)
    S.label(S.N("R507", "SUP_P"), text="SUP_M")


draw(wrong_label, "etichetta SUP_M", "un'etichetta col nome di un'altra rete")


def text_on_text(S):
    divider(S)
    S.text((50, 50), "PRIMA RIGA")
    S.text((50.2, 50.05), "SECONDA RIGA")


draw(text_on_text, "ILLEGGIBILE", "un testo sopra un altro")


def part_left_out(S):
    divider(S)


draw(part_left_out, "OMESSO: R508 non disegnato", "una parte non disegnata")


def free_pin_as_terminal(S):
    S.term("U509", "2", (60, 60))                    # PA4: on no net


draw_fn = free_pin_as_terminal
try:
    S = Sheet(NET, "circuits/preamp/psu.net", width=122.0)
    draw_fn(S)
    record("un piedino libero usato come terminale", False, "nessun errore")
except AssertionError as e:
    record("un piedino libero usato come terminale", "non collegato" in str(e) or "collega" in str(e),
           str(e)[:110])

caught = sum(ok for _, ok in results)
print(f"\n{caught} / {len(results)} presi")
sys.exit(0 if caught == len(results) else 1)
