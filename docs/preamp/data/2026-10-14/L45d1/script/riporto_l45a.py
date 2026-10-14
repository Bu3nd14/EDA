#!/usr/bin/env python3
"""L45d1: L45a's table (the faults of the gain block) in the form of ADR-070. Solo stdlib.

    riporto_l45a.py <data/2026-10-13> <data/2026-10-14/L45d1>

One row per mode of L45a/fmea_blocco.csv (112), from the CSVs already published, no new run:
  - effect: the filtered peak with today's loads, worst jack, per position (A, F1, F2, B, B at
    +10 dB), from fmea_blocco.csv; the row's figure is the largest;
  - verdict: P10 (ADR-069, the criterion of a fault during listening with the rails inside), from
    L45b/p10_blocco.csv, raw and unloaded, per position: FUORI if one position is out;
  - severity: 4 if P10 is out, else from the peak (motore.g_misurata: <= 100 uV 1, <= 2 mV 2,
    else 3 - above the ceiling for at most 100 ms is still 3, ADR-070); 5 if fmea_blocco's
    'calore' names a part beyond its limits (L45a's sintesi.py writes there only those);
  - detection: 2 if the block's output goes to a rail or oscillates in one position (L45a's
    classes 'rail+', 'rail-', 'oscilla'): the music stops or breaks, and stays so; or if P10 is
    out (a thump above the ceiling for more than 100 ms, which nobody misses); 3 otherwise,
    latent - at most a pop at the fault, then the music plays: L45a's 'continua' is a shift of more
    than 50 mV at the block's output, which the output capacitors keep from the jack and which
    clips nothing below ~9,7 V, and a part may cook in silence (the Vbe multiplier, NC-062). ADR-070:
    2 is "seen at once by the listener (it does not play, ...)", 3 "not seen until a second event".
    Never 1 - the supervisor does not act (0,90 A against 1 A, L45a);
  - probability: the part's type (classi_l45a.py) x the mode's fraction x the instances, the
    positions where the part exists (A, F1, F2, B; B at +10 dB is the same block) times the two
    channels: 8, R113 4 (blocks A and B), R138 / R143 2 (block B).
Writes <L45d1>/fmea_blocco_adr070.csv / .md. Checks the counts of L45b (257 positions out of 544,
on 58 modes) and of L45a (26 modes with a second fault by heat).
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore  # noqa: E402
import classi_l45a as K  # noqa: E402

D, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
blocco = list(csv.DictReader(open(os.path.join(D, "L45a", "fmea_blocco.csv"))))
p10 = list(csv.DictReader(open(os.path.join(D, "L45b", "p10_blocco.csv"))))
POS = ["A", "F1", "F2", "B", "B_g10"]

per_modo = {}
for q in p10:
    per_modo.setdefault(q["modo"], {})[q["posizione"]] = q
n_fuori = sum(1 for q in p10 if q["p10"] != "entro")
if (len(p10), n_fuori, len([m for m, d in per_modo.items() if any(q["p10"] != "entro" for q in d.values())])) != (544, 257, 58):
    raise SystemExit("RIFIUTATO: p10_blocco.csv non da' i conti di L45b (544 posizioni, 257 fuori, 58 modi)")


def volt(s):
    """A peak cell of fmea_blocco: a number, '>=x' (a lower bound: x), '-' (the part is absent)."""
    s = s.strip()
    if s in ("", "-"):
        return None
    return float(s.lstrip(">="))


righe = []
for b in blocco:
    modo = b["modo"]
    ref, suf = modo.rsplit("_", 1)
    q = per_modo[modo]
    picchi = {p: volt(b[p + "_V"]) for p in POS}
    pm = max(v for v in picchi.values() if v is not None)
    fuori = [p for p in POS if p in q and q[p]["p10"] != "entro"]
    sopra = max(max(float(q[p][j + "_sopra_ms"]) for j in ("main", "fix1", "fix2")) for p in q)
    if fuori:
        verd = "FUORI: " + ", ".join(
            "%s %.0f ms%s" % (p, max(float(q[p][j + "_sopra_ms"]) for j in ("main", "fix1", "fix2")),
                              " (ancora sopra alla fine)" if "alla fine" in q[p]["p10"] else "")
            for p in fuori)
    else:
        verd = "entro" + (", sopra il tetto per meno di 100 ms" if pm > motore.TETTO else
                          ", sopra l'obiettivo di 2 mV" if pm > motore.OBIETTIVO else "")
    G = motore.g_misurata(verd, pm, None)
    calore = b["calore"].strip()
    if calore:
        G = 5
    classi = {b["classe_A"].strip(), b["classe_B"].strip()}
    R = 2 if (classi & {"rail+", "rail-", "oscilla"} or fuori) else 3
    # probability: the instances are the positions where the part exists, times two channels
    t = K.tipo_di(ref)
    fit, fonte, dist = K.TIPI[t]
    chiave = K.CHIAVE[suf]
    istanze = 2 * len([p for p in ("A", "F1", "F2", "B") if p in q])
    fm = fit * dist[chiave] * istanze
    P = motore.classe_p(fm)
    rim = []
    if fuori:
        rim.append("rivelatore")
    if calore:
        rim.append("calore_vbe" if ref in K.VBE else "calore")
    if not rim:
        rim.append("dentro" if G == 3 else "nessuno")
    nota = "; ".join(x for x in (
        ("calore: " + calore) if calore else "",
        ("uscita del blocco: A %s, B %s" % (b["classe_A"] or "-", b["classe_B"] or "-")),
        b["note"].strip()) if x)
    righe.append(dict(
        ref=ref, funzione=b["parte"], modo=b["guasto"], caso=modo, come="simulato (L45a, L45b a vuoto)",
        criterio="P10", verdetto=verd, G=G, tipo=t, fit_parte="%g" % fit, fonte=fonte,
        frazione="%s %.3g x %d" % (chiave, dist[chiave], istanze), fit_modo="%.3g" % fm, P=P, R=R,
        priorita=motore.priorita(G, P, R), rimedi=" / ".join(K.RIMEDI[x] for x in rim),
        picco_V="%.4g" % pm, picco_dB="%.1f" % motore.db(pm),
        **{"picco_%s_V" % p: b[p + "_V"] for p in POS},
        posizioni_fuori=" ".join(fuori), sopra_max_ms="%.1f" % sopra, calore=calore,
        classe_A=b["classe_A"], classe_B=b["classe_B"], nota=nota))

n_cal = sum(1 for r in righe if r["calore"])
if len(righe) != 112 or n_cal != 26:
    raise SystemExit("RIFIUTATO: %d modi (attesi 112), %d col calore (attesi 26)" % (len(righe), n_cal))

CAMPI = ["ref", "funzione", "modo", "caso", "come", "criterio", "verdetto", "G", "tipo", "fit_parte",
         "fonte", "frazione", "fit_modo", "P", "R", "priorita", "rimedi", "picco_V", "picco_dB"] + \
        ["picco_%s_V" % p for p in POS] + ["posizioni_fuori", "sopra_max_ms", "calore", "classe_A",
                                            "classe_B", "nota"]
MD = ["ref", "funzione", "modo", "verdetto", "G", "fit_modo", "P", "R", "priorita", "picco_V",
      "picco_dB", "sopra_max_ms", "nota", "rimedi"]
motore.scrivi(os.path.join(OUT, "fmea_blocco_adr070"), righe, CAMPI, MD,
              "L45a — i guasti del blocco di guadagno nella forma di ADR-070 (riporto di L45d1)",
              "Una riga per modo (112). L'effetto e' il picco filtrato coi carichi di oggi, il jack peggiore "
              "della posizione peggiore (`data/2026-10-13/L45a/fmea_blocco.csv`); il verdetto e' P10 "
              "(ADR-069), grezzo e a vuoto, posizione per posizione (`data/2026-10-13/L45b/p10_blocco.csv`). "
              "Le colonne di ADR-070 le aggiunge `script/riporto_l45a.py` (le regole nella sua "
              "intestazione). Il FIT conta le istanze del blocco: 8 (quattro posizioni per due canali), "
              "4 per R113, 2 per R138 / R143. Ordinata per priorita', poi gravita', poi FIT.",
              {"picco_V": "picco filtrato, il peggiore (V)", "picco_dB": "dB SPL a 1 m",
               "sopra_max_ms": "sopra 0,87 V a vuoto, il peggiore (ms)"})
print("scritto fmea_blocco_adr070.csv / .md: %d modi, %d fuori da P10, %d col calore; priorita' %s"
      % (len(righe), sum(1 for r in righe if r["posizioni_fuori"]), n_cal, motore.conta(righe)))
