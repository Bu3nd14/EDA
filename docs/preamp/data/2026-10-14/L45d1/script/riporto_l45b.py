#!/usr/bin/env python3
"""L45d1: L45b's table (the faults of the controls) in the form of ADR-070. Solo stdlib.

    riporto_l45b.py <data/2026-10-13/L45b> <data/2026-10-14/L45d1>          the table
    riporto_l45b.py --prova                                                 the reader on known cells

L45b wrote its figures as text ("7,1 µV (10 dB SPL)", "≤ 29,7 mV (~83 dB SPL), ADR-051",
"princ. 579 ms; Singxer 3082 ms"). This reads them back:
  - the peak: every number followed by nV / µV / uV / mV / V in the columns 'principale' and
    'fisse', the largest ('< 1 µV' reads 1 µV, '0 (nessun gradino)' reads 0; the dB SPL are not
    read, they follow from the volts);
  - P10: every number followed by 'ms' in 'p10_vuoto' and 'p10_carico', the largest; above 100 ms
    the row is out of P10 (ADR-069).
Severity: 4 out of P10, else from the peak (motore.g_misurata), raised to the row's minimum
(classi_l45b.CLASSI). A row with no figure and no declared minimum above 1 is refused. Writes
<L45d1>/fmea_controlli_adr070.csv / .md.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motore  # noqa: E402
import classi_l45b as K  # noqa: E402

UNITA = {"nV": 1e-9, "µV": 1e-6, "uV": 1e-6, "mV": 1e-3, "V": 1.0}
NUM = r"(\d+(?:[.,]\d+)?)"


def volt(s):
    """The largest voltage in a cell, or None if the cell has none."""
    v = [float(x.replace(",", ".")) * UNITA[u] for x, u in re.findall(NUM + r"\s*(nV|µV|uV|mV|V)\b", s)]
    if v:
        return max(v)
    return 0.0 if s.strip().startswith("0") else None


def ms(s):
    v = [float(x.replace(",", ".")) for x in re.findall(NUM + r"\s*ms\b", s)]
    return max(v) if v else None


if sys.argv[1:] == ["--prova"]:
    casi = [("7,1 µV (10 dB SPL)", 7.1e-6), ("≤ 29,7 mV (~83 dB SPL), ADR-051", 29.7e-3),
            ("13,6 V (136 dB SPL)", 13.6), ("< 1 µV", 1e-6), ("0 (nessun gradino)", 0.0),
            ("1,55 µV; Stax 5 dB SPL", 1.55e-6), ("7,1 µV; Stax 18 dB SPL", 7.1e-6),
            ("≤ la continua della sorgente", None), ("—", None)]
    casi_ms = [("princ. 579 ms; Singxer 3082 ms; Stax 3082 ms (6 s)", 3082.0), ("0 ms", 0.0),
               ("princ. ≥ 2000 ms", 2000.0), ("—", None), ("0 ms per una sorgente sana", 0.0)]
    def diverso(x, a):
        return (x is None) != (a is None) or (a is not None and abs(x - a) > 1e-9 * max(abs(a), 1e-12))
    ko = [(s, volt(s), a) for s, a in casi if diverso(volt(s), a)] + \
         [(s, ms(s), a) for s, a in casi_ms if diverso(ms(s), a)]
    print("lettore: %d celle, %d sbagliate %s" % (len(casi) + len(casi_ms), len(ko), ko))
    sys.exit(1 if ko else 0)

L, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
pubblicata = list(csv.DictReader(open(os.path.join(L, "fmea_controlli.csv"))))
righe = []
for p in pubblicata:
    n = int(p["n"])
    r = dict(p)
    r["funzione"] = next((v for k, v in K.GRUPPI.items() if p["gruppo"].startswith(k)), p["gruppo"])
    r["ref"], r["modo"], r["nota"] = p["parte"], p["modo"], p["effetto"]
    pm, pf = volt(p["principale"]), volt(p["fisse"])
    t10 = [x for x in (ms(p["p10_vuoto"]), ms(p["p10_carico"])) if x is not None]
    r["picco_V"] = "" if pm is None and pf is None else "%.3g" % max(pm or 0, pf or 0)
    r["sopra_max_ms"] = "%g" % max(t10) if t10 else ""
    if n in K.RIMANDO:
        r["come"] = "rimando a " + K.RIMANDO[n]
        r["verdetto"] = "vedi " + K.RIMANDO[n].split(":")[0].split(" (")[0]
        righe.append(r)
        continue
    termini, gmin, R, rim, nota = K.CLASSI[n]
    r["come"] = p["fonte"]
    fuori = bool(t10) and max(t10) > 100
    r["criterio"] = p["requisiti"]
    if fuori:
        r["verdetto"] = "FUORI: P10 (a vuoto %s; col carico %s)" % (p["p10_vuoto"], p["p10_carico"])
    else:
        m = max(pm or 0, pf or 0)
        r["verdetto"] = "entro" + (", sopra il tetto per meno di 100 ms" if m > motore.TETTO else
                                   ", sopra l'obiettivo di 2 mV" if m > motore.OBIETTIVO else "")
    if pm is None and pf is None and gmin <= 1:
        raise SystemExit("RIFIUTATO: riga %d senza numero e senza gravita' dichiarata" % n)
    G = max(motore.g_misurata(r["verdetto"], pm, pf), gmin)
    fm, desc, fonti = 0.0, [], []
    for tipo, chiave, k in termini:
        fit, fonte, dist = K.TIPI[tipo]
        f = motore.fr(dist, chiave)
        fm += fit * f * k
        desc.append("%s %s %.3g%s" % (tipo, chiave, f, (" x %d" % k) if k > 1 else ""))
        if fonte not in fonti:
            fonti.append(fonte)
    P = motore.classe_p(fm)
    r.update(G=G, tipo=" + ".join(t[0] for t in termini), fit_parte=" + ".join(
        "%g" % K.TIPI[t[0]][0] for t in termini), fonte="; ".join(fonti), frazione=" + ".join(desc),
        fit_modo="%.3g" % fm, P=P, R=R, priorita=motore.priorita(G, P, R), rimedi=K.RIMEDI[rim])
    if nota:
        r["nota"] = r["nota"] + "; " + nota
    righe.append(r)

assert len(righe) == len(pubblicata) == 78
mancano = set(range(1, 79)) - set(K.CLASSI) - set(K.RIMANDO)
if mancano:
    raise SystemExit("RIFIUTATO: righe senza classe ne' rimando: %s" % sorted(mancano))

CAMPI = ["n", "ref", "funzione", "modo", "come", "criterio", "verdetto", "G", "tipo", "fit_parte",
         "fonte", "frazione", "fit_modo", "P", "R", "priorita", "rimedi", "picco_V", "sopra_max_ms",
         "principale", "fisse", "p10_vuoto", "p10_carico", "a_chi", "nota"]
MD = ["n", "ref", "funzione", "modo", "verdetto", "G", "fit_modo", "P", "R", "priorita",
      "principale", "fisse", "p10_vuoto", "nota", "rimedi"]
motore.scrivi(os.path.join(OUT, "fmea_controlli_adr070"), righe, CAMPI, MD,
              "L45b — i guasti dei controlli nella forma di ADR-070 (riporto di L45d1)",
              "Le righe, gli effetti e i numeri sono quelli di L45b (`data/2026-10-13/L45b/fmea_controlli.csv`), "
              "riletti dal testo da `script/riporto_l45b.py` (il lettore e' provato con `--prova`). Le "
              "colonne di ADR-070 vengono da `script/classi_l45b.py`; le righe che rimandano a L45c1, L45c2 "
              "o L54 non hanno classe qui. Ordinata per priorita', poi gravita', poi FIT.",
              {"n": "n", "principale": "al principale", "fisse": "alle fisse", "p10_vuoto": "P10 a vuoto"})
print("scritto fmea_controlli_adr070.csv / .md: %d righe, %d classificate, %d rimandi; fuori da P10 %d; "
      "priorita' %s" % (len(righe), len(K.CLASSI), len(K.RIMANDO),
                        sum(1 for r in righe if r.get("verdetto", "").startswith("FUORI")), motore.conta(righe)))
