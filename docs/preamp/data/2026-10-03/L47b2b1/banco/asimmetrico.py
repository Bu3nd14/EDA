"""asimmetrico.py - L47b2b1: il migliore inserimento e il migliore rilascio di famiglia_versi.csv,
per ciascun criterio di E3, e la corsa che li accoppia (tabelle diverse nei due versi).

Il criterio:
  e3      E3 a 20 kHz al connettore (rapido.zin_e3), >= 102 kohm, in tutto il verso;
  carico  il solo ramo della cella, R_s + (R_p || 1 M) >= 102 kohm (L29b, ldr_catena/post.py).
Inserimento: mute <= -70 dB a fine sfumatura su tutte le curve.

    /usr/bin/python3 asimmetrico.py <famiglia_versi.csv> <uscita.json> [td_s]
"""
import csv
import json
import sys

import famiglia as F
if len(sys.argv) > 3:          # il tempo della griglia (famiglia.py ... td_s)
    F.TD = float(sys.argv[3])
import rapido as R

righe = list(csv.DictReader(open(sys.argv[1])))
for r in righe:
    for k in list(r):
        r[k] = float(r[k])


def migliore(verso, crit):
    kE = {"e3": "E3_%s_k", "carico": "carico_%s_k"}[crit] % verso
    ok = [r for r in righe if r[kE] >= 102 and (verso == "rel" or r["mute_max_dB"] <= -70)]
    return min(ok, key=lambda r: r["S_" + verso]) if ok else None


def corsa(pi, pr):
    si, di = F.funzioni(*F.tabelle(pi["a"], pi["b"], pi["i0"], pi["g"]))
    sr, dr = F.funzioni(*F.tabelle(pr["a"], pr["b"], pr["i0"], pr["g"]))
    t_ins, td = R.T_INS, F.TD
    t_rel = t_ins + td + 1.0

    def d(t):
        if t < t_rel:
            return min(max((t - t_ins) / td, 0.0), 1.0)
        return min(max(1 - (t - t_rel) / td, 0.0), 1.0)
    out = {}
    for c in "ABCDE":
        r = R.sequenza(lambda t: si(d(t)) if t < t_rel else sr(d(t)),
                       lambda t: di(d(t)) if t < t_rel else dr(d(t)), td, (c, c))
        out[c] = {k: round(r[k] / (1e3 if k.startswith(("e3", "carico")) else 1), 2)
                  for k in ("S_ins_dB", "S_rel_dB", "liv_mute_dB", "e3_ins", "e3_rel",
                            "carico_ins", "carico_rel")}
    return out


def par(r):
    return {k: r[k] for k in ("a", "b", "i0", "g")}


ris = {}
for crit in ("e3", "carico"):
    pi, pr = migliore("ins", crit), migliore("rel", crit)
    print("== criterio %s" % crit)
    print("   inserimento:", None if pi is None else (par(pi), pi["S_ins"], pi["E3_ins_k"], pi["carico_ins_k"], pi["mute_max_dB"]))
    print("   rilascio:   ", None if pr is None else (par(pr), pr["S_rel"], pr["E3_rel_k"], pr["carico_rel_k"]))
    if pi is None or pr is None:
        ris[crit] = None
        continue
    c = corsa(pi, pr)
    S = max(max(v["S_ins_dB"], v["S_rel_dB"]) for v in c.values())
    e3 = min(min(v["e3_ins"], v["e3_rel"]) for v in c.values())
    car = min(min(v["carico_ins"], v["carico_rel"]) for v in c.values())
    prof = max(v["liv_mute_dB"] for v in c.values())
    print("   accoppiati: S %.2f dB, mute %.1f dB, E3 %.1f k, carico %.1f k" % (S, prof, e3, car))
    ris[crit] = {"inserimento": par(pi), "rilascio": par(pr), "S_max_dB": S, "mute_max_dB": prof,
                 "E3_min_k": e3, "carico_min_k": car, "per_curva": c}
json.dump(ris, open(sys.argv[2], "w"), indent=1)
