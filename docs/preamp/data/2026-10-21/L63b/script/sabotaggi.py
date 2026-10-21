#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sabotaggi.py - L63b: the folded page must REFUSE, or it is decorative.

The audio page draws the gain block once and the left channel only; Sheet.fold()
derives what the drawing stands for, finish() expands it into all 570 parts, and
scripts/check_schematic.py compares the expansion with preamp_audio.net. Each case
below breaks one link on purpose and asserts that it is refused, for the reason it
was broken:

  A. the expanded manifest, tampered with: check_schematic.py must see it;
  B. the fold, on the real page (audio_draw.py run with the kit patched, or on a
     netlist copy broken on purpose): a wrong table, a wrong base, a wrong
     left -> right rule, a right part rewired, a value changed, a core part gone,
     an optional part not declared;
  C. small drawings with the kit: a part drawn that the fold expands, a left part
     or a template part not drawn, a box not drawn or with a port missing, a
     changeover wired on the wrong throw, a rotary throw on the wrong net, a relay
     with its contacts left out, a text on a ground symbol;
  D. the 14 sabotages of L63a, on the extended kit.

Run (the venv: B and C need schemdraw):
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/data/2026-10-21/L63b/script/sabotaggi.py
Exit 0 when every sabotage was caught.
"""
import copy
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")
NET = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
BLOCK = os.path.join(REPO, "circuits", "preamp", "gain_block.net")
MANIFEST = os.path.join(SCHEM, "audio.manifest.json")
DRAW = os.path.join(SCHEM, "audio_draw.py")
CHECK = os.path.join(REPO, "scripts", "check_schematic.py")
L63A = os.path.join(REPO, "docs", "preamp", "data", "2026-10-21", "L63a", "script", "sabotaggi.py")
sys.path.insert(0, SCHEM)

import sheet_kit                  # noqa: E402
from sheet_kit import Sheet       # noqa: E402

TMP = tempfile.mkdtemp(prefix="l63b_sab_")
os.environ["AUDIO_SHEET_DIR"] = TMP
results = []


def record(name, ok, detail):
    results.append((name, ok))
    print(f"  {'PRESO ' if ok else 'SFUGGITO'}  {name}: {detail}")


def run_check(manifest_path, net=NET):
    p = subprocess.run(["/usr/bin/python3", CHECK, manifest_path, net],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


# =============================================================================
# A. the expanded manifest, tampered with
# =============================================================================
print("A. scripts/check_schematic.py sul manifesto espanso")
base = json.load(open(MANIFEST, encoding="utf-8"))


def check_dict(m):
    path = os.path.join(TMP, "m.json")
    with open(path, "w") as f:
        json.dump(m, f)
    return run_check(path)


rc, out = check_dict(base)
record("il manifesto vero passa (570 / 570)", rc == 0 and "570 nel disegno" in out, f"rc={rc}")
m = copy.deepcopy(base)
m["devices"]["R363"]["1"] = "R_FIXC1"            # a pin of the RIGHT channel, expanded
rc, out = check_dict(m)
record("un piedino del destro spostato", rc == 1 and "DISCORDE    R363.1" in out, f"rc={rc}")
m = copy.deepcopy(base)
del m["devices"]["R741"]                         # a part of an instance (F1R), expanded
rc, out = check_dict(m)
record("una parte di un'istanza tolta", rc == 1 and "OMESSO      R741" in out, f"rc={rc}")


# =============================================================================
# B. the fold, on the real page
# =============================================================================
print("B. Sheet.fold() sulla pagina vera (audio_draw.py col kit manomesso)")
ORIG_FOLD, ORIG_INIT = Sheet.fold, Sheet.__init__


class Stop(Exception):
    pass


def run_page(fold=None, netlist=None):
    """Run audio_draw.py with Sheet.fold and / or the netlist replaced; returns the
    exception text, or None if the page drew."""
    def init(self, nl, *a, **k):
        ORIG_INIT(self, netlist if (netlist and os.path.basename(nl) == "preamp_audio.net") else nl,
                  *a, **k)
    Sheet.__init__ = init
    if fold:
        Sheet.fold = fold
    try:
        runpy.run_path(DRAW, run_name="__main__")
        return None
    except Stop as e:
        return f"STOP {e}"
    except AssertionError as e:
        return str(e)
    finally:
        Sheet.fold, Sheet.__init__ = ORIG_FOLD, ORIG_INIT


def expect(name, msg, needle):
    ok = msg is not None and needle in msg
    shown = "nessun errore" if msg is None else (needle if ok else msg.splitlines()[0])
    record(name, ok, shown[:120])


# B1: two refs swapped in the table -> the expanded manifest disagrees with the netlist
def swapped(self, *a, **k):
    F = ORIG_FOLD(self, *a, **k)
    t = F["table"]["AR"]
    t["R111"], t["R112"] = t["R112"], t["R111"]
    return F


msg = run_page(fold=swapped)
if msg is None:
    rc, out = run_check(os.path.join(TMP, "audio.manifest.json"))
    record("due sigle scambiate nella tabella", rc == 1 and "DISCORDE    R31" in out, f"rc={rc}")
else:
    record("due sigle scambiate nella tabella", False, f"la pagina non si e' disegnata: {msg[:90]}")


def with_args(change):
    def fold(self, instances, optional, tbase, left, ref_lr, net_lr, pairs, **k):
        a = change(dict(instances=instances, optional=optional, ref_lr=ref_lr))
        return ORIG_FOLD(self, a["instances"], a["optional"], tbase, left, a["ref_lr"],
                         net_lr, pairs, **k)
    return fold


expect("la base di un'istanza sbagliata",
       run_page(fold=with_args(lambda a: {**a, "instances": [(t, 401 if t == "BR" else b)
                                                            for t, b in a["instances"]]})),
       "soluzioni della numerazione")
expect("la regola sinistro -> destro sbagliata (+201)",
       run_page(fold=with_args(lambda a: {**a, "ref_lr": lambda r: (lambda q: q[0] + str(int(q[1:]) + 1)
                                                                   if q[1:].isdigit() else q)(a["ref_lr"](r))})),
       "->")
expect("una parte opzionale non dichiarata (R_g10)",
       run_page(fold=with_args(lambda a: {**a, "optional": {k: v for k, v in a["optional"].items()
                                                           if k != "R_g10"}})),
       "soluzioni della numerazione")


def netcopy(edit, name):
    src = open(NET, encoding="utf-8").read()
    out = edit(src)
    assert out != src, f"{name}: la manomissione non ha cambiato la netlist"
    path = os.path.join(TMP, name + ".net")
    open(path, "w", encoding="utf-8").write(out)
    return path


def move_node(src, ref, pin, to_net):
    """Move one pin of the netlist onto another net (the node, out of its net)."""
    pat = re.compile(r'\(node\s*\(ref "%s"\)\s*\(pin "%s"\)\s*\(pintype "[^"]*"\)\)' % (ref, pin))
    m = pat.search(src)
    assert m, f"{ref}.{pin} non trovato"
    node_txt = m.group(0)
    src = src[:m.start()] + src[m.end():]
    anchor = f'(name "{to_net}")'
    i = src.index(anchor) + len(anchor)
    return src[:i] + "\n      " + node_txt + src[i:]


expect("un pezzo del destro ricablato (R363.1 su R_FIXC1)",
       run_page(netlist=netcopy(lambda s: move_node(s, "R363", "1", "R_FIXC1"), "rewired")),
       "cade a destra")
expect("un valore del destro diverso (R363 330k)",
       run_page(netlist=netcopy(lambda s: re.sub(r'(\(ref "R363"\)\s*\(value ")470k', r"\g<1>330k", s),
                                "value_right")),
       "R163")
expect("un'istanza senza una parte del nucleo (R533 rinominata R599)",
       run_page(netlist=netcopy(lambda s: s.replace('(ref "R533")', '(ref "R599")'), "missing")),
       "soluzioni della numerazione")


# B5: a value that differs in one instance is not an error: it is PRINTED in the table
def capture(self, *a, **k):
    F = ORIG_FOLD(self, *a, **k)
    raise Stop(json.dumps(F["diffs"]))


msg = run_page(fold=capture,
               netlist=netcopy(lambda s: re.sub(r'(\(ref "R533"\)\s*\(value ")22', r"\g<1>33", s),
                               "value_inst"))
diffs = json.loads(msg[5:]) if msg and msg.startswith("STOP ") else None
record("un valore diverso in un'istanza finisce nella tabella (R533 33 Ω)",
       diffs is not None and diffs.get("F1L") == {"R134": "33"}
       and all(not v for t, v in diffs.items() if t != "F1L"),
       f"differenze: {diffs}")


# =============================================================================
# C. small drawings with the kit
# =============================================================================
print("C. sheet_kit.py: disegni sbagliati apposta sulla pagina ripiegata")


def left(ref):
    letter, n = Sheet._num(ref)
    return (100 <= n < 300 and (n % 100 > 60 or letter == "J")) or 900 <= n < 910


def ref_lr(ref):
    letter, n = Sheet._num(ref)
    return f"{letter}{n + (10 if n >= 900 else 200)}"


def net_lr(n):
    for a, c in (("L_", "R_"), ("AL_", "AR_"), ("BL_", "BR_"), ("F1L_", "F1R_"), ("F2L_", "F2R_")):
        if n.startswith(a):
            return c + n[len(a):]
    return n


def sheet():
    S = Sheet(NET, "circuits/preamp/preamp_audio.net", width=172.5, page=(594 / 25.4, 420 / 25.4))
    S.template(BLOCK, "BLK", "circuits/preamp/gain_block.net")
    S.fold([("AL", 100), ("BL", 200), ("AR", 300), ("BR", 400),
            ("F1L", 500), ("F2L", 600), ("F1R", 700), ("F2R", 800)],
           {"R_IN": ("IN", "GND"), "R_g": ("FB", "RG"), "R_g10": ("FB", "RG10")}, 100,
           left, ref_lr, net_lr, [("AL", "AR"), ("BL", "BR"), ("F1L", "F1R"), ("F2L", "F2R")],
           value_lr=lambda v: v.replace("_L", "_R"))
    return S


def finish_msg(S):
    try:
        S.finish(os.path.join(TMP, "s.svg"), os.path.join(TMP, "s.pdf"), os.path.join(TMP, "s.json"))
        return None
    except AssertionError as e:
        return str(e)


S = sheet()
S.two("R363", {"R_FIXOUT1": (20, 40), "GND": (20, 37)})       # the right twin of R163
msg = finish_msg(S)
expect("una parte disegnata che il ripiegamento espande (R363)", msg, "DOPPIO: R363")
expect("una parte del sinistro non disegnata (R163)", msg, "OMESSO: R163 non disegnato")
expect("una parte del blocco non disegnata (R108 del modello)", msg, "OMESSO: BLK:R108 non disegnato")
expect("il riquadro di un'istanza non disegnato (AL)", msg, "riquadro dell'istanza AL")
expect("una parte di un'istanza non chiesta al disegno (R541 non e' OMESSO)",
       None if msg is None or "OMESSO: R541" in msg else "ok", "ok")


def build(fn):
    S = sheet()
    try:
        fn(S)
    except AssertionError as e:
        return str(e)
    return finish_msg(S)


def k4_wrong(S):
    S.two("R264", {"L_MAINC": (60, 90), "GND": (60, 87.6)})
    k = S.relay_pole("K4", 1, (62, 90))
    S.wire(S.N("R264", "L_MAINC"), k["NC"])                  # the NC is GND, the cap side COM


expect("un deviatore cablato sul contatto sbagliato (K4: NC invece di COM)", build(k4_wrong),
       "reti diverse")


def sw1_wrong(S):
    p = S.rotary_pole("SW1", 0, (130, 70))
    n = S.node("vt", "VTRIM", (136, 71))
    S.wire(p[1], n)                                          # position 1 of pole a is RLY_RET


expect("una posizione del rotativo sulla rete sbagliata (SW1 a, 1)", build(sw1_wrong), "reti diverse")
expect("il riquadro di un'istanza senza una porta (BL senza RG10)",
       build(lambda S: S.instance("BL", 50, 90, 6, 5, {"IN": ("l", 1), "OUT": ("r", 1), "RG": ("r", 3)})),
       "porte")
msg = build(lambda S: S.relay_coil("K2", (120, 110), (120, 107.6)))
expect("un rele' con la bobina sola (K2, contatti non disegnati)", msg,
       "OMESSO: K2, piedini del simbolo non disegnati")


def text_on_ground(S):
    S.two("R265", {"L_ATT_W": (40, 90), "GND": (40, 87.6)}, side="r")
    S.gnd(S.N("R265", "GND"))
    S.text((40.2, 87.4), "SCRITTA SULLA MASSA")


expect("un testo sopra un simbolo di massa", build(text_on_ground), "simbolo GND")


# =============================================================================
# D. L63a's sabotages, on the extended kit
# =============================================================================
print("D. i 14 sabotaggi di L63a sul kit esteso")
p = subprocess.run([sys.executable, L63A], capture_output=True, text=True)
tail = [ln for ln in p.stdout.splitlines() if "presi" in ln]
record("L63a: 14 su 14 ancora presi", p.returncode == 0 and tail and tail[-1].startswith("14 / 14"),
       tail[-1] if tail else p.stdout[-200:])

caught = sum(ok for _, ok in results)
print(f"\n{caught} / {len(results)} presi")
sys.exit(0 if caught == len(results) else 1)
