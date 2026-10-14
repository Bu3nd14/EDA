#!/usr/bin/env python3
"""L45c2: the fixed point of a sequence case whose FAULT is in MUTE_G's own chain. Solo stdlib.

    accetta.py <seq>/<caso>

corri_seq.sh refuses two kinds of pass that L45c1 never met, and both come from ponte.c's rule
for MUTE_G_IN (its header): where the core's MUTE_REQ differs from the one that drove the circuit,
the pin is REBUILT from the supervisors the core reads, ASSUMING THEM HEALTHY (MUTE_G = MUTE_REQ
unless a supervisor is out). When the fault is a supervisor, the reference or MUTE_G's own chain,
that assumption is the fault itself:

  A. "uscite uguali ma con sostituzioni": core_g<n>.csv equals core_g<n-1>.csv BYTE FOR BYTE, and
     every substitution falls on the very tick where the core changes MUTE_REQ (the core's state
     before the step against the driving output after it). Accepted when both hold.
  B. "NESSUN punto fisso": the core oscillates between passes, because the rebuilt pin says what a
     healthy circuit would do and the faulty circuit does something else. Accepted when what the
     bridge carries to the audio board is the SAME in the last two passes: the rails (|dV| <= 2 mV
     at every common sample from TE), the jack's instant and the gain relays' instant (estrai_ponte's
     rules, within 0.2 ms - two samples of the grid). Then the core's oscillation changes nothing
     the audio board sees, and the last pass is the case.

Writes punto_fisso.txt (the last pass) and accettato.txt (which rule, and the figures), or refuses
with exit 1. The log guard of corri_seq.sh is not touched: a pass whose log has an error is never
accepted here (analizza_psu.py and estrai_ponte.py check it again)."""
import csv
import os
import re
import sys

TE = 2.0
V_RIL, T_RIL, V_OP = 1.2, 3e-3, 9.6
MALE = ("error", "singular", "no such", "non-increasing", "transient op", "timestep too small",
        "aborted", "too many args")
d = os.path.abspath(sys.argv[1])
caso = os.path.basename(d)
passi = sorted(int(m.group(1)) for f in os.listdir(d) for m in [re.match(r"core_g(\d+)\.csv$", f)] if m)
g = passi[-1]
if g < 2:
    raise SystemExit("%s: meno di due giri - rifiutato" % caso)


def log_pulito(n):
    p = os.path.join(d, "tb_psu_seq_%s_g%d.log" % (caso, n))
    if not os.path.exists(p):
        return False
    t = open(p).read().lower()
    return not any(w in t for w in MALE)


def leggi(n):
    f = open(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (caso, n)))
    head = f.readline().split()
    cols = {h: [] for h in head}
    for r in f:
        v = r.split()
        if len(v) == len(head):
            for h, x in zip(head, v):
                cols[h].append(float(x))
    return cols


def istanti(S):
    t, vr = S["time"], S["v(vrelay)"]
    j = next((t[k] for k in range(len(t)) if t[k] >= TE and vr[k] - S["v(mute_cmd)"][k] < V_RIL), None)
    gn = next((t[k] for k in range(len(t)) if t[k] >= TE and
               (vr[k] - S["v(permit_cmd)"][k] < V_OP or vr[k] < V_OP)), None)
    return (None if j is None else j + T_RIL), gn


if not (log_pulito(g) and log_pulito(g - 1)):
    raise SystemExit("%s: un log degli ultimi due giri ha un errore - rifiutato" % caso)
ug = open(os.path.join(d, "core_g%d.csv" % g)).read()
up = open(os.path.join(d, "core_g%d.csv" % (g - 1))).read()
righe = [r for r in csv.reader(ug.splitlines()) if r and r[0] != "t"]
cambi = [float(righe[k][0]) for k in range(1, len(righe)) if righe[k][3] != righe[k - 1][3]]
pt = open(os.path.join(d, "ponte_g%d.txt" % g)).read()
sost = [float(x) for x in re.findall(r"sostituzione di MUTE_G_IN a ([0-9.]+) s", pt)]
n_sost = int(re.search(r"sostituzioni di MUTE_G_IN (\d+)", pt).group(1))
note = ["caso %s, giro %d" % (caso, g)]
if ug == up:
    fuori = [s for s in sost if not any(abs(s - c) < 0.5e-3 for c in cambi)]
    if n_sost > len(sost) or fuori:
        raise SystemExit("%s: uscite uguali, ma sostituzioni fuori dai cambi di MUTE_REQ %s - rifiutato"
                         % (caso, fuori or "(oltre le 5 stampate)"))
    note.append("regola A: core_g%d.csv = core_g%d.csv byte per byte; %d sostituzioni, tutte nel "
                "tick di un cambio di MUTE_REQ (%s)" % (g, g - 1, n_sost, ", ".join("%.6f" % s for s in sost)))
else:
    A, B = leggi(g), leggi(g - 1)
    ja, ga = istanti(A)
    jb, gb = istanti(B)

    def uguale(x, y):
        return (x is None and y is None) or (x is not None and y is not None and abs(x - y) <= 0.2e-3)

    n = min(len(A["time"]), len(B["time"]))
    k0 = next(k for k in range(n) if A["time"][k] >= TE)
    dv = max(max(abs(A[c][k] - B[c][k]) for k in range(k0, n)) for c in ("v(vplus)", "v(vminus)"))
    dt = max(abs(A["time"][k] - B["time"][k]) for k in range(k0, n))
    if dt > 1e-9 or dv > 2e-3 or not uguale(ja, jb) or not uguale(ga, gb):
        raise SystemExit("%s: gli ultimi due giri danno alla scheda audio cose diverse (rail %.2g V, "
                         "jack %s / %s, guadagno %s / %s) - rifiutato" % (caso, dv, ja, jb, ga, gb))
    note.append("regola B: nessun punto fisso del core (%d sostituzioni nell'ultimo giro); gli ultimi "
                "due giri danno alla scheda audio gli stessi rail (|dV| max %.3g V) e gli stessi "
                "istanti: jack %s / %s s, guadagno %s / %s s" % (n_sost, dv, ja, jb, ga, gb))
open(os.path.join(d, "punto_fisso.txt"), "w").write("%d\n" % g)
open(os.path.join(d, "accettato.txt"), "w").write("\n".join(note) + "\n")
print("\n".join(note))
