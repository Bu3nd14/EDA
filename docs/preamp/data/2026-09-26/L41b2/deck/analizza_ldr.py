#!/usr/bin/env python3
"""L41b2: the LDR drive against the v4 table with the 12 mA top (ADR-050), from tb_psu_ldr*.log.

COPIED from L41b1's analizza_ldr.py, which stays as it was. L41b2 changes the
calibration's abscissa: e_k = off + r_ohm * I_READ_k, not I_WANT_k - the ohmic
drop happens at the current that flows. It is what timer_core.c does
(timer_cal_fit); L41b1's version is the firmware's timer_cal_fit_x with
x = the wanted current, and test_legge proves it returns L41b1's cal.json.
The top is read from the deck (the d0 / d1 target), so 12 mA or 20 mA alike.

Solo stdlib. /usr/bin/python3 analizza_ldr.py <log> [--scrivi-cal <cal.json>]

Reads every 'PUNTO <mode> <string> <name> <T> <target> <code>' block and the
string currents printed after it, and writes <log>.csv plus a verdict.

Modes: nocomp (the firmware's law at 25 C whatever the chassis), comp (the law
at the chassis temperature - the micro's sensor, ADR-049), cal (comp plus the
two-point calibration below), dac_reset (the DAC shut down: the floor).

THE CALIBRATION (ADR-049; the firmware's, L41b2): at 20 mA and 2 mA the micro
reads the string current on its 10 ohm sense (200 and 20 mV), and fits the
extra base voltage the law missed as e(I) = off + r_ohm * I - the op-amp's
offset, the pair's mismatch and the ohmic drops of the transistors at the top.
Here the reads are the simulated currents, exact: the ADC's quantisation is
the firmware's to budget (20 mV on a 1.1 V 10-bit reference is ~19 LSB).

THE CRITERIA, written before the runs (L41b1):
  - cal: every table point from 0.19 uA up within +-1 dB, at every chassis
    temperature; the 10 nA idle within 5-20 nA (+-6 dB: below the knee it
    only has to stay dark and never 0);
  - dac_reset: every string above 0 and below the 190 nA knee;
  - no mode may leave a string with no current at all (never 0).
"""
import csv
import json
import math
import re
import sys

K_B, Q_E = 1.380649e-23, 1.602176634e-19


def vt(tc):
    return K_B * (tc + 273.15) / Q_E


def leggi(path):
    """The points; each marked `ripiego` if ngspice's DC solve fell back to
    the transient op before it (the message precedes the point's echo)."""
    rows, cur, ripiego = [], None, False
    for line in open(path, errors="replace"):
        if "Transient op started" in line or "source stepping failed" in line:
            ripiego = True
        m = re.match(r"PUNTO (\S+) (\S+) (\S+) (\d+) (\S+) (-?\d+)", line)
        if m:
            cur = {"modo": m.group(1), "s": m.group(2), "nome": m.group(3),
                   "t": int(m.group(4)), "target": float(m.group(5)), "code": int(m.group(6)),
                   "ripiego": ripiego}
            ripiego = False
            rows.append(cur)
            continue
        m = re.match(r"(i\(vls\)|i\(vlp\)|v\(\w+\)) = (\S+)", line)
        if m and cur is not None:
            cur[m.group(1)] = float(m.group(2))
    return rows


def main(argv):
    path = argv[1]
    rows = leggi(path)
    out = []
    for r in rows:
        i_s, i_p = r.get("i(vls)"), r.get("i(vlp)")
        i = i_s if r["s"] == "S" else i_p
        r["i_meas"] = i
        r["err_db"] = 20 * math.log10(i / r["target"]) if i and i > 0 else float("nan")
        out.append(r)
    keys = ["modo", "s", "nome", "t", "target", "code", "i_meas", "err_db",
            "i(vls)", "i(vlp)", "v(mir_e2_s)", "v(ldr_s_a)", "v(mir_e2_p)", "v(ldr_p_a)"]
    with open(path + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow(r)
    # the table, per mode
    for modo in ("nocomp", "comp", "cal"):
        sel = [r for r in out if r["modo"] == modo]
        if not sel:
            continue
        print("== %s: errore in dB contro la tabella v4" % modo)
        nomi = []
        for r in sel:
            if (r["s"], r["nome"]) not in nomi:
                nomi.append((r["s"], r["nome"]))
        temps = sorted({r["t"] for r in sel})
        print("   %-14s %s" % ("punto", "  ".join("%6d C" % t for t in temps)))
        for s, n in nomi:
            vals = [next(r["err_db"] for r in sel if r["s"] == s and r["nome"] == n and r["t"] == t)
                    for t in temps]
            print("   %-14s %s" % (s + " " + n, "  ".join("%+8.2f" % v for v in vals)))
    fails = []
    # the guard: a point solved by the transient-op fallback is not a DC
    # operating point (C_X uncharged, L41b1) - refuse the whole run
    for r in out:
        if r["ripiego"]:
            fails.append("%s %s %s %d C: risolto dal ripiego in transitorio, non e' un "
                         "punto di lavoro" % (r["modo"], r["s"], r["nome"], r["t"]))
    cal = [r for r in out if r["modo"] == "cal"]
    for r in cal:
        if r["nome"] == "riposo":
            if not 5e-9 <= r["i_meas"] <= 20e-9:
                fails.append("cal %s %s %d C: %.3g A fuori da 5-20 nA" % (r["s"], r["nome"], r["t"], r["i_meas"]))
        elif r["target"] >= 0.19e-6 and not abs(r["err_db"]) <= 1.0:
            fails.append("cal %s %s %d C: %+.2f dB fuori da +-1 dB" % (r["s"], r["nome"], r["t"], r["err_db"]))
    print("== dac_reset (DAC in shutdown): le due stringhe")
    for r in out:
        if r["modo"] != "dac_reset":
            continue
        print("   %d C: serie %.3g A, derivazione %.3g A" % (r["t"], r["i(vls)"], r["i(vlp)"]))
        for k in ("i(vls)", "i(vlp)"):
            if not 0 < r[k] < 190e-9:
                fails.append("dac_reset %d C %s = %.3g A (voluto > 0 e < 190 nA)" % (r["t"], k, r[k]))
    for r in out:
        if r["modo"] in ("nocomp", "comp", "cal") and not (r["i(vls)"] > 0 and r["i(vlp)"] > 0):
            fails.append("%s %s %s %d C: una stringa a 0" % (r["modo"], r["s"], r["nome"], r["t"]))
    if len(argv) > 3 and argv[2] == "--scrivi-cal":
        calj = {}
        for s in ("S", "P"):
            for t in sorted({r["t"] for r in out}):
                pts = {r["nome"]: r for r in out if r["modo"] == "comp" and r["s"] == s and r["t"] == t}
                top = pts["d0" if s == "S" else "d1"]
                mid = pts["cal_2mA"]
                e1 = vt(t) * math.log(top["target"] / top["i_meas"])
                e2 = vt(t) * math.log(mid["target"] / mid["i_meas"])
                # L41b2: the abscissa is the current read (timer_cal_fit)
                r_ohm = (e1 - e2) / (top["i_meas"] - mid["i_meas"])
                off = e2 - r_ohm * mid["i_meas"]
                calj["%s_%d" % (s, t)] = {"off": off, "r_ohm": r_ohm}
                print("   cal %s %d C: off %+.2f mV, r_ohm %.3f ohm" % (s, t, off * 1e3, r_ohm))
        json.dump(calj, open(argv[3], "w"), indent=1)
    print("VERDETTO%s: %s" % ("" if cal else " (senza calibrazione: solo le guardie)",
                               "PASSA" if not fails else "FALLISCE"))
    for f in fails:
        print("   " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
