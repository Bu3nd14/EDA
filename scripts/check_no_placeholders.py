#!/usr/bin/env python3
"""
check_no_placeholders.py - no canonical testbench and no generated block may
simulate a hand-written placeholder model.

WHY THIS EXISTS (L39, NC-017)
-----------------------------
Until L39 the gain block instantiated LSK489X, NSS2N5551, PSS2N5401,
NMJE15032, PMJE15033 and D1N4148: hand-written models with KF = 0 in
spice/preamp/placeholder_devices.lib. L39 put the manufacturer models of
models/ in their place, in circuits/preamp/gain_block.py and in every deck of
spice/preamp/tb/. The placeholder library stays in the repo, because the dated
decks under docs/preamp/data/ include it and must stay re-runnable. So nothing
stops a copied deck header, or a model name typed back into the source, from
bringing a placeholder back - and ngspice would simulate it without a word.

This is block 2i of run_tests.sh. Until L39 block 2i checked the JFET variant
derived by scripts/derive_jfet_variant.py; since the generated block names
LSK489A itself, that derivation has nothing left to do and is retired.

WHAT IT CHECKS
--------------
  1. no deck under spice/*/tb/ has an .include of placeholder_devices.lib;
  2. no device line (Q/J/D/M) of the generated blocks - spice/preamp/*.inc,
     spice/preamp/*.subckt - names a model DEFINED in placeholder_devices.lib
     (the names are read from that file, not listed here);
  3. no device line of a deck itself names one of those models.
A comment line ('*') is never a finding: the decks may say what they used to
simulate.

USAGE
-----
    /usr/bin/python3 scripts/check_no_placeholders.py <repo-root>

Exit codes:  0 = no placeholder is simulated
             1 = at least one is
             2 = bad invocation, or the placeholder library or the generated
                 block cannot be read (a check with nothing to read does not pass)
"""

import glob
import os
import re
import sys

LIB = os.path.join("spice", "preamp", "placeholder_devices.lib")


def model_names(path):
    names = set()
    with open(path) as f:
        for ln in f:
            m = re.match(r"^\s*\.model\s+(\S+)", ln, re.I)
            if m:
                names.add(m.group(1).upper())
    return names


def device_hits(path, names):
    """[(line number, text)] of device lines whose last token is a placeholder."""
    out = []
    with open(path, errors="replace") as f:
        for n, ln in enumerate(f, 1):
            t = ln.split()
            if not t or ln.lstrip().startswith(("*", ".")):
                continue
            if t[0][0].upper() in "QJDM" and t[-1].upper() in names:
                out.append((n, ln.rstrip()))
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    repo = os.path.abspath(argv[1])
    lib = os.path.join(repo, LIB)
    if not os.path.exists(lib):
        print(f"   UNREADABLE: {LIB} not found")
        return 2
    names = model_names(lib)
    if not names:
        print(f"   UNREADABLE: no .model in {LIB}")
        return 2
    blocks = sorted(glob.glob(os.path.join(repo, "spice", "preamp", "*.inc"))
                    + glob.glob(os.path.join(repo, "spice", "preamp", "*.subckt")))
    decks = sorted(glob.glob(os.path.join(repo, "spice", "*", "tb", "*.cir")))
    if not blocks or not decks:
        print("   UNREADABLE: no generated block or no deck found")
        return 2
    bad = 0
    inc = re.compile(r"^\s*\.include\s+\S*placeholder_devices\.lib\b", re.I)
    for d in decks:
        with open(d, errors="replace") as f:
            for n, ln in enumerate(f, 1):
                if inc.match(ln):
                    bad += 1
                    print(f"   {os.path.relpath(d, repo)}:{n}: includes the placeholder library")
    for p in blocks + decks:
        for n, ln in device_hits(p, names):
            bad += 1
            print(f"   {os.path.relpath(p, repo)}:{n}: placeholder model - {ln}")
    print(f"   {'OK' if not bad else f'{bad} FOUND'}: {len(decks)} decks, "
          f"{len(blocks)} generated blocks, {len(names)} placeholder model names "
          f"({', '.join(sorted(names))})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
