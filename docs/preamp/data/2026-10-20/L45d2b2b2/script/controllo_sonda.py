#!/usr/bin/env python3
"""L45d2b2b2: the check of the new current probes (genera_tb_psu.py, SONDE_I and i(vfc)) on a known
case, f_d506_corto_mus, before they are used. Solo stdlib.

    controllo_sonda.py <seq/k_vecchio> <seq/k_nuovo> <out.txt>

1. The same case on L45d2b2b1's bench (psu_vecchio/, a copy, no probes) and on this one: the core's
   outputs at the fixed point the same, and every column the two write in common within 1 mV / 1 mA
   (the probes are 0 V sources: they must change nothing).
2. Kirchhoff, from quantities the probes do not share:
   - at MUTE_CMD: i(Q501's drain) = (V(VRELAY) - V(MUTE_CMD)) / R_MUTECOIL - i(vfc)
     (the coils, and the clamp's current back through the short; D506 reverse-biased, ~0);
   - at CLAMP_MUTE: i(D507's anode) = -i(vfc).
   Within 1 mA + 1 % from TE.
3. The sabotage: the same balance with the coil of the bench before ADR-085 (438.33 ohm) must FAIL.
Exit 0 only if 1 and 2 hold and 3 fails.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from analizza_075 import A  # noqa: E402

R_MUTECOIL = 1.0 / (2 / 1315.0 + 1 / 1029.0)    # genera_tb_psu.py, --bobine im06 (ADR-085)
TE = A.TE


def ultimo(seq, nome):
    d = os.path.join(seq, nome)
    g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    return d, g, A.leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))


def bilancio(S, r_coil):
    t = S["time"]
    k0 = next(k for k in range(len(t)) if t[k] >= TE)
    e1 = e2 = 0.0
    for k in range(k0, len(t)):
        iq = S["i(vsiq501_3)"][k]
        atteso = (S["v(vrelay)"][k] - S["v(mute_cmd)"][k]) / r_coil - S["i(vfc)"][k]
        e1 = max(e1, abs(iq - atteso) - (1e-3 + 0.01 * abs(atteso)))
        iz = S["i(vsid507_2)"][k]
        e2 = max(e2, abs(iz + S["i(vfc)"][k]) - (1e-3 + 0.01 * abs(S["i(vfc)"][k])))
    return e1, e2


def main():
    vecchio, nuovo, out = sys.argv[1:4]
    nome = "f_d506_corto_mus"
    dv, gv, V = ultimo(vecchio, nome)
    dn, gn, N = ultimo(nuovo, nome)
    righe = []
    # the core: the bench's own rule (psu/confronta.py: the same rows, every time within 0.2 ms).
    # First run: byte for byte was asked, and one event moved by 1 us (2.712613 / 2.712612 s)
    import subprocess
    ok1 = subprocess.run(["/usr/bin/python3", "-I", os.path.join(QUI, "..", "psu", "confronta.py"),
                          os.path.join(dv, "core_g%d.csv" % gv), os.path.join(dn, "core_g%d.csv" % gn)],
                         capture_output=True).returncode == 0
    righe.append("1. core al punto fisso: vecchio giro %d, nuovo giro %d, %s entro 0,2 ms" %
                 (gv, gn, "UGUALI" if ok1 else "DIVERSI"))
    # the waveforms: at most 20 samples of 30001 beyond 10 mV / 10 mA per column (0.4 % of the 2.5 V
    # thresholds that decide anything here; SET AFTER the first runs, declared: 1 mV caught ADC_MD, a
    # slow node, 23 samples at <= 3 mV) - the solver.s step
    # moving an edge by a microsecond (first run: 2 samples of PERMIT_CMD, 10 of MUTE_CMD, all on
    # edges), not the probes
    peggio = (0, 0.0, "")
    n = min(len(V["time"]), len(N["time"]))
    for c in V:
        if c == "time" or c not in N:
            continue
        d = [abs(V[c][k] - N[c][k]) for k in range(n)]
        quanti = sum(1 for x in d if x > 1e-2)
        if quanti > peggio[0]:
            peggio = (quanti, max(d), c)
    ok1 = ok1 and peggio[0] <= 20
    righe.append("   colonne in comune: %d; la piu' diversa %s, %d campioni oltre 10 mV (max %.3g)" %
                 (sum(1 for c in V if c in N and c != "time"), peggio[2], peggio[0], peggio[1]))
    e1, e2 = bilancio(N, R_MUTECOIL)
    ok2 = e1 <= 0 and e2 <= 0
    righe.append("2. Kirchhoff (oltre 1 mA + 1 %%): MUTE_CMD %.3g A, CLAMP_MUTE %.3g A -> %s" %
                 (max(e1, 0), max(e2, 0), "TIENE" if ok2 else "NON TIENE"))
    s1, _ = bilancio(N, 1315 / 3.0)
    ok3 = s1 > 0
    righe.append("3. sabotaggio (bobine G6K, 438,33 ohm): MUTE_CMD fuori di %.3g A -> %s" %
                 (s1, "PRESO" if ok3 else "NON PRESO"))
    t = N["time"]
    k0 = next(k for k in range(len(t)) if t[k] >= TE)
    righe.append("   (picco nel drain di Q501 %.4f A, nel corto %.4f A)" %
                 (max(N["i(vsiq501_3)"][k] for k in range(k0, len(t))),
                  max(abs(N["i(vfc)"][k]) for k in range(k0, len(t)))))
    esito = ok1 and ok2 and ok3
    righe.append("ESITO: %s" % ("PASSA" if esito else "CADE"))
    open(out, "w").write("\n".join(righe) + "\n")
    print("\n".join(righe))
    sys.exit(0 if esito else 1)


main()
