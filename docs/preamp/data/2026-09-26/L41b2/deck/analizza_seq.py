#!/usr/bin/env python3
"""L41b2: the sequences on the circuit, with the firmware core as the micro.

Solo stdlib. /usr/bin/python3 analizza_seq.py <seq_dir> <caso> [<caso> ...]

Reads, per case, the fixed-point pass (<seq_dir>/<caso>/punto_fisso.txt):
the SPICE pins (tb_psu_seq_<caso>_g<g>_out.txt, 100 us grid) and the core's
outputs (core_g<g>.csv). A coil is ENERGISED when VRELAY - its drain > 6 V
(half its 12 V). The string currents are the sense voltages / 10 ohm.

THE CRITERIA, written before the runs of every case but the power-up (whose
fixed point had been looked at while the bridge was built):
  every case, from TE = 2 s:
    F  the fixed point: the core's outputs equal to the pass before (the
       same rows and values, times within 0.2 ms: confronta.py), with 0
       substitutions of MUTE_G_IN (corri_seq.sh; checked again here);
    C2 MUTE_CMD energised => PERMIT_CMD energised, at every sample (J4:
       PERMIT_CMD energised no later than MUTE_CMD, released >= D after);
    C3 every release of MUTE_CMD is followed by PERMIT_CMD's >= 16.9 ms
       later (L41b1's minimum corner), or not within the run;
  accensione:
    a  the DAC on >= 100 ms after the rails are first in regulation on the
       circuit (ADC_SUP_P > 2.55 V, ADC_SUP_M < 1.20 V) - spec 4.1 step 2;
    b  the series string <= 50 nA while the shunt is calibrated;
    c  the shunt at d = 1 after its calibration within +-0.5 dB of 12 mA
       (ADR-050), read 47 ms after the corrected code;
    d  MUTE_CMD energised >= 13 ms after VRELAY at J1 >= 9.6 V (ADR-027);
    e  when MUTE_CMD energises the shunt is still >= 10 mA: d has not moved
       (ADR-039: the relay before d);
  rilascio: e as above; f the series at 12 mA +-0.5 dB after its calibration
    in MUSICA (at the end of the run);
  inversione: g MUTE_CMD never released; h the series' minimum within
    +-1.5 dB of the table at the reversal's d; the shunt below 1 uA
    throughout (d never passed 0.5); f at the end;
  spegnimento: i MUTE_CMD released 6.52 s +- 5 ms after FRONT_IN crosses
    V5 / 2 at the pin [CHANGED after the first run: it read "after the front",
    with the spec's 0.1 ms pole; the opening edge charges through R518 100k x
    C532 100 nF, 10 ms, and crosses 2.5 V 7.0 ms after the switch opens - the
    first run gave 6.529 s from the switch, 6.522 from the pin]; j K501's
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
                     "perm": int(v[4]), "dac": int(v[5]), "cs": int(v[6]), "cp": int(v[7]),
                     "stato": v[8], "d": float(v[9])})
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
    i_s = [x / 10 for x in S["v(ldr_s_k)"]]
    i_p = [x / 10 for x in S["v(ldr_p_k)"]]
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
    if caso == "accensione":
        t_rail = primo(t, lambda k: S["v(adc_sup_p)"][k] > 2.55 and S["v(adc_sup_m)"][k] < 1.20)
        t_dac = t_core(lambda r: r["dac"] == 1)
        crit("a", t_dac - t_rail >= 0.100 - 1e-4, "DAC acceso %.1f ms dopo i rail in regolazione"
             % ((t_dac - t_rail) * 1e3))
        t_vren = t_core(lambda r: r["vrel"] == 1)
        smax = max(i_s[k] for k in range(len(t)) if t_dac <= t[k] <= t_vren)
        crit("b", smax <= 50e-9, "serie durante la calibrazione della derivazione: max %.3g A" % smax)
        k47 = min(range(len(t)), key=lambda k: abs(t[k] - (t_vren + 0.047)))
        e = db(i_p[k47], 12e-3)
        crit("c", abs(e) <= 0.5, "derivazione a d = 1 dopo la calibrazione: %.4f mA, %+.3f dB" % (i_p[k47] * 1e3, e))
        t_vr = primo(t, lambda k: vr[k] >= 9.6)
        crit("d", t_mute_on - t_vr >= 13e-3, "MUTE_CMD eccitato %.1f ms dopo VRELAY >= 9,6 V" % ((t_mute_on - t_vr) * 1e3))
        k = min(range(len(t)), key=lambda k: abs(t[k] - t_mute_on))
        crit("e", i_p[k] >= 10e-3, "derivazione quando MUTE_CMD si eccita: %.3f mA" % (i_p[k] * 1e3))
        fatti.update(t_mains=t_core(lambda r: r["mains"] == 1) - TE, t_rail=t_rail - TE,
                     t_dac=t_dac - TE, t_vren=t_vren - TE, t_mute_on=t_mute_on - TE)
    if caso == "rilascio":
        k = min(range(len(t)), key=lambda k: abs(t[k] - t_mute_on))
        crit("e", i_p[k] >= 10e-3, "derivazione quando MUTE_CMD si eccita: %.3f mA" % (i_p[k] * 1e3))
        e = db(i_s[-1], 12e-3)
        crit("f", abs(e) <= 0.5, "serie alla fine, dopo la calibrazione in MUSICA: %.4f mA, %+.3f dB" % (i_s[-1] * 1e3, e))
        t_mus = t_core(lambda r: r["stato"] == "MUSICA")
        fatti.update(t_mute_on=t_mute_on - TE, t_musica=t_mus - TE)
    if caso == "inversione":
        crit("g", not fm, "MUTE_CMD rilasciato: %s" % ("mai" if not fm else "a %.4f" % fm[0]))
        dmax = max(r["d"] for r in core if r["t"] >= TE)
        # the table at dmax (ADR-039, top 12 mA)
        pts = [(0, 12e-3), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, 10e-9), (1, 10e-9)]
        for (d0, i0), (d1, i1) in zip(pts, pts[1:]):
            if d0 <= dmax <= d1:
                tab = math.exp(math.log(i0) + (dmax - d0) / (d1 - d0) * (math.log(i1) - math.log(i0)))
        smin = min(i_s[k] for k in range(len(t)) if t[k] >= TE)
        crit("h", abs(db(smin, tab)) <= 1.5, "serie minima %.3g A contro %.3g A della tabella a d = %.4f (%+.2f dB)"
             % (smin, tab, dmax, db(smin, tab)))
        pmax = max(i_p[k] for k in range(len(t)) if t[k] >= TE)
        crit("h2", pmax < 1e-6, "derivazione massima %.3g A" % pmax)
        e = db(i_s[-1], 12e-3)
        crit("f", abs(e) <= 0.5, "serie alla fine: %.4f mA, %+.3f dB" % (i_s[-1] * 1e3, e))
        fatti.update(dmax=dmax)
    if caso == "spegnimento":
        t_pin = primo(t, lambda k: S["v(front_in)"][k] > 2.5)
        crit("i", bool(fm) and abs(fm[0] - t_pin - 6.52) <= 5e-3,
             "MUTE_CMD rilasciato %.4f s dopo FRONT_IN a V5/2 (il pin a +%.2f ms dal frontale)"
             % ((fm[0] - t_pin) if fm else -1, (t_pin - TE) * 1e3))
        t_k = primo(t, lambda k: S["v(k501_f)"][k] < 0.5)
        crit("j", fp and t_k - fp[0] >= 50e-3, "K501 aperto %.1f ms dopo il rilascio di PERMIT_CMD" % ((t_k - fp[0]) * 1e3))
        ok_k = all(S["v(adc_sup_p)"][k] >= 2.49 and S["v(adc_sup_m)"][k] <= 1.25
                   for k in range(len(t)) if TE <= t[k] <= fm[0])
        crit("k", ok_k, "rail in regolazione fino al rilascio di MUTE_CMD")
        crit("l", core[-1]["stato"] == "STANDBY", "stato finale del core: %s" % core[-1]["stato"])
        fatti.update(t_mute_off=fm[0] - TE, t_permit_off=fp[0] - TE, t_k501=t_k - TE)
    if caso in ("buco20", "buco200", "guasto"):
        crit("m", bool(fm) and fm[0] - TE <= 16e-3, "MUTE_CMD rilasciato %.2f ms dopo l'evento" % ((fm[0] - TE) * 1e3 if fm else -1))
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
    if caso == "guasto":
        tc = t_core(lambda r: r["mute"] == 0)
        t_k = primo(t, lambda k: S["v(k501_f)"][k] < 0.5)
        chiuso_dopo = any(S["v(k501_f)"][k] > 0.5 for k in range(len(t)) if t_k and t[k] > t_k + 0.01)
        crit("p", t_k is not None and t_k - tc >= 50e-3 and not chiuso_dopo,
             "K501 aperto %.1f ms dopo MUTE_REQ, %s" % ((t_k - tc) * 1e3 if t_k else -1,
                                                       "richiuso" if chiuso_dopo else "aperto fino alla fine"))
        re = primo(t, lambda k: mute_on[k], dopo=fm[0] if fm else TE)
        crit("q", core[-1]["stato"] == "GUASTO" and re is None, "stato finale %s, MUTE_CMD %s"
             % (core[-1]["stato"], "mai rieccitato" if re is None else "rieccitato a %.3f" % re))
    return res, fatti


def main(argv):
    d = argv[1]
    tot = True
    for caso in argv[2:]:
        res, fatti = analizza(d, caso)
        print("== %s" % caso)
        for nome, ok, testo in res:
            print("   %-3s %s  %s" % (nome, "ok  " if ok else "NO  ", testo))
            tot = tot and ok
        for k, v in fatti.items():
            print("   . %s: %s" % (k, ("%.4f" % v) if isinstance(v, float) else v))
    print("VERDETTO: %s" % ("PASSA" if tot else "FALLISCE"))
    return 0 if tot else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
