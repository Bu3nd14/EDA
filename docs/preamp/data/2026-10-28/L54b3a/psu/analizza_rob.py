#!/usr/bin/env python3
"""L54b3a: the robustness cases of the comparator timer (corri_an.sh), from the waveforms and the
log's .meas (genera_tb_psu.py --sonde-piu).

The columns of analizza_an.py (L54a: the thresholds of analizza_seq.py, the G6K's worst corner),
computed the same way, plus:
  n_giu / n_su   the de-energisings / energisings of MUTE_CMD after TE (the mute / the music);
  n_k501         K501's contact openings after TE;
  t_rit_ms       the mains back: the last change of v(env) after TE (empty if it never changes or
                 never comes back to its final level from below);
  dmus_ms        t_mus - t_rit: the music after the mains came back (criterion >= 500 ms);
  ritenuta       the latch held at the end: v(at_bn) > 0.4 V (or, without the probe, VRELAY_EN
                 below 1.5 V with the front switch closed);
  bn_max0, bn_max, on_min   the log's .meas (the latch base before / after TE, VRELAY_EN's minimum
                 after TE), on the transient's own points;
  rawv_max, rawp_max, raw_m_min, v5_min   after TE, on the 100 us grid.
Solo stdlib. /usr/bin/python3 -I analizza_rob.py [--te=3.0] <out.csv> <seq_dir>/<caso> [...]
"""
import csv
import os
import re
import sys

TE = 3.0


def leggi(path):
    with open(path) as f:
        nomi = f.readline().split()
        righe = [list(map(float, r.split())) for r in f if r.strip()]
    return {n: [r[k] for r in righe] for k, n in enumerate(nomi)}


def primo(t, cond, da=None):
    da = TE if da is None else da
    for k, x in enumerate(t):
        if x >= da and cond(k):
            return x
    return None


def meas(d):
    out = {}
    for f in os.listdir(d):
        if f.endswith("_g1.log"):
            for r in open(os.path.join(d, f), errors="replace"):
                m = re.match(r"\s*(bn_max0|bn_max|on_min|x_max|x_min)\s*=\s*([-+0-9.eE]+)", r)
                if m:
                    out[m.group(1)] = round(float(m.group(2)), 4)
    return out


def caso(d):
    nome = os.path.basename(d.rstrip("/"))
    if not os.path.exists(os.path.join(d, "ok.txt")):
        return dict(caso=nome, esito="CORSA RIFIUTATA")
    fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    assert len(fs) == 1, (d, fs)
    w = leggi(os.path.join(d, fs[0]))
    t = w["time"]
    n = len(t)
    vr, mc, pc = w["v(vrelay)"], w["v(mute_cmd)"], w["v(permit_cmd)"]
    vp, k5, env = w["v(vplus)"], w["v(k501_f)"], w["v(env)"]
    mute_on = [vr[k] - mc[k] > 6 for k in range(n)]
    perm_on = [vr[k] - pc[k] > 6 for k in range(n)]
    kte = min(range(n), key=lambda k: abs(t[k] - TE))
    r = dict(caso=nome, musica_TE=int(mute_on[kte]))
    r["C2"] = int(all(perm_on[k] or not mute_on[k] for k in range(n)))
    ok3 = True
    for k in range(1, n):
        if mute_on[k - 1] and not mute_on[k]:
            tp = primo(t, lambda j: not perm_on[j], t[k])
            if tp is not None and tp - t[k] < 0.0169:
                ok3 = False
    r["C3"] = int(ok3)
    tj = primo(t, lambda k: vr[k] - mc[k] < 1.2)
    tg = primo(t, lambda k: vr[k] - pc[k] < 9.6 or vr[k] < 9.6)
    tv = primo(t, lambda k: vp[k] < 10.6)
    tk = primo(t, lambda k: k5[k] < 0.5)
    r["t_jack_ms"] = "" if tj is None else round((tj - TE + 0.003) * 1e3, 2)
    r["t_gain_ms"] = "" if tg is None else round((tg - TE) * 1e3, 2)
    r["t_v106_ms"] = "" if tv is None else round((tv - TE) * 1e3, 2)
    r["t_k501_ms"] = "" if tk is None else round((tk - TE) * 1e3, 2)
    r["r41"] = "" if tj is None else int(tg is None or tj + 0.003 <= tg)
    r["s41"] = "" if tj is None else int(tv is None or tj + 0.003 <= tv)
    tm = None
    giu = su = nk = 0
    for k in range(1, n):
        if t[k] < TE:
            continue
        if mute_on[k] and not mute_on[k - 1]:
            tm = t[k]
            su += 1
        if mute_on[k - 1] and not mute_on[k]:
            giu += 1
        if k5[k - 1] >= 0.5 > k5[k]:
            nk += 1
    r["t_mus_ms"] = "" if tm is None else round((tm - TE) * 1e3, 2)
    r["n_giu"], r["n_su"], r["n_k501"] = giu, su, nk
    # the mains back: the last sample after TE where env differs from its final value
    trit = None
    for k in range(n - 1, 0, -1):
        if t[k] < TE:
            break
        if abs(env[k] - env[-1]) > 1e-3:
            trit = t[k + 1] if k + 1 < n else None
            break
    if trit is not None and env[-1] < max(env[kte:]) - 1e-3:
        trit = None        # it ended lower than it was: not a return (a loss for good)
    r["t_rit_ms"] = "" if trit is None else round((trit - TE) * 1e3, 2)
    r["dmus_ms"] = "" if (trit is None or tm is None or tm < trit) else round((tm - trit) * 1e3, 1)
    r["mus_end"] = int(mute_on[-1])
    r["k501_end"] = int(k5[-1] > 0.5)
    r["vplus_end"] = round(vp[-1], 3)
    if "v(at_bn)" in w:
        r["ritenuta"] = int(w["v(at_bn)"][-1] > 0.4)
    else:
        r["ritenuta"] = int(w["v(vrelay_en)"][-1] < 1.5)
    r.update(meas(d))
    for nome_v, chiave, f in (("v(raw_v)", "rawv_max", max), ("v(raw_p)", "rawp_max", max),
                              ("v(raw_m)", "rawm_min", min), ("v(v5)", "v5_min", min)):
        if nome_v in w:
            r[chiave] = round(f(w[nome_v][kte:]), 3)
    r["esito"] = "letto"
    return r


CAMPI = ["caso", "musica_TE", "C2", "C3", "r41", "s41", "t_jack_ms", "t_gain_ms", "t_v106_ms",
         "t_k501_ms", "t_mus_ms", "n_giu", "n_su", "n_k501", "t_rit_ms", "dmus_ms", "mus_end",
         "k501_end", "vplus_end", "ritenuta", "bn_max0", "bn_max", "on_min", "x_max", "x_min", "rawv_max",
         "rawp_max", "rawm_min", "v5_min", "esito"]


def main():
    global TE
    a = sys.argv[1:]
    if a[0].startswith("--te="):
        TE = float(a.pop(0)[5:])
    out, dirs = a[0], a[1:]
    rs = []
    for d in dirs:
        x = caso(d)
        x["caso"] = os.path.basename(os.path.dirname(d.rstrip("/"))) + "/" + x["caso"]
        rs.append(x)
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, CAMPI)
        wr.writeheader()
        for r in rs:
            wr.writerow(r)
    for r in rs:
        print(",".join(str(r.get(c, "")) for c in CAMPI))


main()
