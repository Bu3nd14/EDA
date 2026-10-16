#!/usr/bin/env python3
"""falsi.py - L60c2: the relay safe-state checker against a sabotaged K3.

K3 (the Stax's mute relay) is a TE Axicom IM06TS since L60c2 (ADR-085): the
same pin map as the G6K-2F-Y, but a POLARISED coil (+ on pin 1), and a part
the checker did not know. Each sabotage below edits ONE thing in a copy of
preamp_audio.net, and scripts/check_relay_safe_state.py must exit non-zero on
it with the finding named in EXPECT. The unsabotaged netlist must exit 0.
A checker that cannot fail proves nothing.

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
CHECK = REPO / "scripts/check_relay_safe_state.py"

NODE = r'\(node\s*\(ref "%s"\)\s*\(pin "%s"\)[^()]*(\([^()]*\)[^()]*)*\)'


def net_of(text, ref, pin):
    nets = text.split("(nets", 1)[-1]
    for chunk in re.split(r"\(net\s*\(code", nets)[1:]:
        if re.search(NODE % (re.escape(ref), re.escape(pin)), chunk):
            return re.search(r'\(name "([^"]*)"\)', chunk).group(1)
    raise AssertionError((ref, pin))


def drop_pin(text, ref, pin):
    new, n = re.subn(NODE % (re.escape(ref), re.escape(pin)), "", text, count=1)
    assert n == 1, (ref, pin)
    return new


def move_pin(text, ref, pin, to_net):
    m = re.search(NODE % (re.escape(ref), re.escape(pin)), text)
    assert m, (ref, pin)
    node = m.group(0)
    text = text[:m.start()] + text[m.end():]
    k = text.index('(name "%s")' % to_net)
    k = text.index("(node", k)
    return text[:k] + node + " " + text[k:]


def swap_pins(text, ref, a, b):
    na, nb = net_of(text, ref, a), net_of(text, ref, b)
    text = move_pin(text, ref, a, nb)
    return move_pin(text, ref, b, na)


def rename_part(text, ref, old, new):
    pat = re.compile(r'(\(comp\s*\(ref "%s"\).*?\(part ")%s(")' % (re.escape(ref), re.escape(old)), re.S)
    out, n = pat.subn(r"\g<1>%s\g<2>" % new, text, count=1)
    assert n == 1, (ref, old)
    return out


SABOTAGES = [
    # (name, edit, a phrase the finding must contain)
    ("K3 bobina al contrario (pin 1 sul comando, 8 su VRELAY)",
     lambda t: swap_pins(t, "K3", "1", "8"), "bobina polarizzata"),
    ("K3 pin 1 (+) a GND",
     lambda t: move_pin(t, "K3", "1", "GND"), "bobina polarizzata"),
    ("K3 polo 1: NC 2 e NO 4 scambiati",
     lambda t: swap_pins(t, "K3", "2", "4"), "K3 polo 1 (riga 1-2-3-4): il contatto NC (pin 2) dovrebbe essere a massa"),
    ("K3 polo 2: COM 6 e NC 7 scambiati (la NC-014 sul polo alto)",
     lambda t: swap_pins(t, "K3", "6", "7"), "K3 polo 2 (riga 8-7-6-5): il contatto NC (pin 7) dovrebbe essere a massa"),
    ("K3 polo 2: NO 5 aperto (il jack della Stax R senza contatto)",
     lambda t: drop_pin(t, "K3", "5"), "K3 polo 2 (riga 8-7-6-5): COM ('R_FIXC2') o NO (None) non collegato"),
    ("K3 pin 8 di bobina aperto",
     lambda t: drop_pin(t, "K3", "8"), "K3: il pin di bobina 8 non e' collegato"),
    ("K3 parte sconosciuta (IM05 invece di IM06)",
     lambda t: rename_part(t, "K3", "IM06", "IM05"), "rele' sconosciuto"),
]

src = AUDIO.read_text()
lines = []


def run(path):
    p = subprocess.run(["/usr/bin/python3", str(CHECK), str(path)],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


rc, out = run(AUDIO)
ok_clean = rc == 0
lines.append(f"{'OK ' if ok_clean else 'NO '} netlist vera: exit {rc} (atteso 0)")
caught = 0
for i, (name, edit, phrase) in enumerate(SABOTAGES, 1):
    f = OUT / f"falso_{i:02d}.net"
    f.write_text(edit(src))
    rc, out = run(f)
    hit = rc != 0 and phrase in out
    caught += hit
    first = next((ln.strip() for ln in out.splitlines()
                  if phrase in ln), out.strip().splitlines()[-1][:160])
    lines.append(f"{'OK ' if hit else 'NO '} {i:02d} {name}: exit {rc}; {first[:220]}")
lines.append(f"presi {caught} su {len(SABOTAGES)}; netlist vera {'pulita' if ok_clean else 'NON pulita'}")
(OUT / "verdetti.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if ok_clean and caught == len(SABOTAGES) else 1)
