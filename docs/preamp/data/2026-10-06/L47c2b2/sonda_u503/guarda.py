import sys
nomi = ["front_in", "mute_sw_in", "mute_g_in", "adc_sup_p", "adc_sup_m", "adc_sup_vr", "adc_md", "mute_cmd",
        "permit_cmd", "vrelay", "vrelay_reg", "vplus", "vminus", "k501_f", "mute_g", "permit_g", "env",
        "mute_req", "permit_req", "mains_req", "vrelay_en"]
t, rows = [], []
f = open(sys.argv[1]); head = f.readline().split()
nomi = [h[2:-1] for h in head[1:]]
for r in f:
    v = r.split()
    if len(v) != len(head):
        continue
    t.append(float(v[0]))
    rows.append([float(x) for x in v[1:]])
print("righe", len(t), "fine", t[-1])
t0 = float(sys.argv[2])
# step density per ms after t0
import collections
c = collections.Counter(int((x - t0) * 1e3) for x in t if x >= t0)
print("passi per ms dopo t0 (primi e piu' densi):", sorted(c.items())[:5], c.most_common(5))
show = ["vrelay_reg", "vrelay", "mute_cmd", "permit_cmd", "mute_g_in", "adc_sup_vr", "k501_f", "vplus"]
last = None
for x, r in zip(t, rows):
    if x < t0:
        continue
    ms = round((x - t0) * 1e3, 1)
    if last is None or ms - last >= float(sys.argv[3]):
        last = ms
        print("%8.1f ms " % ms + " ".join("%s=%.4g" % (n, r[nomi.index(n)]) for n in show))
