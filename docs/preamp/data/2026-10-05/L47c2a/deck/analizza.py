#!/usr/bin/env python3
"""L42b: reads the wrdata files of tb_psu_rete / tb_psu_guasti and prints P9's figures.

Solo stdlib. /usr/bin/python3 analizza.py <dir> [t_evento]  -> analisi.csv in <dir>

COPIED from L41a's analizza.py (docs/preamp/data/2026-09-26/L41a/deck/), which
stays as it was. Two declared changes, both from today's circuit:
  - one probe more, vrelay_reg (L42b's genera_tb_psu.py, SAVE_RETE);
  - vr_hold / vr80_hold are read on VRELAY_REG, the regulator's output, which
    is what L41a's VRELAY was before L41b1 put Q505 between it and J1: so the
    column means what L41a's meant. The same at J1 (vrelay, which Q505 cuts by
    design D2 after PERMIT_CMD, ADR-049) is in two new columns, vrj1_hold_ms
    and vrj1_80_hold_ms.
Before any data file is read, its deck's log is (limitations #35): any line
with Error, singular, no such, too many args, Transient op, Timestep too
small or aborted refuses the directory.

L41a's header follows.

Columns: wrdata writes (time, value) per vector, in the order of SAVE in
genera_tb_psu.py - kept in VEC below; a mismatch in count stops the script.

Per file:
  regime_*   : mean VPLUS / VMINUS / VRELAY / V5 over the last 0.2 s, raw valleys
  others     : from the event t_ev (default 2.0 s):
     t_off   - the jack relays' coil current (VRELAY - MUTE_CMD) / (1315/3)
               below 10 % of its value just before the event: MUTE_CMD released
     t_md    - the mains detector's MD above VREF
     t_p135, t_p106 / t_m135, t_m106 - the rails crossing 13.5 and 10.6 V
     trip_after_135 - t_off minus the first 13.5 V crossing (P9: <= 1 ms)
     vr_hold - how long VRELAY stays >= 11.4 V (12 V -5 %) after t_off (P9: >= 25 ms)
     vr80_hold - the same >= 9.6 V (80 %: the coils still up; the U503 fault)
     v_rails_at_off - the rails when MUTE_CMD is released
"""
import glob
import os
import sys

VEC = ["vplus", "vminus", "vrelay", "v5", "raw_p", "raw_m", "raw_v", "rect_v", "mute_g",
       "permit_g", "md", "sup_p", "sup_m", "vref", "mute_cmd", "permit_cmd", "mains_coil",
       "vrelay_reg"]
R_MUTE = 1315 / 3.0
GUARDIE = ("error", "singular", "no such", "too many args", "transient op",
           "timestep too small", "aborted")


def guardia(d):
    logs = sorted(glob.glob(os.path.join(d, "*.log")))
    if not logs:
        raise SystemExit("%s: nessun log - il log si legge prima dei dati (#35)" % d)
    for lg in logs:
        for riga in open(lg, errors="replace"):
            low = riga.lower()
            if any(g in low for g in GUARDIE):
                raise SystemExit("%s: %s" % (lg, riga.strip()))


def leggi(path):
    t, cols = [], {v: [] for v in VEC}
    for riga in open(path):
        x = riga.split()
        if not x:
            continue
        if len(x) != 2 * len(VEC):
            raise SystemExit("%s: %d columns, expected %d" % (path, len(x), 2 * len(VEC)))
        t.append(float(x[0]))
        for i, v in enumerate(VEC):
            cols[v].append(float(x[2 * i + 1]))
    return t, cols


def primo(t, y, cond, t0):
    for ti, yi in zip(t, y):
        if ti >= t0 and cond(yi):
            return ti
    return None


def media(t, y, a, b):
    s = [yi for ti, yi in zip(t, y) if a <= ti <= b]
    return sum(s) / len(s)


def ms(x, ref):
    return "" if x is None or ref is None else "%.3f" % ((x - ref) * 1e3)


def tenuta(t, y, soglia, t0):
    x = primo(t, y, lambda v: v < soglia, t0)
    return ms(x, t0) if x else ">%s" % ms(t[-1], t0)


def main(d, t_ev):
    guardia(d)
    righe = ["file,vplus,vminus,vrelay,v5,raw_p_min,raw_m_min_abs,raw_v_min,"
             "t_off_ms,t_md_ms,t_p135_ms,t_p106_ms,t_m135_ms,t_m106_ms,trip_after_135_ms,"
             "vr_hold_ms,vr80_hold_ms,vplus_at_off,vminus_at_off,vrelay_reg,vrj1_hold_ms,vrj1_80_hold_ms"]
    for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
        nome = os.path.basename(f)[:-4]
        t, c = leggi(f)
        if nome.startswith("regime"):
            te = t[-1]
            a = te - 0.2
            w = lambda v: [yi for ti, yi in zip(t, c[v]) if ti >= a]
            righe.append("%s,%.4f,%.4f,%.4f,%.4f,%.3f,%.3f,%.3f,,,,,,,,,,,,%.4f,," % (
                nome, media(t, c["vplus"], a, te), media(t, c["vminus"], a, te),
                media(t, c["vrelay"], a, te), media(t, c["v5"], a, te), min(w("raw_p")),
                min(-x for x in w("raw_m")), min(w("raw_v")), media(t, c["vrelay_reg"], a, te)))
            continue
        i_coil = [(vr - mc) / R_MUTE for vr, mc in zip(c["vrelay"], c["mute_cmd"])]
        i0 = media(t, i_coil, t_ev - 0.02, t_ev)
        t_off = primo(t, i_coil, lambda y: y < 0.1 * i0, t_ev)
        t_md = primo(t, [m - r for m, r in zip(c["md"], c["vref"])], lambda y: y > 0, t_ev)
        tp135 = primo(t, c["vplus"], lambda y: y < 13.5, t_ev)
        tp106 = primo(t, c["vplus"], lambda y: y < 10.6, t_ev)
        tm135 = primo(t, c["vminus"], lambda y: y > -13.5, t_ev)
        tm106 = primo(t, c["vminus"], lambda y: y > -10.6, t_ev)
        first135 = min([x for x in (tp135, tm135) if x is not None], default=None)
        t0 = t_off if t_off else t_ev
        idx = min(range(len(t)), key=lambda i: abs(t[i] - t_off)) if t_off else None
        righe.append("%s,,,,,,,,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,,%s,%s" % (
            nome, ms(t_off, t_ev), ms(t_md, t_ev), ms(tp135, t_ev), ms(tp106, t_ev),
            ms(tm135, t_ev), ms(tm106, t_ev), ms(t_off, first135),
            tenuta(t, c["vrelay_reg"], 11.4, t0), tenuta(t, c["vrelay_reg"], 9.6, t0),
            "%.3f" % c["vplus"][idx] if idx is not None else "",
            "%.3f" % c["vminus"][idx] if idx is not None else "",
            tenuta(t, c["vrelay"], 11.4, t0), tenuta(t, c["vrelay"], 9.6, t0)))
    out = os.path.join(d, "analisi.csv")
    open(out, "w").write("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 2.0)
