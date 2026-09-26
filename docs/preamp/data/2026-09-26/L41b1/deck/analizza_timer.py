#!/usr/bin/env python3
"""L41b1: the timer deck's verdicts, from tb_psu_timer_<angolo>.log.

Solo stdlib. /usr/bin/python3 analizza_timer.py <log> [<log> ...]

Reads each 'CASO <name>' block and its `meas` lines; writes <log>.csv and the
verdicts. THE CRITERIA, written before the runs (L41b1):
  - micro stopped (reset / driven low), mains loss or U503 failing with the
    micro reset: D = t_permit - t_mute >= 10 ms (ADR-045), and the audio
    board's VRELAY still >= 9.6 V (80 %) when PERMIT_CMD releases;
  - the micro stuck high through a mains loss: MUTE_CMD released by the
    detector, PERMIT_CMD not before 10 ms after it (or not at all);
  - a firmware that drops PERMIT_REQ alone: neither command releases;
  - the release, MUTE_REQ raised alone: PERMIT_CMD energised no later than
    MUTE_CMD (J4 contract);
  - the counterfactual without C528 must FAIL the D criterion;
  - standby: the audio board's VRELAY below 0.5 V (NC-037).
The guards: 0 lines with 'Error', 'singular', 'no such', 'non-increasing',
'Transient op' in the log.
"""
import csv
import re
import sys

GUARDIE = ("Error", "singular", "no such", "non-increasing", "Transient op", "Timestep too small")


def leggi(path):
    casi, cur, guardie = {}, None, []
    for line in open(path, errors="replace"):
        # a `meas` that finds no event says "Error: measure ... out of
        # interval": that is a measure, read below, not a simulator error
        misura = "measure" in line or "meas tran" in line
        for g in GUARDIE:
            if g.lower() in line.lower() and not misura:
                guardie.append(line.strip())
        m = re.match(r"CASO (\S+)", line)
        if m:
            cur = casi.setdefault(m.group(1), {})
            continue
        m = re.match(r"^(\w+)\s*=\s*([-+0-9.eE]+)", line)
        if m and cur is not None:
            cur[m.group(1)] = float(m.group(2))
        m = re.match(r"^\s*(\w+)\s*.*failed", line)
        if m and cur is not None:
            cur.setdefault("_failed", []).append(m.group(1))
    return casi, guardie


def ms(x):
    return "%.2f ms" % (x * 1e3)


def main(paths):
    esito = 0
    for path in paths:
        casi, guardie = leggi(path)
        print("== %s" % path)
        fails, righe = [], []
        for g in guardie:
            fails.append("guardia: %s" % g)
        for nome in ("micro_reset", "micro_a_zero", "perdita_rete_micro_reset",
                     "guasto_U503_micro_reset", "controfattuale_senza_C528"):
            c = casi.get(nome)
            if c is None:
                fails.append("%s: caso mancante" % nome)
                continue
            if "t_mute" not in c or "t_permit" not in c:
                fails.append("%s: una misura manca (%s)" % (nome, c.get("_failed")))
                continue
            d = c["t_permit"] - c["t_mute"]
            vr = c.get("t_vr80")
            d2 = (vr - c["t_permit"]) if vr else None
            vr_ok = vr is None or vr > c["t_permit"]
            righe.append({"caso": nome, "t_mute_ms": (c["t_mute"] - 2.0) * 1e3,
                          "D_ms": d * 1e3, "D2_ms": d2 * 1e3 if d2 else "",
                          "vrelay_min": c.get("vrelay_min", "")})
            print("   %-32s MUTE_CMD a +%s, D = %s, VRELAY < 9,6 V %s dopo PERMIT"
                  % (nome, ms(c["t_mute"] - 2.0), ms(d), ms(d2) if d2 else "mai"))
            if nome == "controfattuale_senza_C528":
                if d >= 10e-3:
                    fails.append("controfattuale: D = %s, doveva fallire" % ms(d))
                else:
                    print("      il controfattuale fallisce come deve (D < 10 ms)")
            else:
                if d < 10e-3:
                    fails.append("%s: D = %s < 10 ms" % (nome, ms(d)))
                if not vr_ok:
                    fails.append("%s: VRELAY sotto 9,6 V prima di PERMIT_CMD" % nome)
        c = casi.get("perdita_rete_micro_fermo_alto", {})
        if "t_mute" not in c:
            fails.append("perdita_rete_micro_fermo_alto: MUTE_CMD non rilasciato")
        else:
            tp = c.get("t_permit")
            print("   %-32s MUTE_CMD a +%s, PERMIT_CMD %s" % (
                "perdita_rete_micro_fermo_alto", ms(c["t_mute"] - 2.0),
                ("a +%s (D = %s)" % (ms(tp - 2.0), ms(tp - c["t_mute"]))) if tp else "mai nei 400 ms"))
            if tp and tp - c["t_mute"] < 10e-3:
                fails.append("perdita_rete_micro_fermo_alto: PERMIT prima di D")
            righe.append({"caso": "perdita_rete_micro_fermo_alto",
                          "t_mute_ms": (c["t_mute"] - 2.0) * 1e3,
                          "D_ms": (tp - c["t_mute"]) * 1e3 if tp else "",
                          "vrelay_min": c.get("vrelay_min", "")})
        c = casi.get("solo_permit_req_giu", {})
        pm, mm = c.get("permit_max"), c.get("mute_max")
        print("   %-32s drain di PERMIT_CMD max %.3f V, di MUTE_CMD max %.3f V (6 V = rilascio)"
              % ("solo_permit_req_giu", pm or -1, mm or -1))
        if pm is None or pm >= 6 or mm is None or mm >= 6:
            fails.append("solo_permit_req_giu: un comando si e' rilasciato")
        c = casi.get("rilascio_solo_mute_req", {})
        tm, tp = c.get("t_mute_on"), c.get("t_permit_on")
        if tm is None or tp is None:
            fails.append("rilascio_solo_mute_req: una misura manca (%s)" % c.get("_failed"))
        else:
            print("   %-32s PERMIT_CMD eccitato a +%s, MUTE_CMD a +%s (anticipo %s)"
                  % ("rilascio_solo_mute_req", ms(tp - 2.0), ms(tm - 2.0), ms(tm - tp)))
            if tp > tm:
                fails.append("rilascio: PERMIT_CMD dopo MUTE_CMD")
        c = casi.get("standby", {})
        vj = c.get("vrelay_j1_max")
        print("   %-32s VRELAY a J1 max %.4f V, VRELAY_REG %.3f V, potenza da T2 %.1f mW, da T1 %.2f mW"
              % ("standby", vj if vj is not None else -1, c.get("vreg_avg", -1),
                 c.get("p_t2_avg", 0) * 1e3, c.get("p_t1_avg", 0) * 1e3))
        if vj is None or vj >= 0.5:
            fails.append("standby: VRELAY alla scheda audio non tolta")
        righe.append({"caso": "standby", "vrelay_min": vj,
                      "D2_ms": "", "D_ms": "", "t_mute_ms": "",
                      "p_t2_mW": c.get("p_t2_avg", 0) * 1e3})
        with open(path + ".csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["caso", "t_mute_ms", "D_ms", "D2_ms",
                                              "vrelay_min", "p_t2_mW"], extrasaction="ignore")
            w.writeheader()
            for r in righe:
                w.writerow(r)
        print("VERDETTO %s: %s" % (path, "PASSA" if not fails else "FALLISCE"))
        for f in fails:
            print("   " + f)
        if fails:
            esito = 1
    return esito


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
