#!/usr/bin/env python3
"""L45d2b2a: the two rails at a power-up with the soft-start (NC-063). Stdlib.

Uso: misura_ss.py <out.csv> SEQDIR...      (SEQDIR = seq/<etichetta>/<caso>, at its fixed point)

Per run, from the deck at the fixed point (punto_fisso.txt) and the core's CSV:
  - t0: MAINS_REQ above 2.5 V; every time below is from t0, in ms;
  - per rail, t_on: the regulator's IN past its UVLO (RAW_P > 2.67 V, RAW_M < -2 V);
    t_fw: the rail past the firmware's threshold (timer_spec.md 4.1: ADC_SUP_P > 2.55 V, i.e.
    VPLUS > 2.55 x 54.2 / 10 = 13.82 V; ADC_SUP_M < 1.20 V, read on v(adc_sup_m) itself);
    t_999: the rail at 99.9 % of its final value (the mean of the last 0.1 s);
    ss_ms: t_999 - t_on, against the datasheets' t_SS;
  - the gap between the two t_fw, and the - rail's slope between -3 and -12 V (V/s);
  - per regulator: the peak input current and the peak of (IN - OUT) x I_IN, and its energy
    from t0 to the end;
  - the core: ACCENSIONE, VRELAY_EN up, MUSICA or GUASTO (the states of core_g<n>.csv), and the
    jack relays energised (VRELAY - MUTE_CMD > 6 V), with both rails' values at that instant.
A run without its fixed point is refused.
"""
import csv
import os
import sys


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


def primo(t, v, cond, da):
    for i in range(len(t)):
        if t[i] >= da and cond(v[i]):
            return t[i]
    return None


def ms(x, t0):
    return "" if x is None else "%.1f" % ((x - t0) * 1e3)


def misura(d):
    caso = os.path.basename(d.rstrip("/"))
    pf = os.path.join(d, "punto_fisso.txt")
    if not os.path.exists(pf):
        raise SystemExit("RIFIUTATO: %s senza punto fisso" % d)
    g = open(pf).read().strip()
    c = leggi(os.path.join(d, "tb_psu_seq_%s_g%s_out.txt" % (caso, g)))
    t = c["time"]
    vp, vm = c["v(vplus)"], c["v(vminus)"]
    # the regulators' IN pins: behind R550 / R551 (ADR-092) when the netlist has them
    rp = c.get("v(raw_pr)", c["v(raw_p)"])
    rm = c.get("v(raw_mr)", c["v(raw_m)"])
    ip, im = c["i(v.xu501.vsns)"], c["i(v.xu502.vsns)"]
    t0 = primo(t, c["v(mains_req)"], lambda x: x > 2.5, 0.0)
    fine = t[-1]
    coda = [i for i in range(len(t)) if t[i] >= fine - 0.1]
    vp_f = sum(vp[i] for i in coda) / len(coda)
    vm_f = sum(vm[i] for i in coda) / len(coda)
    r = {"corsa": os.path.relpath(d, os.path.dirname(os.path.dirname(d.rstrip("/")))),
         "vplus_fine": "%.4f" % vp_f, "vminus_fine": "%.4f" % vm_f}
    on_p = primo(t, rp, lambda x: x > 2.67, t0)
    on_m = primo(t, rm, lambda x: x < -2.0, t0)
    fw_p = primo(t, vp, lambda x: x > 13.82, t0)
    fw_m = primo(t, c["v(adc_sup_m)"], lambda x: x < 1.20, t0)
    # 99.9 % only if the rail got there before the end (a 12 s ramp does not)
    ok_p = vp_f > 14.9
    ok_m = vm_f < -14.9
    p999 = primo(t, vp, lambda x: x > 0.999 * vp_f, t0) if ok_p else None
    m999 = primo(t, vm, lambda x: x < 0.999 * vm_f, t0) if ok_m else None
    r.update(on_p_ms=ms(on_p, t0), on_m_ms=ms(on_m, t0), fw_p_ms=ms(fw_p, t0), fw_m_ms=ms(fw_m, t0),
             p999_ms=ms(p999, t0), m999_ms=ms(m999, t0),
             ss_p_ms="" if p999 is None else "%.1f" % ((p999 - on_p) * 1e3),
             ss_m_ms="" if m999 is None else "%.1f" % ((m999 - on_m) * 1e3),
             scarto_fw_ms="" if None in (fw_p, fw_m) else "%.1f" % ((fw_m - fw_p) * 1e3))
    a = primo(t, vm, lambda x: x < -3.0, t0)
    b = primo(t, vm, lambda x: x < -12.0, t0)
    r["pendenza_m_V_s"] = "" if None in (a, b) else "%.3f" % (9.0 / (b - a))
    for nome, i_in, vin, vout in (("u501", ip, rp, vp), ("u502", im, rm, vm)):
        imax, pmax, e = 0.0, 0.0, 0.0
        for k in range(1, len(t)):
            if t[k] < t0:
                continue
            p = abs(vin[k] - vout[k]) * abs(i_in[k])
            imax, pmax = max(imax, abs(i_in[k])), max(pmax, p)
            e += p * (t[k] - t[k - 1])
        r["%s_imax_A" % nome] = "%.3f" % imax
        r["%s_pmax_W" % nome] = "%.2f" % pmax
        r["%s_energia_J" % nome] = "%.2f" % e
    stati = {}
    righe = [x.strip().split(",") for x in open(os.path.join(d, "core_g%s.csv" % g))][1:]
    prima_en = None
    for x in righe:
        stati.setdefault(x[5], float(x[0]))
        if x[2] == "1" and prima_en is None:
            prima_en = float(x[0])
    r["accensione_ms"] = ms(stati.get("ACCENSIONE"), t0)
    r["vrelay_en_ms"] = ms(prima_en, t0)
    r["musica_ms"] = ms(stati.get("MUSICA"), t0)
    r["guasto_ms"] = ms(stati.get("GUASTO"), t0)
    tj = None
    for k in range(len(t)):
        if t[k] > t0 and c["v(vrelay)"][k] - c["v(mute_cmd)"][k] > 6.0:
            tj = k
            break
    r["jack_ms"] = "" if tj is None else ms(t[tj], t0)
    r["vplus_al_jack"] = "" if tj is None else "%.3f" % vp[tj]
    r["vminus_al_jack"] = "" if tj is None else "%.3f" % vm[tj]
    return r


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    rs = [misura(d) for d in dirs]
    campi = list(rs[0].keys())
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        for r in rs:
            w.writerow(r)
    for r in rs:
        print(" ".join("%s=%s" % (k, r[k]) for k in campi))


if __name__ == "__main__":
    main()
