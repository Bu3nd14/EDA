#!/usr/bin/env python3
"""L54a: the sequence cases of an analog timer (corri_an.sh), from the waveforms alone.

The thresholds are analizza_seq.py's (L41c / L47c2b2), the G6K's worst corner (en-g6k.pdf p. 2):
  jack  = MUTE_CMD released at the LATEST: the first sample after the event with
          VRELAY - MUTE_CMD < 1.2 V, plus 3 ms;
  gain  = the gain relays released at the EARLIEST: VRELAY - PERMIT_CMD < 9.6 V or
          VRELAY < 9.6 V, plus 0 ms;
  a coil is ENERGISED when VRELAY - its drain > 6 V.
Per case, from TE = 2 s (the event):
  musica_TE  MUTE_CMD energised at TE (the case starts in music; for accensione / fredda, mute);
  C2   MUTE_CMD energised => PERMIT_CMD energised, at every sample (J4);
  C3   every release of MUTE_CMD followed by PERMIT_CMD's >= 16.9 ms later, or not in the run;
  r41  jack <= gain; s41 jack before V+ < 10.6 V;
  t_jack, t_gain, t_v106, t_k501 (K501's contact open: k501_f < 0.5), t_mus (the last
  energising of MUTE_CMD after TE), mus_end (energised at the end of the run).
Solo stdlib. /usr/bin/python3 -I analizza_an.py [--te=3.0] <out.csv> <seq_dir>/<caso> [...]
"""
import csv
import os
import sys

TE = 2.0


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


def caso(d):
    nome = os.path.basename(d.rstrip("/"))
    pf = os.path.join(d, "punto_fisso.txt")
    if os.path.exists(pf):
        # the micro (corri_seq.sh): the fixed-point pass is the case
        g = open(pf).read().strip()
        fs = [f for f in os.listdir(d) if f.endswith("_g%s_out.txt" % g)]
    elif os.path.exists(os.path.join(d, "ok.txt")):
        fs = [f for f in os.listdir(d) if f.endswith("_g1_out.txt")]
    else:
        return dict(caso=nome, esito="CORSA RIFIUTATA")
    assert len(fs) == 1, (d, fs)
    w = leggi(os.path.join(d, fs[0]))
    t = w["time"]
    vr, mc, pc = w["v(vrelay)"], w["v(mute_cmd)"], w["v(permit_cmd)"]
    vp, k5 = w["v(vplus)"], w["v(k501_f)"]
    mute_on = [vr[k] - mc[k] > 6 for k in range(len(t))]
    perm_on = [vr[k] - pc[k] > 6 for k in range(len(t))]
    kte = min(range(len(t)), key=lambda k: abs(t[k] - TE))
    r = dict(caso=nome, musica_TE=int(mute_on[kte]))
    r["C2"] = int(all(perm_on[k] or not mute_on[k] for k in range(len(t))))
    ok3 = True
    for k in range(1, len(t)):
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
    for k in range(1, len(t)):
        if t[k] >= TE and mute_on[k] and not mute_on[k - 1]:
            tm = t[k]
    r["t_mus_ms"] = "" if tm is None else round((tm - TE) * 1e3, 2)
    r["mus_end"] = int(mute_on[-1])
    r["k501_end"] = int(k5[-1] > 0.5)
    r["vplus_end"] = round(vp[-1], 3)
    r["esito"] = "letto"
    return r


def main():
    global TE
    a = sys.argv[1:]
    if a[0].startswith("--te="):
        # the event's instant = genera_tb_psu.py's --tss (3.0 for the analog timers)
        TE = float(a.pop(0)[5:])
    out, dirs = a[0], a[1:]
    rs = [caso(d) for d in dirs]
    campi = ["caso", "musica_TE", "C2", "C3", "r41", "s41", "t_jack_ms", "t_gain_ms", "t_v106_ms",
             "t_k501_ms", "t_mus_ms", "mus_end", "k501_end", "vplus_end", "esito"]
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, campi)
        wr.writeheader()
        for r in rs:
            wr.writerow(r)
    for r in rs:
        print(",".join(str(r.get(c, "")) for c in campi))


main()
