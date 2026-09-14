import csv, sys
p = sys.argv[1]
rows = list(csv.DictReader(open(p)))
print(len(rows), "righe; celle vuote:",
      sum(1 for r in rows for v in r.values() if v.strip() == ''))
modes = sorted({r['mode'] for r in rows}, key=lambda s: int(s.replace('db', '')))
loads = sorted({r.get('rload', '100k') for r in rows})
for gm in modes:
    for rl in loads:
        for pos in ('1', '2'):
            sel = [r for r in rows if r['mode'] == gm and r.get('rload', '100k') == rl and r['pos'] == pos]
            if not sel:
                continue
            m = min(sel, key=lambda r: abs(float(r['pm_deg'])))
            bare = [r for r in sel if r['rsrc'] == '1m' and r['cprobe'] == '1f'][0]
            print(f"{gm:5} RL={rl:4} pos{pos}: min {abs(float(m['pm_deg'])):8.3f} deg @ rsrc {m['rsrc']:4} C {m['cprobe']:5}"
                  f" | nudo {abs(float(bare['pm_deg'])):.3f} deg, T10Hz {float(bare['tdb_10hz']):.2f} dB,"
                  f" fc {float(bare['fcross_hz'])/1e3:.0f} kHz")
for gm in modes:
    for rl in loads:
        per = {}
        for rs in ('1m', '1k', '2.5k'):
            v = [abs(float(r['pm_deg'])) for r in rows if r['mode'] == gm and r.get('rload', '100k') == rl
                 and r['pos'] == '1' and r['rsrc'] == rs]
            per[rs] = round(min(v), 3)
        print(f"{gm:5} RL={rl:4} jack, minimo per sorgente: {per}")
