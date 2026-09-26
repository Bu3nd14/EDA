#!/usr/bin/env python3
"""L41a: check_psu_harness.py made to fail, one sabotage at a time.

Solo stdlib. /usr/bin/python3 falsi.py <preamp_audio.net> <psu.net>
Writes each sabotaged copy in this folder and runs the checker on it. Every
sabotage must FAIL, and the good pair must PASS; exit 1 otherwise.

The sabotages rename pins inside the NETS section only (a node is
'(ref "X")\\n        (pin "N")' there; in the components section the ref is
followed by the value), so the components stay as they are.
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(QUI, "..", "..", "..", "..", "..", "..", "scripts", "check_psu_harness.py")


def node(ref, pin):
    return '(ref "%s")\n        (pin "%s")' % (ref, pin)


def swap(text, ref, a, b):
    """Swap two pins of one part in the nets section."""
    na, nb = node(ref, a), node(ref, b)
    assert text.count(na) == 1 and text.count(nb) == 1, (ref, a, b)
    return text.replace(na, "@@A@@").replace(nb, na).replace("@@A@@", nb)


def move(text, ref, pin, net_to):
    """Detach ref/pin from its net and attach it to net `net_to`."""
    n = node(ref, pin)
    blk = re.escape("      (node\n        " + n + "\n        (pintype \"") + "[^\"]*" + re.escape("\"))")
    m = re.search(blk, text)
    assert m, (ref, pin)
    text = text[:m.start()] + text[m.end():]
    head = '(name "%s")' % net_to
    i = text.index(head)
    j = text.index("(node", i)
    ins = '(node\n        %s\n        (pintype "PASSIVE"))\n      ' % n
    return text[:j] + ins + text[j:]


def main(audio, psu):
    ta, tp = open(audio).read(), open(psu).read()
    casi = [
        ("buono", ta, tp, 0),
        # J1 + and - swapped on the supply: -15 V on the audio board's VPLUS
        ("psu_J1_1_3_scambiati", ta, swap(tp, "J1", "1", "3"), 1),
        # the same on the audio side
        ("audio_J1_1_3_scambiati", swap(ta, "J1", "1", "3"), tp, 1),
        # MUTE_CMD and PERMIT_CMD swapped on the audio's J4 (ADR-045 undone)
        ("audio_J4_1_2_scambiati", swap(ta, "J4", "1", "2"), tp, 1),
        # the series and shunt LED strings swapped on the audio's J3
        ("audio_J3_1_3_scambiati", swap(ta, "J3", "1", "3"), tp, 1),
        # the MUTE_CMD sink returns to GND instead of RLY_RET
        ("psu_Q501_source_a_GND", ta, move(tp, "Q501", "2", "GND"), 1),
        # VPLUS from the negative regulator's pins: U501 OUT moved away
        ("psu_U501_OUT_staccato", ta,
         move(move(tp, "U501", "1", "RAW_P"), "U501", "20", "RAW_P"), 1),
        # MUTE_CMD's MOSFET moved onto PERMIT_CMD: MUTE_CMD has no sink left
        ("psu_Q501_drain_su_PERMIT", ta, move(move(tp, "Q502", "3", "RLY_RET"), "Q501", "3", "PERMIT_CMD"), 1),
        # the TPS7A3301's pad back on IN, L41a's first draft
        ("psu_U502_pad_su_IN", ta, move(tp, "U502", "21", "RAW_M"), 1),
    ]
    esito = 0
    for nome, a, p, atteso in casi:
        fa, fp = os.path.join(QUI, nome + "_audio.net"), os.path.join(QUI, nome + "_psu.net")
        open(fa, "w").write(a)
        open(fp, "w").write(p)
        r = subprocess.run(["/usr/bin/python3", CHECK, fa, fp], capture_output=True, text=True)
        motivo = [l for l in r.stdout.splitlines() if l.startswith(("FAIL", "OK"))]
        ok = (r.returncode == 0) == (atteso == 0)
        print("%-26s rc=%d atteso=%s %s  %s" % (nome, r.returncode, "PASS" if atteso == 0 else "FAIL",
                                               "ok" if ok else "SBAGLIATO", " | ".join(motivo)[:200]))
        if not ok:
            esito = 1
        os.remove(fa)
        os.remove(fp)
    return esito


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
