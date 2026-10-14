#!/usr/bin/env python3
"""L45c1: the runs that stop on «Timestep too small» with both methods (trap, three tries of
corri.sh; gear, rifai_gear.sh), read up to the abort. Solo stdlib.

    fino_all_aborto.py <corse> <out.csv> <cella> [<cella> ...]

After an abort the .dat runs on to tstop with zeros (limitations #35): only the rows before the
abort instant in the log are read. Per jack: max |v| from t_ins (manifest) to the abort.
Why that is the whole event: the jack contact opens at the bridge's t_jack (printed), and the
bench's contact (BSJKR, tb_v2_mute_graduale.cir) bounces for 521 us after it - closed again
151-300 us and 451-520 us, each time joining the jack to the block, which by then is at its rail
(the 13.8 V spikes of the rail short). Both runs abort AFTER the last bounce (t_jack + 0.521 ms <
t_abort; checked below and refused otherwise); from then the contact is open for good and nothing
drives the jack but its bleeds and the open contact's 0.1 pF.
The read STOPS at the end of the bounces (t_jack + 0.521 ms), not at the abort: in the C501 short
at 100 k the solver sat on one instant (4.2007 ms, after the bounces) for many rows with the jack
at 0.84 V before aborting - a run on its way to the abort, not a voltage (the same case unloaded,
which ends, has 8.9 mV at most). With the bench's 1e-18 F of cable an open jack has nothing to
hold a voltage, so nothing after the last bounce can raise the peak.
"""
import csv
import json
import os
import re
import sys

corse, out = sys.argv[1], sys.argv[2]
man = {r["cella"]: r for r in csv.DictReader(open(os.path.join(corse, "manifest.csv")))}
k = list(next(iter(man.values())).keys())
ponte = os.path.join(corse, "..", "ponte")
celle = sys.argv[3:]
if celle == ["--da-tempi"]:
    # the runs whose LAST line in tempi.txt (corri.sh, then rifai_gear.sh) is not rc=0
    u = {}
    for r in open(os.path.join(corse, "tempi.txt")):
        p = r.split()
        if p:
            u[p[0]] = p[1]
    celle = [k for k, v in u.items() if v != "rc=0"]
    if not celle:
        print("nessuna corsa fallita")
        sys.exit(0)
righe = []
for c in celle:
    log = open(os.path.join(corse, "corsa_%s.log" % c)).read()
    m = re.search(r"Timestep too small; time = ([0-9.eE+-]+)", log)
    if not m:
        raise SystemExit("%s: nessun aborto nel log" % c)
    t_ab = float(m.group(1))
    t_ins = float(man[c][k[7]])
    j = json.load(open(os.path.join(ponte, c[:-len("_l41c")] + ".json")))
    if j["t_jack"] is None or j["t_jack"] + 521e-6 >= t_ab:
        raise SystemExit("%s: l'aborto (%.5f s) cade prima della fine dei rimbalzi del jack - "
                         "la lettura fino all'aborto non basta" % (c, t_ab))
    picco, sopra, tprev = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], None
    for r in open(os.path.join(corse, c + ".dat")):
        p = r.split()
        if len(p) != 6:
            continue
        t = float(p[0])
        if t >= min(t_ab, j["t_jack"] + 521e-6 + 10e-6):
            break
        if t < t_ins:
            tprev = t
            continue
        v = [abs(float(p[1])), abs(float(p[3])), abs(float(p[5]))]
        dt = 0.0 if tprev is None else t - tprev
        for i in range(3):
            picco[i] = max(picco[i], v[i])
            if v[i] > 0.87:
                sopra[i] += dt
        tprev = t
    righe.append({"cella": c, "t_abort_ms": "%.2f" % ((t_ab - 1.0) * 1e3),
                  "letto_fino_ms": "%.3f" % ((j["t_jack"] + 531e-6 - 1.0) * 1e3),
                  "t_jack_ms": "%.2f" % ((j["t_jack"] - 1.0) * 1e3) if j["t_jack"] else "",
                  "main_picco_V": "%.4g" % picco[0], "fix1_picco_V": "%.4g" % picco[1],
                  "fix2_picco_V": "%.4g" % picco[2],
                  "main_sopra_ms": "%.2f" % (sopra[0] * 1e3), "fix1_sopra_ms": "%.2f" % (sopra[1] * 1e3),
                  "fix2_sopra_ms": "%.2f" % (sopra[2] * 1e3)})
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(righe[0].keys()))
    w.writeheader()
    w.writerows(righe)
for r in righe:
    print(r)
