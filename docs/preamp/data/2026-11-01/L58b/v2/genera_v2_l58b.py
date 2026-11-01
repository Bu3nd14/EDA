#!/usr/bin/env python3
"""L58b: V2 at the power-up with Q501 shorted (D-S / G-D, ADR-076): the jack's coils energised from the
rails' start (psu/censimento.py: 2.5 ms after the front), against the base (the known answer: L58a2's
l58_base_acc). Only CASI and the output's name changed. COPIED from L58a2's generator, which follows:

L58a2: V2 at the power-up for the FMEA rows of D536 (open / short), whose music comes right at power
good instead of ~660 ms after it. Stdlib.

A copy of L45d2b2a's v2/genera_v2_accensione.py (data/2026-10-20/L45d2b2a/v2/), with the rails and the
release taken from THIS lot's sequence runs instead of the firmware's sequence:
  - the rails VPLUS / VMINUS sampled every 30 ms from their start (35 points to 1.02 s, then held:
    limitations #66), as L45d2b2a;
  - the release (vkcb and, 1 ms later, vtrser) at the run's own jack instant: the first sample after
    the rails start with VRELAY - MUTE_CMD > 6 V (analizza_mc.py's mute_on);
  - nominal rails only: the release follows power good, which follows the rails, so a +-20 % ramp
    would need the timer run again (declared in the report).
Each case is a copy of L29c's on_r300s_iii with ONLY the two PWLs, the two release times, the end
(release + 3 s) and the manifest row changed - asserted, line by line, as L45d2b2a.

The cases: the base (accensione from standby, fredda from cold) and D536 open / short in each.

Uso: genera_v2_l58b.py   -> v2/tb_v2_l58b.cir (the versioned deck is not touched)
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
DECK = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_casopeggiore.cir")
SEQ = os.path.join(LOTTO, "seq")
T0_ON = 0.1                        # L29c's T0_ON: the rails start here in the V2 deck

CASI = {"l58_base_acc": "l58b_base/accensione",
        "l58_q501c_acc": "l58b/f_q501_corto_accs",
        "l58_q501gd_acc": "l58b/f_q501_gd_accs"}


def leggi(path):
    f = open(path)
    nomi = f.readline().split()
    col = {n: [] for n in nomi}
    for r in f:
        p = r.split()
        if len(p) == len(nomi):
            for n, x in zip(nomi, p):
                col[n].append(float(x))
    return col


def campiona(t, v, ts):
    """(time in the V2 deck, value): the rail from its start, every 30 ms to 1.02 s, then held."""
    pts, tt = [], 0.0
    while tt <= 1.02 + 1e-9:
        i = min(range(len(t)), key=lambda j: abs(t[j] - (ts + tt)))
        pts.append((T0_ON + tt, v[i]))
        tt += 0.03
    return "0 0 %s 1000 %.6g" % (" ".join("%.6g %.6g" % p for p in pts), pts[-1][1])


testo = open(DECK).read()
m = re.search(r"\* ---- L29d2 5: on_r300s_iii ----\n.*?>> tb_v2_casopeggiore_manifest.csv\n", testo, re.S)
blocco = m.group(0)
assert blocco.count("alter vkcb dc = 2.600000\n") == 1 and blocco.count("alter vtrser dc = 2.601000\n") == 1
assert blocco.count("tran 1e-05 5.6 0 1e-05\n") == 1
nuovi = []
for nome, rel_dir in CASI.items():
    d = os.path.join(SEQ, rel_dir)
    f = [x for x in os.listdir(d) if x.endswith("_g1_out.txt")][0]
    c = leggi(os.path.join(d, f))
    t, vp, vm = c["time"], c["v(vplus)"], c["v(vminus)"]
    t0 = next(t[k] for k in range(len(t)) if c["v(mains_req)"][k] > 2.5 and t[k] >= 3.0)
    ts = next(t[k] for k in range(len(t)) if t[k] > t0 and (vp[k] > 0.01 or vm[k] < -0.01))
    tj = next(t[k] for k in range(len(t)) if t[k] > ts and c["v(vrelay)"][k] - c["v(mute_cmd)"][k] > 6)
    rel = tj - ts
    tr, tf = T0_ON + rel, T0_ON + rel + 3.0
    kj = min(range(len(t)), key=lambda k: abs(t[k] - tj))
    b = blocco.replace("on_r300s_iii", nome)
    b = b.replace("alter @vpp[pwl] = [ 0 0 0.1 0 0.4 15 1000 15 ]",
                  "alter @vpp[pwl] = [ %s ]" % campiona(t, vp, ts))
    b = b.replace("alter @vmm[pwl] = [ 0 0 0.1 0 0.4 -15 1000 -15 ]",
                  "alter @vmm[pwl] = [ %s ]" % campiona(t, vm, ts))
    b = b.replace("alter vkcb dc = 2.600000\n", "alter vkcb dc = %.6f\n" % tr)
    b = b.replace("alter vtrser dc = 2.601000\n", "alter vtrser dc = %.6f\n" % (tr + 0.001))
    b = b.replace("tran 1e-05 5.6 0 1e-05\n", "tran 1e-05 %.4f 0 1e-05\n" % tf)
    b = b.replace(",0.1,2.6,5.6,", ",0.1,%.6f,%.4f," % (tr, tf))
    b = b.replace("* ---- L29d2 5: %s ----" % nome,
                  "* ---- L58b: %s - the rails of %s, release %.4f s ----" % (nome, rel_dir, tr))
    diff = [x for x, y in zip(blocco.splitlines(), b.splitlines()) if x != y]
    assert len(diff) == 9 and len(blocco.splitlines()) == len(b.splitlines()), (nome, len(diff))
    nuovi.append(b)
    print("%s (%s): rails start %.1f ms after MAINS_REQ; release %.1f ms after the rails' start, "
          "rails there %.3f / %.3f V (final %.3f / %.3f)"
          % (nome, rel_dir, (ts - t0) * 1e3, rel * 1e3, vp[kj], vm[kj], vp[-1], vm[-1]))
ultimo = re.search(r"\* ---- L29d2 5: on_r300m_iii ----\n.*?>> tb_v2_casopeggiore_manifest.csv\n",
                   testo, re.S)
fine = ultimo.end()
out = testo[:fine] + "".join(nuovi) + testo[fine:]
open(os.path.join(QUI, "tb_v2_l58b.cir"), "w").write(out)
print("deck -> v2/tb_v2_l58b.cir")
