#!/usr/bin/env python3
"""L45c2: the relay line and the commands of every case, from the last pass of its fixed point
(seq/<caso>/), next to analizza_psu.py's rails. Solo stdlib.

    analizza_rele.py <seq> <out.csv> @<lista>

Per case, from TE (the fault with the event mus, the event otherwise) to the end:
    vreg_min/max, vrelay_min/max    VRELAY_REG (U503's output) and VRELAY (the audio board's)
    bobina_min_V                    the jack coils' voltage, VRELAY - MUTE_CMD, at its lowest
                                    while the jack is still closed (before t_jack - 3 ms)
    permit_min_V                    K6's coil, VRELAY - PERMIT_CMD, at its lowest before t_guadagno
    mute_g_fine, permit_g_fine      the two gates at the end (V)
    k501_fine                       K501's contact at the end (1 closed, 0 open)
    anticipo_guadagno_ms            t_jack - t_guadagno (estrai_ponte.py's rules: the jack the
                                    latest, the gain the earliest): > 0 = the gain relays move with
                                    the jack still closed, D lost (ADR-045)
    vrelay_standby                  VRELAY at the end with the front off (spegn): the audio board
                                    powered in standby
The same refusals as analizza_psu.py (punto_fisso.txt, the log's words)."""
import csv
import os
import sys

TE = 2.0
V_RIL, T_RIL, V_OP = 1.2, 3e-3, 9.6
MALE = ("error", "singular", "no such", "non-increasing", "transient op", "timestep too small",
        "aborted", "too many args")


def leggi(path):
    f = open(path)
    head = f.readline().split()
    cols = {n: [] for n in head}
    for r in f:
        v = r.split()
        if len(v) == len(head):
            for n, x in zip(head, v):
                cols[n].append(float(x))
    return cols


def caso(seq, nome):
    d = os.path.join(seq, nome)
    g = int(open(os.path.join(d, "punto_fisso.txt")).read())
    log = open(os.path.join(d, "tb_psu_seq_%s_g%d.log" % (nome, g))).read().lower()
    if any(w in log for w in MALE):
        raise SystemExit("%s: il log ha un errore - rifiutato" % nome)
    S = leggi(os.path.join(d, "tb_psu_seq_%s_g%d_out.txt" % (nome, g)))
    t = S["time"]
    vr, vg, mc, pc = S["v(vrelay)"], S["v(vrelay_reg)"], S["v(mute_cmd)"], S["v(permit_cmd)"]
    dopo = [k for k in range(len(t)) if t[k] >= TE]
    tj = next((t[k] for k in dopo if vr[k] - mc[k] < V_RIL), None)
    tg = next((t[k] for k in dopo if vr[k] - pc[k] < V_OP or vr[k] < V_OP), None)
    chiuso = [k for k in dopo if tj is None or t[k] < tj]
    prima_g = [k for k in dopo if tg is None or t[k] < tg]
    r = {"caso": nome,
         "vreg_min": min(vg[k] for k in dopo), "vreg_max": max(vg[k] for k in dopo),
         "vrelay_min": min(vr[k] for k in dopo), "vrelay_max": max(vr[k] for k in dopo),
         "bobina_min_V": min(vr[k] - mc[k] for k in chiuso) if chiuso else "",
         "permit_min_V": min(vr[k] - pc[k] for k in prima_g) if prima_g else "",
         "mute_g_fine": S["v(mute_g)"][-1], "permit_g_fine": S["v(permit_g)"][-1],
         "k501_fine": S["v(k501_f)"][-1],
         "anticipo_guadagno_ms": "" if tj is None or tg is None else (tj + T_RIL - tg) * 1e3,
         "vrelay_fine": vr[-1]}
    return r


CAMPI = ["caso", "vreg_min", "vreg_max", "vrelay_min", "vrelay_max", "bobina_min_V", "permit_min_V",
         "mute_g_fine", "permit_g_fine", "k501_fine", "anticipo_guadagno_ms", "vrelay_fine"]

if __name__ == "__main__":
    seq, out, lista = sys.argv[1], sys.argv[2], sys.argv[3]
    nomi = [r.strip() for r in open(lista[1:]) if r.strip()]
    righe = [caso(seq, n) for n in nomi]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPI)
        w.writeheader()
        for r in righe:
            w.writerow({a: ("%.4f" % b if isinstance(b, float) else b) for a, b in r.items()})
    print("scritto %s: %d casi" % (out, len(righe)))
