"""fronte.py - il compromesso S contro E3 in una tabella di famiglia.py: per ogni soglia di E3 a
20 kHz, il profilo col S piu' basso che la raggiunge (mute <= -70 dB).

    /usr/bin/python3 fronte.py <famiglia.csv>
"""
import csv
import sys

righe = list(csv.DictReader(open(sys.argv[1])))
for r in righe:
    for k in ("S_max", "mute_max_dB", "E3_min_k", "carico_min_k"):
        r[k] = float(r[k])
righe = [r for r in righe if r["mute_max_dB"] <= -70]
print("E3 massimo nella famiglia: %.1f k" % max(r["E3_min_k"] for r in righe))
for soglia in (80, 85, 88, 90, 92, 94, 96, 98, 100):
    ok = [r for r in righe if r["E3_min_k"] >= soglia]
    if not ok:
        print("E3 >= %3d k: nessuno" % soglia)
        continue
    b = min(ok, key=lambda r: r["S_max"])
    print("E3 >= %3d k: S %.2f dB  (a %s b %s i0 %s g %s; E3 %.1f k, carico %.1f k, mute %.1f dB)" % (
        soglia, b["S_max"], b["a"], b["b"], b["i0"], b["g"], b["E3_min_k"], b["carico_min_k"],
        b["mute_max_dB"]))
