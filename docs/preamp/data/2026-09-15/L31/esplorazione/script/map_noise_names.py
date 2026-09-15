#!/usr/bin/env python3
"""
map_noise_names.py - L31: what the per-device noise vectors of
tb_noise_vectors.cir named when they were written (L4), and what they are
called in today's generated include.

The mapping is derived from the NODES, never from the names (limitations
#22, rule a): a device is matched to today's element of the same type
letter with the same node tuple. Zero matches or more than one is a refusal
- a merged net can change name between two generations (#23), and then
this script must stop rather than guess.

Every name the deck cites TODAY is also classified, because a renumbering
leaves two kinds of wrong name and only one of them gives an error:
    dead        the device does not exist today  (ngspice: "no such vector")
    live-other  the name exists today but is ANOTHER device (silent)
    live-same   the name exists and is the same device

git is not called from here: the L4 files are exported with `git show`
first.

USAGE
    python3 map_noise_names.py <include_L4> <deck_L4> <include_today> <deck_today>

Exit: 0 every L4 device has exactly one match today; 1 otherwise; 2 usage.
"""
import sys
from pathlib import Path

NODE_COUNT = {"r": 2, "c": 2, "l": 2, "d": 2, "q": 3, "j": 3, "v": 2}
RESERVED = {"spectrum", "total"}


def elements(path):
    """{name: (type letter, node tuple)} of the netlist lines outside .control."""
    out = {}
    in_control = False
    first = True
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        if first:                      # a .cir's line 1 is its title
            first = False
            if path.endswith(".cir"):
                continue
        s = raw.split(";")[0].strip()
        low = s.lower()
        if not s or s.startswith("*"):
            continue
        if low.startswith(".control"):
            in_control = True
            continue
        if low.startswith(".endc"):
            in_control = False
            continue
        if in_control or s.startswith((".", "+")):
            continue
        toks = s.split()
        n = NODE_COUNT.get(toks[0][0].lower())
        if n is None:
            continue
        out[toks[0].lower()] = (toks[0][0].lower(),
                                tuple(t.upper() for t in toks[1:1 + n]))
    return out


def wrdata_devices(deck):
    """Device names of the per-device noise vectors on the deck's wrdata line."""
    for raw in Path(deck).read_text(encoding="utf-8").splitlines():
        toks = raw.split()
        if toks and toks[0].lower() == "wrdata":
            names = []
            for t in toks[2:]:
                kind, _, dev = t.lower().partition("noise_")
                if kind in ("o", "i") and dev not in RESERVED:
                    names.append(dev)
            return names
    raise SystemExit(f"{deck}: no wrdata line")


def main(argv):
    if len(argv) != 5:
        print(__doc__)
        return 2
    inc_old, deck_old, inc_new, deck_new = argv[1:]
    old = {**elements(inc_old), **elements(deck_old)}
    new = {**elements(inc_new), **elements(deck_new)}

    bad = 0
    mapping = {}
    print("== L4 devices -> today, matched by type and nodes ==")
    for dev in wrdata_devices(deck_old):
        if dev not in old:
            print(f"   {dev}: NOT A DEVICE of the L4 files - refusing")
            bad += 1
            continue
        kind, nodes = old[dev]
        hits = [n for n, (k, nd) in new.items() if k == kind and nd == nodes]
        if len(hits) != 1:
            print(f"   {dev} {' '.join(nodes)}: {len(hits)} matches today "
                  f"{hits} - refusing")
            bad += 1
            continue
        mapping[dev] = hits[0]
        print(f"   {dev:6s} {' '.join(nodes):22s} -> {hits[0]}")

    print("\n== names the deck cites today ==")
    inverse = {v: k for k, v in mapping.items()}
    for dev in wrdata_devices(deck_new):
        if dev not in new:
            state = "dead"
        elif dev in mapping and mapping[dev] == dev:
            state = "live-same"
        elif dev in mapping:
            state = (f"live-other: today {dev} is {' '.join(new[dev][1])}, "
                     f"the L4 device is now {mapping[dev]}")
        else:
            state = "not in the L4 list"
        print(f"   {dev:6s} {state}")

    print("\n== renamed wrdata vectors, in the L4 order ==")
    print("   " + " ".join(f"onoise_{mapping.get(d, d)}"
                          for d in wrdata_devices(deck_old)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
