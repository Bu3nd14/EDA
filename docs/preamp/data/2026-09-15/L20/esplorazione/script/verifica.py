#!/usr/bin/env python3
"""
verifica.py - L20: every control on the three runs, then the numbers.

Usage:
  python3 verifica.py <repo> <dir tb_idss_op_noise> <dir tb_idss_loop> <dir tb_idss_jfet>

The three directories are the outputs of scripts/run_simulation.sh. The same
script judges the real runs and the sabotaged copies: a control counts only if
it falls, and only the one expected to fall.

References, all read from files:
  L7        I_DSS 2.59283 mA, V_GS(off) -1.124355 V, V_GS 500 uA -0.650211 V (25 C)
  vto       docs/preamp/data/2026-09-15/L20/esplorazione/vto_dichiarati.csv
  L27 op    docs/preamp/data/2026-09-14/L27/dopo/tb_op/tb_op.log
  L27 noise docs/preamp/data/2026-09-14/L27/dopo/tb_noise_breakdown/tb_noise_breakdown.log
  L16 loop  docs/preamp/data/2026-09-14/L16/dopo/tb_loop/tb_loop_margini.csv

Exit: 0 every control passed, 1 at least one failed, 2 bad invocation.
"""
import csv
import math
import os
import re
import sys

FAILS = []


def check(name, ok, detail=""):
    print(f"   [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def num(s):
    return float(s)


def close(a, b, rel, absol=0.0):
    return abs(a - b) <= max(rel * abs(b), absol)


def log_values(path, start=None, end=None):
    out, inside = {}, start is None
    with open(path, errors="replace") as f:
        for ln in f:
            if start and start in ln:
                inside = True
                continue
            if end and end in ln:
                inside = False
                continue
            if not inside:
                continue
            m = re.match(r"^\s*([vi@]\S*)\s*=\s*(\S+)\s*$", ln)
            if m:
                try:
                    out[m.group(1).lower()] = float(m.group(2))
                except ValueError:
                    pass
    return out


def errors_in(path):
    with open(path, errors="replace") as f:
        return [ln.rstrip() for ln in f if re.search(r"\berror\b", ln, re.I)]


def empty_cells(rs):
    return sum(1 for r in rs for v in r.values() if v is None or v.strip() == "")


def main(argv):
    if len(argv) != 5:
        print(__doc__)
        return 2
    repo, d_on, d_loop, d_jf = argv[1:5]
    L20 = os.path.join(repo, "docs/preamp/data/2026-09-15/L20")
    vto = {r["variante"].lower(): r for r in rows(os.path.join(L20, "esplorazione/vto_dichiarati.csv"))}

    print("== A. logs: no line with Error ==")
    for d, n in ((d_on, "tb_idss_op_noise"), (d_loop, "tb_idss_loop"), (d_jf, "tb_idss_jfet")):
        e = errors_in(os.path.join(d, n + ".log"))
        check(f"A {n}.log has 0 Error lines", not e, f"{len(e)}: {e[:2]}" if e else "")

    print("== B. the JFET alone ==")
    jf = rows(os.path.join(d_jf, "tb_idss_jfet_tab.csv"))
    check("B 10 rows, no empty cell", len(jf) == 10 and empty_cells(jf) == 0,
          f"{len(jf)} rows, {empty_cells(jf)} empty")
    xcols = ("idss_x_a", "gfs_x_s", "vgsoff_x_v", "vgs500_x_v")
    check("B LSK489X never moves", len({tuple(r[c] for c in xcols) for r in jf}) == 1)
    a25 = next(r for r in jf if r["var"] == "a_come_e" and r["temp_c"] == "25")
    check("B LSK489A as published = L7",
          close(num(a25["idss_a_a"]), 2.59283e-3, 0, 1e-8)
          and close(num(a25["vgsoff_a_v"]), -1.124355, 0, 1e-5)
          and close(num(a25["vgs500_a_v"]), -0.650211, 0, 2e-6),
          f"{a25['idss_a_a']} A, {a25['vgsoff_a_v']} V, {a25['vgs500_a_v']} V")
    bad = []
    for r in jf:
        ref = vto[r["var"]]
        col = "idss_25c_a" if r["temp_c"] == "25" else "idss_27c_a"
        if not close(num(r["idss_a_a"]), num(ref[col]), 1e-5):
            bad.append(f"{r['var']} {r['temp_c']}C {r['idss_a_a']} vs {ref[col]}")
    check("B I_DSS of every variant = vto_dichiarati.csv", not bad, "; ".join(bad))

    print("== C. the block: operating point ==")
    op = {r["var"]: r for r in rows(os.path.join(d_on, "tb_idss_op_noise_op.csv"))}
    check("C 8 rows, no empty cell", len(op) == 8 and empty_cells(op.values()) == 0,
          f"{len(op)} rows, {empty_cells(op.values())} empty")
    x27 = num(next(r for r in jf if r["temp_c"] == "27")["idss_x_a"])
    probe_ref = {"a_come_e": vto["a_come_e"]["idss_27c_a"], "a_come_e_kf0": vto["a_come_e"]["idss_27c_a"],
                 "a_ripristinato": vto["a_come_e"]["idss_27c_a"], "a_tip": vto["a_tip"]["idss_27c_a"],
                 "b_min": vto["b_min"]["idss_27c_a"], "b_tip": vto["b_tip"]["idss_27c_a"],
                 "b_max": vto["b_max"]["idss_27c_a"], "xa": x27}
    bad = [f"{k}: probe {op[k]['idss_probe_27c_a']} vs {v}" for k, v in probe_ref.items()
           if k in op and not close(num(op[k]["idss_probe_27c_a"]), num(v), 1e-5)]
    check("C probe I_DSS (27 C) = the declared variant, in every row", not bad, "; ".join(bad))
    same = [c for c in op["a_come_e"] if op["a_come_e"][c] != op["a_ripristinato"][c] and c != "var"]
    check("C a_ripristinato = a_come_e in every cell (altermods undone)", not same, str(same))
    diff_kf = [c for c in op["a_come_e"] if c not in ("var", "kf") and op["a_come_e"][c] != op["a_come_e_kf0"][c]]
    check("C kf does not touch the operating point", not diff_kf, str(diff_kf))

    ref_op = log_values(os.path.join(repo, "docs/preamp/data/2026-09-14/L27/dopo/tb_op/tb_op.log"))
    xa_op = log_values(os.path.join(d_on, "tb_idss_op_noise.log"),
                       "=== XA: THE PRINTS OF tb_op.cir ===", "=== XA: END ===")
    # tb_op.cir drives IN directly; this deck through RSRC = 430 ohm. The gate
    # current of JQ110A (~9.7 pA, reverse) drops ~4.2 nV on it, so IN and G1 sit
    # higher by exactly that. The first version of this check compared them
    # with 1 nV of tolerance and FAILED on those two nodes only: the deck comment
    # had estimated the shift at "~4 pV", 1000 times too small. Now the shift is
    # PREDICTED (I_G * 430) and subtracted, not tolerated.
    missing = sorted(set(ref_op) ^ set(xa_op))
    shift = xa_op.get("v(in)", float("nan"))
    ig = abs(num(op["xa"]["ig_a"])) if "xa" in op else float("nan")
    check("C xa: v(IN) = I_G(JQ110A) * 430 ohm, the only expected difference from tb_op",
          close(shift, ig * 430, 1e-3), f"v(in) {shift:.6g} V, I_G*430 {ig*430:.6g} V")
    for k in set(ref_op) & set(xa_op):
        a, b = xa_op[k], ref_op[k]
        if k in ("v(in)", "v(g1)"):
            a -= shift
            ok = close(a, b, 0, 1e-13)
        else:
            ok = close(a, b, 1e-6, 1e-9)
        if not ok:
            missing.append(f"{k} {a:g} vs {b:g}")
    check(f"C xa prints the {len(ref_op)} values of L27 tb_op (rel 1e-6; IN, G1 less the shift)",
          len(ref_op) >= 81 and not missing, "; ".join(missing[:6]))

    print("== D. the block: noise ==")
    nz = rows(os.path.join(d_on, "tb_idss_op_noise_rumore.csv"))
    check("D 40 rows, no empty cell", len(nz) == 40 and empty_cells(nz) == 0,
          f"{len(nz)} rows, {empty_cells(nz)} empty")
    N = {(r["var"], r["cfg"]): num(r["onoise_total_v"]) for r in nz}
    cfgs = ["a_0db_1r", "b_0db_430r", "c_0db_2500r", "d_10db_2500r", "e_3db_2500r"]
    ref_n = []
    with open(os.path.join(repo, "docs/preamp/data/2026-09-14/L27/dopo/tb_noise_breakdown/tb_noise_breakdown.log")) as f:
        for ln in f:
            m = re.match(r"^onoise_total\s*=\s*(\S+)", ln)
            if m:
                ref_n.append(float(m.group(1)))
    bad = [f"{c} {N.get(('xa', c))} vs {r}" for c, r in zip(cfgs, ref_n)
           if ("xa", c) not in N or not close(N[("xa", c)], r, 1e-5)]
    check("D xa = the five totals of L27 tb_noise_breakdown", len(ref_n) == 5 and not bad, "; ".join(bad))
    bad = [c for c in cfgs if N.get(("a_ripristinato", c)) != N.get(("a_come_e", c))]
    check("D a_ripristinato = a_come_e", not bad, str(bad))

    def spectrum(var):
        p = os.path.join(d_on, f"tb_idss_op_noise_d_{var}.csv")
        with open(p) as f:
            rs = list(csv.reader(f))[1:]
        return [(float(r[0]), float(r[1])) for r in rs]
    s_kf, s_k0, s_xa = spectrum("a_come_e"), spectrum("a_come_e_kf0"), spectrum("xa")
    r20 = s_kf[0][1] / s_k0[0][1]
    check("D the JFET's 1/f is simulated: kf column above kf=0 at 20 Hz",
          len(s_kf) == 301 and r20 > 1.0001, f"ratio at {s_kf[0][0]:g} Hz = {r20:.6f}")

    print("== E. the loop ==")
    lp = rows(os.path.join(d_loop, "tb_idss_loop_margini.csv"))
    check("E 550 rows, no empty cell", len(lp) == 550 and empty_cells(lp) == 0,
          f"{len(lp)} rows, {empty_cells(lp)} empty")
    tdb = [num(r["tdb_10hz"]) for r in lp]
    check("E |T| at 10 Hz within 71.5-72.6 dB on every row (#24)",
          all(71.5 <= t <= 72.6 for t in tdb), f"{min(tdb):.4f}..{max(tdb):.4f}")
    l16 = {(r["rsrc"], r["cprobe"], r["rload"]): r for r in
           rows(os.path.join(repo, "docs/preamp/data/2026-09-14/L16/dopo/tb_loop/tb_loop_margini.csv"))
           if r["mode"] == "0db" and r["pos"] == "1"}
    bad = []
    for r in lp:
        if r["var"] != "xa":
            continue
        ref = l16.get((r["rsrc"], r["cprobe"], r["rload"]))
        if ref is None or not close(num(r["pm_deg"]), num(ref["pm_deg"]), 0, 5e-4) \
                or not close(num(r["fcross_hz"]), num(ref["fcross_hz"]), 1e-5):
            bad.append(f"{r['rsrc']}/{r['cprobe']}/{r['rload']}: {r['pm_deg']} vs {ref and ref['pm_deg']}")
    nxa = sum(1 for r in lp if r["var"] == "xa")
    check("E xa = the 110 cells of L16 tb_loop (0db, jack)", nxa == 110 and not bad, "; ".join(bad[:4]))

    print()
    print("== NUMBERS ==")
    order = ["xa", "a_come_e", "a_tip", "b_min", "b_tip", "b_max"]
    print("-- the JFET alone (V_DG = 15 V) --")
    print("   var        vto      T   I_DSS mA   Gfs mS   V_GS(off) V   V_GS@500uA V")
    x = jf[0]
    for tc in ("25", "27"):
        xr = next(r for r in jf if r["temp_c"] == tc)
        print(f"   LSK489X  -1.500   {tc}  {num(xr['idss_x_a'])*1e3:8.5f}  {num(xr['gfs_x_s'])*1e3:7.4f}"
              f"  {num(xr['vgsoff_x_v']):10.5f}  {num(xr['vgs500_x_v']):10.5f}")
    for r in jf:
        print(f"   {r['var']:<8} {r['vto_v']:>6}   {r['temp_c']}  {num(r['idss_a_a'])*1e3:8.5f}"
              f"  {num(r['gfs_a_s'])*1e3:7.4f}  {num(r['vgsoff_a_v']):10.5f}  {num(r['vgs500_a_v']):10.5f}")

    print("-- operating point at 0 dB, 27 C --")
    cols = [("id_a", 1e3, "I_D A mA"), ("id_b", 1e3, "I_D B mA"), ("vgs_a", 1, "V_GS A"),
            ("gm_a", 1e3, "gm A mS"), ("vds_a", 1, "V_DS A"), ("ic_q106", 1e3, "tail mA"),
            ("vce_q106", 1, "Vce Q106"), ("ic_q117", 1e3, "casc mA"), ("v_ncasc", 1, "NCASC V"),
            ("ic_q122", 1e3, "VAS mA"), ("ic_q132", 1e3, "out mA"), ("v_src", 1, "SRC V"),
            ("v_out", 1e3, "OUT mV"), ("ig_a", 1e12, "I_G pA")]
    print("   " + " ".join(f"{h:>10}" for _, _, h in cols))
    for v in order + ["a_come_e_kf0", "a_ripristinato"]:
        print(f"   {v:<14}" + " ".join(f"{num(op[v][c])*k:10.5f}" for c, k, _ in cols))
    base = op["a_come_e"]
    print("   spread over a_come_e..b_max (max - min):")
    for c, k, h in cols:
        vals = [num(op[v][c]) * k for v in ("a_come_e", "a_tip", "b_min", "b_tip", "b_max")]
        vb = [num(op[v][c]) * k for v in ("b_min", "b_tip", "b_max")]
        print(f"     {h:<10} all {max(vals)-min(vals):11.6f}   B only {max(vb)-min(vb):11.6f}")

    print("-- junction capacitances at the operating point, FROM THE MODEL FORMULA --")
    print("   ngspice JFET level 1: C(V) = C0 / sqrt(1 - V/PB) (mj is ignored), V < FC*PB")
    for v in order:
        c0gs, c0gd = (2.9e-12, 1.1e-12) if v == "xa" else (2.92e-12, 3.19e-12)
        vgs = num(op[v]["vgs_a"])
        vgd = vgs - num(op[v]["vds_a"])
        cgs = c0gs / math.sqrt(1 - vgs / 0.8)
        cgd = c0gd / math.sqrt(1 - vgd / 0.8)
        print(f"   {v:<9} Vgs {vgs:8.4f}  Vgd {vgd:8.4f}  Cgs {cgs*1e12:6.3f} pF  Cgd {cgd*1e12:6.3f} pF")

    print("-- common-mode range: VSRC -3.82..+3.82 V at 0 dB --")
    print("   margin_sat = (V_D - V_G) - |V_P(27 C)|, terminal voltages; >0 = saturation")
    vp27 = {r["var"]: abs(num(r["vgsoff_a_v"])) for r in jf if r["temp_c"] == "27"}
    vp27["xa"] = abs(num(next(r for r in jf if r["temp_c"] == "27")["vgsoff_x_v"]))
    for v in order:
        p = os.path.join(d_on, f"tb_idss_op_noise_cm_{v}.csv")
        with open(p) as f:
            rs = [list(map(float, r)) for r in list(csv.reader(f))[1:]]
        ok = len(rs) == 383
        ma = min((r[1] - r[3] - vp27[v], r[0]) for r in rs)
        mb = min((r[5] - r[7] - vp27[v], r[0]) for r in rs)
        vc = min((r[9] - r[11], r[0]) for r in rs)
        err = max(abs(r[13] - r[0]) for r in rs)
        check(f"G {v}: 383 points, both halves saturated, Q106 Vce > 1 V",
              ok and ma[0] > 0 and mb[0] > 0 and vc[0] > 1.0,
              f"sat A min {ma[0]:.3f} V at {ma[1]:+.2f}, B {mb[0]:.3f} V at {mb[1]:+.2f}, "
              f"Vce Q106 min {vc[0]:.3f} V at {vc[1]:+.2f}, max |OUT-VSRC| {err*1e3:.2f} mV")

    print("-- noise 20 Hz - 20 kHz, onoise_total uV RMS --")
    print("   " + " ".join(f"{c:>13}" for c in cfgs))
    for v in order + ["a_come_e_kf0"]:
        print(f"   {v:<14}" + " ".join(f"{N[(v, c)]*1e6:13.5f}" for c in cfgs))
    worst = max(N.values())
    budget = math.sqrt(10.0 ** 2 - 1.0 ** 2)
    check("E5 every variant, every configuration <= sqrt(10^2 - 1^2) uV (ADR-020 quota)",
          worst * 1e6 <= budget, f"max {worst*1e6:.5f} uV against {budget:.4f}")
    d = "d_10db_2500r"
    flick = math.sqrt(max(N[("a_come_e", d)] ** 2 - N[("a_come_e_kf0", d)] ** 2, 0))
    print(f"   D: JFET 1/f contribution sqrt(kf^2 - kf0^2) = {flick*1e6:.4f} uV")
    print(f"   D: a_come_e - xa = {(N[('a_come_e', d)] - N[('xa', d)])*1e6:+.5f} uV; "
          f"b_max - a_come_e = {(N[('b_max', d)] - N[('a_come_e', d)])*1e6:+.5f} uV")
    for f0 in (20, 100, 1000, 20000):
        i = min(range(len(s_kf)), key=lambda k: abs(s_kf[k][0] - f0))
        print(f"   D spectrum at {s_kf[i][0]:8.1f} Hz: kf {s_kf[i][1]*1e9:8.4f}  kf0 {s_k0[i][1]*1e9:8.4f}"
              f"  xa {s_xa[i][1]*1e9:8.4f} nV/sqrt(Hz)")

    print("-- loop, block B 0 dB, probe at the jack --")
    by = {}
    for r in lp:
        by.setdefault(r["var"], []).append(r)
    mins = {}
    for v in ("xa", "a_come_e", "b_min", "b_tip", "b_max"):
        m = min(by[v], key=lambda r: num(r["pm_deg"]))
        mins[v] = num(m["pm_deg"])
        for rl in ("100k", "10k"):
            mr = min((r for r in by[v] if r["rload"] == rl), key=lambda r: num(r["pm_deg"]))
            print(f"   {v:<9} load {rl:>4}: min {num(mr['pm_deg']):8.4f} deg at rsrc {mr['rsrc']}, "
                  f"{mr['cprobe']}, fcross {num(mr['fcross_hz'])/1e3:7.1f} kHz")
    cells = {}
    for r in lp:
        cells.setdefault((r["rsrc"], r["cprobe"], r["rload"]), {})[r["var"]] = num(r["pm_deg"])
    disp_b = max(max(c[v] for v in ("b_min", "b_tip", "b_max")) - min(c[v] for v in ("b_min", "b_tip", "b_max"))
                 for c in cells.values())
    disp_all = max(max(c[v] for v in ("a_come_e", "b_min", "b_tip", "b_max"))
                   - min(c[v] for v in ("a_come_e", "b_min", "b_tip", "b_max")) for c in cells.values())
    shift = [c["a_come_e"] - c["xa"] for c in cells.values()]
    print(f"   largest spread over the B grade in one cell: {disp_b:.4f} deg; "
          f"with a_come_e too: {disp_all:.4f} deg")
    print(f"   model change xa -> a_come_e, per cell: {min(shift):+.4f} .. {max(shift):+.4f} deg; "
          f"minimum {mins['xa']:.4f} -> {mins['a_come_e']:.4f}")
    extend = disp_b > 1.63 or min(mins.values()) < 60.0
    print(f"   RULE (written before the data): extend V1 to the fixed-output buffer and block A if "
          f"B spread > 1.63 deg or any minimum < 60 deg -> {'EXTEND' if extend else 'not needed'}")
    check("V1 every variant >= 60 deg on every cell", min(mins.values()) >= 60.0,
          f"lowest {min(mins.values()):.4f} deg")

    print()
    print(f"== {len(FAILS)} FAILED ==" if FAILS else "== every control passed ==")
    for f in FAILS:
        print(f"   - {f}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
