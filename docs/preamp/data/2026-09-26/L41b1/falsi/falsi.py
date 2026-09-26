#!/usr/bin/env python3
"""L41b1: the two checkers extended in this lot, made to fail one sabotage at a time.

Solo stdlib. /usr/bin/python3 falsi.py <preamp_audio.net> <psu.net>

  2j  scripts/check_psu_harness.py <audio> <psu>      (check_timer: switch,
      micro, J3 sources)
  2e  scripts/check_relay_safe_state.py --timer <psu> (ADR-022 condition 1)

Each sabotaged psu.net is written next to this file, the checker it targets
runs on it, and the copy is removed. Every sabotage must FAIL its checker and
the good netlist must PASS both; exit 1 otherwise. esito.txt keeps the table.

The sabotages move pins inside the NETS section only (the helpers are L41a's,
copied: docs/preamp/data/2026-09-26/L41a/falsi/falsi.py), or change one value
in the components section.
"""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(QUI, "..", "..", "..", "..", "..", "..", "scripts")
HARNESS = os.path.join(SCRIPTS, "check_psu_harness.py")
SAFE = os.path.join(SCRIPTS, "check_relay_safe_state.py")


def node(ref, pin):
    return '(ref "%s")\n        (pin "%s")' % (ref, pin)


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


def revalue(text, old, new):
    a, b = '(value "%s")' % old, '(value "%s")' % new
    assert text.count(a) == 1, old
    return text.replace(a, b)


def main(audio, psu):
    ta, tp = open(audio).read(), open(psu).read()
    casi = [
        # (name, checker, psu text, expected: 0 pass / 1 fail)
        ("buono_2j", "2j", tp, 0),
        ("buono_2e", "2e", tp, 0),
        # ---- 2j: the standby switch
        # the switch's drain taken off VRELAY: J1 pin 4 fed by nothing
        ("2j_Q505_drain_staccato", "2j", move(tp, "Q505", "3", "VRELAY_REG"), 1),
        # the switch's source from V5 instead of U503's output
        ("2j_Q505_source_da_V5", "2j", move(tp, "Q505", "2", "V5"), 1),
        # ---- 2j: the placeholder, the micro
        ("2j_J509_di_nuovo", "2j", revalue(tp, "UPDI", "TIMER_IO"), 1),
        ("2j_MUTE_REQ_non_dal_micro", "2j", move(tp, "U509", "11", "UPDI"), 1),
        ("2j_VRELAY_EN_non_dal_micro", "2j", move(tp, "U509", "8", "UPDI"), 1),
        # ---- 2j: J3's sources and returns
        ("2j_anodo_S_senza_PNP", "2j", move(tp, "Q511", "3", "V5"), 1),
        ("2j_catodo_P_a_RLY_RET", "2j", move(tp, "R567", "2", "RLY_RET"), 1),
        # ---- 2e --timer (ADR-022 condition 1)
        # T2: MUTE_REQ's pull-down gone (both ends on RLY_RET)
        ("2e_T2_senza_pulldown_MUTE_REQ", "2e", move(tp, "R525", "1", "RLY_RET"), 1),
        # T2: MAINS_REQ's pull-down gone
        ("2e_T2_senza_pulldown_MAINS_REQ", "2e", move(tp, "R528", "1", "RLY_RET"), 1),
        # T1: the mains relay's gate without its resistor to the source
        ("2e_T1_Q503_senza_R_gate", "2e", move(tp, "R521", "2", "MAINS_G"), 1),
        # T3: no capacitor on PERMIT_T: no RC, no delay D
        ("2e_T3_senza_C_su_PERMIT_T", "2e", move(tp, "C528", "1", "RLY_RET"), 1),
        # T3b: PERMIT_REQ wired straight onto PERMIT_G, around the RC
        ("2e_T3b_PERMIT_REQ_sul_gate", "2e", move(tp, "R533", "2", "PERMIT_G"), 1),
        # T4: the MUTE_G <= PERMIT_G clamp gone
        ("2e_T4_senza_D522", "2e", move(tp, "D522", "1", "RLY_RET"), 1),
        # T5: PERMIT_T no longer charged from MUTE_REQ
        ("2e_T5_PERMIT_T_non_da_MUTE_REQ", "2e", move(tp, "D520", "2", "RLY_RET"), 1),
        # T5: VR_T charged from VRELAY_EN only, not from PERMIT_T
        ("2e_T5_VR_T_non_da_PERMIT_T", "2e", move(tp, "D523", "2", "VE_A"), 1),
    ]
    esito, righe = 0, []
    for nome, chk, p, atteso in casi:
        fp = os.path.join(QUI, nome + "_psu.net")
        open(fp, "w").write(p)
        if chk == "2j":
            cmd = ["/usr/bin/python3", HARNESS, audio, fp]
            tags = ("FAIL", "OK")
        else:
            cmd = ["/usr/bin/python3", SAFE, "--timer", fp]
            tags = ("  timer", "OK", "FALLITO")
        r = subprocess.run(cmd, capture_output=True, text=True)
        motivo = [l.strip() for l in r.stdout.splitlines() if l.startswith(tags)]
        ok = (r.returncode == 0) == (atteso == 0)
        riga = "%-34s %s rc=%d atteso=%s %s  %s" % (
            nome, chk, r.returncode, "PASS" if atteso == 0 else "FAIL",
            "ok" if ok else "SBAGLIATO", " | ".join(motivo)[:220])
        print(riga)
        righe.append(riga)
        if not ok:
            esito = 1
        os.remove(fp)
    righe.append("")
    righe.append("esito: %s (%d casi)" % ("tutti come attesi" if esito == 0 else "QUALCOSA NON TORNA",
                                           len(casi)))
    open(os.path.join(QUI, "esito.txt"), "w").write("\n".join(righe) + "\n")
    return esito


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
