"""riassunto_e3.py - il minimo di |Zin| a 20 Hz, a 20 kHz e su tutta la banda, per curva, dai CSV
di tb_e3_seq_<curva>.cir (genera_e3_sequenza.py), su trim e selettore.

    /usr/bin/python3 riassunto_e3.py <cartella out> <uscita.csv>
"""
import csv
import glob
import os
import sys

righe = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "tb_e3_seq_*.csv"))):
    righe += list(csv.DictReader(open(p)))
out = []
for c in "ABCDE":
    rr = [r for r in righe if r["curva"] == c]
    z20 = min(rr, key=lambda r: float(r["z20_ohm"]))
    z20k = min(rr, key=lambda r: float(r["z20k_ohm"]))
    zmin = min(rr, key=lambda r: min(float(r["zmin_ohm"]), float(r["z20k_ohm"])))
    o = {"curva": c, "righe": len(rr),
         "z20Hz_min_kohm": "%.1f" % (float(z20["z20_ohm"]) / 1e3), "a_t_s": z20["t_s"],
         "z20kHz_min_kohm": "%.1f" % (float(z20k["z20k_ohm"]) / 1e3),
         "banda_min_kohm": "%.1f" % (min(float(zmin["zmin_ohm"]), float(zmin["z20k_ohm"])) / 1e3),
         "pos_csel_del_minimo": "%s/%s" % (z20k["pos"], z20k["csel"])}
    out.append(o)
    print(o)
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
