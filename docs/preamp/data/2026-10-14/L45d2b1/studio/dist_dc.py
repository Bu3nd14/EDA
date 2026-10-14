import csv, sys, glob, os
base = sys.argv[1]
rows = []
for f in sorted(glob.glob(os.path.join(base, "analisi_vuoto_*.csv"))):
    for r in csv.DictReader(open(f)):
        if r.get("p10") != "FUORI":
            continue
        try:
            avg = float(r["out_avg"]); mx = float(r["out_max"]); mn = float(r["out_min"])
        except Exception:
            avg = mx = mn = float("nan")
        rows.append((abs(avg), os.path.basename(f), r["modo"], avg, r["p10_sopra_ms_max"],
                     r["main_grezzo_V"], r["fix1_grezzo_V"], r["fix2_grezzo_V"]))
rows.sort()
print("n FUORI", len(rows))
for x in rows[:45]:
    print("%-28s %-12s avg=%8.3f sopra=%s main=%s f1=%s f2=%s" % x[1:])
import collections
bins = collections.Counter()
for x in rows:
    a = x[0]
    b = "<1" if a < 1 else "<2" if a < 2 else "<5" if a < 5 else "<10" if a < 10 else ">=10"
    bins[b] += 1
print(bins)
