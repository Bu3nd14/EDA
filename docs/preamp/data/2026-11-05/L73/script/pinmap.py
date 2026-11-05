"""
L73: the symbol-pin -> footprint-pad map of the SMD transistors, for the TRIAL
boards only.

The finding (L45d2b3b2b1's README already noted it, "un rilievo per il layout"):
Device:Q_NPN / Q_PNP name their pins "B", "C", "E" (and Q_NMOS / Q_PMOS "G",
"D", "S"), while KiCad's SOT-23 / SOT-223 footprints number their pads "1",
"2", "3". kinet2pcb joins a net to a pad by name, so EVERY such transistor
lands on the board with no net on any pad, without an error. L49a's board
(2026-10-09, "100 %, DRC 0 / 0") had all its SOT-23 and TO-220 transistors
unconnected for this reason. Only the TO-220 + heatsink footprint of ADR-099
(library/preamp.pretty) names its pads B / C / E.

The fix for G2 (a pad map per footprint, or footprints with named pads) is a
decision for the source. Here the trial netlist is rewritten so the router
sees the real connections. Each pin-out is read from the datasheet in vendor/
(top-view drawing, 2026-11-05), matched to KiCad's pad positions:
- SOT-23 BJT, Diodes Inc. MMBT5551 / MMBT5401 (and BC847 / BC857, DS11108 /
  DS11207): C alone on one side, B and E on the other -> 1 = B, 2 = E, 3 = C;
- SOT-223 BJT, Diodes Inc. DZT5551 / DZT5401: leads E, C, B top to bottom,
  the tab C -> 1 = B, 2 = C (and the tab, TabPin2), 3 = E;
The supply board is not affected: its transistors use KiCad's own symbols
(Transistor_FET:2N7002 / AO3401A, Transistor_BJT:BC847 / BC857), whose pins are
numbered like the pads (checked on the board: no empty pad, README).
"""
import re

MAPS = {
    ("SOT-23", "BJT"): {"B": "1", "E": "2", "C": "3"},
    ("SOT-223-3_TabPin2", "BJT"): {"B": "1", "C": "2", "E": "3"},
}


def remap(text):
    """Rewrite the nodes of the netlist text. Returns (text, {ref: {pin: pad}})."""
    comps = text.split("(comp\n")
    kind = {}
    for b in comps[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', b).group(1)
        fp = re.search(r'\(footprint "([^"]+)"\)', b)
        part = re.search(r'\(part "([^"]+)"\)', b)
        if not fp or not part:
            continue
        name = fp.group(1).split(":")[1]
        p = part.group(1)
        if p in ("Q_NPN", "Q_PNP"):
            k = (name, "BJT")
        else:
            continue
        if k in MAPS:
            kind[ref] = MAPS[k]
    done = {}

    def sub(m):
        ref, pin = m.group(1), m.group(3)
        if ref in kind and pin in kind[ref]:
            done.setdefault(ref, {})[pin] = kind[ref][pin]
            return f'(ref "{ref}"){m.group(2)}(pin "{kind[ref][pin]}")'
        return m.group(0)

    head, sep, nets = text.partition("(nets")
    nets = re.sub(r'\(ref "([^"]+)"\)(\s*)\(pin "([^"]+)"\)', sub, nets)
    missing = sorted(set(kind) - set(done))
    assert not missing, ("transistors with no remapped pin", missing)
    return head + sep + nets, done
