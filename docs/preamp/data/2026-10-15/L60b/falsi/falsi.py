#!/usr/bin/env python3
"""falsi.py - L60b: the harness checker against sabotaged copies of the netlists.

J1 POWER is seven pins since L60b (ADR-082 point 2, ADR-083): 1-2 VPLUS,
3-4 GND, 5-6 VMINUS, 7 VRELAY. J4 MUTE_TIMER is three pins again (ADR-081).
Each sabotage below edits ONE pin of a copy of preamp_audio.net or psu.net,
in the nets section, and scripts/check_psu_harness.py must exit 1 on it.
The unsabotaged pair must exit 0. A checker that cannot fail proves nothing.

Usage: falsi.py <repo> <outdir>   (writes the copies and verdetti.txt there)
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
AUDIO = REPO / "circuits/preamp/preamp_audio.net"
PSU = REPO / "circuits/preamp/psu.net"
CHECK = REPO / "scripts/check_psu_harness.py"


def drop_pin(text, ref, pin):
    """Remove (node (ref ref) (pin pin) ...) from the nets: the pin unconnected."""
    pat = re.compile(r'\(node\s*\(ref "%s"\)\s*\(pin "%s"\)[^()]*(\([^()]*\)[^()]*)*\)'
                     % (re.escape(ref), re.escape(pin)))
    new, n = pat.subn("", text, count=1)
    assert n == 1, (ref, pin)
    return new


def move_pin(text, ref, pin, to_net):
    """Move the node of (ref, pin) into the net named to_net."""
    pat = re.compile(r'\(node\s*\(ref "%s"\)\s*\(pin "%s"\)[^()]*(\([^()]*\)[^()]*)*\)'
                     % (re.escape(ref), re.escape(pin)))
    m = pat.search(text)
    assert m, (ref, pin)
    node = m.group(0)
    text = text[:m.start()] + text[m.end():]
    k = text.index('(name "%s")' % to_net)
    k = text.index("(node", k)
    return text[:k] + node + " " + text[k:]


SABOTAGES = [
    # (name, board, edit)
    ("audio J1 pin 2 aperto (un filo del + solo)", "audio", lambda t: drop_pin(t, "J1", "2")),
    ("audio J1 pin 4 aperto (un filo di massa solo)", "audio", lambda t: drop_pin(t, "J1", "4")),
    ("audio J1 pin 6 aperto (un filo del - solo)", "audio", lambda t: drop_pin(t, "J1", "6")),
    ("psu J1 pin 1 aperto", "psu", lambda t: drop_pin(t, "J1", "1")),
    ("psu J1 pin 3 aperto", "psu", lambda t: drop_pin(t, "J1", "3")),
    ("psu J1 pin 5 aperto", "psu", lambda t: drop_pin(t, "J1", "5")),
    ("audio J1 pin 2 su VMINUS (le coppie incrociate)", "audio", lambda t: move_pin(t, "J1", "2", "VMINUS")),
    ("psu J1 pin 6 su VPLUS", "psu", lambda t: move_pin(t, "J1", "6", "VPLUS")),
    ("psu J1 pin 7 su GND (VRELAY persa)", "psu", lambda t: move_pin(t, "J1", "7", "GND")),
]


def run(audio, psu):
    r = subprocess.run(["/usr/bin/python3", str(CHECK), str(audio), str(psu)],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()


lines = ["# L60b: check_psu_harness.py contro i sabotaggi di J1 a sette pin (ADR-083)",
         "# atteso: 0 sulla coppia intatta, 1 su ogni sabotaggio"]
rc, out = run(AUDIO, PSU)
lines.append("intatta: exit %d  %s" % (rc, out[-1] if out else ""))
ok = rc == 0
base = {"audio": AUDIO.read_text(), "psu": PSU.read_text()}
for i, (name, board, edit) in enumerate(SABOTAGES, 1):
    texts = dict(base)
    texts[board] = edit(texts[board])
    a = OUT / ("s%02d_audio.net" % i)
    p = OUT / ("s%02d_psu.net" % i)
    a.write_text(texts["audio"])
    p.write_text(texts["psu"])
    rc, out = run(a, p)
    first = next((x for x in out if "J1" in x), out[0] if out else "")
    lines.append("s%02d %s: exit %d  %s" % (i, name, rc, first.strip()))
    ok = ok and rc == 1
    a.unlink()
    p.unlink()
lines.append("ESITO: %s" % ("tutti i sabotaggi presi, la coppia intatta passa" if ok else "FALLITO"))
(OUT / "verdetti.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if ok else 1)
