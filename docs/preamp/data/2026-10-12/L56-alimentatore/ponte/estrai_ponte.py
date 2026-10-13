#!/usr/bin/env python3
"""L41c: the bridge from the supply board to the audio board (NC-036).

L47c2b2: COPIED from L41c's (data/2026-09-26/L41c/ponte/), which stays as it
was. Two changes, both from ADR-062 (the mute with the relays alone):
  - the LED strings' currents (is, ip) are gone: the strings are gone from the
    circuit, and the audio generator does not read them since L47c2b1;
  - spegnimento_l's own window (T0 = TE + 5.4 s, t_ins = TE + 6.4 s) was the
    fade's: MUTE_CMD was released ~TE + 6.53 s. With the cut it is released
    ~21 ms after the front's pin, and the case ends at TE + 1.1 s (the user's
    choice): the old window would start after the data end. spegnimento_l
    takes the faults' window, t_ins 10 ms before the front opens.
L41c's header follows (the LED strings and the fade's window are L41c's).

Solo stdlib.
  /usr/bin/python3 estrai_ponte.py <seq_dir> <out_dir> <caso> [<caso> ...]

One board does not fit in one deck: the chain runs in TWO STEPS and one way.
The supply board with its timer and the firmware core runs first, to its
fixed point (psu/corri_seq.sh); this script reads that pass and writes, per
case, <out_dir>/<caso>.json with what the audio board's bench of L30
(genera_tb_v2_casopeggiore.py --matrice l41c) takes instead of the hand-drawn
supply of L30. Nothing flows back: the supply sees the audio board as the
loads of genera_tb_psu.py (the rails 56.6 ohm each, the coils, the LEDs).

WHAT IS BRIDGED, per case:
  - the two rails, v(vplus) and v(vminus), as PWLs for @vpp / @vmm;
  - the two LED strings' currents, v(ldr_s_k) / 10 ohm and v(ldr_p_k) / 10
    ohm (the sense resistors, psu.py R_SENSE), as PWLs that REPLACE L30's
    BILS / BILP (profile x VPWL): they carry ADR-050's 12 mA top by
    themselves;
  - the jack relays' contact (K2-K4, MUTE_CMD) and the gain relays' contact
    (K1/K5, fed through K6 / VHOLD from PERMIT_CMD), as instants, at the
    WORST corner of the G6K (en-g6k.pdf p. 2, 12 VDC coil: must operate
    <= 80 % = 9.6 V, must release >= 10 % = 1.2 V, release <= 3 ms):
      t_jack = first sample with VRELAY - MUTE_CMD < 1.2 V, + 3 ms (LATEST);
      t_gain = first sample with VRELAY - PERMIT_CMD < 9.6 V or VRELAY <
               9.6 V, + 0 ms (EARLIEST).
    The same thresholds as psu/analizza_seq.py, criteria r and s.

THE TIME AXIS. The audio bench's event sits at 1 s (L30's T_OFF): its op and
1 s of settling come first. t_audio = t_psu - T0, with T0 = TE - 1 s for the
faults (the event at TE = 2 s) and T0 = TE + 5.4 s for the soft power-down
(the front opens at TE; d reaches 1 at ~TE + 6.03 s, MUTE_CMD is released at
~TE + 6.53 s; the fade itself is V2's insertion, covered since L29d2/L29e).
t_ins, where V2's A_ins starts reading, is 10 ms before the event for the
faults and TE + 6.4 s for the power-down. Each case gets its own REFERENCE:
the same PWL points up to t_ins, held from there, the contacts never moving - so A_ins reads
what happens after t_ins and nothing else.

POINTS. ngspice 47 drops an `alter @v[pwl] = [ ... ]` with 1000 numbers or
more, printing only "alter: too many args." and exiting 0 (L41c: 400 points
pass, 500 do not). Every PWL is reduced (greedy: a point is kept when the
straight line from the last kept one misses a sample by more than the
tolerance) to at most MAX_PUNTI points; the tolerance starts at TOL and is
doubled until it fits, and the one used and the worst miss are in the JSON.

REFUSES a case without punto_fisso.txt, a pass whose log has any of the
words of limitations #33 / #35, or whose data end before the case's end.
"""
import json
import os
import sys

TE = 2.0
T_EVENTO_AUDIO = 1.0
MAX_PUNTI = 350
TOL = {"rail": 0.5e-3}      # V
V_OP, V_RIL, T_RIL = 9.6, 1.2, 3e-3      # G6K 12 VDC: must operate, must release, release time
MALE = ("error", "singular", "no such", "non-increasing", "transient op", "timestep too small",
        "aborted", "too many args")
# per case: (T0, t_ins in psu time)
FINESTRA = {}       # L47c2b2: spegnimento_l takes the faults' window (the header)
FINESTRA_DEF = (TE - T_EVENTO_AUDIO, TE - 0.010)


def leggi(path):
    f = open(path)
    head = f.readline().split()
    cols = {n: [] for n in head}
    for r in f:
        v = r.split()
        if len(v) != len(head):
            continue
        for n, x in zip(head, v):
            cols[n].append(float(x))
    return cols


def riduci(t, y, tol, rel):
    """PWL reduction (Douglas-Peucker on the vertical miss): a segment is split
    at its worst sample while that sample misses the straight line by more
    than tol (rel: tol x |y| + 0.1 nA). Returns (points, worst miss)."""
    keep = {0, len(t) - 1}
    stack = [(0, len(t) - 1)]
    worst = 0.0
    while stack:
        a, b = stack.pop()
        km, em, over = None, 0.0, False
        for k in range(a + 1, b):
            yl = y[a] + (y[b] - y[a]) * (t[k] - t[a]) / (t[b] - t[a])
            e = abs(y[k] - yl)
            lim = (tol * abs(y[k]) + 1e-10) if rel else tol
            if e > lim:
                over = True
            if e > em:
                km, em = k, e
        if over:
            keep.add(km)
            stack += [(a, km), (km, b)]
        else:
            worst = max(worst, em)
    keep = sorted(keep)
    return [(t[k], y[k]) for k in keep], worst


def pwl_di(t, y, tipo):
    rel = tipo == "led"
    tol = TOL[tipo]
    while True:
        pts, worst = riduci(t, y, tol, rel)
        if len(pts) <= MAX_PUNTI:
            return pts, tol, worst
        tol *= 2


def primo(t, cond, dopo):
    for k in range(len(t)):
        if t[k] >= dopo and cond(k):
            return t[k]
    return None


def caso(seq, out, nome):
    d = os.path.join(seq, nome)
    pf = os.path.join(d, "punto_fisso.txt")
    if not os.path.exists(pf):
        raise SystemExit("%s: nessun punto fisso - rifiutato" % nome)
    g = int(open(pf).read())
    log = open(os.path.join(d, "tb_psu_seq_%s_g%d.log" % (nome, g))).read().lower()
    bad = [w for w in MALE if w in log]
    if bad:
        raise SystemExit("%s giro %d: il log ha %s - rifiutato (limitations #33, #35)" % (nome, g, bad))
    S = leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    t = S["time"]
    t0, t_ins = FINESTRA.get(nome, FINESTRA_DEF)
    vr = S["v(vrelay)"]
    jack = primo(t, lambda k: vr[k] - S["v(mute_cmd)"][k] < V_RIL, TE)
    gain = primo(t, lambda k: vr[k] - S["v(permit_cmd)"][k] < V_OP or vr[k] < V_OP, TE)
    jack = None if jack is None else jack + T_RIL
    # the window: from t0 to the end of the pass
    k0 = next(k for k in range(len(t)) if t[k] >= t0)
    tt = [x - t0 for x in t[k0:]]
    fine = tt[-1]
    res = {"caso": nome, "giro": g, "sorgente": os.path.relpath(d, out), "T0_psu": t0,
           "t_ins": t_ins - t0, "t_fine": fine, "t_jack": None if jack is None else jack - t0,
           "t_gain": None if gain is None else gain - t0,
           "soglie": {"V_op": V_OP, "V_ril": V_RIL, "T_ril": T_RIL}}
    if res["t_jack"] is not None and res["t_jack"] > fine:
        raise SystemExit("%s: il jack si apre dopo la fine dei dati" % nome)
    for chiave, col, scala, tipo in (("vpp", "v(vplus)", 1.0, "rail"), ("vmm", "v(vminus)", 1.0, "rail")):
        y = [x * scala for x in S[col][k0:]]
        pts, tol, worst = pwl_di(tt, y, tipo)
        res[chiave] = {"punti": pts, "tolleranza": tol, "scarto_max": worst, "n": len(pts)}
        # the reference: the SAME points up to t_ins, then held at the PWL's
        # own value there - identical to the case before t_ins, sample by sample
        ti = res["t_ins"]
        a = max(k for k in range(len(pts)) if pts[k][0] <= ti)
        (ta, ya), (tb, yb) = pts[a], pts[min(a + 1, len(pts) - 1)]
        yi = ya if tb == ta else ya + (yb - ya) * (ti - ta) / (tb - ta)
        pts_r = pts[:a + 1] + ([(ti, yi)] if ti > ta else []) + [(fine, yi)]
        res[chiave + "_rif"] = {"punti": pts_r, "n": len(pts_r)}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, nome + ".json"), "w"), indent=1)
    print("%-16s giro %d  t_ins %.4f  jack %s  guadagno %s  fine %.3f  punti %s" % (
        nome, g, res["t_ins"], "-" if res["t_jack"] is None else "%.5f" % res["t_jack"],
        "-" if res["t_gain"] is None else "%.5f" % res["t_gain"], fine,
        " ".join("%s=%d(%.2g)" % (c, res[c]["n"], res[c]["scarto_max"]) for c in ("vpp", "vmm"))))


if __name__ == "__main__":
    for n in sys.argv[3:]:
        caso(sys.argv[1], sys.argv[2], n)
