#!/usr/bin/env python3
"""
check_deck_refs.py - every device a testbench NAMES must exist in the circuit
the testbench READS.

WHY THIS EXISTS (L10)
---------------------
ngspice does not fail on a device name it cannot find inside a .control
block. `alter r138 = 1e12` on a netlist with no R138 prints

    Error: no such device or model name r138

and carries on, and the run exits 0. So when L22 merged the two halves of
the LS352 into one Part and every later reference slid by -1, the deck
tb_switch_v2_counterfactual.cir kept opening "R138" - which no longer
existed. Its state B, "R_f open, loop broken", silently became a copy of
state A: v(OUT) -0.0522 V in both, where before L22 the same deck drove the
output to -13.677 V. The falsifiable half of V2 stopped falsifying anything,
and nothing said so. The block diagram had the same disease (NC-026).

A renumbering is exactly when this happens, so the check has to be
mechanical rather than a line in a checklist.

WHAT IT CHECKS
--------------
For each deck: the element names defined by the deck itself and by every
file it .include's (after @REPO@ substitution), against every device the
deck cites by name:

    @name[param]          print / let / meas / save / wrdata
    alter name = ...      alter @name[param] = ...

Names are compared case-insensitively, as SPICE does. A cited name with a
subcircuit path (x1.q106) is checked on its last component.

USAGE
-----
    /usr/bin/python3 scripts/check_deck_refs.py <repo-root> <deck.cir>...

Exit codes:  0 = every cited device exists
             1 = at least one cited device does not exist
             2 = bad invocation / unreadable input / a deck with no citations
                 at all among decks that were expected to have some is NOT an
                 error - but a deck whose includes cannot be read IS.
"""
import re
import sys
from pathlib import Path

ELEMENT = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s")
INCLUDE = re.compile(r"^\s*\.include\s+(\S+)", re.IGNORECASE)
AT_REF = re.compile(r"@([A-Za-z][A-Za-z0-9_.]*)\[")
ALTER = re.compile(r"^\s*alter\s+([A-Za-z][A-Za-z0-9_.]*)\s*=", re.IGNORECASE)


def logical_lines(text):
    """Strip comments; keep the line number for reporting."""
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split(";")[0]
        s = line.strip()
        if not s or s.startswith("*"):
            continue
        yield n, line


def defined_names(path, repo, seen):
    """Element names defined in `path` and, recursively, in its includes."""
    path = path.resolve()
    if path in seen:
        return set()
    seen.add(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    names = set()
    in_control = False
    for _, line in logical_lines(text):
        s = line.strip()
        low = s.lower()
        if low.startswith(".control"):
            in_control = True
            continue
        if low.startswith(".endc"):
            in_control = False
            continue
        m = INCLUDE.match(line)
        if m:
            inc = Path(m.group(1).replace("@REPO@", str(repo)))
            if not inc.is_file():
                raise FileNotFoundError(f"{path}: include not found: {inc}")
            names |= defined_names(inc, repo, seen)
            continue
        if in_control or s.startswith(".") or s.startswith("+"):
            continue
        m = ELEMENT.match(line)
        if m:
            names.add(m.group(1).lower())
    return names


def cited_names(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    out = []
    first = True
    for n, line in logical_lines(text):
        if first:            # line 1 of a .cir is always the title
            first = False
            if n == 1:
                continue
        for m in AT_REF.finditer(line):
            out.append((n, m.group(1)))
        m = ALTER.match(line)
        if m:
            out.append((n, m.group(1)))
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    repo = Path(argv[1]).resolve()
    missing = 0
    cited_total = 0
    for deck in map(Path, argv[2:]):
        try:
            names = defined_names(deck, repo, set())
        except (OSError, FileNotFoundError) as e:
            print(f"UNREADABLE: {e}")
            return 2
        cites = cited_names(deck)
        cited_total += len(cites)
        bad = [(n, c) for n, c in cites
               if c.split(".")[-1].lower() not in names]
        for n, c in bad:
            print(f"   {deck.name}:{n}: '{c}' is not a device of this deck")
        missing += len(bad)
        status = "OK" if not bad else f"{len(bad)} MISSING"
        print(f"   {status}: {deck.name} ({len(cites)} citations, "
              f"{len(names)} devices)")
    if cited_total == 0:
        # A checker that finds nothing to check and exits 0 is decorative.
        print("   no device citations found in any deck - refusing to pass")
        return 2
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
