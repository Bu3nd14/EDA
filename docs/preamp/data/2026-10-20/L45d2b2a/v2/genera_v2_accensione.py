#!/usr/bin/env python3
"""L45d2b2a: V2 at the power-up with the rails of the supply bench, not L29c's ramps. Stdlib.

L29c's V2 matrix (spice/preamp/tb/tb_v2_casopeggiore.cir, geometry iii) has six power-up runs on an
ASSUMPTION its header declares: linear rails in 10 or 300 ms, skewed by <= 50 ms, the jack released
2.5 s after the ramp starts. With the soft-start of ADR-091 the rails take 0.56-0.65 s and the
firmware releases the jack 0.70 s after they start (timer_spec.md 4.1: both rails past the threshold
for 100 ms, then 50 ms). This writes a deck with, after the six runs of L29c:
  - on_ss_nom_iii: VPLUS and VMINUS sampled every 2 ms from the bench's power-up on today's psu.net
    (seq/sorgente/accensione at its fixed point), from the rails' start; the release (vkcb and,
    1 ms later, vtrser) at the bench's own jack instant;
  - on_ss_ps_iii / on_ss_pf_iii: the + rail 20 % slower and the - rail 20 % faster, and the other way
    round (C507 / C508 at the ends of a +-20 % tolerance, the ramps scaled in time); the release at
    max(the two thresholds) + 151.1 ms, the bench's delay (VRELAY_EN 101.0 ms after the later
    threshold, the jack 50.1 ms after VRELAY_EN);
each a copy of on_r300s_iii with ONLY the two PWLs, the two release times, the end (release + 3 s)
and the manifest row changed - asserted, line by line.

Uso: genera_v2_accensione.py   -> v2/tb_v2_accensione.cir (the versioned deck is not touched)
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
REPO = os.path.abspath(os.path.join(LOTTO, "..", "..", "..", "..", ".."))
DECK = os.path.join(REPO, "spice", "preamp", "tb", "tb_v2_casopeggiore.cir")
SEQ = os.path.join(LOTTO, "seq", "sorgente", "accensione")
T0_ON = 0.1                        # L29c's T0_ON: the rails start here in the V2 deck
DT_FW = 0.1511                     # the later threshold -> the jack (the bench, above)


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


g = open(os.path.join(SEQ, "punto_fisso.txt")).read().strip()
c = leggi(os.path.join(SEQ, "tb_psu_seq_accensione_g%s_out.txt" % g))
t, vp, vm = c["time"], c["v(vplus)"], c["v(vminus)"]
t0 = next(t[k] for k in range(len(t)) if c["v(mains_req)"][k] > 2.5)
ts = next(t[k] for k in range(len(t)) if t[k] > t0 and (vp[k] > 0.01 or vm[k] < -0.01))
tj = next(t[k] for k in range(len(t)) if t[k] > t0 and c["v(vrelay)"][k] - c["v(mute_cmd)"][k] > 6)
fw_p = next(t[k] for k in range(len(t)) if t[k] > t0 and vp[k] > 13.82) - ts
fw_m = next(t[k] for k in range(len(t)) if t[k] > t0 and c["v(adc_sup_m)"][k] < 1.20) - ts
rel_nom = tj - ts
assert abs(rel_nom - (max(fw_p, fw_m) + DT_FW)) < 0.002, (rel_nom, fw_p, fw_m)


def campiona(v, k):
    """(time in the V2 deck, value): the bench's rail from its start, scaled in time by k, every
    30 ms to 1.02 s (35 points, linear between them), then held. Not finer: with 500 points the
    alter line stopped ngspice ("alter: too many args"), and the run went on with L29c's rails -
    the guard (guardia_v2.py) refused it (L45d2b2a, first try)."""
    pts, tt = [], 0.0
    while tt <= 1.02 + 1e-9:
        tb = ts + tt / k
        i = min(range(len(t)), key=lambda j: abs(t[j] - tb))
        pts.append((T0_ON + tt, v[i]))
        tt += 0.03
    return "0 0 %s 1000 %.6g" % (" ".join("%.6g %.6g" % p for p in pts), pts[-1][1])


# (time factor of the + rail, of the - rail, release: None = the firmware's, else L29c's 2.5 s after
# the ramp). The verdict wants >= 2 s of window for A_ins (the filter, REQUIREMENTS V2): with the
# firmware's release the ramp's window is 0.7 s and A_ins is refused; the on_ssl_* runs give the ramp
# its window with L29c's release, the on_ss_* runs judge the release at its real instant (A_rel)
VARIANTI = {"on_ss_nom_iii": (1.0, 1.0, None), "on_ss_ps_iii": (1 / 1.2, 1.2, None),
            "on_ss_pf_iii": (1.2, 1 / 1.2, None),
            "on_ssl_nom_iii": (1.0, 1.0, 2.5), "on_ssl_ps_iii": (1 / 1.2, 1.2, 2.5),
            "on_ssl_pf_iii": (1.2, 1 / 1.2, 2.5)}

testo = open(DECK).read()
m = re.search(r"\* ---- L29d2 5: on_r300s_iii ----\n.*?>> tb_v2_casopeggiore_manifest.csv\n", testo, re.S)
blocco = m.group(0)
assert blocco.count("alter vkcb dc = 2.600000\n") == 1 and blocco.count("alter vtrser dc = 2.601000\n") == 1
assert blocco.count("tran 1e-05 5.6 0 1e-05\n") == 1
nuovi = []
for nome, (kp, km, fisso) in VARIANTI.items():
    rel = rel_nom if kp == km == 1.0 else max(fw_p / kp, fw_m / km) + DT_FW
    if fisso is not None:
        rel = fisso
    tr, tf = T0_ON + rel, T0_ON + rel + 3.0
    b = blocco.replace("on_r300s_iii", nome)
    b = b.replace("alter @vpp[pwl] = [ 0 0 0.1 0 0.4 15 1000 15 ]",
                  "alter @vpp[pwl] = [ %s ]" % campiona(vp, kp))
    b = b.replace("alter @vmm[pwl] = [ 0 0 0.1 0 0.4 -15 1000 -15 ]",
                  "alter @vmm[pwl] = [ %s ]" % campiona(vm, km))
    b = b.replace("alter vkcb dc = 2.600000\n", "alter vkcb dc = %.6f\n" % tr)
    b = b.replace("alter vtrser dc = 2.601000\n", "alter vtrser dc = %.6f\n" % (tr + 0.001))
    b = b.replace("tran 1e-05 5.6 0 1e-05\n", "tran 1e-05 %.4f 0 1e-05\n" % tf)
    b = b.replace(",0.1,2.6,5.6,", ",0.1,%.6f,%.4f," % (tr, tf))
    b = b.replace("* ---- L29d2 5: %s ----" % nome,
                  "* ---- L45d2b2a: %s - the bench's rails x (%.4g, %.4g) in time, release %.4f s ----"
                  % (nome, 1 / kp, 1 / km, tr))
    diff = [x for x, y in zip(blocco.splitlines(), b.splitlines()) if x != y]
    assert len(diff) == (7 if fisso is not None else 9) and len(blocco.splitlines()) == len(b.splitlines()), (nome, len(diff))
    nuovi.append(b)
    print("%s: + x%.3g, - x%.3g in time; thresholds %.1f / %.1f ms; release %.4f s, end %.4f s"
          % (nome, 1 / kp, 1 / km, fw_p / kp * 1e3, fw_m / km * 1e3, tr, tf))
fine = testo.index(blocco) + len(blocco)
# after the last of L29c's six power-up runs
ultimo = re.search(r"\* ---- L29d2 5: on_r300m_iii ----\n.*?>> tb_v2_casopeggiore_manifest.csv\n",
                   testo, re.S)
fine = ultimo.end()
out = testo[:fine] + "".join(nuovi) + testo[fine:]
open(os.path.join(QUI, "tb_v2_accensione.cir"), "w").write(out)
print("rails start at %.4f s after MAINS_REQ (the bench); deck -> v2/tb_v2_accensione.cir" % (ts - t0))
