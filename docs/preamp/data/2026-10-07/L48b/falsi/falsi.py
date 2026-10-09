#!/usr/bin/env python3
"""L48b (ADR-065): the sabotages that must make 2e and 2f fail on C_T and R_G.

Builds sabotaged copies of the regenerated audio netlist by text, runs the 2e
checker (check_relay_safe_state.py) and the 2f block diagram
(preamp_blocks_draw.py, through PREAMP_AUDIO_NET) on each, and writes
verdetti.txt. A sabotage passes only if each check that must fail exits
NONZERO with the finding it was built for in its output: a check that fails
for another reason has not been tested. The helpers are L48a's
(data/2026-10-06/L48a/falsi/falsi.py).

    /usr/bin/python3 docs/preamp/data/2026-10-07/L48b/falsi/falsi.py

Bases: main_audio.net (the netlist on main before L48b: the trim's COM
straight on the volume's top, no R_G) and circuits/preamp/preamp_audio.net.
"""
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
NEW_AUDIO = REPO / "circuits" / "preamp" / "preamp_audio.net"
CHECK_2E = REPO / "scripts" / "check_relay_safe_state.py"
DRAW_2F = REPO / "docs" / "preamp" / "schematic" / "preamp_blocks_draw.py"
VENV_PY = "/Users/roberto/EDA/env/venv/bin/python3"
NODE = r'\(node\s*\(ref "{ref}"\)\s*\(pin "{pin}"\)\s*(\(pinfunction "[^"]*"\)\s*)?\(pintype "[^"]*"\)\)'


def take(text, ref, pin):
    pat = re.compile(NODE.format(ref=re.escape(ref), pin=re.escape(pin)))
    m = pat.search(text)
    assert m, (ref, pin)
    return text[:m.start()] + text[m.end():], m.group(0)


def move_pin(text, ref, pin, new_net):
    """Take (ref, pin) off its net and put it alone on a new net."""
    text, node = take(text, ref, pin)
    i = text.rindex(")")
    j = text.rindex(")", 0, i)
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


def set_value(text, ref, value):
    pat = re.compile(r'(\(comp\s*\(ref "%s"\)\s*\(value ")([^"]*)(")' % re.escape(ref))
    m = pat.search(text)
    assert m, ref
    return text[:m.start(2)] + value + text[m.end(2):]


new_a = NEW_AUDIO.read_text()
main_a = (HERE / "main_audio.net").read_text()

# (name, netlist text, what 2e must say, what 2f must say or None = 2f must pass)
CASES = [
    ("main", main_a, "e' NC-041", "non sta sul solo C265"),
    ("ct_cortocircuitato_L", join_pin(new_a, "J120", "1", "L_TRIM_OUT"),
     "e' NC-041", "non sta sul solo C265"),
    ("ct_cortocircuitato_R", join_pin(new_a, "J320", "1", "R_TRIM_OUT"),
     "e' NC-041", "non sta sul solo C465"),
    ("ct_scavalcato_da_r",
     join_pin(join_pin(new_a, "R265", "1", "L_ATT_TOP"), "R265", "2", "L_TRIM_OUT"),
     "nessuna strada in continua", "non sta sul solo C265"),
    ("rg_staccata_da_gnd", move_pin(new_a, "R465", "2", "R_RG_SOSPESA"),
     "R_G = 1M verso GND", "non va a massa"),
    ("rg_100k", set_value(new_a, "R265", "100k"),
     "R_G = 1M verso GND", "non sono 1M / 10u"),
    ("rg_tolta_dal_cursore", move_pin(new_a, "R265", "1", "L_RG_SOLA"),
     "R_G = 1M verso GND", "non porta solo l'ingresso del blocco B"),
    ("connettore_rinominato", set_value(new_a, "J120", "ATT_L 10k"),
     "il connettore del volume VOL_L", None),
]


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


lines = []
ok_all = True
for name, text, want_2e, want_2f in CASES:
    net = HERE / ("%s.net" % name)
    net.write_text(text)
    rc_e, out_e = run(["/usr/bin/python3", str(CHECK_2E), str(net)])
    env = dict(os.environ, PREAMP_AUDIO_NET=str(net),
               PREAMP_BLOCKS_SVG=str(HERE / "scarto.svg"))
    rc_f, out_f = run([VENV_PY, str(DRAW_2F)], env=env)
    e_ok = rc_e != 0 and want_2e in out_e
    f_ok = (rc_f != 0 and want_2f in out_f) if want_2f else rc_f == 0
    ok_all &= e_ok and f_ok
    lines.append("%-24s 2e rc=%d %s   2f rc=%d %s" % (
        name, rc_e, "CADE COME DEVE" if e_ok else "NON CADE",
        rc_f, ("CADE COME DEVE" if f_ok else "NON CADE") if want_2f
        else ("PASSA COME DEVE" if f_ok else "NON PASSA")))
    net.unlink()
(HERE / "scarto.svg").unlink(missing_ok=True)

# The real netlist must pass both.
rc_e, out_e = run(["/usr/bin/python3", str(CHECK_2E), str(NEW_AUDIO)])
env = dict(os.environ, PREAMP_BLOCKS_SVG=str(HERE / "scarto.svg"))
rc_f, out_f = run([VENV_PY, str(DRAW_2F)], env=env)
(HERE / "scarto.svg").unlink(missing_ok=True)
lines.append("%-24s 2e rc=%d   2f rc=%d" % ("preamp_audio.net", rc_e, rc_f))
ok_all &= rc_e == 0 and rc_f == 0
n_ok = sum("NON " not in l for l in lines[:-1])
lines.append("%d falsi su %d cadono dove devono; netlist vera %s"
             % (n_ok, len(CASES), "passa" if rc_e == 0 and rc_f == 0 else "NON passa"))
(HERE / "verdetti.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
raise SystemExit(0 if ok_all else 1)
