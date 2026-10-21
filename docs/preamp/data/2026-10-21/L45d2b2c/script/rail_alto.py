#!/usr/bin/env python3
"""L45d2b2c: the audio rails in ADR-078's rows (psu/modi.py, RIGHE_078) - how high they go, at
the three mains levels, for the block's parts.

Solo stdlib. /usr/bin/python3 -I rail_alto.py <seq_dir> <out.csv> <caso> [<caso> ...]
            (a <caso> starting with @ is a file with one case per line)

Per case, the fixed-point pass (<seq_dir>/<caso>/punto_fisso.txt): the vector names from the
deck's wrdata line, the values from its _out.txt (the decks set wr_singlescale and wr_vecnames:
one time column, and the header must name the deck's vectors in the same order - asserted). TE = 2 s (the fault's instant of every f_* case, corri_seq.sh).
  vp_prima / vm_prima   the mean of the 100 ms before TE
  vp_max / vm_min       the extreme after TE (the instantaneous one, ripple included)
  vp_fine / vm_fine     the mean of the last 100 ms; *_pp_mV the ripple there, peak to peak
  pin_p_max / pin_m_min the regulators' OUT pins after TE (v(vplus_reg) / v(vminus_reg), when
                        the deck writes them); raw_p_max / raw_m_min the reservoirs
  jack_fine             the jack relays at the end: "chiuso" when VRELAY - MUTE_CMD > 6 V (half the
                        coil's 12 V, analizza_seq.py's rule)
Checked on L45c1's decks (controllo_l45c1.sh): vp_max 20.3253 V, vm_min -20.2980 V.
"""
import csv
import os
import sys

TE = 2.0


def leggi(cartella, caso):
    g = open(os.path.join(cartella, caso, "punto_fisso.txt")).read().split()[0]
    cir = os.path.join(cartella, caso, "tb_psu_seq_%s_g%s.cir" % (caso, g))
    nomi = None
    for r in open(cir):
        p = r.split()
        if p and p[0] == "wrdata":
            nomi = p[2:]
    assert nomi, cir
    out = os.path.join(cartella, caso, "tb_psu_seq_%s_g%s_out.txt" % (caso, g))
    t, col, testa = [], dict((n, []) for n in nomi), None
    for r in open(out):
        p = r.split()
        if not p:
            continue
        if not p[0][0] in "0123456789-+.":
            # wr_singlescale + wr_vecnames: one time column, the names on the first line
            testa = p
            assert testa[1:] == nomi, (out, testa[:3], nomi[:2])
            continue
        assert testa and len(p) == 1 + len(nomi), (out, len(p), len(nomi))
        t.append(float(p[0]))
        for k, n in enumerate(nomi):
            col[n].append(float(p[k + 1]))
    return g, t, col


def media(t, v, a, b):
    x = [y for s, y in zip(t, v) if a <= s <= b]
    assert x, (a, b)
    return sum(x) / len(x), max(x) - min(x)


def caso_righe(cartella, caso):
    g, t, c = leggi(cartella, caso)
    tf = t[-1]
    dopo = [i for i, s in enumerate(t) if s >= TE]
    vp, vm = c["v(vplus)"], c["v(vminus)"]
    r = {"caso": caso, "giro": g, "t_fine_s": "%.4f" % tf}
    r["vp_prima"] = "%.4f" % media(t, vp, TE - 0.1, TE)[0]
    r["vm_prima"] = "%.4f" % media(t, vm, TE - 0.1, TE)[0]
    r["vp_max"] = "%.4f" % max(vp[i] for i in dopo)
    r["vm_min"] = "%.4f" % min(vm[i] for i in dopo)
    m, pp = media(t, vp, tf - 0.1, tf)
    r["vp_fine"], r["vp_pp_mV"] = "%.4f" % m, "%.1f" % (pp * 1e3)
    m, pp = media(t, vm, tf - 0.1, tf)
    r["vm_fine"], r["vm_pp_mV"] = "%.4f" % m, "%.1f" % (pp * 1e3)
    for k, n, f in (("pin_p_max", "v(vplus_reg)", max), ("pin_m_min", "v(vminus_reg)", min),
                    ("raw_p_max", "v(raw_p)", max), ("raw_m_min", "v(raw_m)", min)):
        r[k] = "%.4f" % f(c[n][i] for i in dopo) if n in c else ""
    j = c["v(vrelay)"][-1] - c["v(mute_cmd)"][-1]
    r["jack_fine"] = "chiuso" if j > 6 else "aperto"
    return r


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    casi = []
    for a in sys.argv[3:]:
        casi += [x.strip() for x in open(a[1:]) if x.strip()] if a.startswith("@") else [a]
    righe = [caso_righe(cartella, c) for c in casi]
    with open(uscita, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
        w.writeheader()
        w.writerows(righe)
    for r in righe:
        print("%-28s vp_max %8s vm_min %9s  fine %8s / %9s  jack %s" % (
            r["caso"], r["vp_max"], r["vm_min"], r["vp_fine"], r["vm_fine"], r["jack_fine"]))


if __name__ == "__main__":
    main()
