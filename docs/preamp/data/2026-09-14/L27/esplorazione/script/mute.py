"""tb_mute_corto: class-A state per row vs L12, and P7 at +3 dB (ADR-021)."""
import csv
base = "/Users/roberto/EDA/.claude/worktrees/L27/docs/preamp/data/2026-09-14"
a = list(csv.DictReader(open(f"{base}/L12/dopo/tb_mute_corto/tb_mute_corto_regime.csv")))
b = list(csv.DictReader(open(f"{base}/L27/dopo/tb_mute_corto/tb_mute_corto_regime.csv")))
print("righe L12", len(a), "L27", len(b))
empty = sum(1 for r in b for v in r.values() if (v or "").strip() == "")
print("celle vuote L27:", empty)
key = lambda r: (r["blk"], r["modo_db"], r["f_hz"], r["vin_pk"], r["k_att"], r["caso"])
ia = {key(r): r for r in a}
classA = lambda r: float(r["icmin_q132"]) > 0 and float(r["icmax_q133"]) < 0
changed, common, maxdp = 0, 0, 0.0
for r in b:
    k = key(r)
    if k in ia:
        common += 1
        if classA(r) != classA(ia[k]):
            changed += 1
            print("  stato cambiato:", k)
        for c in ("p_q132", "p_q133"):
            d = abs(float(r[c]) - float(ia[k][c]))
            maxdp = max(maxdp, d)
print(f"righe in comune {common}, stato di classe A cambiato {changed}, max |dP| MJE {maxdp*1e3:.3f} mW")
# P7: worst MJE per block, per mode; Tj = 60 + P * 62.5
for blk in ("A", "F1", "F2", "B"):
    for gm in ("0", "3", "10"):
        rows = [r for r in b if r["blk"] == blk and r["modo_db"] == gm]
        if not rows: continue
        w = max(rows, key=lambda r: max(float(r["p_q132"]), float(r["p_q133"])))
        p = max(float(w["p_q132"]), float(w["p_q133"]))
        print(f"  {blk:2} {gm:>2} dB: MJE peggiore {p*1e3:7.1f} mW, Tj {60 + p*62.5:5.1f} C (caso {w['caso']}, f {w['f_hz']}, k {w['k_att']})")
# listenable paths in class A at +3 dB (ADR-023)
listen = {"0": {"A", "F1", "F2", "B"}, "1": set(), "2": {"A", "F2", "B"}, "5": {"A", "F2", "B"},
          "6": {"A", "F2", "B"}, "3": {"A", "F1", "B"}, "4": {"A", "F1", "F2"}}
bad = [key(r) for r in b if r["blk"] in listen[r["caso"]] and not classA(r)]
print("righe ascoltabili fuori dalla classe A (tutte le modalita'):", len(bad))
for k in bad[:10]: print("  ", k)
# resistors at +3 dB vs +10 dB, block B
for gm in ("3", "10"):
    rows = [r for r in b if r["blk"] == "B" and r["modo_db"] == gm]
    print(f"  B {gm:>2} dB: p_rsep max {max(float(r['p_rsep']) for r in rows):.3f} W, "
          f"p_r134 max {max(float(r['p_r134']) for r in rows)*1e3:.1f} mW")
t = list(csv.DictReader(open(f"{base}/L27/dopo/tb_mute_corto/tb_mute_corto_transitorio.csv")))
for r in t:
    print("  transitorio", {k: r[k] for k in ("modo_db", "vin_pk", "ppk_b132_ins", "ppk_b132_mute", "vjm_max_rel", "vjm_min_rel")})
