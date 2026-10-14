#!/usr/bin/env python3
"""L45c1: the supply side of every case, from the last pass of its fixed point (seq/<caso>/).
Solo stdlib.

    analizza_psu.py <seq> <out.csv> <caso> [<caso> ...]

Refuses a case without punto_fisso.txt or whose log has a word of limitations #33 / #35
(estrai_ponte.py's list). Per case, times in ms from TE = 2 s (the fault with the event mus,
the event otherwise):
    vp_prima, vm_prima      the rails' mean over the 100 ms before TE
    vp_min/max, vm_min/max  the rails from TE to the end (vm_min = the most negative)
    t_fuori_ms              first instant a rail is inside |13,5 V| (P9 (b): the supervisor's line)
    t_mute_g_ms             MUTE_G below 1 V (the supervisor, the mains detector or the firmware)
    t_10_6_ms               first instant a rail is inside |10,6 V| (L41c's criterion s)
    sorvegliante_1ms        P9 (b): MUTE_G low within 1 ms of t_fuori
    jack_prima              P9 (b): the jack open (latest corner) before t_10_6
    t_jack_ms               VRELAY - MUTE_CMD < 1,2 V, + 3 ms: the jack contacts open, the latest
                            (estrai_ponte.py's rule); empty = never in the run
    t_guadagno_ms           the gain relays' contact, the earliest (estrai_ponte.py's rule)
    jack_prima              si / no / "-": the jack opened before a rail left |13,5 V|
    sopra_15_5              a rail beyond |15,5 V| at any instant after TE (over-voltage)
    vp_fine, vm_fine        the rails at the end
    ondulazione_vp/vm_mV    peak-to-peak over the last 200 ms
    out_meno_in_max         D510 / D511: max of V(vplus) - V(raw_p) and of V(raw_m) - V(vminus)
                            after TE (the fault cases only: the raw rails are their probes)
"""
import csv
import os
import sys

TE = 2.0
V_REG = 13.5
# P9 (b), "the outputs disconnect before the circuit leaves regulation": L41c's criterion s
# (L47c2b2's s41), the jack open before a rail reaches 10,6 V
V_FUORI = 10.6
V_RIL, T_RIL, V_OP = 1.2, 3e-3, 9.6
MALE = ("error", "singular", "no such", "non-increasing", "transient op", "timestep too small",
        "aborted", "too many args")


def leggi(path):
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


def primo(t, cond, dopo=TE):
    for k in range(len(t)):
        if t[k] >= dopo and cond(k):
            return t[k]
    return None


def ms(x):
    return "" if x is None else "%.2f" % ((x - TE) * 1e3)


def caso(seq, nome):
    d = os.path.join(seq, nome)
    pf = os.path.join(d, "punto_fisso.txt")
    if not os.path.exists(pf):
        raise SystemExit("%s: nessun punto fisso - rifiutato" % nome)
    g = int(open(pf).read())
    log = open(os.path.join(d, "tb_psu_seq_%s_g%d.log" % (nome, g))).read().lower()
    bad = [w for w in MALE if w in log]
    if bad:
        raise SystemExit("%s giro %d: il log ha %s - rifiutato" % (nome, g, bad))
    S = leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    t, vp, vm = S["time"], S["v(vplus)"], S["v(vminus)"]
    vr, mc, pc, mg = S["v(vrelay)"], S["v(mute_cmd)"], S["v(permit_cmd)"], S["v(mute_g)"]
    k0 = next(k for k in range(len(t)) if t[k] >= TE)
    pre = [k for k in range(len(t)) if TE - 0.1 <= t[k] < TE]
    dopo = range(k0, len(t))
    t_fuori = primo(t, lambda k: vp[k] < V_REG or vm[k] > -V_REG)
    t_106 = primo(t, lambda k: vp[k] < V_FUORI or vm[k] > -V_FUORI)
    t_jack = primo(t, lambda k: vr[k] - mc[k] < V_RIL)
    t_jack = None if t_jack is None else t_jack + T_RIL
    t_gain = primo(t, lambda k: vr[k] - pc[k] < V_OP or vr[k] < V_OP)
    t_mg = primo(t, lambda k: mg[k] < 1.0)
    coda = [k for k in range(len(t)) if t[k] >= t[-1] - 0.2]
    r = {"caso": nome, "giro": g,
         "ripiego": "si" if any(x.startswith("ripiego_g%d" % g) for x in os.listdir(d)) else "no",
         "vp_prima": sum(vp[k] for k in pre) / len(pre), "vm_prima": sum(vm[k] for k in pre) / len(pre),
         "vp_min": min(vp[k] for k in dopo), "vp_max": max(vp[k] for k in dopo),
         "vm_min": min(vm[k] for k in dopo), "vm_max": max(vm[k] for k in dopo),
         "t_fuori_ms": ms(t_fuori), "t_mute_g_ms": ms(t_mg), "t_jack_ms": ms(t_jack),
         "t_guadagno_ms": ms(t_gain),
         "t_10_6_ms": ms(t_106),
         "sorvegliante_1ms": "-" if t_fuori is None else
         ("si" if t_mg is not None and t_mg <= t_fuori + 1e-3 else "no"),
         "jack_prima": "-" if t_106 is None else ("si" if t_jack is not None and t_jack <= t_106 else "no"),
         "sopra_15_5": "si" if max(vp[k] for k in dopo) > 15.5 or min(vm[k] for k in dopo) < -15.5 else "no",
         "vp_fine": vp[-1], "vm_fine": vm[-1],
         "ondulazione_vp_mV": (max(vp[k] for k in coda) - min(vp[k] for k in coda)) * 1e3,
         "ondulazione_vm_mV": (max(vm[k] for k in coda) - min(vm[k] for k in coda)) * 1e3,
         "t_fine_ms": (t[-1] - TE) * 1e3}
    if "v(raw_p)" in S:
        rp, rm = S["v(raw_p)"], S["v(raw_m)"]
        r["out_meno_in_max_p"] = max(vp[k] - rp[k] for k in dopo)
        r["out_meno_in_max_m"] = max(rm[k] - vm[k] for k in dopo)
        r["raw_p_min"] = min(rp[k] for k in dopo)
        r["raw_m_max"] = max(rm[k] for k in dopo)
    for n in ("v(vplus_psu)", "v(vminus_psu)"):
        if n in S:
            r[n[2:-1] + "_min"] = min(S[n][k] for k in dopo)
            r[n[2:-1] + "_max"] = max(S[n][k] for k in dopo)
    return r


CAMPI = ["caso", "giro", "ripiego", "vp_prima", "vm_prima", "vp_min", "vp_max", "vm_min", "vm_max",
         "t_fuori_ms", "t_mute_g_ms", "t_jack_ms", "t_guadagno_ms", "t_10_6_ms", "sorvegliante_1ms",
         "jack_prima", "sopra_15_5",
         "vp_fine", "vm_fine", "ondulazione_vp_mV", "ondulazione_vm_mV", "t_fine_ms",
         "out_meno_in_max_p", "out_meno_in_max_m", "raw_p_min", "raw_m_max",
         "vplus_psu_min", "vplus_psu_max", "vminus_psu_min", "vminus_psu_max"]

if __name__ == "__main__":
    seq, out = sys.argv[1], sys.argv[2]
    nomi = sys.argv[3:]
    if len(nomi) == 1 and nomi[0].startswith("@"):      # @file: one case per line
        nomi = [r.strip() for r in open(nomi[0][1:]) if r.strip()]
    righe = [caso(seq, n) for n in nomi]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI)
        w.writeheader()
        for r in righe:
            w.writerow({a: ("%.4f" % b if isinstance(b, float) else b) for a, b in r.items()})
    print("scritto %s: %d casi" % (out, len(righe)))
