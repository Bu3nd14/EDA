"""V3: compare L27 vs L12 overload waveforms (v(OUT), v(JACK)) on L12's time grid."""
import csv, bisect
base = "/Users/roberto/EDA/.claude/worktrees/L27/docs/preamp/data/2026-09-14"
def load(p):
    r = list(csv.reader(open(p)))
    head, data = r[0], [[float(x) for x in row] for row in r[1:]]
    return head, data
ha, a = load(f"{base}/L12/dopo/tb_v3_overload/tb_v3_overload.csv")
hb, b = load(f"{base}/L27/dopo/tb_v3_overload/tb_v3_overload.csv")
print("colonne", ha)
# wrdata: col0 t, col1 SRCN, col2 t, col3 OUT, col4 t, col5 JACK ...
tb = [row[0] for row in b]
def interp(t, col):
    i = bisect.bisect_left(tb, t)
    if i <= 0: return b[0][col]
    if i >= len(b): return b[-1][col]
    t0, t1 = tb[i-1], tb[i]
    y0, y1 = b[i-1][col], b[i][col]
    return y0 + (y1 - y0) * (t - t0) / (t1 - t0) if t1 > t0 else y1
for name, col in (("OUT", 3), ("JACK", 5)):
    d = max(abs(row[col] - interp(row[0], col)) for row in a)
    print(f"{name}: L12 max {max(r[col] for r in a):.4f} min {min(r[col] for r in a):.4f} | "
          f"L27 max {max(r[col] for r in b):.4f} min {min(r[col] for r in b):.4f} | max |diff| {d*1e3:.3f} mV")
print("JACK finale L12 %.2f mV, L27 %.2f mV" % (a[-1][5]*1e3, b[-1][5]*1e3))
