#!/usr/bin/env python3
"""L54b1: the two checkers rewritten for the comparator timer (ADR-102), made to fail one sabotage
at a time.

Solo stdlib. /usr/bin/python3 -I falsi.py <preamp_audio.net> <psu.net>

  2j  scripts/check_psu_harness.py <audio> <psu>      (check_timer: the switch, the requests from
      comparators, no micro)
  2e  scripts/check_relay_safe_state.py --timer <psu> (T0-T6: ADR-022 condition 1, D, D2, the latch)

Each sabotaged psu.net is written next to this file, the checker it targets runs on it, and the
copy is removed. Every sabotage must FAIL its checker and the good netlist must PASS both; exit 1
otherwise. verdetti.txt keeps the table.

The sabotages move pins inside the NETS section only (move(), L41b1's helper, copied:
docs/preamp/data/2026-09-26/L41b1/falsi/falsi.py), or relabel one part's library and symbol
(relib(): the part a wrong BOM line or a wrong symbol would bring).
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
    assert text.count(head) == 1, net_to
    i = text.index(head)
    j = text.index("(node", i)
    ins = '(node\n        %s\n        (pintype "PASSIVE"))\n      ' % n
    return text[:j] + ins + text[j:]


def relib(text, ref, lib, part):
    """The libsource of component `ref` becomes lib / part (pins untouched)."""
    i = text.index('(comp\n      (ref "%s")' % ref)
    j = text.index("(libsource", i)
    k = text.index(")\n        (part", j)
    m = text.index("))", k)
    return text[:j] + '(libsource\n        (lib "%s")\n        (part "%s"))' % (lib, part) + text[m + 2:]


def main(audio, psu):
    tp = open(psu).read()
    casi = [
        # (name, checker, psu text, expected: 0 pass / 1 fail)
        ("buono_2j", "2j", tp, 0),
        ("buono_2e", "2e", tp, 0),
        # ---- 2j: the standby switch (L41b1's two, kept)
        ("2j_Q505_drain_staccato", "2j", move(tp, "Q505", "3", "VRELAY_REG"), 1),
        ("2j_Q505_source_da_V5", "2j", move(tp, "Q505", "2", "V5"), 1),
        # ---- 2j: the requests from comparators, no micro
        # U514 (mg, sw, mq, mp) relabelled as the ATtiny of before
        ("2j_micro_di_nuovo", "2j", relib(tp, "U514", "MCU_Microchip_ATtiny", "ATtiny3216-S"), 1),
        # mq's output taken off MUTE_REQ: only pull-up, pull-down and R513 / R532 left
        ("2j_MUTE_REQ_senza_comparatore", "2j", move(tp, "U514", "14", "AT_PG"), 1),
        # the front channel's output taken off VRELAY_EN
        ("2j_VRELAY_EN_senza_comparatore", "2j", move(tp, "U515", "2", "AT_PG"), 1),
        # ---- 2e --timer
        # T0: the micro back
        ("2e_T0_micro_di_nuovo", "2e", relib(tp, "U514", "MCU_Microchip_ATtiny", "ATtiny3216-S"), 1),
        # T0: a comparator symbol the checker does not read (an LM393 in place of U515)
        ("2e_T0_comparatore_sconosciuto", "2e", relib(tp, "U515", "Comparator", "LM393"), 1),
        # T1: the mains relay's gate without its resistor to the source
        ("2e_T1_Q503_senza_R_gate", "2e", move(tp, "R521", "2", "MAINS_G"), 1),
        # T2: MUTE_REQ's pull-down gone (both ends on RLY_RET)
        ("2e_T2_senza_pulldown_MUTE_REQ", "2e", move(tp, "R525", "1", "RLY_RET"), 1),
        # T2: VRELAY_EN's pull-down gone
        ("2e_T2_senza_pulldown_VRELAY_EN", "2e", move(tp, "R527", "1", "RLY_RET"), 1),
        # T2: a quad op-amp (push-pull) in place of U514, same pinout
        ("2e_T2_operazionale_al_posto_U514", "2e", relib(tp, "U514", "Amplifier_Operational", "LM324"), 1),
        # T2: MAINS_REQ's pull-up from VRELAY_REG instead of V5: up with the timer dead
        ("2e_T2_pullup_MAINS_REQ_da_VRELAY_REG", "2e", move(tp, "R566", "1", "VRELAY_REG"), 1),
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
        # T6: the NPN's collector off the PNP's base: no thyristor
        ("2e_T6_ritenuta_spezzata", "2e", move(tp, "Q507", "3", "RLY_RET"), 1),
        # T6: the latch's anode on V5 instead of VRELAY_EN: tripped, it would hold nothing
        ("2e_T6_anodo_su_V5", "2e", move(tp, "Q508", "2", "V5"), 1),
        # T6: the NPN's 1 nF base-emitter gone (shorted out on RLY_RET)
        ("2e_T6_senza_C_base_NPN", "2e", move(tp, "C543", "1", "RLY_RET"), 1),
        # T6: the PNP's 100k base-emitter gone
        ("2e_T6_senza_R_base_PNP", "2e", move(tp, "R571", "2", "VRELAY_EN"), 1),
        # T6: the latch fed from MUTE_REQ (a request, a comparator output too) instead of AT_F
        ("2e_T6_innesco_da_MUTE_REQ", "2e", move(tp, "R569", "1", "MUTE_REQ"), 1),
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
        riga = "%-38s %s rc=%d atteso=%s %s  %s" % (
            nome, chk, r.returncode, "PASS" if atteso == 0 else "FAIL",
            "ok" if ok else "SBAGLIATO", " | ".join(motivo)[:260])
        print(riga)
        righe.append(riga)
        if not ok:
            esito = 1
        os.remove(fp)
    righe.append("")
    righe.append("esito: %s (%d casi)" % ("tutti come attesi" if esito == 0 else "QUALCOSA NON TORNA",
                                           len(casi)))
    open(os.path.join(QUI, "verdetti.txt"), "w").write("\n".join(righe) + "\n")
    return esito


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
