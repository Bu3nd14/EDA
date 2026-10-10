#!/usr/bin/env python3
"""L41b2: the sequences on the circuit, with the firmware core as the micro.
L47c2a: the firmware of the mute with the relays alone (ADR-062).

L47c2b2: COPIED from L47c2a's (data/2026-10-05/L47c2a/deck/), which stays as it
was, with L41c's cases and criteria BROUGHT BACK from L41c's analizza_seq.py
(data/2026-09-26/L41c/psu/) - L47c2a had dropped them. WRITTEN BEFORE THE RUNS
of L47c2b2. The coil thresholds are the G6K's (en-g6k.pdf p. 2, 12 VDC coil):
must operate <= 80 % (9.6 V), must release >= 10 % (1.2 V), release time
<= 3 ms. The worst corner is taken on purpose:
  jack  = the jack relays (K2-K4, MUTE_CMD) released at the LATEST: the first
          sample with VRELAY - MUTE_CMD < 1.2 V after TE, plus 3 ms;
  gain  = the gain relays (K1/K5 through K6 / VHOLD, PERMIT_CMD) released at
          the EARLIEST: the first sample with VRELAY - PERMIT_CMD < 9.6 V or
          VRELAY < 9.6 V after TE, plus 0 ms;
  every L41c case, from TE:
    r41  jack <= gain (ADR-045: the gain never moves with the jack connected);
    s41  jack before V+ falls below 10.6 V (L30: regulation lost on the + rail);
    (L41c called them r and s: renamed, since L47c2a's rilascio has its own r)
  spegnimento_l: i, j, k, l as spegnimento below (L47c2a's: i is 20-25 ms
    after the pin, no fade). It ends at TE + 1.1 s, the user's choice in
    L47c2b2 («1,1 s»): K501 opens ~0.13 s after TE, and L41c ended ~0.97 s
    after K501 too;
  perdita, perdita_min, guasto_u501, guasto_u503, guasto_u503_min: m (MUTE_CMD
    released within 16 ms of the event - for U503 the event is the
    regulator's, and the supervisor waits for VRELAY_REG < 11 V: 40 ms), n;
  guasto_u501: p, q as guasto;
  cf_nodelta: C3 and r41 MUST FAIL (L30: 69 mV at the jack without D) - the
    case passes when they fail;
  corto_u503: NO verdict - its criterion is the user's decision (NC-036,
    ADR-051); every figure is printed, none counted.

L47c2a's header follows.

Solo stdlib. /usr/bin/python3 analizza_seq.py <seq_dir> <caso> [<caso> ...]

Reads, per case, the fixed-point pass (<seq_dir>/<caso>/punto_fisso.txt):
the SPICE pins (tb_psu_seq_<caso>_g<g>_out.txt, 100 us grid) and the core's
outputs (core_g<g>.csv). A coil is ENERGISED when VRELAY - its drain > 6 V
(half its 12 V).

THE CRITERIA. L41b2's, written before its runs; L47c2a changes those that the
fade defined (marked), written before L47c2a's runs:
  every case, from TE = 2 s:
    F  the fixed point: the core's outputs equal to the pass before (the
       same rows and values, times within 0.2 ms: confronta.py), with 0
       substitutions of MUTE_G_IN (corri_seq.sh; checked again here);
    C2 MUTE_CMD energised => PERMIT_CMD energised, at every sample (J4:
       PERMIT_CMD energised no later than MUTE_CMD, released >= D after);
    C3 every release of MUTE_CMD is followed by PERMIT_CMD's >= 16.9 ms
       later (L41b1's minimum corner), or not within the run;
  accensione:
    a  [L47c2a] VRELAY_EN >= 100 ms after the rails are first in regulation
       on the circuit (ADC_SUP_P > 2.55 V, ADC_SUP_M < 1.20 V) - spec 4.1
       step 2 (L41b2: the DAC on; the calibration is gone);
    d  MUTE_CMD energised >= 13 ms after VRELAY at J1 >= 9.6 V (ADR-027);
    e  [L47c2a] the core reaches MUSICA (the hardware did not refuse the
       release); L41b2's e (the shunt still at its top) is gone with it;
  rilascio: [L47c2a] r MUTE_CMD energised 20-25 ms after SW3 closes (the
    20 ms debounce, then the gate: ADR-062, the relays at once); e as above;
    L41b2's f (the series' calibration) is gone;
  inversione: [L47c2a] gone with the fade;
  spegnimento: i [L47c2a] MUTE_CMD released 20-25 ms after FRONT_IN crosses
    V5 / 2 at the pin (L41b2: 6.52 s, the fade and its 0.5 s hold); j K501's
    contact open >= 50 ms after PERMIT_CMD's release (ADR-046); k the rails
    in regulation (ADC_SUP_P >= 2.49 V, i.e. >= 13.5 V) until MUTE_CMD is
    released (P9); l the core ends in STANDBY;
  buco20, buco200: m MUTE_CMD released within 16 ms of the mains going
    (L41b1: 14.3 ms); n the core's MUTE_REQ low within 1 ms of MUTE_G_IN's
    fall; o MUTE_CMD energised again only >= 500 ms after the mains are back
    (spec 4.5: first class) - or, second class, after the power-up path
    (ACCENSIONE in the core's states); the class is reported;
  guasto: m as above (here the - rail); p K501 open >= 50 ms after the
    core's MUTE_REQ fell, and open to the end; q the core ends in GUASTO,
    and MUTE_CMD is never energised again.
"""
import math
import os
import sys

TE = 2.0


def leggi_out(path):
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


def leggi_core(path):
    rows = []
    for r in open(path):
        if r.startswith("t,"):
            continue
        v = r.strip().split(",")
        rows.append({"t": float(v[0]), "mains": int(v[1]), "vrel": int(v[2]), "mute": int(v[3]),
                     "perm": int(v[4]), "stato": v[5]})
    return rows


def core_a(rows, t):
    r = rows[0]
    for x in rows:
        if x["t"] <= t + 1e-9:
            r = x
        else:
            break
    return r


def fronti(t, on):
    """[(t, True/False)] of the changes of a boolean list."""
    out = []
    for k in range(1, len(on)):
        if on[k] != on[k - 1]:
            out.append((t[k], on[k]))
    return out


def primo(t, cond, dopo=TE):
    for k in range(len(t)):
        if t[k] >= dopo and cond(k):
            return t[k]
    return None


def db(a, b):
    return 20 * math.log10(a / b) if a > 0 else float("-inf")


def analizza(d, caso):
    g = int(open(os.path.join(d, caso, "punto_fisso.txt")).read())
    S = leggi_out(os.path.join(d, caso, "tb_psu_seq_%s_g%d_out.txt" % (caso, g)))
    core = leggi_core(os.path.join(d, caso, "core_g%d.csv" % g))
    pon = open(os.path.join(d, caso, "ponte_g%d.txt" % g)).read()
    t = S["time"]
    vr = S["v(vrelay)"]
    mute_on = [vr[k] - S["v(mute_cmd)"][k] > 6 for k in range(len(t))]
    perm_on = [vr[k] - S["v(permit_cmd)"][k] > 6 for k in range(len(t))]
    res = []

    def crit(nome, ok, testo):
        res.append((nome, ok, testo))

    conf = open(os.path.join(d, caso, "confronto_g%d.txt" % g)).read().strip()
    crit("F", conf.startswith("uguali") and pon.strip().endswith("MUTE_G_IN 0"),
         "punto fisso al giro %d (%s), sostituzioni 0" % (g, conf))
    bad = [t[k] for k in range(len(t)) if t[k] >= TE and mute_on[k] and not perm_on[k]]
    crit("C2", not bad, "MUTE_CMD eccitato senza PERMIT_CMD: %s" % ("mai" if not bad else "a %.5f s" % bad[0]))
    fm = [x for x, on in fronti(t, mute_on) if not on and x >= TE]
    fp = [x for x, on in fronti(t, perm_on) if not on and x >= TE]
    deltas = []
    for x in fm:
        nxt = [y for y in fp if y >= x]
        deltas.append((nxt[0] - x) if nxt else None)
    okd = all(dd is None or dd >= 16.9e-3 for dd in deltas)
    crit("C3", okd, "Delta ai rilasci: %s" % (", ".join("mai" if dd is None else "%.2f ms" % (dd * 1e3)
                                                         for dd in deltas) or "nessun rilascio"))
    st = [r["stato"] for r in core]
    stati = []
    for s_ in st:
        if not stati or stati[-1] != s_:
            stati.append(s_)
    fatti = {"stati": " -> ".join(stati)}

    def t_core(cond, dopo=TE):
        for r in core:
            if r["t"] >= dopo and cond(r):
                return r["t"]
        return None

    t_mute_on = primo(t, lambda k: mute_on[k])
    t_mus = t_core(lambda r: r["stato"] == "MUSICA")
    if caso == "accensione":
        t_rail = primo(t, lambda k: S["v(adc_sup_p)"][k] > 2.55 and S["v(adc_sup_m)"][k] < 1.20)
        t_vren = t_core(lambda r: r["vrel"] == 1)
        crit("a", t_vren - t_rail >= 0.100 - 1e-4, "VRELAY_EN %.1f ms dopo i rail in regolazione"
             % ((t_vren - t_rail) * 1e3))
        t_vr = primo(t, lambda k: vr[k] >= 9.6)
        crit("d", t_mute_on - t_vr >= 13e-3, "MUTE_CMD eccitato %.1f ms dopo VRELAY >= 9,6 V" % ((t_mute_on - t_vr) * 1e3))
        crit("e", t_mus is not None, "MUSICA %s" % ("mai" if t_mus is None else "a +%.4f s" % (t_mus - TE)))
        fatti.update(t_mains=t_core(lambda r: r["mains"] == 1) - TE, t_rail=t_rail - TE,
                     t_vren=t_vren - TE, t_mute_on=t_mute_on - TE)
    if caso == "rilascio":
        crit("r", t_mute_on is not None and 20e-3 <= t_mute_on - TE <= 25e-3,
             "MUTE_CMD eccitato %.2f ms dopo SW3" % ((t_mute_on - TE) * 1e3 if t_mute_on else -1))
        crit("e", t_mus is not None, "MUSICA %s" % ("mai" if t_mus is None else "a +%.4f s" % (t_mus - TE)))
        fatti.update(t_mute_on=t_mute_on - TE, t_musica=t_mus - TE)
    if caso in ("spegnimento", "spegnimento_l"):
        t_pin = primo(t, lambda k: S["v(front_in)"][k] > 2.5)
        crit("i", bool(fm) and 20e-3 <= fm[0] - t_pin <= 25e-3,
             "MUTE_CMD rilasciato %.2f ms dopo FRONT_IN a V5/2 (il pin a +%.2f ms dal frontale)"
             % ((fm[0] - t_pin) * 1e3 if fm else -1, (t_pin - TE) * 1e3))
        t_k = primo(t, lambda k: S["v(k501_f)"][k] < 0.5)
        crit("j", fp and t_k is not None and t_k - fp[0] >= 50e-3,
             "K501 aperto %.1f ms dopo il rilascio di PERMIT_CMD" % ((t_k - fp[0]) * 1e3 if t_k and fp else -1))
        ok_k = all(S["v(adc_sup_p)"][k] >= 2.49 and S["v(adc_sup_m)"][k] <= 1.25
                   for k in range(len(t)) if TE <= t[k] <= fm[0])
        crit("k", ok_k, "rail in regolazione fino al rilascio di MUTE_CMD")
        crit("l", core[-1]["stato"] == "STANDBY", "stato finale del core: %s" % core[-1]["stato"])
        fatti.update(t_mute_off=fm[0] - TE, t_permit_off=fp[0] - TE, t_k501=t_k - TE)
    if caso in ("buco20", "buco200", "guasto") + L41C_M:
        lim_m = 40e-3 if "u503" in caso else 16e-3
        crit("m", bool(fm) and fm[0] - TE <= lim_m, "MUTE_CMD rilasciato %.2f ms dopo l'evento" % ((fm[0] - TE) * 1e3 if fm else -1))
        tg = primo(t, lambda k: S["v(mute_g_in)"][k] < 2.5)
        tc = t_core(lambda r: r["mute"] == 0)
        crit("n", tg is not None and tc - tg <= 1e-3 + 1e-6, "MUTE_REQ giu' %.3f ms dopo la caduta di MUTE_G_IN" % ((tc - tg) * 1e3))
        fatti.update(t_mute_g_in=tg - TE, t_mute_req=tc - TE)
    if caso in ("buco20", "buco200"):
        dur = 0.020 if caso == "buco20" else 0.200
        t_back = TE + dur
        classe2 = "ACCENSIONE" in stati[stati.index("BUCO_RETE"):] if "BUCO_RETE" in stati else False
        t_re = primo(t, lambda k: mute_on[k], dopo=fm[0] if fm else TE)
        crit("o", t_re is None or t_re - t_back >= 0.5 or classe2,
             "classe %d; MUTE_CMD di nuovo eccitato %s" % (2 if classe2 else 1,
                                                         "mai" if t_re is None else "%.3f s dopo il ritorno della rete" % (t_re - t_back)))
        rmin = min(S["v(adc_sup_p)"][k] for k in range(len(t)) if t[k] >= TE)
        fatti.update(classe=2 if classe2 else 1, sup_p_min=rmin, vplus_min=rmin * 54.2 / 10)
    if caso in ("guasto", "guasto_u501"):
        tc = t_core(lambda r: r["mute"] == 0)
        t_k = primo(t, lambda k: S["v(k501_f)"][k] < 0.5)
        chiuso_dopo = any(S["v(k501_f)"][k] > 0.5 for k in range(len(t)) if t_k and t[k] > t_k + 0.01)
        crit("p", t_k is not None and t_k - tc >= 50e-3 and not chiuso_dopo,
             "K501 aperto %.1f ms dopo MUTE_REQ, %s" % ((t_k - tc) * 1e3 if t_k else -1,
                                                       "richiuso" if chiuso_dopo else "aperto fino alla fine"))
        re = primo(t, lambda k: mute_on[k], dopo=fm[0] if fm else TE)
        crit("q", core[-1]["stato"] == "GUASTO" and re is None, "stato finale %s, MUTE_CMD %s"
             % (core[-1]["stato"], "mai rieccitato" if re is None else "rieccitato a %.3f" % re))
    if caso in L41C:
        vp = S["v(vplus)"]
        jack = primo(t, lambda k: vr[k] - S["v(mute_cmd)"][k] < 1.2)
        jack = None if jack is None else jack + 3e-3
        gain = primo(t, lambda k: vr[k] - S["v(permit_cmd)"][k] < 9.6 or vr[k] < 9.6)
        t106 = primo(t, lambda k: vp[k] < 10.6)
        ok_r = jack is not None and (gain is None or jack <= gain)
        crit("r41", ok_r, "jack (tardi) a +%s ms, guadagno (presto) a +%s ms"
             % ("-" if jack is None else "%.2f" % ((jack - TE) * 1e3),
                "mai" if gain is None else "%.2f" % ((gain - TE) * 1e3)))
        crit("s41", jack is not None and (t106 is None or jack <= t106),
             "jack (tardi) a +%s ms, V+ sotto 10,6 V a +%s ms"
             % ("-" if jack is None else "%.2f" % ((jack - TE) * 1e3),
                "mai" if t106 is None else "%.2f" % ((t106 - TE) * 1e3)))
        fatti.update(t_jack_tardi=None if jack is None else jack - TE,
                     t_guadagno_presto=None if gain is None else gain - TE,
                     t_vplus_10_6=None if t106 is None else t106 - TE,
                     vplus_fine=vp[-1], vminus_fine=S["v(vminus)"][-1], t_fine=t[-1] - TE)
    if caso == "cf_nodelta":
        # the counterfactual: C3 and r41 must fail - rename them and invert
        res[:] = [(n + "*", not ok, "DEVE FALLIRE: " + x) if n in ("C3", "r41") else (n, ok, x)
                  for n, ok, x in res]
    return res, fatti


# L41c's cases (the header): the ones with m / n, and all of them
L41C_M = ("perdita", "perdita_min", "guasto_u501", "guasto_u503", "guasto_u503_min", "cf_nodelta",
          "corto_u503")
L41C = ("spegnimento_l",) + L41C_M
INFO = ("corto_u503",)


def main(argv):
    d = argv[1]
    tot = True
    for caso in argv[2:]:
        print("== %s" % caso)
        # a case without its fixed point has no deck to judge: it fails here,
        # and the others are still analysed (L41b2: a traceback stopped the
        # whole analysis at the first such case)
        if not os.path.exists(os.path.join(d, caso, "punto_fisso.txt")):
            print("   F   NO    nessun punto fisso (corri_%s.txt)" % caso)
            tot = False
            continue
        res, fatti = analizza(d, caso)
        for nome, ok, testo in res:
            if caso in INFO:
                print("   %-3s %s  %s" % (nome, "info", testo))
                continue
            print("   %-3s %s  %s" % (nome, "ok  " if ok else "NO  ", testo))
            tot = tot and ok
        for k, v in fatti.items():
            print("   . %s: %s" % (k, ("%.6f" % v) if isinstance(v, float) else v))
    print("VERDETTO: %s" % ("PASSA" if tot else "FALLISCE"))
    return 0 if tot else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
