"""cerca_pilota.py - L47b2b1, NC-045: i parametri migliori di P1 e P2 (pilota_semplice.py).

Il micro da' i fronti: serie giu' a t_ins + ds_i, su a t_rel + ds_r; derivazione su a t_ins + dp_i,
giu' a t_rel + dp_r. Ogni stringa ha tau_su e tau_giu. Ricerca casuale (N punti) e poi locale,
sul costo
    S peggiore (due versi) + 2 dB per dB di mute meno profondo di -70 + 1 per kohm di E3 sotto 102
sulle curve della ricerca (D, E, A: le estreme); poi il migliore su A-E e, per P2, agli angoli
(15 e 60 C, Vbe -+18 mV, RC +-10 %).

    /usr/bin/python3 cerca_pilota.py p1|p2 <N> <seme> <uscita.json> [--carico]
--carico: il vincolo e' il criterio di L29b (ramo della cella >= 102 k) invece di E3 a 20 kHz.
"""
import json
import math
import random
import sys
from multiprocessing import Pool

import pilota_semplice as P
import rapido as R

TIPO, N, SEME, USCITA = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
CARICO = "--carico" in sys.argv
TD = 3.0
T_INS = R.T_INS
T_REL = T_INS + TD + 1.0
RE = 100.0
CURVE_CERCA = "DEA"
# (nome, basso, alto, log?)
SPAZIO = [("ds_i", 0.0, 1.5, False), ("ds_r", 0.0, 2.9, False),
          ("dp_i", 0.0, 2.9, False), ("dp_r", 0.0, 1.5, False),
          ("ts_su", 0.02, 5.0, True), ("ts_giu", 0.02, 5.0, True),
          ("tp_su", 0.02, 5.0, True), ("tp_giu", 0.02, 5.0, True)]


def correnti(p, angolo=(25.0, 0.0, 1.0)):
    tc, dv, krc = angolo
    s = P.RC([(0.0, 1), (T_INS + p["ds_i"], 0), (T_REL + p["ds_r"], 1)],
             p["ts_su"] * krc, p["ts_giu"] * krc)
    d = P.RC([(0.0, 0), (T_INS + p["dp_i"], 1), (T_REL + p["dp_r"], 0)],
             p["tp_su"] * krc, p["tp_giu"] * krc)
    if TIPO == "p1":
        return P.p1(s), P.p1(d)
    vb = P.vb_top_per(P.ION, RE)
    e = P.Esponenziale(vb, RE, tc, dv)
    return e.corrente(s), e.corrente(d)


def valuta(p, curve=CURVE_CERCA, angoli=((25.0, 0.0, 1.0),)):
    S, prof, e3, car, det = 0.0, -999.0, 1e12, 1e12, []
    for ang in angoli:
        for c in curve:
            i_s, i_p = correnti(p, ang)
            r = R.sequenza(i_s, i_p, TD, (c, c))
            S = max(S, r["S_ins_dB"], r["S_rel_dB"])
            prof = max(prof, r["liv_mute_dB"])
            e3 = min(e3, r["e3_min"])
            car = min(car, r["carico_min"])
            det.append((ang, c, round(r["S_ins_dB"], 2), round(r["S_rel_dB"], 2),
                        round(r["liv_mute_dB"], 1), round(r["e3_min"] / 1e3, 1),
                        round(r["carico_min"] / 1e3, 1)))
    vinc = car if CARICO else e3
    costo = S + 2.0 * max(0.0, prof + 70.0) + max(0.0, 102e3 - vinc) / 1e3
    return {"costo": costo, "S": S, "prof": prof, "E3_k": e3 / 1e3, "carico_k": car / 1e3,
            "par": p, "det": det}


def casuale(rng):
    p = {}
    for nome, lo, hi, lg in SPAZIO:
        p[nome] = math.exp(rng.uniform(math.log(lo), math.log(hi))) if lg else rng.uniform(lo, hi)
    return p


def vicino(p, rng, scala):
    q = dict(p)
    for nome, lo, hi, lg in SPAZIO:
        if lg:
            q[nome] = min(max(q[nome] * math.exp(rng.gauss(0, scala)), lo), hi)
        else:
            q[nome] = min(max(q[nome] + rng.gauss(0, scala * (hi - lo) / 3), lo), hi)
    return q


def main():
    rng = random.Random(SEME)
    with Pool(10) as pool:
        punti = [casuale(rng) for _ in range(N)]
        ris = pool.map(valuta, punti, chunksize=2)
        ris.sort(key=lambda r: r["costo"])
        print("casuale: migliore costo %.2f S %.2f prof %.1f E3 %.1f k carico %.1f k" % (
            ris[0]["costo"], ris[0]["S"], ris[0]["prof"], ris[0]["E3_k"], ris[0]["carico_k"]), flush=True)
        migliori = ris[:5]
        for scala in (0.5, 0.25, 0.12, 0.06):
            for _ in range(3):
                cand = [vicino(m["par"], rng, scala) for m in migliori for _ in range(4)]
                nuovi = pool.map(valuta, cand, chunksize=2)
                migliori = sorted(migliori + nuovi, key=lambda r: r["costo"])[:5]
            print("scala %.2f: costo %.2f S %.2f prof %.1f E3 %.1f k carico %.1f k" % (
                scala, migliori[0]["costo"], migliori[0]["S"], migliori[0]["prof"],
                migliori[0]["E3_k"], migliori[0]["carico_k"]), flush=True)
        best = migliori[0]["par"]
        angoli = [(25.0, 0.0, 1.0)]
        if TIPO == "p2":
            angoli = [(tc, dv, k) for tc in (15.0, 60.0) for dv in (-18e-3, 18e-3) for k in (0.9, 1.1)]
        else:
            angoli = [(25.0, 0.0, k) for k in (0.9, 1.0, 1.1)]
        tutti = pool.starmap(valuta, [(best, c, (a,)) for a in angoli for c in "ABCDE"])
    S = max(r["S"] for r in tutti)
    prof = max(r["prof"] for r in tutti)
    out = {"tipo": TIPO, "vincolo": "carico L29b" if CARICO else "E3 20 kHz", "par": best,
           "nominale_curve_cerca": {k: migliori[0][k] for k in ("S", "prof", "E3_k", "carico_k")},
           "angoli_A_E": {"S_max": round(S, 2), "mute_max_dB": round(prof, 1),
                          "E3_min_k": round(min(r["E3_k"] for r in tutti), 1),
                          "carico_min_k": round(min(r["carico_k"] for r in tutti), 1)},
           "dettaglio": [d for r in tutti for d in r["det"]]}
    json.dump(out, open(USCITA, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("tipo", "vincolo", "par", "nominale_curve_cerca", "angoli_A_E")}, indent=1))


if __name__ == "__main__":
    main()
