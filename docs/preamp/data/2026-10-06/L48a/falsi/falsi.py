#!/usr/bin/env python3
"""L48a (ADR-064): the sabotages that must make 2e fail on the selector.

Builds sabotaged copies of the regenerated audio netlist by text, runs the
2e checker on each, and writes verdetti.txt. A sabotage passes only if the
checker exits NONZERO and its output contains the finding it was built for:
a check that fails for another reason has not been tested.

    /usr/bin/python3 docs/preamp/data/2026-10-06/L48a/falsi/falsi.py

Bases: main_audio.net (the netlist on main before L48a: one DC-coupled
input per channel, no selector) and circuits/preamp/preamp_audio.net.
2j is not sabotaged here: L48a changes no pin of the harness between the
boards (J1, J2, J4), and 2j passes on the new netlist unchanged.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
NEW_AUDIO = REPO / "circuits" / "preamp" / "preamp_audio.net"
CHECK_2E = REPO / "scripts" / "check_relay_safe_state.py"
NODE = r'\(node\s*\(ref "{ref}"\)\s*\(pin "{pin}"\)\s*(\(pinfunction "[^"]*"\)\s*)?\(pintype "[^"]*"\)\)'


def take(text, ref, pin):
    pat = re.compile(NODE.format(ref=re.escape(ref), pin=re.escape(pin)))
    m = pat.search(text)
    assert m, (ref, pin)
    return text[:m.start()] + text[m.end():], m.group(0)


def move_pin(text, ref, pin, new_net):
    """Take (ref, pin) off its net and put it alone on a new net."""
    text, node = take(text, ref, pin)
    i = text.rindex(")")          # the netlist's closing paren
    j = text.rindex(")", 0, i)    # the nets section's closing paren
    net = ('\n    (net\n      (code 9999)\n      (name "%s")\n      (class "Default")\n      %s)'
           % (new_net, node))
    return text[:j] + net + text[j:]


def join_pin(text, ref, pin, net_name):
    """Take (ref, pin) off its net and put it on the existing net_name."""
    text, node = take(text, ref, pin)
    a = '(name "%s")\n      (class "Default")' % net_name
    assert text.count(a) == 1, net_name
    i = text.index(a) + len(a)
    return text[:i] + "\n      " + node + text[i:]


def add_pin(text, ref, pin, net_name):
    """Put a pin that sits on no net (an unconnected NC) on net_name."""
    assert not re.search(NODE.format(ref=re.escape(ref), pin=re.escape(pin)), text)
    node = '(node (ref "%s") (pin "%s") (pintype "PASSIVE"))' % (ref, pin)
    a = '(name "%s")\n      (class "Default")' % net_name
    assert text.count(a) == 1, net_name
    i = text.index(a) + len(a)
    return text[:i] + "\n      " + node + text[i:]


def set_part(text, ref, part):
    """Change the libsource part of component ref."""
    pat = re.compile(r'(\(comp\s*\(ref "%s"\).*?\(part ")([^"]*)(")' % re.escape(ref),
                     re.S)
    m = pat.search(text)
    assert m, ref
    return text[:m.start(2)] + part + text[m.end(2):]


def write(name, text):
    p = HERE / name
    p.write_text(text)
    return p


new_a = NEW_AUDIO.read_text()

cases = []   # (name, args, expected substring)
cases.append(("main: un ingresso in continua, nessun selettore",
              [HERE / "main_audio.net"], "attesi esattamente i rele' SEL1..SEL4"))
cases.append(("IN1_L in continua sull'ingresso del blocco A (NC-040 rimessa)",
              [write("2e_ingresso_in_continua.net",
                     join_pin(new_a, "J101", "1", "AL_IN"))],
              "in continua: e' NC-040"))
cases.append(("R_SEL di IN1_L tolta (lato del preamp sospeso)",
              [write("2e_senza_rsel.net", move_pin(new_a, "R171", "2", "R171_SOSPESA"))],
              "porta 0 resistenze a GND"))
cases.append(("R_J di IN2_R tolta (jack vuoto sospeso)",
              [write("2e_senza_rj.net", move_pin(new_a, "R376", "2", "R376_SOSPESA"))],
              "a jack vuoto l'ingresso resta sospeso"))
cases.append(("il NC di SEL1 sull'ingresso del blocco A L",
              [write("2e_nc_sul_blocco.net", add_pin(new_a, "K13", "2", "AL_IN"))],
              "il NC sta su"))
cases.append(("IN3_L sul NO del rele' sbagliato",
              [write("2e_rele_sbagliato.net",
                     move_pin(new_a, "K15", "4", "K15_NO_ALTROVE"))],
              "non va al NO del polo 1"))
cases.append(("la manopola in posizione 2 alimenta SEL1",
              [write("2e_manopola_scambiata.net",
                     join_pin(new_a, "SW4", "2", "SEL1_HI"))],
              "SW4 in posizione 2, in mute: alimenta le bobine SEL['1'], attesa solo SEL2"))
cases.append(("il diodo di ricircolo di SEL3 al contrario",
              [write("2e_diodo_al_contrario.net",
                     join_pin(join_pin(new_a, "D18", "1", "RLY_RET"),
                              "D18", "2", "SEL3_HI"))],
              "nessun diodo di ricircolo"))
cases.append(("SEL2 bistabile",
              [write("2e_sel_bistabile.net", set_part(new_a, "K14", "G6KU-2"))],
              "il ruolo SEL vuole un rele' monostabile"))
cases.append(("la bobina di SEL4 a GND invece che su RLY_RET",
              [write("2e_bobina_a_massa.net", join_pin(new_a, "K16", "8", "GND"))],
              "la bobina torna su GND"))

controls = [("controllo: netlist nuova", [NEW_AUDIO])]

lines, bad = [], 0
for name, args, want in cases:
    r = subprocess.run([sys.executable, str(CHECK_2E)] + [str(a) for a in args],
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    ok = r.returncode != 0 and want in out
    bad += not ok
    lines.append("%s  rc=%d  %s  [atteso: %s]"
                 % ("CADE " if ok else "NON CADE", r.returncode, name, want))
for name, args in controls:
    r = subprocess.run([sys.executable, str(CHECK_2E)] + [str(a) for a in args],
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
