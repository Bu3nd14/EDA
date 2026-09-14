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
             2 = bad invocation, an include that cannot be read, or NO device
                 citation found in any deck (a check with nothing to check
                 does not pass). A single deck without citations is fine.

WHAT IT CANNOT SEE: a citation of a device that EXISTS but is the wrong one.
After L22, tb_bias_sweep.cir swept `r130`, which had become the other leg of
the Vbe multiplier - a live name, so this check passes it. Only comparing a
deck's numbers before and after a renumbering catches that (limitations #22).

WHAT IT ALSO CHECKS (L27): NODES THE BLOCK LEAVES DANGLING
----------------------------------------------------------
L27 gave the gain block a second relay-contact node, RG10 (ADR-026). A deck
written for one contact node leaves RG10 on a single terminal - R143 - and
ngspice does NOT complain: a node on one resistor is not a singular matrix,
it simply follows FB. Measured, not assumed, on the unmodified decks:
tb_op.cir gave the same 87 values as before, and tb_ac.cir's "10db" mode,
which only closes RG, printed +3.04 dB at 1 kHz instead of +9.95 dB - under
a file name that still says 10db, with exit code 0.

So, for every file a deck includes directly:
  * a GENERATED FLAT include declares "External nodes: ..." in its header.
    Any of those nodes that has exactly ONE terminal inside the include is a
    contact node, and the deck's own element lines must connect it;
  * a .subckt instantiated by an X line must receive exactly as many nodes
    as it declares ports, and every port with ONE terminal inside the body
    must be connected by some other element line of the deck.
The rule is derived from the generated files, not from a list of names, so
a third contact node would be caught without touching this script.
"""
import re
import sys
from pathlib import Path

ELEMENT = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s")
INCLUDE = re.compile(r"^\s*\.include\s+(\S+)", re.IGNORECASE)
AT_REF = re.compile(r"@([A-Za-z][A-Za-z0-9_.]*)\[")
ALTER = re.compile(r"^\s*alter\s+([A-Za-z][A-Za-z0-9_.]*)\s*=", re.IGNORECASE)
EXTERNAL = re.compile(r"External nodes:\s*(.+?)\s*$")
SUBCKT = re.compile(r"^\s*\.subckt\s+(\S+)\s+(.*)$", re.IGNORECASE)
# Terminal count by element letter, for the generated block files only
# (circuits/preamp/spice_export.py writes R C D with 2 nodes, Q J with 3).
# Anything else inside a block file is refused rather than guessed.
NODE_COUNT = {"r": 2, "c": 2, "l": 2, "d": 2, "q": 3, "j": 3}


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


def block_nodes(path, line_no, line):
    """Node names of one element line inside a generated block file."""
    toks = line.split()
    n = NODE_COUNT.get(toks[0][0].lower())
    if n is None:
        raise ValueError(f"{path}:{line_no}: element '{toks[0]}' of a type "
                         f"this check does not know how to count")
    return [t.lower() for t in toks[1:1 + n]]


def included_blocks(deck, repo):
    """What the files `deck` includes DIRECTLY declare.

    flats: [(include name, [dangling external nodes])]
    subs:  {subckt name: ([ports], [indices of dangling ports])}
    A node is dangling when exactly one terminal inside the file touches it.
    """
    flats, subs = [], {}
    for _, line in logical_lines(deck.read_text(encoding="utf-8",
                                                errors="replace")):
        m = INCLUDE.match(line)
        if not m:
            continue
        inc = Path(m.group(1).replace("@REPO@", str(repo)))
        text = inc.read_text(encoding="utf-8", errors="replace")
        external = None
        for raw in text.splitlines():
            e = EXTERNAL.search(raw)
            if e:
                external = [t.lower() for t in e.group(1).split() if t != "0"]
                break
        top_counts, cur = {}, None
        for n, raw in logical_lines(text):
            s = raw.strip()
            sub = SUBCKT.match(s)
            if sub:
                cur = (sub.group(1).lower(),
                       [p.lower() for p in sub.group(2).split()], {})
                continue
            if s.lower().startswith(".ends"):
                name, ports, counts = cur
                subs[name] = (ports, [i for i, p in enumerate(ports)
                                      if counts.get(p, 0) == 1])
                cur = None
                continue
            if s.startswith((".", "+")):
                continue
            if cur is None and external is None:
                continue          # a model library: nothing to count
            counts = cur[2] if cur else top_counts
            for node in block_nodes(inc, n, s):
                counts[node] = counts.get(node, 0) + 1
        if external is not None:
            flats.append((inc.name, [x for x in external
                                     if top_counts.get(x, 0) == 1]))
    return flats, subs


def deck_elements(deck):
    """The deck's OWN netlist lines: {node token: {line numbers}}, X lines."""
    mentions, xlines = {}, []
    in_control = False
    first = True
    for n, line in logical_lines(deck.read_text(encoding="utf-8",
                                                errors="replace")):
        if first:
            first = False
            if n == 1:
                continue
        s = line.strip()
        low = s.lower()
        if low.startswith(".control"):
            in_control = True
            continue
        if low.startswith(".endc"):
            in_control = False
            continue
        if in_control or s.startswith((".", "+")):
            continue
        toks = s.split()
        for t in toks[1:]:
            mentions.setdefault(t.lower(), set()).add(n)
        if toks[0][0].lower() == "x":
            xlines.append((n, toks))
    return mentions, xlines


def dangling_findings(deck, repo):
    flats, subs = included_blocks(deck, repo)
    mentions, xlines = deck_elements(deck)
    out = []
    for inc, dangling in flats:
        for node in dangling:
            if node not in mentions:
                out.append(f"{deck.name}: node {node.upper()} of {inc} has "
                           f"one terminal in the block and nothing in this "
                           f"deck connects it - an unterminated relay "
                           f"contact runs silently (ADR-026)")
    for n, toks in xlines:
        name = toks[-1].lower()
        if name not in subs:
            continue
        ports, dangling = subs[name]
        nodes = toks[1:-1]
        if len(nodes) != len(ports):
            out.append(f"{deck.name}:{n}: {toks[0]} passes {len(nodes)} "
                       f"nodes to {name.upper()}, which declares "
                       f"{len(ports)}: {' '.join(p.upper() for p in ports)}")
            continue
        for i in dangling:
            node = nodes[i].lower()
            if not (mentions.get(node, set()) - {n}):
                out.append(f"{deck.name}:{n}: {toks[0]} port "
                           f"{ports[i].upper()} -> {nodes[i]}, which no "
                           f"other element of this deck connects")
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
            dangling = dangling_findings(deck, repo)
        except (OSError, FileNotFoundError, ValueError) as e:
            print(f"UNREADABLE: {e}")
            return 2
        cites = cited_names(deck)
        cited_total += len(cites)
        bad = [(n, c) for n, c in cites
               if c.split(".")[-1].lower() not in names]
        for n, c in bad:
            print(f"   {deck.name}:{n}: '{c}' is not a device of this deck")
        for f in dangling:
            print(f"   {f}")
        missing += len(bad) + len(dangling)
        status = ("OK" if not (bad or dangling)
                  else f"{len(bad)} MISSING, {len(dangling)} DANGLING")
        print(f"   {status}: {deck.name} ({len(cites)} citations, "
              f"{len(names)} devices)")
    if cited_total == 0:
        # A checker that finds nothing to check and exits 0 is decorative.
        print("   no device citations found in any deck - refusing to pass")
        return 2
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
