#!/usr/bin/env python3
"""L45d2b2b1: the supply side of ADR-074's rows (the raw side's shorts), from the last pass of each
case's fixed point (seq/<etichetta>/<caso>/). Solo stdlib.

    analizza_074.py <seq/etichetta> <out.csv> <caso> [<caso> ...]     (@file: one case per line)

Every column of L45c1's analizza_psu.py (imported from data/2026-10-13/L45c1/script/, which stays as
it was: same refusals, same rules for t_fuori, t_10_6, t_jack, jack_prima...), plus, from TE to the
end of the run:
    in_p, in_m              the node read as the regulator's IN: raw_pr / raw_mr behind R550 / R551
                            (ADR-092), raw_p / raw_m on a netlist without them
    out_p, out_m            the regulator's OUT pin node: vplus / vminus, or vplus_reg / vminus_reg
                            with --variante uscita (the series diode after the pin)
    iser50x_pk_A, _min_A    --variante uscita: the series diode's largest |current| and its least
                            (a negative value would be reverse current)
    oi_pin_p, oi_pin_m      max of V(OUT_P) - V(IN_P) and of V(IN_M) - V(OUT_M): OUT beyond IN at the
                            PIN. U502's absolute maximum is -0.3 V OUT to IN (SBVS169D p. 5), i.e.
                            oi_pin_m <= 0.3 V
    t_oi_m_ms, t_oi_p_ms    how long that quantity stays above 0.3 V (total, ms)
    id510_pk_A, id511_pk_A  the Schottkys' peak forward current (i(vsdd510) / i(vsdd511), the fault
    i2t_510, i2t_511        cases' probe) and their I^2 t (A^2 s)
    q510_mC, q511_mC        the charge through each (mC)
    pr550_pk_W, er550_J     the peak power and the energy in R550 / R551 ((V(raw) - V(raw_r))^2 / R,
    pr551_pk_W, er551_J     R = 4.7 ohm, ADR-092), on a netlist that has them
    vp_al_jack, vm_al_jack  the rails when the jack opens (t_jack)
"""
import csv
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
_L45C1 = os.path.join(QUI, "..", "..", "..", "2026-10-13", "L45c1", "script", "analizza_psu.py")
_s = importlib.util.spec_from_file_location("analizza_psu_l45c1", _L45C1)
A = importlib.util.module_from_spec(_s)
_s.loader.exec_module(A)

R_PRE = 4.7          # R550 / R551, ADR-092
V_OI = 0.3           # SBVS169D p. 5: OUT pin to IN pin, -0.3 V


def integra(t, y, k0):
    return sum(0.5 * (y[k] + y[k - 1]) * (t[k] - t[k - 1]) for k in range(k0 + 1, len(t)))


def caso(seq, nome):
    r = A.caso(seq, nome)
    d = os.path.join(seq, nome)
    g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    S = A.leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    t, vp, vm = S["time"], S["v(vplus)"], S["v(vminus)"]
    k0 = next(k for k in range(len(t)) if t[k] >= A.TE)
    dopo = range(k0, len(t))
    ip = "raw_pr" if "v(raw_pr)" in S else "raw_p"
    im = "raw_mr" if "v(raw_mr)" in S else "raw_m"
    IP, IM = S["v(%s)" % ip], S["v(%s)" % im]
    r["in_p"], r["in_m"] = ip, im
    # --variante uscita: the regulator's OUT is its pin node, before the series diode
    # (the same node names in the netlist since ADR-093: VPLUS_REG / VMINUS_REG)
    PP = S.get("v(vplus_reg)", vp)
    PM = S.get("v(vminus_reg)", vm)
    r["out_p"] = "vplus_reg" if "v(vplus_reg)" in S else "vplus"
    r["out_m"] = "vminus_reg" if "v(vminus_reg)" in S else "vminus"
    op = [PP[k] - IP[k] for k in range(len(t))]
    om = [IM[k] - PM[k] for k in range(len(t))]
    # the series diode: --variante uscita's probe, or the netlist's D515 / D516 (ADR-093)
    for x, cols in (("501", ("i(vsser501)", "i(vsdd515)")), ("502", ("i(vsser502)", "i(vsdd516)"))):
        col = next((c for c in cols if c in S), None)
        if col:
            r["iser%s_pk_A" % x] = max(abs(S[col][k]) for k in dopo)
            r["iser%s_min_A" % x] = min(S[col][k] for k in dopo)
    r["oi_pin_p"] = max(op[k] for k in dopo)
    r["oi_pin_m"] = max(om[k] for k in dopo)
    for nm, y in (("t_oi_p_ms", op), ("t_oi_m_ms", om)):
        r[nm] = 1e3 * sum(t[k] - t[k - 1] for k in range(k0 + 1, len(t)) if y[k] > V_OI and y[k - 1] > V_OI)
    for dref, coppia in (("510", "513"), ("511", "514")):
        col = "i(vsdd%s)" % dref
        if col not in S:
            continue
        i = S[col]
        # ADR-093: two SB340 in parallel on the pin - the pair's total current
        if "i(vsdd%s)" % coppia in S:
            i = [a + b for a, b in zip(i, S["i(vsdd%s)" % coppia])]
        r["id%s_pk_A" % dref] = max(i[k] for k in dopo)
        r["i2t_%s" % dref] = integra(t, [x * x for x in i], k0)
        r["q%s_mC" % dref] = 1e3 * integra(t, i, k0)
    for rref, a, b in (("550", "v(raw_p)", "v(raw_pr)"), ("551", "v(raw_m)", "v(raw_mr)")):
        if a in S and b in S:
            p = [(S[a][k] - S[b][k]) ** 2 / R_PRE for k in range(len(t))]
            r["pr%s_pk_W" % rref] = max(p[k] for k in dopo)
            r["er%s_J" % rref] = integra(t, p, k0)
    tj = r["t_jack_ms"]
    if tj != "":
        kj = next((k for k in range(len(t)) if t[k] >= A.TE + float(tj) * 1e-3), len(t) - 1)
        r["vp_al_jack"], r["vm_al_jack"] = vp[kj], vm[kj]
    return r


CAMPI = A.CAMPI + ["in_p", "in_m", "out_p", "out_m", "iser501_pk_A", "iser501_min_A", "iser502_pk_A",
                   "iser502_min_A", "oi_pin_p", "oi_pin_m", "t_oi_p_ms", "t_oi_m_ms",
                   "id510_pk_A", "id511_pk_A", "i2t_510", "i2t_511", "q510_mC", "q511_mC",
                   "pr550_pk_W", "er550_J", "pr551_pk_W", "er551_J", "vp_al_jack", "vm_al_jack"]

if __name__ == "__main__":
    seq, out = sys.argv[1], sys.argv[2]
    nomi = sys.argv[3:]
    if len(nomi) == 1 and nomi[0].startswith("@"):
        nomi = [x.strip() for x in open(nomi[0][1:]) if x.strip()]
    righe = [caso(seq, n) for n in nomi]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI)
        w.writeheader()
        for x in righe:
            w.writerow({a: ("%.5g" % b if isinstance(b, float) else b) for a, b in x.items()})
    print("scritto %s: %d casi" % (out, len(righe)))
