#!/usr/bin/env python3
"""L45d2b2b2: ADR-075's rows - the parts of the relay command, the reference, the mains detector and
the logic supply against their limits - from the last pass of each case's fixed point
(seq/<etichetta>/<caso>/). Solo stdlib.

    analizza_075.py <seq/etichetta> <out.csv> <caso> [<caso> ...]     (@file: one case per line)

The P9 (b) / Delta columns are NOT rewritten: they are analizza_074.py's (L45c1's analizza_psu.py,
the same rules) and L45c2's analizza_rele.py (anticipo_guadagno_ms > 0 = Delta lost), imported.

Per part, from TE (the fault) to the end, from the probes of genera_tb_psu.py (SONDE_I, i(vfc)):
    <p>_ipk_A        the largest current
    <p>_ppk_W        the largest instantaneous power
    <p>_p10_W        the largest mean power over any 10 ms window (the SOA's 10 ms curve)
    <p>_p100_W       the same over 100 ms
    <p>_e_J          the energy from TE to the end
    <p>_t50_ms       the time with the power above half its peak (how long the stress lasts)
    <p>_pfin_W       the mean power over the last 50 ms of the run (what remains: a steady state)
the parts (current, voltage):
    q501 / q502 / q503   2N7002: drain current x V(drain) - V(RLY_RET)
    q505                 AO3401A: the current out of its drain to VRELAY x V(VRELAY_REG) - V(VRELAY)
    d507 / d509          the clamp zeners IN FORWARD: current into the anode (VRELAY) x V(VRELAY) - V(clamp)
    u507                 LM4040: the shunt current x V(VREF) - V(RLY_RET)
    q504                 BC847: Ic x Vce + Ib x Vbe
    u503 / u504          the regulators: output current x (V(IN) - V(OUT))
    guasto               the fault's own current, i(vfc) (its power is not a part's)
and v5_max (the micro's supply, 6 V absolute maximum, DS40002205A), vref_max, vrelay_reg_min.
"""
import csv
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))


def carica(nome, path):
    s = importlib.util.spec_from_file_location(nome, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


A74 = carica("analizza_074_l45d2b2b2", os.path.join(QUI, "analizza_074.py"))
REL = carica("analizza_rele_l45c2", os.path.join(QUI, "..", "..", "..", "2026-10-14", "L45c2", "script",
                                                 "analizza_rele.py"))
A = A74.A
TE = A.TE

# (part, current column, sign, voltage: (+node, -node))
PARTI = [
    ("q501", "i(vsiq501_3)", 1, ("v(mute_cmd)", "v(rly_ret)")),
    ("q502", "i(vsiq502_3)", 1, ("v(permit_cmd)", "v(rly_ret)")),
    ("q503", "i(vsiq503_3)", 1, ("v(mains_coil)", "v(rly_ret)")),
    ("q505", "i(vsiq505_3)", -1, ("v(vrelay_reg)", "v(vrelay)")),
    ("d507", "i(vsid507_2)", 1, ("v(vrelay)", "v(clamp_mute)")),
    ("d509", "i(vsid509_2)", 1, ("v(vrelay)", "v(clamp_permit)")),
    ("u507", "i(vsiu507_1)", 1, ("v(vref)", "v(rly_ret)")),
    ("u503", "i(vsiu503_1)", -1, ("v(raw_v)", "v(vrelay_reg)")),
    ("u504", "i(vsiu504_3)", -1, ("v(vrelay_reg)", "v(v5)")),
]
MISURE = ("ipk_A", "ppk_W", "p10_W", "p100_W", "e_J", "t50_ms", "pfin_W")


def integra(t, y, k0, k1=None):
    k1 = len(t) if k1 is None else k1
    return sum(0.5 * (y[k] + y[k - 1]) * (t[k] - t[k - 1]) for k in range(k0 + 1, k1))


def media_max(t, p, k0, w):
    """The largest mean of p over a window w (s) starting at or after TE (the 100 us grid of
    linearize: the windows slide by one sample)."""
    cum = [0.0] * len(t)
    for k in range(1, len(t)):
        cum[k] = cum[k - 1] + 0.5 * (p[k] + p[k - 1]) * (t[k] - t[k - 1])
    best, j = 0.0, k0
    for i in range(k0, len(t)):
        while j < len(t) - 1 and t[j] - t[i] < w:
            j += 1
        if t[j] - t[i] < w * 0.999:
            break
        best = max(best, (cum[j] - cum[i]) / (t[j] - t[i]))
    return best


def misura(t, i, v, k0):
    p = [abs(a * b) for a, b in zip(i, v)]
    dopo = range(k0, len(t))
    ppk = max(p[k] for k in dopo)
    kf = next(k for k in range(len(t)) if t[k] >= t[-1] - 0.05)
    return {"ipk_A": max(abs(i[k]) for k in dopo), "ppk_W": ppk,
            "p10_W": media_max(t, p, k0, 0.010), "p100_W": media_max(t, p, k0, 0.100),
            "e_J": integra(t, p, k0),
            "t50_ms": 1e3 * sum(t[k] - t[k - 1] for k in range(k0 + 1, len(t))
                                if p[k] > 0.5 * ppk and p[k - 1] > 0.5 * ppk),
            "pfin_W": integra(t, p, kf) / (t[-1] - t[kf])}


def ultimo_giro(d, nome):
    """The last pass a run left (no fixed point): its log must still be clean."""
    gs = [int(f[len("core_g"):-4]) for f in os.listdir(d) if f.startswith("core_g") and f.endswith(".csv")]
    g = max(x for x in gs if os.path.exists(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, x))))
    log = open(os.path.join(d, "tb_psu_seq_%s_g%d.log" % (nome, g))).read().lower()
    if any(w in log for w in A.MALE):
        raise SystemExit("%s: il log dell'ultimo giro ha un errore - rifiutato" % nome)
    return g


def caso(seq, nome):
    d = os.path.join(seq, nome)
    if os.path.exists(os.path.join(d, "punto_fisso.txt")):
        r = A74.caso(seq, nome)
        rr = REL.caso(seq, nome)
        for k in ("vreg_min", "vrelay_min", "anticipo_guadagno_ms", "k501_fine"):
            r[k] = rr[k]
        g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    else:
        # L45d2b2b2: R503 shorted puts the logic at ~2.5 V and the firmware chatters (hundreds of
        # MUTE_G_IN substitutions a pass): there is no fixed point to reach. The parts' stress does
        # not depend on it (the LM4040 takes U504's limit whatever the micro does): the LAST pass,
        # declared in "giro"; the jack's columns stay empty
        g = ultimo_giro(d, nome)
        r = {"caso": nome, "giro": "g%d SENZA punto fisso" % g}
    S = A.leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    t = S["time"]
    k0 = next(k for k in range(len(t)) if t[k] >= TE)
    parti = list(PARTI)
    if "v(q503_rk)" in S:
        # --rk: Q503's drain is behind the resistor; the resistor is a part of its own
        parti = [p if p[0] != "q503" else ("q503", p[1], 1, ("v(q503_rk)", "v(rly_ret)")) for p in parti]
        parti.append(("rk", "i(vsiq503_3)", 1, ("v(mains_coil)", "v(q503_rk)")))
    if "v(mains_sink)" in S:
        # ADR-094 in the netlist: R552 (47 ohm) between the coil and Q503's drain, MAINS_SINK
        parti = [p if p[0] != "q503" else ("q503", p[1], 1, ("v(mains_sink)", "v(rly_ret)")) for p in parti]
        parti.append(("rk", "i(vsiq503_3)", 1, ("v(mains_coil)", "v(mains_sink)")))
    if "v(v5_pre)" in S:
        # ADR-094 in the netlist: U504 on V5_PRE, U512 from V5_PRE to V5
        parti = [p if p[0] != "u504" else ("u504", p[1], -1, ("v(vrelay_reg)", "v(v5_pre)")) for p in parti]
        parti.append(("u512", "i(vsiu512_3)", -1, ("v(v5_pre)", "v(v5)")))
    for nm, col, seg, (a, b) in parti:
        if col not in S:
            continue
        i = [seg * x for x in S[col]]
        v = [x - y for x, y in zip(S[a], S[b])]
        for m, x in misura(t, i, v, k0).items():
            r["%s_%s" % (nm, m)] = x
    # Q504: Ic x Vce + Ib x Vbe
    if "i(vsiq504_3)" in S:
        ic, ib = S["i(vsiq504_3)"], S["i(vsiq504_1)"]
        vce = [x - y for x, y in zip(S["v(md)"], S["v(rly_ret)"])]
        vbe = [x - y for x, y in zip(S["v(md_b)"], S["v(rly_ret)"])]
        p = [abs(a * b) + abs(c * e) for a, b, c, e in zip(ic, vce, ib, vbe)]
        x = misura(t, p, [1.0] * len(t), k0)
        x["ipk_A"] = max(abs(ic[k]) for k in range(k0, len(t)))
        x["ibpk_A"] = max(abs(ib[k]) for k in range(k0, len(t)))
        for m, y in x.items():
            r["q504_%s" % m] = y
    if "i(vfc)" in S:
        r["guasto_ipk_A"] = max(abs(S["i(vfc)"][k]) for k in range(k0, len(t)))
        kf = next(k for k in range(len(t)) if t[k] >= t[-1] - 0.05)
        r["guasto_ifin_A"] = integra(t, S["i(vfc)"], kf) / (t[-1] - t[kf])
    r["v5_max"] = max(S["v(v5)"][k] for k in range(k0, len(t)))
    r["v5_min"] = min(S["v(v5)"][k] for k in range(k0, len(t)))
    r["vref_max"] = max(S["v(vref)"][k] for k in range(k0, len(t)))
    return r


CAMPI = (A.CAMPI + ["vreg_min", "vrelay_min", "anticipo_guadagno_ms", "k501_fine"]
         + ["%s_%s" % (p[0], m) for p in PARTI + [("rk",), ("u512",)] for m in MISURE]
         + ["q504_%s" % m for m in MISURE + ("ibpk_A",)]
         + ["guasto_ipk_A", "guasto_ifin_A", "v5_max", "v5_min", "vref_max"])

if __name__ == "__main__":
    seq, out = sys.argv[1], sys.argv[2]
    nomi = sys.argv[3:]
    if len(nomi) == 1 and nomi[0].startswith("@"):
        nomi = [x.strip() for x in open(nomi[0][1:]) if x.strip()]
    righe = [caso(seq, n) for n in nomi]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI, extrasaction="ignore")
        w.writeheader()
        for x in righe:
            w.writerow({a: ("%.5g" % b if isinstance(b, float) else b) for a, b in x.items()})
    print("scritto %s: %d casi" % (out, len(righe)))
