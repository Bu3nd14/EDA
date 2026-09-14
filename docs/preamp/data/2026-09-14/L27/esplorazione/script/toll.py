import csv
rows = list(csv.DictReader(open('/Users/roberto/.claude/jobs/cbe5116a/tmp/toll/out/toll_L27_tab.csv')))
print(len(rows), "righe; celle vuote:", sum(1 for r in rows for v in r.values() if v.strip() == ''))
for m in ('0', '3'):
    sel = [r for r in rows if r['mode'] == m]
    w = min(sel, key=lambda r: abs(float(r['pm_deg'])))
    print(f"mode {m}: min {abs(float(w['pm_deg'])):.3f} deg  | {w}")
