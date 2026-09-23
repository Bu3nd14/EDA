#!/usr/bin/env python3
"""L40: i costi dei candidati, dai deck flat corsi da genera_cand.sh.
  - tb_op: I_q Q132/Q133, correnti di rail, potenza a riposo del blocco
    (15 V x (|I(VPP)| + |I(VMM)|));
  - tb_noise_breakdown: E5, i cinque casi (a..e), e il peggiore;
  - tb_zout_psrr_noise: PSRR dal rail + e dal rail - (p10k, modo basso e +10 dB),
    Zout a 20 kHz (za20k) nel modo basso;
  - tb_v3_overload: il metodo di L39/script/v3.py (clip, G, recupero, DC al jack).
Uso: /Users/roberto/EDA/env/venv/bin/python3 cand_costi.py [fase]
"""
import glob
import os
import re
import sys

import numpy as np

L40 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fase = sys.argv[1] if len(sys.argv) > 1 else "candidati"
D = os.path.join(L40, fase)
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def valori(deck, cand, chiave):
    p = glob.glob(os.path.join(D, "%s__%s" % (deck, cand), "*.log"))
    if not p:
        return []
    return [float(x) for x in re.findall(r"^%s = (%s)" % (re.escape(chiave), NUM),
                                          open(p[0]).read(), re.M)]


def v3(cand):
    p = os.path.join(D, "tb_v3_overload__%s" % cand, "tb_v3_overload__%s.csv" % cand)
    d = np.loadtxt(p, delimiter=",", skiprows=1)
    t, src, out, jack = d[:, 0], d[:, 1], d[:, 3], d[:, 5]
    ov = (t >= 1e-3) & (t <= 6e-3)
    lin = (t >= 12e-3) & (t <= 20e-3)
    g = float(np.dot(src[lin], out[lin]) / np.dot(src[lin], src[lin]))
    err = np.abs(out - g * src)
    dopo6 = np.where(t > 6e-3)[0]
    fuori = dopo6[err[dopo6] >= 0.05 * g * 0.5]
    t_rec = (t[fuori[-1]] - 6e-3) if len(fuori) else 0.0
    return out[ov].max(), out[ov].min(), g, t_rec * 1e6, float(np.mean(jack[t >= 19e-3])) * 1e3


cands = sorted({os.path.basename(p).split("__", 1)[1]
                for p in glob.glob(os.path.join(D, "tb_op__*")) if os.path.isdir(p)})
print("%-8s %6s %6s %7s %7s | %-40s %6s | %6s %6s %6s %6s %6s | %s" % (
    "cand", "Iq+", "Iq-", "I_rail", "P_blk", "E5 a..e [uV]", "E5max",
    "p+10k0", "p+10k10", "p-10k0", "p-10k10", "za20k", "V3: clip+/-, G, rec, DC"))
for c in cands:
    ic = valori("tb_op", c, "@q132[ic]")[0], valori("tb_op", c, "@q133[ic]")[0]
    ir = abs(valori("tb_op", c, "i(vpp)")[0]), abs(valori("tb_op", c, "i(vmm)")[0])
    pb = 15 * (ir[0] + ir[1])
    e5 = [x * 1e6 for x in valori("tb_noise_breakdown", c, "onoise_total")]
    p10 = valori("tb_zout_psrr_noise", c, "p10k")
    za = valori("tb_zout_psrr_noise", c, "za20k")
    cp, cm, g, rec, dc = v3(c)
    print("%-8s %6.2f %6.2f %7.2f %7.3f | %-40s %6.3f | %6.1f %6.1f %6.1f %6.1f %6.3f | %+.2f/%+.2f V G %.3f %.2f us %+.2f mV" % (
        c, ic[0] * 1e3, abs(ic[1]) * 1e3, (ir[0] + ir[1]) / 2 * 1e3, pb,
        " ".join("%.3f" % x for x in e5), max(e5),
        p10[0], p10[2], p10[3], p10[5], za[0], cp, cm, g, rec, dc))
