"""Compare L27/dopo against L12/dopo: every csv both runs produced (same name),
max relative difference over numeric cells, plus log '=' lines for tb_op."""
import csv, os, re, sys
base = "/Users/roberto/EDA/.claude/worktrees/L27/docs/preamp/data/2026-09-14"
decks = sys.argv[1:]
num = re.compile(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$")
for deck in decks:
    a_dir, b_dir = f"{base}/L12/dopo/{deck}", f"{base}/L27/dopo/{deck}"
    if not os.path.isdir(a_dir):
        print(f"{deck}: nessun dato L12"); continue
    a_files = {f for f in os.listdir(a_dir) if f.endswith(".csv")}
    b_files = {f for f in os.listdir(b_dir) if f.endswith(".csv")}
    only_b = sorted(b_files - a_files); only_a = sorted(a_files - b_files)
    worst = (0.0, None)
    shape = []
    for f in sorted(a_files & b_files):
        ra = list(csv.reader(open(f"{a_dir}/{f}"))); rb = list(csv.reader(open(f"{b_dir}/{f}")))
        if len(ra) != len(rb):
            shape.append(f"{f}: righe {len(ra)} -> {len(rb)}"); continue
        for i, (x, y) in enumerate(zip(ra, rb)):
            for j, (u, v) in enumerate(zip(x, y)):
                if num.match(u.strip()) and num.match(v.strip()):
                    fu, fv = float(u), float(v)
                    den = max(abs(fu), abs(fv), 1e-30)
                    rel = abs(fu - fv) / den
                    if abs(fu - fv) < 1e-15:
                        rel = 0.0
                    if rel > worst[0]:
                        worst = (rel, f"{f} r{i} c{j}: {u} -> {v}")
                elif u != v:
                    shape.append(f"{f} r{i} c{j}: '{u}' -> '{v}'")
    print(f"{deck}: {len(a_files & b_files)} csv in comune, max scarto relativo {worst[0]:.3e} ({worst[1]})")
    if only_b: print(f"   solo L27: {only_b[:8]}{' ...' if len(only_b) > 8 else ''} ({len(only_b)})")
    if only_a: print(f"   solo L12: {only_a}")
    for s in shape[:6]: print("   " + s)
