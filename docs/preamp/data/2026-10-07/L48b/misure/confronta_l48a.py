#!/usr/bin/env python3
"""L48b: E3, E5 e l'attenuazione del trim dei due deck canonici, contro L48a."""
import csv
import os

DATA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def rd(p):
    return list(csv.DictReader(open(os.path.join(DATA, p))))


out = []
for name, d, key in (("tb_trim_e5.csv", "tb_trim", ("cand", "pos", "mode", "att", "rsrc")),
                     ("tb_e3_e5_e5.csv", "tb_e3_e5", ("pos", "mode", "att", "rsrc"))):
    a = rd(f"2026-10-06/L48a/misure/{d}/{name}")
    b = rd(f"2026-10-07/L48b/misure/{d}/{name}")
    ma = {tuple(r[k] for k in key): float(r["onoise_uv"]) for r in a}
    mb = {tuple(r[k] for k in key): float(r["onoise_uv"]) for r in b}
    out.append("%s: E5 peggiore prima %.4f uV, dopo %.4f uV; scarto relativo massimo %.2e"
               % (name, max(ma.values()), max(mb.values()),
                  max(abs(mb[k] / ma[k] - 1) for k in ma)))
for name, d in (("tb_trim_e3.csv", "tb_trim"), ("tb_e3_e5_e3.csv", "tb_e3_e5")):
    a = rd(f"2026-10-06/L48a/misure/{d}/{name}")
    b = rd(f"2026-10-07/L48b/misure/{d}/{name}")
    out.append("%s: E3 zmin prima %.1f, dopo %.1f ohm" % (
        name, min(float(r["zmin_ohm"]) for r in a), min(float(r["zmin_ohm"]) for r in b)))
    if "att1k_db" in a[0]:
        for ra, rb in zip(a, b):
            if ra["csel"] == "1f" and ra["pos"] in ("6", "12"):
                out.append("  trim cand %s pos %s: attenuazione a 1 kHz prima %s, dopo %s dB"
                           % (ra["cand"], ra["pos"], ra["att1k_db"], rb["att1k_db"]))
print("\n".join(out))
open(os.path.join(DATA, "2026-10-07/L48b/misure/confronto_l48a.txt"), "w").write("\n".join(out) + "\n")
