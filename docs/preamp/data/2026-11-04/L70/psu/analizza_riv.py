#!/usr/bin/env python3
"""L45d2b1: i casi del rivelatore di continua sul banco dell'alimentatore (ADR-072). Stdlib.

Uso: analizza_riv.py SEQDIR OUT.csv CASO...

Per ogni caso legge l'ultimo giro (punto_fisso.txt) di seq/<caso>/: le sonde di SONDE
(genera_tb_psu.py) e il CSV del firmware. Tempi dall'evento TE = 2,0 s, in ms:
  t_dc        DC_FLT sotto 2,5 V (la linea tirata)
  t_mute      MUTE_CMD rilasciato: la bobina dei jack senza corrente, V(vrelay, mute_cmd) < 1 V
  t_vrelay    VRELAY sotto 6 V (meta' della tensione: le bobine non tengono, G6K must-release 10 %)
  t_k501      il contatto di K501 aperto (k501_f sotto 0,5, il modello del banco)
  t_vp_135    VPLUS sotto 13,5 V (il sorvegliante), t_vp_5 / t_vp_1 sotto 5 / 1 V
  t_vm_1      |VMINUS| sotto 1 V
  t_rilascio  DC_FLT di nuovo sopra 2,5 V (il rivelatore senza alimentazione)
  guasto      il firmware in GUASTO (istante), e se esce da GUASTO prima della fine
  e_r144_J    con un carico su VPLUS (f_riv_c145*): l'energia in 10 ohm, V(vplus)^2 / 10 integrata
              dall'evento alla fine; p_r144_max_W la potenza massima
"""
import csv
import os
import sys

TE = 2.0


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


def primo(t, cond, da=TE):
    for i in range(len(t)):
        if t[i] >= da and cond(i):
            return (t[i] - TE) * 1e3
    return None


def main(seqdir, out, casi):
    righe = []
    for caso in casi:
        d = os.path.join(seqdir, caso)
        g = open(os.path.join(d, "punto_fisso.txt")).read().strip()
        c = leggi(os.path.join(d, "tb_psu_seq_%s_g%s_out.txt" % (caso, g)))
        t = c["time"]
        vr, mc = c["v(vrelay)"], c["v(mute_cmd)"]
        vp, vm = c["v(vplus)"], c["v(vminus)"]
        dc = c["v(dc_flt)"]
        r = {"caso": caso, "giro": g}
        r["t_dc"] = primo(t, lambda i: dc[i] < 2.5)
        r["t_mute"] = primo(t, lambda i: vr[i] - mc[i] < 1.0)
        r["t_vrelay"] = primo(t, lambda i: vr[i] < 6.0)
        r["t_k501"] = primo(t, lambda i: c["v(k501_f)"][i] < 0.5)
        r["t_vp_135"] = primo(t, lambda i: vp[i] < 13.5)
        r["t_vp_5"] = primo(t, lambda i: vp[i] < 5.0)
        r["t_vp_1"] = primo(t, lambda i: vp[i] < 1.0)
        r["t_vm_1"] = primo(t, lambda i: vm[i] > -1.0)
        td = r["t_dc"]
        r["t_rilascio"] = None if td is None else primo(t, lambda i: dc[i] > 2.5, TE + td / 1e3 + 1e-4)
        stati = list(csv.DictReader(open(os.path.join(d, "core_g%s.csv" % g))))
        tg = [float(s["t"]) for s in stati if s["stato"] == "GUASTO"]
        r["guasto_ms"] = (tg[0] - TE) * 1e3 if tg else None
        r["stato_finale"] = stati[-1]["stato"]
        r["mains_req_finale"] = stati[-1]["mains_req"]
        if "f_riv_c145" in caso:
            e, pmax = 0.0, 0.0
            for i in range(1, len(t)):
                if t[i] < TE:
                    continue
                p = vp[i] ** 2 / 10.0
                e += p * (t[i] - t[i - 1])
                pmax = max(pmax, p)
            r["e_r144_J"] = e
            r["p_r144_max_W"] = pmax
            # il tempo con R144 sopra la sua potenza a regime nominale di 0,25 W x 10 (un impulso
            # breve; il calcolo vero del calore e' nel report, contro il datasheet)
            r["t_p_sopra_1W"] = None
            for i in range(len(t) - 1, -1, -1):
                if t[i] >= TE and vp[i] ** 2 / 10.0 > 1.0:
                    r["t_p_sopra_1W"] = (t[i] - TE) * 1e3
                    break
        righe.append(r)
    chiavi = []
    for r in righe:
        for k in r:
            if k not in chiavi:
                chiavi.append(k)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=chiavi)
        w.writeheader()
        for r in righe:
            w.writerow({k: ("%.3f" % v if isinstance(v, float) else ("" if v is None else v))
                        for k, v in r.items()})
    for r in righe:
        print(" ".join("%s=%s" % (k, ("%.2f" % v if isinstance(v, float) else v)) for k, v in r.items()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
