#!/usr/bin/env python3
"""L71 (NC-083): what psu/analizza_mc.py does not say about a sequence with the front / SW3 moved.

Per run (seq/<etichetta>/<caso>, the waveform of corri_an.sh):
  n_chiude       the jack's closures after TE (VRELAY - MUTE_CMD rising through 9.6 V, the G6K's
                 must-operate: the EARLIEST the contact can close)
  t_chiude_ms    the first and the last of them, from TE
  perm_anticipo_ms   ADR-045 (3): at the mute's release PERMIT_CMD energises NOT AFTER MUTE_CMD.
                 The smallest, over the closures, of t_close - (the last rise of K6's coil, the gain's
                 permissive, through 9.6 V at or before it): >= 0 is the rule; empty if the
                 permissive was up since before TE. NEGATIVE = the permissive after the jack (and
                 then C2 of an_l71.csv says whether it was ever off with the jack closed)
  vp_chiude / vm_chiude   V+ / V- at the last closure (V), to compare with the references' closure
                 (accensione, rilascio); and dvp50_mv: V+'s excursion in the 50 ms before it
  mus_min_ms     the shortest MUSICA interval (a closure through 9.6 V to the next release through
                 1.2 V + 3 ms): a music that comes and goes at once shows here
  perm_dopo      the closures at which K6's coil is below 9.6 V (the permissive not yet up)
  gap_min_ms     the shortest jack-open interval (release through 1.2 V + 3 ms, to the next
                 closure through 9.6 V): a chatter would show here
  r41_min_ms     ADR-045 (2) as the bridge reads it, at EVERY opening of the jack after a closure:
                 (the first instant after it at which K6's coil is below 9.6 V - the gain free, the
                 EARLIEST) - (the jack's coil below 1.2 V + 3 ms - the contact surely open, the
                 LATEST). The smallest over the openings; >= 0 is the rule (r41 of analizza_mc.py
                 reads only the first event after TE). Empty if the jack never opened after closing
  atteso         the end state each family should reach, WRITTEN BEFORE THE RUNS:
                   acc_spento    off: no music, K501 open, latch not held
                   spl_riacceso  on again: music, K501 closed, latch not held
                   spl_sw3       off: no music, K501 open, latch not held
                   ins_ritorno   music again, K501 closed
                   ril_ritorno   mute again (no music), K501 closed
                   (the references accensione / rilascio: music; inserimento: mute; spegnimento_l: off)
  esito          'atteso' or what differs
Solo stdlib. /usr/bin/python3 -I stato_finale.py <out.csv> <seq_dir>/<etichetta>/<caso> [...]
"""
import csv
import os
import re
import sys

TE = 3.0
V_OP, V_RIL, T_RIL = 9.6, 1.2, 3e-3
ATTESO = {"acc_spento": (0, 0, 0), "spl_riacceso": (1, 1, 0), "spl_sw3": (0, 0, 0),
          "ins_ritorno": (1, 1, 0), "ril_ritorno": (0, 1, 0),
          "accensione": (1, 1, 0), "rilascio": (1, 1, 0), "inserimento": (0, 1, 0),
          "spegnimento_l": (0, 0, 0)}


def leggi(path, cols):
    with open(path) as f:
        nomi = f.readline().split()
        idx = [nomi.index(c) for c in cols]
        out = {c: [] for c in cols}
        for r in f:
            v = r.split()
            if len(v) != len(nomi):
                continue
            for c, i in zip(cols, idx):
                out[c].append(float(v[i]))
    return out


def salite(t, y, soglia, da):
    return [t[k] for k in range(1, len(t)) if t[k] >= da and y[k - 1] < soglia <= y[k]]


def discese(t, y, soglia, da):
    return [t[k] for k in range(1, len(t)) if t[k] >= da and y[k - 1] >= soglia > y[k]]


def caso(d):
    nome = os.path.basename(d.rstrip("/"))
    etich = os.path.basename(os.path.dirname(d.rstrip("/")))
    r = dict(caso=etich + "/" + nome)
    if not os.path.exists(os.path.join(d, "ok.txt")):
        r["esito"] = "CORSA RIFIUTATA"
        return r
    f = [x for x in os.listdir(d) if x.endswith("_g1_out.txt")]
    assert len(f) == 1, (d, f)
    w = leggi(os.path.join(d, f[0]), ["time", "v(vrelay)", "v(mute_cmd)", "v(permit_cmd)",
                                      "v(vplus)", "v(vminus)", "v(k501_f)", "v(at_bn)"])
    t, vr = w["time"], w["v(vrelay)"]
    mj = [a - b for a, b in zip(vr, w["v(mute_cmd)"])]
    mg = [min(a - b, a) for a, b in zip(vr, w["v(permit_cmd)"])]
    vp, vm = w["v(vplus)"], w["v(vminus)"]
    ch = salite(t, mj, V_OP, TE)
    ap = [x + T_RIL for x in discese(t, mj, V_RIL, TE)]
    gs = salite(t, mg, V_OP, 0.0)
    r["n_chiude"] = len(ch)
    r["t_chiude_ms"] = "" if not ch else "%.2f / %.2f" % ((ch[0] - TE) * 1e3, (ch[-1] - TE) * 1e3)
    gs_te = [g for g in gs if g >= TE]
    marg = [x - max(g for g in gs_te if g <= x) for x in ch if any(g <= x for g in gs_te)]
    late = [x for x in ch if mg[min(range(len(t)), key=lambda i: abs(t[i] - x))] < V_OP]
    r["perm_anticipo_ms"] = "" if not marg else round(min(marg) * 1e3, 2)
    r["perm_dopo"] = len(late)
    if ch:
        k = min(range(len(t)), key=lambda i: abs(t[i] - ch[-1]))
        r["vp_chiude"] = round(vp[k], 4)
        r["vm_chiude"] = round(vm[k], 4)
        win = [vp[i] for i in range(len(t)) if ch[-1] - 0.05 <= t[i] <= ch[-1]]
        r["dvp50_mv"] = round((max(win) - min(win)) * 1e3, 2)
    gaps = [min(c for c in ch if c > a) - a for a in ap if any(c > a for c in ch)]
    r["gap_min_ms"] = "" if not gaps else round(min(gaps) * 1e3, 2)
    r41 = []
    for c in ch:
        a = [x for x in ap if x > c]
        if a:
            g = next((t[k] for k in range(len(t)) if t[k] >= a[0] - T_RIL and mg[k] < V_OP), None)
            r41.append((g if g is not None else t[-1]) - a[0])
    r["r41_min_ms"] = "" if not r41 else round(min(r41) * 1e3, 2)
    mm = [min(a for a in ap if a > c) - c for c in ch if any(a > c for a in ap)]
    r["mus_min_ms"] = "" if not mm else round(min(mm) * 1e3, 2)
    mus, k5, rit = int(mj[-1] > 6), int(w["v(k501_f)"][-1] > 0.5), int(w["v(at_bn)"][-1] > 0.4)
    r["mus_end"], r["k501_end"], r["ritenuta"] = mus, k5, rit
    fam = re.sub(r"_[0-9p]+$", "", nome)
    a = ATTESO.get(fam)
    r["atteso"] = "" if a is None else "musica %d, K501 %d, ritenuta %d" % a
    if a is None:
        r["esito"] = "famiglia senza atteso"
    else:
        diff = [n for n, x, y in zip(("musica", "K501", "ritenuta"), (mus, k5, rit), a) if x != y]
        r["esito"] = "atteso" if not diff else "DIVERSO: " + ", ".join(diff)
    return r


CAMPI = ["caso", "n_chiude", "t_chiude_ms", "perm_anticipo_ms", "perm_dopo", "vp_chiude", "vm_chiude",
         "dvp50_mv", "gap_min_ms", "mus_min_ms", "r41_min_ms", "mus_end", "k501_end", "ritenuta", "atteso", "esito"]


def main():
    out, dirs = sys.argv[1], sys.argv[2:]
    rs = [caso(d) for d in dirs]
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, CAMPI)
        wr.writeheader()
        wr.writerows(rs)
    for r in rs:
        print(",".join(str(r.get(c, "")) for c in CAMPI))


main()
