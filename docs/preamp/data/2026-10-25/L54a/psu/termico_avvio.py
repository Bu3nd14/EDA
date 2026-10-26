#!/usr/bin/env python3
"""L45d2b2a: how hot the two regulators get at a power-up with the soft-start, against how hot they
run at regime. Stdlib. A question of the user's («accorcia la vita o mette a rischio rottura il
regolatore?»), asked on the option + 4.7 uF / - 470 nF.

Uso: termico_avvio.py <out.csv> SEQDIR...

The datasheets give no transient thermal impedance (SBVS204G 5.4, SBVS169D: steady figures only),
so this is an ESTIMATE, every figure declared:
  - power: (IN - OUT) x I_IN of each regulator, from the deck at the fixed point (misura_ss.py's
    probes), from t0 (MAINS_REQ) to the end;
  - a two-node Cauer network: junction + package Cj -> R_JCbot -> the board under the pad Cb ->
    R_rest = R_thJA - R_JCbot -> air. TPS7A4701 (RGW): R_thJA 32.5, R_JC(bot) 1.7 C/W (SBVS204G
    table 5.4). TPS7A3301 (RGW): the same package, the same figures (ASSUMED: its table is read
    as the same order; only the + regulator matters here);
  - Cj = 0.04 J/K: the package itself, 5 x 5 x 0.9 mm at ~2 g/cm3 and ~0.8 J/(g K) (ASSUMED);
  - Cb = 1 J/K (and 0.3 J/K, the pessimistic case): the copper and FR4 that the heat reaches under
    the pad in a second, ~3 cm2 of 1.6 mm board (ASSUMED);
  - the regulator starts at the air's temperature (a power-up from standby: the toroid off);
  - R_thJA is the JEDEC board's: the real board is L49b's, not measured.
Printed per run and per regulator: the peak rise over the air during the run, and the steady rise
at the end's power (P_end x R_thJA), the temperature it runs at for hours.
"""
import csv
import os
import sys

RJA, RJC = 32.5, 1.7
CJ = 0.04


def leggi(path):
    f = open(path)
    nomi = f.readline().split()
    col = {n: [] for n in nomi}
    for r in f:
        p = r.split()
        if len(p) != len(nomi):
            continue
        try:
            v = [float(x) for x in p]
        except ValueError:
            continue
        for n, x in zip(nomi, v):
            col[n].append(x)
    return col


def rete(t, p, cb):
    """Explicit Euler on the 100 us grid, substepped; returns the peak junction rise."""
    tj = tb = 0.0
    picco = 0.0
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]
        n = max(1, int(dt / 2e-5))
        h = dt / n
        for _ in range(n):
            q = (tj - tb) / RJC
            tj += h * (p[k] - q) / CJ
            tb += h * (q - tb / (RJA - RJC)) / cb
        picco = max(picco, tj)
    return picco


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    righe = []
    for d in dirs:
        caso = os.path.basename(d.rstrip("/"))
        g = open(os.path.join(d, "punto_fisso.txt")).read().strip()
        c = leggi(os.path.join(d, "tb_psu_seq_%s_g%s_out.txt" % (caso, g)))
        t = c["time"]
        i0 = next(k for k in range(len(t)) if c["v(mains_req)"][k] > 2.5)
        # the IN pins: behind R550 / R551 (ADR-092) when the netlist has them
        vp_in = "v(raw_pr)" if "v(raw_pr)" in c else "v(raw_p)"
        vm_in = "v(raw_mr)" if "v(raw_mr)" in c else "v(raw_m)"
        for nome, vi, vo, ii in (("U501", vp_in, "v(vplus)", "i(v.xu501.vsns)"),
                                 ("U502", vm_in, "v(vminus)", "i(v.xu502.vsns)")):
            tt = t[i0:]
            p = [abs(c[vi][k] - c[vo][k]) * abs(c[ii][k]) for k in range(i0, len(t))]
            pf = sum(p[-1000:]) / 1000.0
            r = {"corsa": os.path.relpath(d, os.path.dirname(os.path.dirname(d.rstrip("/")))),
                 "regolatore": nome, "p_picco_W": "%.2f" % max(p), "p_regime_W": "%.2f" % pf,
                 "dT_avvio_Cb1_K": "%.1f" % rete(tt, p, 1.0),
                 "dT_avvio_Cb0.3_K": "%.1f" % rete(tt, p, 0.3),
                 "dT_regime_K": "%.1f" % (pf * RJA)}
            righe.append(r)
            print(" ".join("%s=%s" % kv for kv in r.items()))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)


if __name__ == "__main__":
    main()
