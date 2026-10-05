#!/usr/bin/env python3
"""L47c1 (ADR-062): the sabotages that must make 2e and 2j fail.

Builds sabotaged copies of the netlists by text, runs the two checkers on
each, and writes verdetti.txt. A sabotage passes only if its checker exits
NONZERO and its output contains the finding it was built for: a check that
fails for another reason has not been tested.

    /usr/bin/python3 docs/preamp/data/2026-10-05/L47c1/falsi/falsi.py

Bases: main_audio.net / main_psu.net (the netlists on main before L47c1,
with the four NSL-32SR3 cells and J3) and the regenerated ones in
circuits/preamp/.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
NEW_AUDIO = REPO / "circuits" / "preamp" / "preamp_audio.net"
NEW_PSU = REPO / "circuits" / "preamp" / "psu.net"
CHECK_2E = REPO / "scripts" / "check_relay_safe_state.py"
CHECK_2J = REPO / "scripts" / "check_psu_harness.py"
NODE = r'\(node\s*\(ref "{ref}"\)\s*\(pin "{pin}"\)\s*(\(pinfunction "[^"]*"\)\s*)?\(pintype "[^"]*"\)\)'


def move_pin(text, ref, pin, new_net):
    """Take (ref, pin) off its net and put it alone on a new net."""
    pat = re.compile(NODE.format(ref=re.escape(ref), pin=re.escape(pin)))
    m = pat.search(text)
    assert m, (ref, pin)
    node = m.group(0)
    text = text[:m.start()] + text[m.end():]
    i = text.rindex(")")          # the netlist's closing paren
    j = text.rindex(")", 0, i)    # the nets section's closing paren
    net = ('\n    (net\n      (code 9999)\n      (name "%s")\n      (class "Default")\n      %s)'
           % (new_net, node))
    return text[:j] + net + text[j:]


def add_comp(text, ref, value, lib, part):
    i = text.index("  (components\n") + len("  (components\n")
    comp = ('    (comp\n      (ref "%s")\n      (value "%s")\n'
            '      (libsource (lib "%s") (part "%s") (description ""))\n    )\n'
            % (ref, value, lib, part))
    return text[:i] + comp + text[i:]


def rename_net(text, old, new):
    a = '(name "%s")' % old
    assert text.count(a) == 1, old
    return text.replace(a, '(name "%s")' % new)


def write(name, text):
    p = HERE / name
    p.write_text(text)
    return p


main_a = (HERE / "main_audio.net").read_text()
main_p = (HERE / "main_psu.net").read_text()
new_a = NEW_AUDIO.read_text()
new_p = NEW_PSU.read_text()

cases = []   # (name, checker, args, expected substring)

# --- 2e: the input with no graduated mute
cases.append(("2e main (le quattro celle)", CHECK_2E,
              [HERE / "main_audio.net"], "una parte del mute graduale"))
cases.append(("2e qualcosa in serie all'ingresso L", CHECK_2E,
              [write("2e_serie_ingresso.net",
                     move_pin(new_a, "J101", "1", "L_IN_SRC"))],
              "il connettore va dritto all'ingresso del blocco A"))
cases.append(("2e una cella fuori dalla libreria Isolator, col valore LDR", CHECK_2E,
              [write("2e_cella_altra_libreria.net",
                     add_comp(new_a, "U999", "NSL-32SR3 LDR_S_L", "Device", "R"))],
              "una parte del mute graduale"))
cases.append(("2e una cella Isolator col valore muto", CHECK_2E,
              [write("2e_cella_valore_muto.net",
                     add_comp(new_a, "U998", "X", "Isolator", "NSL-32"))],
              "una parte del mute graduale"))
cases.append(("2e il freddo dell'ingresso R non a massa", CHECK_2E,
              [write("2e_freddo_non_a_massa.net",
                     move_pin(new_a, "J301", "2", "R_IN_COLD"))],
              "il pin 2 deve stare su GND"))

# --- 2j: J3 on neither board
cases.append(("2j main (J3 sulle due schede)", CHECK_2J,
              [HERE / "main_audio.net", HERE / "main_psu.net"],
              "harness LDR_CMD (J3) is still there"))
cases.append(("2j J3 solo sull'alimentatore", CHECK_2J,
              [NEW_AUDIO, HERE / "main_psu.net"],
              "psu: harness LDR_CMD (J3) is still there"))
cases.append(("2j J3 solo sulla scheda audio", CHECK_2J,
              [HERE / "main_audio.net", NEW_PSU],
              "audio: harness LDR_CMD (J3) is still there"))
cases.append(("2j una rete del pilota rimasta sull'alimentatore", CHECK_2J,
              [NEW_AUDIO, write("2j_rete_ldr_rimasta.net",
                                rename_net(new_p, "MUTE_G_IN", "LDR_S_A"))],
              "net(s) LDR_S_A of the retired LDR_CMD"))

# --- the controls: the regenerated netlists pass
controls = [("2e controllo: netlist nuova", CHECK_2E, [NEW_AUDIO]),
            ("2j controllo: netlist nuove", CHECK_2J, [NEW_AUDIO, NEW_PSU])]

lines, bad = [], 0
for name, chk, args, want in cases:
    r = subprocess.run([sys.executable, str(chk)] + [str(a) for a in args],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    ok = r.returncode != 0 and want in out
    bad += not ok
    lines.append("%s  rc=%d  %s  [atteso: %s]"
                 % ("CADE " if ok else "NON CADE", r.returncode, name, want))
for name, chk, args in controls:
    r = subprocess.run([sys.executable, str(chk)] + [str(a) for a in args],
                       capture_output=True, text=True)
    ok = r.returncode == 0
    bad += not ok
    lines.append("%s  rc=%d  %s" % ("PASSA" if ok else "NON PASSA", r.returncode, name))
lines.append("")
lines.append("%d falsi su %d cadono per il motivo giusto; controlli %s"
             % (sum(1 for l in lines if l.startswith("CADE ")), len(cases),
                "OK" if bad == 0 else "FALLITI"))
(HERE / "verdetti.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if bad else 0)
