#!/usr/bin/env python3
"""L46b (copiato da L46a): una riga per variante con tutto quello che serve alla scelta.

  V1      il criterio di ADR-024 com'e' in L40/script/sintesi_v1.py (copiato qui
          perche' quello legge l'albero di L40): blocco B nei tre modi e buffer,
          pos 1, tutte le sorgenti e i carichi; blocco A cablaggio <= 1 nF; il
          trim (Atrim). Il minimo su tutto, col crossover del blocco B 0 dB a vuoto.
  op      corrente di riposo (Q132), corrente del rail + (riassumi_op.py)
  PSRR+   +10 dB (il modo peggiore) a 1 / 10 / 20 kHz, dalla curva wrdata
  rumore  onoise_total dei casi A (blocco A intrinseco) e D (+10 dB, 2,5 kOhm)
  slew    discesa a gradino, e continua indotta a 20 kHz / 12 V di picco
  distorsione (run/<v>/distorsione.csv, leggi_four.py): al livello lo (-20 dB,
          criterio) il peggiore sui tre modi a 1 / 10 / 20 kHz, la crescita
          20 kHz contro 1 kHz in dB, le armoniche dalla 5a in su, l'IMD; al
          livello hi (stress) THD a 20 kHz e IMD.

Uso: /usr/bin/python3 sintesi.py <variante>...  -> sintesi.csv (e a schermo)
"""
import csv
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
RUN = os.path.join(L46A, "run")
CAB1N = ("1f", "47p", "100p", "220p", "470p", "1n")


def tab(v, deck, f):
    p = os.path.join(RUN, v, deck, f)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def log(v, deck):
    p = os.path.join(RUN, v, deck, deck + ".log")
    if not os.path.exists(p):
        return []
    righe = open(p, errors="replace").read().split("\n")
    for r in righe:
        for x in ("Error", "Transient op started", "aborted", "too many args"):
            if x in r:
                sys.exit("%s: riga rifiutata: %s" % (p, r.strip()))
    return righe


def valori(righe, nome):
    """Ogni `nome = x` del log, con la ricucitura di #37."""
    out = []
    for k, r in enumerate(righe):
        m = re.match(re.escape(nome) + r" = ([-+0-9.eE]+)(Note:|Warning:)?", r)
        if m:
            t = m.group(1)
            if m.group(2):
                j = k + 1
                while not re.match(r"^[-+0-9.eE]+$", righe[j].strip()):
                    j += 1
                t += righe[j].strip()
            out.append(float(t))
    return out


def v1(v):
    lb = tab(v, "tb_loop", "tb_loop_margini.csv")
    la = tab(v, "tb_loop_blockA", "tb_loop_blockA.csv")
    lt = tab(v, "tb_loop_blockA", "tb_loop_blockA_trim.csv")
    lf = tab(v, "tb_loop_bufferfissa", "tb_loop_bufferfissa.csv")
    cel = {
        "B0": (lb, lambda x: x["mode"] == "0db" and x["pos"] == "1"),
        "B3": (lb, lambda x: x["mode"] == "3db" and x["pos"] == "1"),
        "B10": (lb, lambda x: x["mode"] == "10db" and x["pos"] == "1"),
        "A": (la, lambda x: x["cwire"] in CAB1N),
        "Atrim": (lt, lambda x: x["cwire"] in CAB1N),
        "buf": (lf, lambda x: x["pos"] == "1"),
    }
    out = {}
    for c, (r, f) in cel.items():
        r = [x for x in r if f(x)]
        if not r:
            sys.exit("%s: V1 %s senza righe" % (v, c))
        if any(x["pm_deg"] == "" for x in r):
            sys.exit("%s: V1 %s con celle vuote (#26)" % (v, c))
        out[c] = min(float(x["pm_deg"]) for x in r)
    fc = [x for x in lb if x["mode"] == "0db" and x["rsrc"] == "1m" and x["pos"] == "1"
          and x["cprobe"] == "1f" and x["rload"] == "100k"]
    out["fc_khz"] = float(fc[0]["fcross_hz"]) / 1e3
    return out


def curva(v, nome, f0):
    """Il valore della curva wrdata (frequenza, valore) a f0, interpolato in log f."""
    p = os.path.join(RUN, v, "tb_zout_psrr_noise", nome)
    r = [list(map(float, x)) for x in csv.reader(open(p)) if x and re.match(r"[-+0-9]", x[0])]
    for a, b in zip(r, r[1:]):
        if a[0] <= f0 <= b[0]:
            t = (math.log(f0) - math.log(a[0])) / (math.log(b[0]) - math.log(a[0]))
            return a[-1] + t * (b[-1] - a[-1])
    sys.exit("%s: %g fuori dalla curva" % (p, f0))


def op(v):
    r = [x for x in csv.reader(open(os.path.join(RUN, "punto_di_lavoro.csv"))) if x[0] == v]
    return {"iq": float(r[-1][1]), "irail": float(r[-1][4])} if r else {"iq": float("nan"), "irail": float("nan")}


def dist(v):
    r = list(csv.DictReader(open(os.path.join(RUN, v, "distorsione.csv"))))
    out = {}
    for liv in ("lo", "hi"):
        for f in ("1000", "10000", "20000"):
            x = [float(a["thd_pct"]) for a in r if a["livello"] == liv and a["freq"] == f
                 and a["deck"].startswith("thd")]
            out["thd_%s_%s" % (liv, f)] = max(x)
        out["h5su_%s" % liv] = max(float(a["h5su_db"]) for a in r if a["livello"] == liv
                                   and a["deck"].startswith("thd"))
        out["imd_%s" % liv] = max(float(a["imd_d2_db"]) for a in r if a["livello"] == liv
                                  and a["deck"] == "imd")
        out["cresce_%s" % liv] = 20 * math.log10(out["thd_%s_20000" % liv] / out["thd_%s_1000" % liv])
    return out


COL = ["variante", "B0", "B3", "B10", "A", "Atrim", "buf", "v1_min", "fc_khz", "iq_ma", "irail_ma",
       "psrrp_1k", "psrrp_10k", "psrrp_20k", "rum_A_uv", "rum_D_uv", "sr_disc", "dc_20k_fs",
       "thd_lo_1k", "thd_lo_10k", "thd_lo_20k", "cresce_lo_db", "h5su_lo_db", "imd_lo_db",
       "thd_hi_20k", "imd_hi_db"]
righe = []
for v in sys.argv[1:]:
    m = v1(v)
    o = op(v)
    d = dist(v)
    rum = valori(log(v, "tb_noise_breakdown"), "onoise_total")
    if len(rum) != 5:
        sys.exit("%s: %d onoise_total invece di 5" % (v, len(rum)))
    st = tab(v, "slew", "slew_step.csv")
    sw = [x for x in tab(v, "slew", "slew_tab.csv") if x["amp_in"].startswith("3.818")]
    righe.append({
        "variante": v, **{k: "%.2f" % m[k] for k in ("B0", "B3", "B10", "A", "Atrim", "buf")},
        "v1_min": "%.2f" % min(m[k] for k in ("B0", "B3", "B10", "A", "Atrim", "buf")),
        "fc_khz": "%.0f" % m["fc_khz"], "iq_ma": "%.2f" % o["iq"], "irail_ma": "%.2f" % o["irail"],
        "psrrp_1k": "%.1f" % curva(v, "tb_zout_psrr_noise_psrrp_10db.csv", 1e3),
        "psrrp_10k": "%.1f" % curva(v, "tb_zout_psrr_noise_psrrp_10db.csv", 1e4),
        "psrrp_20k": "%.1f" % curva(v, "tb_zout_psrr_noise_psrrp_10db.csv", 2e4),
        "rum_A_uv": "%.3f" % (rum[0] * 1e6), "rum_D_uv": "%.3f" % (rum[3] * 1e6),
        "sr_disc": "%.2f" % float(st[0]["sr_fall_vus"]),
        "dc_20k_fs": "%.3f" % float(sw[0]["vo_mean_dc"]),
        "thd_lo_1k": "%.2g" % d["thd_lo_1000"], "thd_lo_10k": "%.2g" % d["thd_lo_10000"],
        "thd_lo_20k": "%.2g" % d["thd_lo_20000"], "cresce_lo_db": "%.1f" % d["cresce_lo"],
        "h5su_lo_db": "%.0f" % d["h5su_lo"], "imd_lo_db": "%.1f" % d["imd_lo"],
        "thd_hi_20k": "%.3g" % d["thd_hi_20000"], "imd_hi_db": "%.1f" % d["imd_hi"],
    })
with open(os.path.join(L46A, "sintesi.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, COL)
    w.writeheader()
    w.writerows(righe)
for r in righe:
    print(" ".join("%s=%s" % (k, r[k]) for k in COL))
